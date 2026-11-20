"""Offline dependency contracts; deliberately outside One Login's Redis fixtures.

These exercise real signing/parsing, not provider interoperability or a TLS handshake.
The application's existing unverified decode policy is characterized, not hardened.
"""

import base64
import hashlib
import json
import os
import re
import ssl
import sys
from contextlib import closing
from time import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import certifi
import jwt
import pytest
import requests
from botocore.httpsession import URLLib3Session, get_cert_path
from botocore.session import Session as BotocoreSession
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from flask import Flask, current_app, session
from notifications_python_client import authentication as notify_auth
from notifications_python_client.notifications import NotificationsAPIClient

from grc.one_login import one_login_jwt_handler as jwt_module
from grc.one_login import one_login_token_validator as validator_module
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.one_login.one_login_token_request import OneLoginTokenRequest
from grc.one_login.one_login_token_validator import OneLoginTokenValidator
from grc.one_login.one_login_user_info_request import OneLoginUserInfoRequest

KID = "synthetic-key"
JWKS_URI = "https://provider.invalid/jwks"
ACCESS_TOKEN = "synthetic-access-token"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    # Do not consult developer CA/proxy/profile files, credentials or key-log paths.
    for name in (
        "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "AWS_CA_BUNDLE", "SSL_CERT_FILE",
        "SSL_CERT_DIR", "SSLKEYLOGFILE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE",
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
    ):
        monkeypatch.delenv(name, raising=False)
    for name in ("AWS_CONFIG_FILE", "AWS_SHARED_CREDENTIALS_FILE", "BOTO_CONFIG", "NETRC"):
        monkeypatch.setenv(name, os.devnull)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")

    def blocked(*args, **kwargs):
        pytest.fail("Unexpected outbound transport in dependency compatibility test")

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", blocked)
    monkeypatch.setattr(URLLib3Session, "send", blocked)
    validator_module.jti_cache.clear()
    yield
    validator_module.jti_cache.clear()


@pytest.fixture(scope="module")
def keys():
    return {
        "RS256": rsa.generate_private_key(public_exponent=65537, key_size=2048),
        "ES256": ec.generate_private_key(ec.SECP256R1()),
        "ES384": ec.generate_private_key(ec.SECP384R1()),
        "ES512": ec.generate_private_key(ec.SECP521R1()),
    }


@pytest.fixture
def synthetic(keys, monkeypatch):
    config = SimpleNamespace(
        client_id="synthetic-client", issuer="https://provider.invalid",
        authorization_endpoint="https://provider.invalid/authorize",
        user_info_endpoint="https://provider.invalid/userinfo",
        token_endpoint="https://provider.invalid/token", jwks_uri=JWKS_URI,
        auth_redirect_uri="https://client.invalid/callback", kid=KID,
        scope="openid phone email", claims=OneLoginConfig.build_claims(), now=int(time()),
        private_key=keys["RS256"].private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
    )
    monkeypatch.setattr(jwt_module, "time", lambda: config.now)
    monkeypatch.setattr(validator_module, "time", lambda: config.now)
    app = Flask(__name__, static_folder=None)
    app.config.update(
        TESTING=True, SECRET_KEY="synthetic-session-secret-not-for-deployment",
        ONE_LOGIN_DISCOVERY_URL="https://provider.invalid/.well-known/openid-configuration",
    )
    with app.test_request_context():
        session["nonce"] = "synthetic-nonce"
        yield config


def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _jwk(key):
    numbers = key.public_key().public_numbers()

    def uint(value, size=None):
        return _b64(value.to_bytes(size or (value.bit_length() + 7) // 8, "big"))

    if isinstance(key, rsa.RSAPrivateKey):
        return dict(kid=KID, kty="RSA", n=uint(numbers.n), e=uint(numbers.e))
    curves = {"secp256r1": "P-256", "secp384r1": "P-384", "secp521r1": "P-521"}
    size = (key.key_size + 7) // 8
    return dict(kid=KID, kty="EC", crv=curves[key.curve.name],
                x=uint(numbers.x, size), y=uint(numbers.y, size))


@pytest.fixture
def serve_jwks(monkeypatch):
    def install(jwks_keys, status=200):
        def send(adapter, request, **kwargs):
            assert (request.method, request.url) == ("GET", JWKS_URI)
            assert kwargs["verify"] is True
            response = requests.Response()
            response.status_code = status
            response._content = json.dumps({"keys": jwks_keys}).encode()
            response.request = request
            return response

        monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", send)
    return install


def _claims(config):
    return dict(iss=config.issuer, aud=config.client_id, exp=config.now + 120,
                iat=config.now - 5, sub="synthetic-subject", nonce="synthetic-nonce",
                vot="Cl.Cm", at_hash=_b64(hashlib.sha256(ACCESS_TOKEN.encode()).digest()[:16]))


def _token(claims, key, algorithm="RS256", **headers):
    return jwt.encode(claims, key, algorithm=algorithm, headers={"kid": KID, **headers})


def test_authorization_request_and_client_assertion_signatures(synthetic, keys):
    redirect = OneLoginAuthorizationRequest(synthetic).build_authentication_redirect_url()
    query = parse_qs(urlsplit(redirect).query)
    assert redirect.startswith(synthetic.authorization_endpoint + "?")
    assert {k: query[k] for k in ("response_type", "scope", "client_id")} == {
        "response_type": ["code"], "scope": [synthetic.scope], "client_id": [synthetic.client_id],
    }
    request_token = query["request"][0]
    claims = jwt.decode(request_token, keys["RS256"].public_key(), algorithms=["RS256"],
                        audience=synthetic.authorization_endpoint, issuer=synthetic.client_id)
    assert jwt.get_unverified_header(request_token) == {"alg": "RS256", "kid": KID, "typ": "JWT"}
    assert claims == dict(
        response_type="code", scope=synthetic.scope, client_id=synthetic.client_id,
        state=session["state"], nonce=session["nonce"], redirect_uri=synthetic.auth_redirect_uri,
        aud=synthetic.authorization_endpoint, iss=synthetic.client_id, ui_locales="en",
        vtr=["Cl.Cm"], claims=synthetic.claims,
    )
    assert session["state"] and session["nonce"] and session["state"] != session["nonce"]
    request = OneLoginTokenRequest(synthetic)
    data = request._build_token_request_data("synthetic-code", synthetic.auth_redirect_uri)
    assertion = data.pop("client_assertion")
    assert data == dict(grant_type="authorization_code", code="synthetic-code",
                        redirect_uri=synthetic.auth_redirect_uri,
                        client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer")
    claims = jwt.decode(assertion, keys["RS256"].public_key(), algorithms=["RS256"],
                        audience=synthetic.token_endpoint, issuer=synthetic.client_id)
    assert jwt.get_unverified_header(assertion)["kid"] == KID
    assert UUID(claims["jti"]).version == 4
    assert claims == dict(aud=synthetic.token_endpoint, iss=synthetic.client_id,
                          sub=synthetic.client_id, iat=synthetic.now,
                          exp=synthetic.now + 300, jti=claims["jti"])
    assert request._build_token_request_headers() == {"Content-Type": "application/x-www-form-urlencoded"}


@pytest.mark.parametrize("algorithm", ["RS256", "ES256", "ES384", "ES512"])
def test_manual_jwks_round_trip(algorithm, keys, synthetic, serve_jwks):
    key = keys[algorithm]
    claims = _claims(synthetic)
    token = _token(claims, key, algorithm)
    serve_jwks([dict(kid="unrelated", kty="unsupported"), _jwk(key)])
    public_key = JWTHandler.get_public_key_from_jwks(JWKS_URI, token)
    assert public_key.public_numbers() == key.public_key().public_numbers()
    # Signature-verifying oracle is additional to, never a replacement for, the app path.
    assert jwt.decode(token, public_key, algorithms=[algorithm], audience=synthetic.client_id) == claims
    assert JWTHandler.decode_jwt_with_key(token, public_key, algorithm) == claims


@pytest.mark.parametrize("case, message", [
    ("missing-kid", "No 'kid' found in token header."),
    ("unknown-kid", "Public key with kid unknown not found in JWKS."),
    ("unsupported-key", f"Public key with kid {KID} not found in JWKS."),
    ("unsupported-curve", "Unsupported curve: P-999"),
    ("http-error", "Error fetching JWKS: 503"),
])
def test_jwks_errors(case, message, keys, serve_jwks):
    token = _token({}, keys["RS256"], kid="unknown" if case == "unknown-kid" else KID)
    if case == "missing-kid":
        token = jwt.encode({}, keys["RS256"], algorithm="RS256")
        # Default transport remains blocked: a missing KID must fail before fetching.
    else:
        key = _jwk(keys["RS256"])
        if case == "unsupported-key":
            key = dict(kid=KID, kty="oct")
        elif case == "unsupported-curve":
            key = dict(kid=KID, kty="EC", crv="P-999")
        serve_jwks([key], status=503 if case == "http-error" else 200)
    with pytest.raises(Exception, match="^" + re.escape(message) + "$"):
        JWTHandler.get_public_key_from_jwks(JWKS_URI, token)


@pytest.mark.parametrize("algorithm", ["RS256", "ES256"])
def test_existing_unverified_decode_policy(algorithm, keys, synthetic):
    claims = dict(aud="another-client", exp=synthetic.now - 60,
                  iat=synthetic.now + 60, nbf=synthetic.now + 60)
    token = _token(claims, keys[algorithm], algorithm)
    header, payload, signature = token.split(".")
    signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    tampered = ".".join((header, payload, signature))
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(tampered, keys[algorithm].public_key(), algorithms=[algorithm])
    assert JWTHandler.decode_jwt_with_key(tampered, keys[algorithm].public_key(), algorithm) == claims


def test_real_id_validator_accepts_valid_tokens(synthetic, keys, serve_jwks):
    serve_jwks([_jwk(keys["RS256"])])
    token = _token(_claims(synthetic), keys["RS256"])
    validator = OneLoginTokenValidator(synthetic)
    assert validator.validate_access_id_tokens(ACCESS_TOKEN, token) is None
    session.pop("nonce")
    with pytest.raises(Exception, match="Invalid nonce"):
        validator.validate_access_id_tokens(ACCESS_TOKEN, token)


@pytest.mark.parametrize("claim, value, exception, message", [
    ("iss", None, Exception, "Missing iss"), ("iss", "wrong", Exception, "Invalid iss"),
    ("aud", None, Exception, "Missing aud"), ("aud", "wrong", Exception, "Invalid aud"),
    ("aud", ["synthetic-client"], Exception, "Invalid aud"),
    ("exp", -1, Exception, "Token is expired"), ("exp", None, TypeError, None),
    ("exp", "not-an-integer", ValueError, None),
    ("iat", 4_000_000_000, Exception, "issued at time is after"), ("iat", None, TypeError, None),
    ("nonce", None, Exception, "Missing nonce"), ("nonce", "wrong", Exception, "Invalid nonce"),
    ("vot", None, Exception, "Missing vot"), ("vot", "wrong", Exception, "Invalid vot"),
    ("at_hash", None, Exception, "Missing 'at_hash'"),
    ("at_hash", "wrong", Exception, "Access token hash does not match"),
])
def test_app_enforces_id_claims_after_real_decode(claim, value, exception, message,
                                                 synthetic, keys, serve_jwks):
    claims = _claims(synthetic)
    if value is None:
        claims.pop(claim)  # Missing exp/iat deliberately retain the source's int(None) TypeError.
    else:
        claims[claim] = value
    serve_jwks([_jwk(keys["RS256"])])
    with pytest.raises(exception, match=message):
        OneLoginTokenValidator(synthetic).validate_access_id_tokens(
            ACCESS_TOKEN, _token(claims, keys["RS256"]))


@pytest.mark.parametrize("fault", [None, "sub", "jti", "events", "wrong-events"])
def test_real_es256_logout_validation_and_replay(fault, synthetic, keys, serve_jwks):
    claims = dict(iss=synthetic.issuer, aud=synthetic.client_id, exp=synthetic.now + 120,
                  iat=synthetic.now - 5, sub="synthetic-subject", jti="synthetic-jti",
                  events={"http://schemas.openid.net/event/backchannel-logout": {}})
    if fault == "wrong-events":
        claims["events"] = {}
    elif fault:
        claims.pop(fault)
    serve_jwks([_jwk(keys["ES256"])])
    token = _token(claims, keys["ES256"], "ES256")
    validator = OneLoginTokenValidator(synthetic)
    if fault:
        message = "Invalid events" if fault == "wrong-events" else f"Missing {fault}"
        with pytest.raises(Exception, match=message):
            validator.validate_logout_token(token)
    else:
        assert validator.validate_logout_token(token) == claims
        with pytest.raises(Exception, match="JTI already used"):
            validator.validate_logout_token(token)


@pytest.mark.parametrize("algorithm", ["RS256", "ES256"])
def test_2151_accepts_trailing_signature_padding(algorithm, keys, synthetic):
    claims = _claims(synthetic)
    token = _token(claims, keys[algorithm], algorithm)
    signature = token.rsplit(".", 1)[1]
    padded = token + "=" * (-len(signature) % 4)
    assert padded != token
    public_key = keys[algorithm].public_key()
    assert jwt.decode(padded, public_key, algorithms=[algorithm], audience=synthetic.client_id) == claims
    assert JWTHandler.decode_jwt_with_key(padded, public_key, algorithm) == claims


@pytest.mark.parametrize("bad_payload", [
    pytest.param(b"not-json", id="invalid-json"),
    pytest.param(b"[]", id="non-object"),
    pytest.param(b"[" * (sys.getrecursionlimit() + 100) + b"0" +
                 b"]" * (sys.getrecursionlimit() + 100), id="deeply-nested"),
])
def test_real_validator_wraps_malformed_payload(bad_payload, synthetic, keys, serve_jwks):
    segments = _token(_claims(synthetic), keys["RS256"]).split(".")
    segments[1] = _b64(bad_payload)
    token = ".".join(segments)
    serve_jwks([_jwk(keys["RS256"])])
    with pytest.raises(Exception, match="^Failed to decode token: Invalid payload") as error:
        OneLoginTokenValidator(synthetic).validate_access_id_tokens(ACCESS_TOKEN, token)
    assert isinstance(error.value.__context__, jwt.DecodeError)


@pytest.mark.parametrize("segment", [0, 1, 2])
def test_2151_rejects_base64url_junk_and_preserves_error_wrapping(segment, keys):
    segments = _token({}, keys["RS256"]).split(".")
    segments[segment] += "!!!!"
    with pytest.raises(Exception, match="^Failed to decode token: Invalid .* padding$") as error:
        JWTHandler.decode_jwt_with_key(".".join(segments), keys["RS256"].public_key())
    assert isinstance(error.value.__context__, jwt.DecodeError)


@pytest.mark.parametrize("token", ["", "not-a-jwt", "e30.e30"])
def test_decoder_wraps_incomplete_tokens(token, keys):
    with pytest.raises(Exception, match="^Failed to decode token: Not enough segments$") as error:
        JWTHandler.decode_jwt_with_key(token, keys["RS256"].public_key())
    assert isinstance(error.value.__context__, jwt.DecodeError)


def test_notify_sdk_real_hs256_signer(synthetic, monkeypatch):
    service_id = "00000000-0000-4000-8000-000000000001"
    secret = "00000000-0000-4000-8000-000000000002"
    monkeypatch.setattr(notify_auth, "epoch_seconds", lambda: synthetic.now)
    client = NotificationsAPIClient(api_key=f"synthetic-{service_id}-{secret}",
                                    base_url="https://notify.invalid")
    with client.request_session:
        url, kwargs = client._create_request_objects("/v2/notifications/email", {"synthetic": True}, None)
    assert url == "https://notify.invalid/v2/notifications/email"
    scheme, token = kwargs["headers"]["Authorization"].split(" ", 1)
    assert scheme == "Bearer" and isinstance(token, str)
    assert jwt.get_unverified_header(token) == {"typ": "JWT", "alg": "HS256"}
    assert jwt.decode(token, secret, algorithms=["HS256"], issuer=service_id) == {
        "iss": service_id, "iat": synthetic.now,
    }


def test_certifi_bundle_loads_in_required_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=certifi.where())
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
    assert context.cert_store_stats()["x509_ca"] > 0
    assert requests.certs.where() == requests.utils.DEFAULT_CA_BUNDLE_PATH == certifi.where()


@pytest.mark.parametrize("request_ca, curl_ca", [(None, None), (None, "curl"), ("requests", "curl")])
def test_requests_trust_selection(request_ca, curl_ca, monkeypatch):
    for name, value in (("REQUESTS_CA_BUNDLE", request_ca), ("CURL_CA_BUNDLE", curl_ca)):
        if value:
            monkeypatch.setenv(name, f"/synthetic/{value}-ca.pem")
    with requests.Session() as http:
        settings = http.merge_environment_settings(JWKS_URI, {}, None, None, None)
        expected = f"/synthetic/{request_ca or curl_ca}-ca.pem" if request_ca or curl_ca else True
        assert settings["verify"] == expected
        prepared = requests.Request("GET", JWKS_URI).prepare()
        _, tls = http.get_adapter(JWKS_URI).build_connection_pool_key_attributes(prepared, expected)
    assert tls["cert_reqs"] == "CERT_REQUIRED"
    if expected is True:
        assert tls["ssl_context"].cert_store_stats()["x509_ca"] > 0
    else:
        assert tls["ca_certs"] == expected


@pytest.mark.parametrize("override", [None, "/synthetic/aws-ca.pem"])
def test_botocore_trust_selection(override, monkeypatch):
    if override:
        monkeypatch.setenv("AWS_CA_BUNDLE", override)
    with closing(BotocoreSession().create_client(
        "s3", region_name="eu-west-2", endpoint_url="https://s3.invalid",
        aws_access_key_id="synthetic-access-key", aws_secret_access_key="synthetic-secret-key",
    )) as client:
        # Inspect the pinned SDK transport without issuing an AWS operation.
        verify = client._endpoint.http_session._verify
        assert verify == (override or True)
        assert get_cert_path(verify) == (override or certifi.where())


@pytest.mark.parametrize("boundary", ["discovery", "jwks", "token", "userinfo"])
def test_requests_sslerror_boundary(boundary, synthetic, keys, monkeypatch):
    failure = requests.exceptions.SSLError("synthetic CERTIFICATE_VERIFY_FAILED")
    calls = []

    def reject(adapter, request, **kwargs):
        assert kwargs["verify"] is True
        calls.append((request.method, request.url))
        raise failure

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", reject)
    if boundary == "discovery":
        with pytest.raises(requests.exceptions.SSLError) as error:
            OneLoginConfig.get_discovery_metadata()
        assert error.value is failure
        assert calls == [("GET", current_app.config["ONE_LOGIN_DISCOVERY_URL"])]
    elif boundary == "jwks":
        with pytest.raises(requests.exceptions.SSLError) as error:
            JWTHandler.get_public_key_from_jwks(JWKS_URI, _token({}, keys["RS256"]))
        assert error.value is failure
        assert calls == [("GET", JWKS_URI)]
    elif boundary == "token":
        with pytest.raises(Exception, match="^Failed to fetch tokens due to: synthetic CERTIFICATE_VERIFY_FAILED$") as error:
            OneLoginTokenRequest(synthetic).fetch_tokens_auth_request("synthetic-code")
        assert error.value.__context__ is failure
        assert calls == [("POST", synthetic.token_endpoint)]
    else:
        with pytest.raises(Exception, match="^Failed to fetch user information due to: synthetic CERTIFICATE_VERIFY_FAILED$") as error:
            OneLoginUserInfoRequest(synthetic).request_user_info(ACCESS_TOKEN)
        assert error.value.__context__ is failure
        assert calls == [("GET", synthetic.user_info_endpoint)]
