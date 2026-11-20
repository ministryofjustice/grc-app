"""Real Redis regressions; never use the application's configured Redis or app factory.

Run only in an isolated synthetic environment with SESSION_TEST_REDIS_DISPOSABLE=1
and SESSION_TEST_REDIS_URL pointing at its dedicated, disposable Redis server.
Ancestor conftests import application configuration before these fixtures run.
"""

import json
import os
from time import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import jwt
import pytest
import redis
import requests
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from flask import Flask, session
from flask_session import Session
from jinja2 import DictLoader

from grc.one_login import oneLogin
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_token_validator import jti_cache
from grc.one_login.one_login_user_info_request import OneLoginUserInfoRequest
from grc.save_and_return import saveAndReturn
from grc.utils.decorators import LoginRequired


@pytest.fixture
def redis_store():
    if os.environ.get("SESSION_TEST_REDIS_DISPOSABLE") != "1":
        pytest.skip("Requires an explicitly disposable session-test Redis server")
    url = os.environ.get("SESSION_TEST_REDIS_URL")
    if not url:
        pytest.fail("SESSION_TEST_REDIS_URL is required when opting in")
    store = redis.Redis.from_url(url, socket_connect_timeout=2, socket_timeout=2)
    owned_keys = set()
    try:
        store.ping()
        yield store, owned_keys
    finally:
        try:
            if owned_keys:
                store.delete(*owned_keys)
        finally:
            store.close()


@pytest.fixture(scope="module")
def signing_keys():
    return (
        rsa.generate_private_key(public_exponent=65537, key_size=2048),
        ec.generate_private_key(ec.SECP256R1()),
    )


@pytest.fixture
def lifecycle(redis_store, signing_keys, monkeypatch, request):
    store, owned_keys = redis_store
    rsa_key, ec_key = signing_keys
    config = SimpleNamespace(
        client_id="session-test-client", issuer="https://identity.example.invalid",
        jwks_uri="https://identity.example.invalid/jwks",
        end_session_endpoint="https://identity.example.invalid/logout",
        logout_redirect_url_save_and_exit="http://localhost/save-and-return/exit-application",
    )
    monkeypatch.setattr(OneLoginConfig, "_instance", config)
    jwk = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(ec_key.public_key()))
    jwk["kid"] = "session-test-ec"

    def synthetic_http(_self, method, url, **kwargs):
        if method.upper() != "GET" or url != config.jwks_uri:
            pytest.fail("Unexpected outbound HTTP request in session lifecycle test")
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({"keys": [jwk]}).encode()
        return response

    monkeypatch.setattr(requests.sessions.Session, "request", synthetic_http)
    jti_cache.clear()
    request.addfinalizer(jti_cache.clear)
    app = Flask(__name__)
    app.config.update(
        TESTING=True, SECRET_KEY="synthetic-session-test-secret",
        SESSION_TYPE="redis", SESSION_REDIS=store, SESSION_PERMANENT=True,
        # The real mapper hardcodes session:<cookie>; retain production defaults.
        SESSION_KEY_PREFIX="session:", SESSION_USE_SIGNER=False,
    )
    Session(app)
    app.jinja_loader = DictLoader({
        "save-and-return/exit-application.html": "Saved {{ reference_number }}",
    })
    app.register_blueprint(oneLogin)
    app.register_blueprint(saveAndReturn)

    @app.get("/protected")
    @LoginRequired
    def protected():
        return session["reference_number"]

    def new_session(sub=None):
        sub = sub or f"session-test-{uuid4()}"
        mapping = f"user_sub:{sub}"
        owned_keys.add(mapping)
        id_token = jwt.encode(
            {"sub": sub, "iss": config.issuer, "aud": config.client_id,
             "iat": int(time()), "exp": int(time()) + 300},
            rsa_key, algorithm="RS256", headers={"kid": "session-test-rsa"},
        )
        client = app.test_client()
        with client.session_transaction() as state:
            key = f"session:{state.sid}"
            owned_keys.add(key)
            state.update(reference_number="ABCD1234", id_token=id_token, state="test-state")
        cookie = client.get_cookie("session").value
        assert key == f"session:{cookie}"
        # Use the actual mapper with the already-established request cookie,
        # as in the callback; do not manufacture Redis session payloads or sets.
        with app.test_request_context(headers={"Cookie": f"session={cookie}"}):
            OneLoginUserInfoRequest.store_user_info_redis_mapping(sub)
        persisted = store.get(key)
        assert persisted is not None
        assert store.sismember(mapping, key)
        return SimpleNamespace(client=client, cookie=cookie, key=key, mapping=mapping,
                               sub=sub, id_token=id_token, persisted=persisted)

    def logout_token(subject, **changes):
        now = int(time())
        claims = {"iss": config.issuer, "aud": config.client_id, "sub": subject,
                  "iat": now, "exp": now + 300, "jti": str(uuid4()),
                  "events": {"http://schemas.openid.net/event/backchannel-logout": {}}}
        claims.update(changes)
        # Keep the real validator's existing signature-verification policy intact.
        return jwt.encode(claims, ec_key, algorithm="ES256", headers={"kid": jwk["kid"]})

    return SimpleNamespace(app=app, store=store, new_session=new_session,
                           logout_token=logout_token, config=config)


def assert_access(lifecycle, record, allowed):
    client = lifecycle.app.test_client()
    client.set_cookie("session", record.cookie)
    response = client.get("/protected")
    if allowed:
        assert response.status_code == 200
        assert response.data == b"ABCD1234"
    else:
        assert response.status_code == 302
        assert response.headers["Location"] == "/"


def assert_retained(lifecycle, *records):
    for record in records:
        assert lifecycle.store.get(record.key) == record.persisted
        assert lifecycle.store.sismember(record.mapping, record.key)
        assert_access(lifecycle, record, allowed=True)


def test_explicit_logout_deletes_session_only_after_return(lifecycle):
    user, unrelated = lifecycle.new_session(), lifecycle.new_session()
    assert_retained(lifecycle, user, unrelated)
    response = user.client.get("/one-login/logout")
    assert response.status_code == 302
    redirect = urlsplit(response.headers["Location"])
    assert f"{redirect.scheme}://{redirect.netloc}{redirect.path}" == lifecycle.config.end_session_endpoint
    assert parse_qs(redirect.query) == {
        "id_token_hint": [user.id_token], "state": ["test-state"],
        "post_logout_redirect_uri": [lifecycle.config.logout_redirect_url_save_and_exit],
    }
    assert_retained(lifecycle, user, unrelated)
    # Simulate the provider's return locally; never follow its external URL.
    response = user.client.get(urlsplit(lifecycle.config.logout_redirect_url_save_and_exit).path)
    assert response.status_code == 200
    assert b"ABCD-1234" in response.data
    assert user.client.get_cookie("session") is None
    assert lifecycle.store.get(user.key) is None
    # Explicit logout does not remove the subject mapping in the current source.
    assert lifecycle.store.sismember(user.mapping, user.key)
    assert_access(lifecycle, user, allowed=False)
    assert_retained(lifecycle, unrelated)


def test_backchannel_logout_deletes_all_mapped_sessions_not_other_users(lifecycle):
    first = lifecycle.new_session()
    second = lifecycle.new_session(first.sub)
    unrelated = lifecycle.new_session()
    assert_retained(lifecycle, first, second, unrelated)
    assert lifecycle.store.smembers(first.mapping) == {first.key.encode(), second.key.encode()}
    response = lifecycle.app.test_client().post(
        "/one-login/back-channel-logout", data={"logout_token": lifecycle.logout_token(first.sub)},
    )
    assert response.status_code == 200
    assert lifecycle.store.exists(first.key, second.key, first.mapping) == 0
    assert_access(lifecycle, first, allowed=False)
    assert_access(lifecycle, second, allowed=False)
    assert_retained(lifecycle, unrelated)


@pytest.mark.parametrize("changes", [
    {"iss": "https://wrong.example.invalid"}, {"aud": "another-client"},
    {"exp": 0}, {"iat": 4102444800}, {"sub": None}, {"jti": None},
    {"events": {}}, None,
], ids=["issuer", "audience", "expired", "future-issued", "subject", "jti", "events", "malformed"])
def test_rejected_backchannel_token_preserves_sessions(lifecycle, changes):
    user, unrelated = lifecycle.new_session(), lifecycle.new_session()
    token = lifecycle.logout_token(user.sub, **changes) if changes is not None else "not-a-jwt"
    response = lifecycle.app.test_client().post(
        "/one-login/back-channel-logout", data={"logout_token": token},
    )
    # The real route also returns 200 on failure; persisted state is the oracle.
    assert response.status_code == 200
    assert_retained(lifecycle, user, unrelated)


def test_replayed_logout_token_cannot_delete_a_new_session_for_same_subject(lifecycle):
    original, unrelated = lifecycle.new_session(), lifecycle.new_session()
    token = lifecycle.logout_token(original.sub)
    sender = lifecycle.app.test_client()
    assert sender.post("/one-login/back-channel-logout", data={"logout_token": token}).status_code == 200
    assert lifecycle.store.exists(original.key, original.mapping) == 0
    assert_access(lifecycle, original, allowed=False)
    replacement = lifecycle.new_session(original.sub)
    assert replacement.cookie != original.cookie
    assert sender.post("/one-login/back-channel-logout", data={"logout_token": token}).status_code == 200
    assert lifecycle.store.get(original.key) is None
    assert_retained(lifecycle, replacement, unrelated)
