from unittest.mock import patch, MagicMock
from jwt import ExpiredSignatureError
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import base64
from cryptography.hazmat.backends import default_backend
from uuid import UUID
import json

def test_decode_jwt_with_key_success(app, jwt_handler):
    decoded_jwt_token = {"sub": "user123", "iss": "https://issuer.com"}

    with app.app_context():
        with patch("grc.one_login.one_login_jwt_handler.decode") as mock_decode:
            mock_decode.return_value = decoded_jwt_token

            token = "dummy.jwt.token"
            public_key = "mock-public-key"

            result = jwt_handler.decode_jwt_with_key(jwt_token=token, public_key=public_key)

            assert result == decoded_jwt_token
            mock_decode.assert_called_once_with(
                token,
                key=public_key,
                algorithms=["RS256"],
                options={"verify_aud": False, "verify_signature": False}
            )


def test_decode_jwt_with_key_expired_token(app, jwt_handler):
    with app.app_context():
        with patch("grc.one_login.one_login_jwt_handler.decode", side_effect=ExpiredSignatureError):
            token = "expired.jwt.token"
            public_key = "mock-public-key"

            with pytest.raises(Exception, match="Token is expired."):
                jwt_handler.decode_jwt_with_key(jwt_token=token, public_key=public_key)


def test_decode_jwt_with_key_invalid_token(app, jwt_handler):
    with app.app_context():
        with patch("grc.one_login.one_login_jwt_handler.decode", side_effect=Exception("some decode failure")):
            token = "invalid.jwt.token"
            public_key = "mock-public-key"

            with pytest.raises(Exception, match="Failed to decode token: some decode failure"):
                jwt_handler.decode_jwt_with_key(jwt_token=token, public_key=public_key)


@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_kid_from_jwt_token")
@patch("grc.one_login.one_login_jwt_handler.requests.get")
def test_get_public_key_from_jwks_success_rsa(mock_requests_get, mock_get_kid, app, jwt_handler):
    mock_get_kid.return_value = 'test-kid'

    n_int = 1234567890123456789012345678901234567890
    e_int = 65537

    n_bytes = n_int.to_bytes((n_int.bit_length() + 7) // 8, 'big')
    e_bytes = e_int.to_bytes((e_int.bit_length() + 7) // 8, 'big')

    n_b64 = base64.urlsafe_b64encode(n_bytes).decode('utf-8').rstrip("=")
    e_b64 = base64.urlsafe_b64encode(e_bytes).decode('utf-8').rstrip("=")

    jwks = {
        "keys": [
            {
                "kid": "test-kid",
                "kty": "RSA",
                "n": n_b64,
                "e": e_b64
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = jwks
    mock_requests_get.return_value = mock_response

    jwt_token = "mock.jwt.token"
    jwks_uri = "https://example.com/.well-known/jwks.json"

    with app.app_context():
        public_key = jwt_handler.get_public_key_from_jwks(jwks_uri, jwt_token)

        assert isinstance(public_key, rsa.RSAPublicKey)
        mock_requests_get.assert_called_once_with(jwks_uri)
        mock_get_kid.assert_called_once_with(jwt_token)


@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_kid_from_jwt_token")
@patch("grc.one_login.one_login_jwt_handler.requests.get")
def test_get_public_key_from_jwks_http_error(mock_requests_get, mock_get_kid, app, jwt_handler):
    mock_get_kid.return_value = 'test-kid'

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_requests_get.return_value = mock_response

    jwt_token = "mock.jwt.token"
    jwks_uri = "https://example.com/.well-known/jwks.json"

    with app.app_context():
        with pytest.raises(Exception) as exc_info:
            jwt_handler.get_public_key_from_jwks(jwks_uri, jwt_token)

        assert str(exc_info.value) == "Error fetching JWKS: 500"
        mock_requests_get.assert_called_once_with(jwks_uri)
        mock_get_kid.assert_called_once_with(jwt_token)


@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_kid_from_jwt_token")
@patch("grc.one_login.one_login_jwt_handler.requests.get")
def test_get_public_key_from_jwks_kid_not_found(mock_requests_get, mock_get_kid, app, jwt_handler):
    mock_get_kid.return_value = "expected-kid"

    jwks_response = {
        "keys": [
            {
                "kid": "different-kid",
                "kty": "RSA",
                "n": "AQAB",
                "e": "AQAB"
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = jwks_response
    mock_requests_get.return_value = mock_response

    jwt_token = "mock.jwt.token"
    jwks_uri = "https://example.com/.well-known/jwks.json"

    with app.app_context():
        with pytest.raises(Exception) as exc_info:
            jwt_handler.get_public_key_from_jwks(jwks_uri, jwt_token)

        assert str(exc_info.value) == "Public key with kid expected-kid not found in JWKS."
        mock_requests_get.assert_called_once_with(jwks_uri)
        mock_get_kid.assert_called_once_with(jwt_token)


@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_kid_from_jwt_token")
@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_controller_id_from_kid")
@patch("grc.one_login.one_login_jwt_handler.DIDDocumentCache.get_did_document")
def test_get_public_key_from_did_success(mock_get_doc, mock_get_controller_id, mock_get_kid, app, jwt_handler):
    mock_get_kid.return_value = "did:example:123#keys-1"
    mock_get_controller_id.return_value = "did:example:123"

    private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()

    def to_b64url(val):
        byte_len = (val.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(val.to_bytes(byte_len, 'big')).rstrip(b'=').decode()

    x_b64 = to_b64url(public_numbers.x)
    y_b64 = to_b64url(public_numbers.y)

    did_doc = {
        "id": "did:example:123",
        "assertionMethod": [
            {
                "id": "did:example:123#keys-1",
                "publicKeyJwk": {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": x_b64,
                    "y": y_b64
                }
            }
        ]
    }

    mock_get_doc.return_value = did_doc

    jwt_token = "mock.jwt.token"
    did_url = "https://example.com/did.json"

    with app.app_context():
        public_key = jwt_handler.get_public_key_from_did(did_url, jwt_token)
        assert isinstance(public_key, ec.EllipticCurvePublicKey)


@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_kid_from_jwt_token")
@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_controller_id_from_kid")
@patch("grc.one_login.one_login_jwt_handler.DIDDocumentCache.get_did_document")
def test_get_public_key_from_did_mismatched_id(mock_get_doc, mock_get_controller_id, mock_get_kid, app, jwt_handler):
    mock_get_kid.return_value = "did:example:123#keys-1"
    mock_get_controller_id.return_value = "mismatch-id"

    did_doc = {
        "id": "did:example:123",
        "assertionMethod": []
    }
    mock_get_doc.return_value = did_doc

    jwt_token = "mock.jwt.token"
    did_url = "https://example.com/did.json"

    with app.app_context():
        with pytest.raises(Exception) as exc_info:
            jwt_handler.get_public_key_from_did(did_url, jwt_token)
        assert str(exc_info.value) == "Doc ID doesn't match controller ID."


@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_kid_from_jwt_token")
@patch("grc.one_login.one_login_jwt_handler.JWTHandler._get_controller_id_from_kid")
@patch("grc.one_login.one_login_jwt_handler.DIDDocumentCache.get_did_document")
def test_get_public_key_from_did_kid_not_found(mock_get_doc, mock_get_controller_id, mock_get_kid, app, jwt_handler):
    mock_get_kid.return_value = "did:example:123#keys-1"
    mock_get_controller_id.return_value = "did:example:123"

    did_doc = {
        "id": "did:example:123",
        "assertionMethod": [
            {
                "id": "did:example:123#keys-2",
                "publicKeyJwk": {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": "invalid",
                    "y": "invalid"
                }
            }
        ]
    }
    mock_get_doc.return_value = did_doc

    jwt_token = "mock.jwt.token"
    did_url = "https://example.com/did.json"

    with app.app_context():
        with pytest.raises(Exception) as exc_info:
            jwt_handler.get_public_key_from_did(did_url, jwt_token)
        assert str(exc_info.value) == "Public key with kid did:example:123#keys-1 not found in DID document."


def test_build_jwt_assertion(app, jwt_handler):
    private_key = b"mock-private-key"
    algorithm = "HS256"
    aud = "client-123ABC"
    iss = "https://onelogin.gov.uk"
    sub = "subject"
    exp_length = 3600

    fixed_time = 1_700_000_000
    fixed_uuid = UUID("12345678-1234-5678-1234-567812345678")

    with app.app_context():
        with patch("grc.one_login.one_login_jwt_handler.time", return_value=fixed_time), \
             patch("grc.one_login.one_login_jwt_handler.uuid4", return_value=fixed_uuid), \
             patch("grc.one_login.one_login_jwt_handler.encode") as mock_encode:

            mock_encode.return_value = "signed.jwt.token"

            token = jwt_handler.build_jwt_assertion(
                private_key=private_key,
                algorithm=algorithm,
                aud=aud,
                iss=iss,
                sub=sub,
                exp_length=exp_length
            )

            expected_payload = {
                "aud": aud,
                "iss": iss,
                "sub": sub,
                "exp": fixed_time + exp_length,
                "jti": str(fixed_uuid),
                "iat": fixed_time,
            }

            mock_encode.assert_called_once_with(
                expected_payload,
                private_key,
                algorithm=algorithm,
                headers={"kid": "f58a6bef-0d22-444b-b4d3-507a54e9892f"},
            )
            assert token == "signed.jwt.token"


def test_get_controller_id_from_kid_success(app, jwt_handler):
  kid = "did:example:123#key-1"
  controller_id = jwt_handler._get_controller_id_from_kid(kid)
  assert controller_id == "did:example:123"


def test_get_controller_id_from_kid_raises_on_empty_controller(app, jwt_handler):
  kid = "#key-1"
  with pytest.raises(Exception) as exc:
    jwt_handler._get_controller_id_from_kid(kid)
  assert "Controller ID doesn't exist" in str(exc.value)


def test_get_kid_from_jwt_token_success(app, jwt_handler):
  header = {"alg": "RS256", "kid": "abc123"}
  header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
  fake_jwt = f"{header_b64}.payload.signature"

  with pytest.MonkeyPatch.context() as m:
    m.setattr(jwt_handler, "_decode_jwt_header", lambda token: header)
    kid = jwt_handler._get_kid_from_jwt_token(fake_jwt)
    assert kid == "abc123"


def test_get_kid_from_jwt_token_raises_when_no_kid(app, jwt_handler):
  header = {"alg": "RS256"}
  header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
  fake_jwt = f"{header_b64}.payload.signature"

  with pytest.MonkeyPatch.context() as m:
    m.setattr(jwt_handler, "_decode_jwt_header", lambda token: header)
    with pytest.raises(Exception) as exc:
      jwt_handler._get_kid_from_jwt_token(fake_jwt)
    assert "No 'kid' found" in str(exc.value)


def test_decode_jwt_header_success(app, jwt_handler):
  header = {"alg": "RS256", "kid": "abc123"}
  header_json = json.dumps(header).encode()
  header_b64 = base64.urlsafe_b64encode(header_json).rstrip(b'=').decode()

  fake_jwt = f"{header_b64}.payload.signature"
  decoded_header = jwt_handler._decode_jwt_header(fake_jwt)
  assert decoded_header == header


def test_decode_jwt_header_handles_padding(app, jwt_handler):
  header = {"alg": "RS256", "kid": "abc123"}
  header_json = json.dumps(header).encode()
  header_b64 = base64.urlsafe_b64encode(header_json).decode().rstrip("=")

  fake_jwt = f"{header_b64}.payload.signature"
  decoded_header = jwt_handler._decode_jwt_header(fake_jwt)
  assert decoded_header == header