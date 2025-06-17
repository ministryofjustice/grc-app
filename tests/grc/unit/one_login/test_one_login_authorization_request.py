import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, session
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest


@patch.object(OneLoginAuthorizationRequest, "_create_signed_auth_request")
@patch.object(OneLoginAuthorizationRequest, "_build_redirect_url")
def test_build_identity_redirect_url(mock_build_redirect, mock_create_signed, app, config, auth_request):
    with app.test_request_context():
        mock_create_signed.return_value = "mock_jwt_token"
        mock_build_redirect.return_value = "https://onelogin.gov.uk/authorize?response_type=code&scope=openid+phone+email&client_id=client-123ABC&request=mock_jwt_token"

        url = auth_request.build_identity_redirect_url()

        mock_create_signed.assert_called_once_with(
            vtr="Cl.Cm.P2",
            redirect_uri='https://app.gov.uk/identity/callback'
        )

        mock_build_redirect.assert_called_once_with(
            signed_jwt="mock_jwt_token"
        )

        assert url == "https://onelogin.gov.uk/authorize?response_type=code&scope=openid+phone+email&client_id=client-123ABC&request=mock_jwt_token"


@patch.object(OneLoginAuthorizationRequest, "_create_signed_auth_request")
@patch.object(OneLoginAuthorizationRequest, "_build_redirect_url")
def test_build_authentication_redirect_url(mock_build_redirect, mock_create_signed, app, config, auth_request):
    with app.test_request_context():
        mock_create_signed.return_value = "mock_jwt_token"
        mock_build_redirect.return_value = "https://onelogin.gov.uk/authorize?response_type=code&scope=openid+phone+email&client_id=client-123ABC&request=mock_jwt_token"

        url = auth_request.build_authentication_redirect_url()

        mock_create_signed.assert_called_once_with(
            vtr="Cl.Cm",
            redirect_uri='https://app.gov.uk/auth/callback'
        )

        mock_build_redirect.assert_called_once_with(
            signed_jwt="mock_jwt_token"
        )

        assert url == "https://onelogin.gov.uk/authorize?response_type=code&scope=openid+phone+email&client_id=client-123ABC&request=mock_jwt_token"


@patch("grc.one_login.one_login_auth_request.encode")
@patch.object(OneLoginAuthorizationRequest, "_generate_and_store_state_nonce")
def test_create_signed_auth_request_encodes_jwt(mock_generate_and_store, mock_jwt_encode, app, auth_request):
    with app.test_request_context():
        mock_jwt_encode.return_value = "signed.jwt.token"
        mock_generate_and_store.return_value = ("mock-state", "mock-nonce")

        jwt = auth_request._create_signed_auth_request(
            vtr="Cl.Cm",
            redirect_uri="https://app.gov.uk/auth/callback"
        )

        assert jwt == "signed.jwt.token"

        args, kwargs = mock_jwt_encode.call_args
        payload = args[0]

        assert payload["response_type"] == "code"
        assert payload["scope"] == "openid phone email"
        assert payload["client_id"] == "client-123ABC"
        assert payload["redirect_uri"] == "https://app.gov.uk/auth/callback"
        assert payload["nonce"] == 'mock-nonce'
        assert payload["state"] == 'mock-state'
        assert payload["vtr"] == ["Cl.Cm"]
        assert payload["claims"] == {
            "userinfo": {
                "https://vocab.account.gov.uk/v1/coreIdentityJWT": None,
                "https://vocab.account.gov.uk/v1/address": None,
                "https://vocab.account.gov.uk/v1/returnCode": None,
                "https://vocab.account.gov.uk/v1/passport": None,
                "https://vocab.account.gov.uk/v1/drivingPermit": None
            }
        }

        assert kwargs["algorithm"] == "RS256"
        assert kwargs["headers"]["kid"] == "f58a6bef-0d22-444b-b4d3-507a54e9892f"


@patch("grc.one_login.one_login_auth_request.token_urlsafe")
def test_generate_and_store_state_nonce(mock_token_urlsafe, app, auth_request):
    mock_token_urlsafe.side_effect = ["mocked-state", "mocked-nonce"]

    with app.test_request_context():
        state, nonce = auth_request._generate_and_store_state_nonce()
        assert state == "mocked-state"
        assert nonce == "mocked-nonce"
        assert session['state'] == "mocked-state"
        assert session['nonce'] == "mocked-nonce"
        assert mock_token_urlsafe.call_count == 2
        mock_token_urlsafe.assert_any_call(16)