from grc.one_login.one_login_jwt_handler import JWTHandler
import pytest
from unittest.mock import patch
from grc.one_login.one_login_token_validator import OneLoginTokenValidator
from time import time
from flask import session

@patch.object(JWTHandler, "get_public_key_from_jwks")
@patch.object(JWTHandler, "decode_jwt_with_key")
def test_validate_access_id_tokens_successful(mock_decode_jwt, mock_get_public_key, app, token_validator):
    with app.test_request_context():
        mock_public_key = "mock-public-key"
        mock_claims = {
            "iss": "https://onelogin.gov.uk",
            "aud": "client-123ABC",
            "vot": "Cl.Cm",
        }

        mock_get_public_key.return_value = mock_public_key
        mock_decode_jwt.return_value = mock_claims

        access_token = "mock-access-token"
        id_token = "mock-id-token"

        with patch.object(token_validator, '_validate_access_token') as mock_validate_access_token, \
                patch.object(token_validator, '_validate_id_token_claims') as mock_validate_id_token_claims:

            token_validator.validate_access_id_tokens(access_token, id_token)

            mock_validate_id_token_claims.assert_called_once_with(
                id_token_claims=mock_claims,
                expected_iss="https://onelogin.gov.uk",
                expected_aud='client-123ABC',
                expected_vot="Cl.Cm"
            )

            mock_validate_access_token.assert_called_once_with(
                id_token_claims=mock_claims,
                access_token=access_token
            )


@patch.object(JWTHandler, "get_public_key_from_jwks")
@patch.object(JWTHandler, "decode_jwt_with_key")
def test_validate_access_id_tokens_error_id_claims(mock_decode_jwt, mock_get_public_key, app, token_validator):
    with app.test_request_context():
        mock_public_key = "mock-public-key"
        mock_claims = {
            "iss": "error iss",
            "aud": "client-123ABC",
            "vot": "Cl.Cm",
        }

        mock_get_public_key.return_value = mock_public_key
        mock_decode_jwt.return_value = mock_claims

        access_token = "mock-access-token"
        id_token = "mock-id-token"

        with patch.object(token_validator, '_validate_access_token') as mock_validate_access_token, \
             patch.object(token_validator, '_validate_id_token_claims') as mock_validate_id_token_claims:

            mock_validate_id_token_claims.side_effect = Exception("Invalid iss. Expected https://onelogin.gov.uk")

            with pytest.raises(Exception, match="Invalid iss. Expected https://onelogin.gov.uk"):
                token_validator.validate_access_id_tokens(access_token, id_token)

            mock_validate_id_token_claims.assert_called_once_with(
                id_token_claims=mock_claims,
                expected_iss="https://onelogin.gov.uk",
                expected_aud='client-123ABC',
                expected_vot="Cl.Cm"
            )

            mock_validate_access_token.assert_not_called()


@patch.object(JWTHandler, "get_public_key_from_jwks")
@patch.object(JWTHandler, "decode_jwt_with_key")
def test_validate_access_id_tokens_error_access_token(mock_decode_jwt, mock_get_public_key, app, token_validator):
    with app.test_request_context():
        mock_public_key = "mock-public-key"
        mock_claims = {
            "iss": "https://onelogin.gov.uk",
            "aud": "client-123ABC",
            "vot": "Cl.Cm",
        }

        mock_get_public_key.return_value = mock_public_key
        mock_decode_jwt.return_value = mock_claims

        access_token = "mock-access-token"
        id_token = "mock-id-token"

        with patch.object(token_validator, '_validate_access_token') as mock_validate_access_token, \
             patch.object(token_validator, '_validate_id_token_claims') as mock_validate_id_token_claims:

            mock_validate_access_token.side_effect = Exception("Access token hash does not match 'at_hash' in ID token")

            with pytest.raises(Exception, match="Access token hash does not match 'at_hash' in ID token"):
                token_validator.validate_access_id_tokens(access_token, id_token)

            mock_validate_id_token_claims.assert_called_once_with(
                id_token_claims=mock_claims,
                expected_iss="https://onelogin.gov.uk",
                expected_aud='client-123ABC',
                expected_vot="Cl.Cm"
            )

            mock_validate_access_token.assert_called_once_with(
                id_token_claims=mock_claims,
                access_token=access_token
            )


@patch.object(JWTHandler, "get_public_key_from_jwks")
@patch.object(JWTHandler, "decode_jwt_with_key")
def test_validate_logout_token_successful(mock_decode_jwt, mock_get_public_key, app, token_validator):
    mock_public_key = "mock-public-key"
    mock_claims = {
        "iss": "https://onelogin.gov.uk",
        "aud": "client-123ABC",
        "vot": "Cl.Cm",
    }

    mock_get_public_key.return_value = mock_public_key
    mock_decode_jwt.return_value = mock_claims

    logout_token = "mock-logout-token"

    with patch.object(token_validator, '_validate_logout_token_claims') as mock_validate_logout_token_claims:

        logout_claims = token_validator.validate_logout_token(logout_token)

        mock_validate_logout_token_claims.assert_called_once_with(
            logout_token_claims=mock_claims,
            expected_iss="https://onelogin.gov.uk",
            expected_aud='client-123ABC',
        )

        assert logout_claims == mock_claims

@patch.object(JWTHandler, "get_public_key_from_jwks")
@patch.object(JWTHandler, "decode_jwt_with_key")
def test_validate_logout_token_unsuccessful(mock_decode_jwt, mock_get_public_key, app, token_validator):
    with app.test_request_context():
        mock_public_key = "mock-public-key"
        mock_claims = {
            "iss": "error iss",
            "aud": "client-123ABC",
            "vot": "Cl.Cm",
        }

        mock_get_public_key.return_value = mock_public_key
        mock_decode_jwt.return_value = mock_claims

        logout_token = "mock-logout-token"

        with patch.object(token_validator, '_validate_logout_token_claims') as mock_validate_logout_token_claims:
            mock_validate_logout_token_claims.side_effect = Exception("Invalid iss. Expected https://onelogin.gov.uk")

            with pytest.raises(Exception, match="Invalid iss. Expected https://onelogin.gov.uk"):
                token_validator.validate_logout_token(logout_token)

            mock_validate_logout_token_claims.assert_called_once_with(
                logout_token_claims=mock_claims,
                expected_iss="https://onelogin.gov.uk",
                expected_aud='client-123ABC',
            )


@patch.object(OneLoginTokenValidator, "_validate_vot")
@patch.object(OneLoginTokenValidator, "_validate_nonce")
@patch.object(OneLoginTokenValidator, "_validate_iat")
@patch.object(OneLoginTokenValidator, "_validate_exp")
@patch.object(OneLoginTokenValidator, "_validate_aud")
@patch.object(OneLoginTokenValidator, "_validate_iss")
def test_validate_id_token_claims_successful(
    mock_validate_iss,
    mock_validate_aud,
    mock_validate_exp,
    mock_validate_iat,
    mock_validate_nonce,
    mock_validate_vot
):
    claims = {
        "iss": "https://onelogin.gov.uk",
        "aud": "client-123ABC",
        "exp": "1720000000",
        "iat": "1719990000",
        "nonce": "abc123",
        "vot": "Cl.Cm"
    }

    OneLoginTokenValidator._validate_id_token_claims(
        id_token_claims=claims,
        expected_iss="https://onelogin.gov.uk",
        expected_aud="client-123ABC",
        expected_vot="Cl.Cm"
    )

    mock_validate_iss.assert_called_once_with(token_iss="https://onelogin.gov.uk", expected_iss="https://onelogin.gov.uk")
    mock_validate_aud.assert_called_once_with(token_aud="client-123ABC", expected_aud="client-123ABC")
    mock_validate_exp.assert_called_once_with(token_exp=1720000000)
    mock_validate_iat.assert_called_once_with(token_iat=1719990000)
    mock_validate_nonce.assert_called_once_with(token_nonce="abc123")
    mock_validate_vot.assert_called_once_with(token_vot="Cl.Cm", expected_vot="Cl.Cm")


@patch.object(OneLoginTokenValidator, "_validate_events")
@patch.object(OneLoginTokenValidator, "_validate_jti")
@patch.object(OneLoginTokenValidator, "_validate_sub_exists")
@patch.object(OneLoginTokenValidator, "_validate_iat")
@patch.object(OneLoginTokenValidator, "_validate_exp")
@patch.object(OneLoginTokenValidator, "_validate_aud")
@patch.object(OneLoginTokenValidator, "_validate_iss")
def test_validate_logout_token_claims_successful(
    mock_validate_iss,
    mock_validate_aud,
    mock_validate_exp,
    mock_validate_iat,
    mock_validate_sub_exists,
    mock_validate_jti,
    mock_validate_events
):
    claims = {
        "iss": "https://onelogin.gov.uk",
        "aud": "client-123ABC",
        "exp": "1720000000",
        "iat": "1719990000",
        "sub": "user-123",
        "jti": "logout-jti-xyz",
        "events": {"http://schemas.openid.net/event/backchannel-logout": {}}
    }

    OneLoginTokenValidator._validate_logout_token_claims(
        logout_token_claims=claims,
        expected_iss="https://onelogin.gov.uk",
        expected_aud="client-123ABC"
    )

    mock_validate_iss.assert_called_once_with(token_iss="https://onelogin.gov.uk", expected_iss="https://onelogin.gov.uk")
    mock_validate_aud.assert_called_once_with(token_aud="client-123ABC", expected_aud="client-123ABC")
    mock_validate_exp.assert_called_once_with(token_exp=1720000000)
    mock_validate_iat.assert_called_once_with(token_iat=1719990000)
    mock_validate_sub_exists.assert_called_once_with(token_sub="user-123")
    mock_validate_jti.assert_called_once_with(token_jti="logout-jti-xyz")
    mock_validate_events.assert_called_once_with(token_events={"http://schemas.openid.net/event/backchannel-logout": {}})

def test_validate_iss_success(app, token_validator):
    with app.test_request_context():
        token_validator._validate_iss(token_iss="https://issuer.com", expected_iss="https://issuer.com")

def test_validate_iss_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing iss in token."):
            token_validator._validate_iss(token_iss=None, expected_iss="https://issuer.com")

def test_validate_iss_mismatch(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Invalid iss. Expected https://issuer.com"):
            token_validator._validate_iss(token_iss="wrong", expected_iss="https://issuer.com")

def test_validate_aud_success(app, token_validator):
    with app.test_request_context():
        token_validator._validate_aud(token_aud="client-123", expected_aud="client-123")

def test_validate_aud_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing aud in token."):
            token_validator._validate_aud(token_aud=None, expected_aud="client-123")

def test_validate_aud_mismatch(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Invalid aud. Expected client-123"):
            token_validator._validate_aud(token_aud="wrong", expected_aud="client-123")

def test_validate_exp_success(app, token_validator):
    with app.test_request_context():
        future_time = int(time()) + 60
        token_validator._validate_exp(token_exp=future_time)

def test_validate_exp_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing exp in token."):
            token_validator._validate_exp(token_exp=None)

def test_validate_exp_expired(app, token_validator):
    with app.test_request_context():
        past_time = int(time()) - 60
        with pytest.raises(Exception, match="Token is expired."):
            token_validator._validate_exp(token_exp=past_time)

def test_validate_iat_success(app, token_validator):
    with app.test_request_context():
        now = int(time())
        token_validator._validate_iat(token_iat=now)

def test_validate_iat_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing iat in token."):
            token_validator._validate_iat(token_iat=None)

def test_validate_iat_future(app, token_validator):
    with app.test_request_context():
        future_time = int(time()) + 60
        with pytest.raises(Exception, match="Id token's issued at time is after the current time."):
            token_validator._validate_iat(token_iat=future_time)

def test_validate_nonce_success(app, token_validator):
    with app.test_request_context():
        with app.test_client() as client:
            session['nonce'] = "expected-nonce"
            token_validator._validate_nonce(token_nonce="expected-nonce")

def test_validate_nonce_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing nonce in token."):
            token_validator._validate_nonce(token_nonce=None)

def test_validate_vot_success(app, token_validator):
    with app.test_request_context():
        token_validator._validate_vot(token_vot="Cl.Cm", expected_vot="Cl.Cm")

def test_validate_vot_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing vot in token."):
            token_validator._validate_vot(token_vot=None, expected_vot="Cl.Cm")

def test_validate_vot_invalid(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Invalid vot claim. Expected Cl.Cm"):
            token_validator._validate_vot(token_vot="wrong", expected_vot="Cl.Cm")

def test_validate_sub_exists_success(app, token_validator):
    with app.test_request_context():
        token_validator._validate_sub_exists(token_sub="subject-123")

def test_validate_sub_exists_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing sub in token."):
            token_validator._validate_sub_exists(token_sub=None)

def test_validate_events_success(app, token_validator):
    with app.test_request_context():
        expected_events = {
            "http://schemas.openid.net/event/backchannel-logout": {}
        }
        token_validator._validate_events(token_events=expected_events)

def test_validate_events_missing(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match="Missing events in token."):
            token_validator._validate_events(token_events=None)

def test_validate_events_invalid(app, token_validator):
    with app.test_request_context():
        with pytest.raises(Exception, match=r"Invalid events claim. Expected .*"):
            token_validator._validate_events(token_events={"wrong": "value"})
