import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, session
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest
from grc.one_login.one_login_config import OneLoginConfig


@pytest.fixture
def config():
    return OneLoginConfig()

@pytest.fixture
def auth_request(config):
    return OneLoginAuthorizationRequest(config)

@patch.object(OneLoginAuthorizationRequest, "_create_signed_auth_request")
@patch.object(OneLoginAuthorizationRequest, "_build_redirect_url")
def test_build_identity_redirect_url(mock_build_redirect, mock_create_signed, app, config, auth_request):
    with app.test_request_context():
        mock_create_signed.return_value = "mock_jwt_token"
        mock_build_redirect.return_value = "https://oidc.account.gov.uk/authorize?response_type=code&scope=openid+phone+email&client_id=hhJNeUO_5HuSMx7UwmOEjjNLMlE&request=mock_jwt_token"

        url = auth_request.build_identity_redirect_url()

        mock_create_signed.assert_called_once_with(
            vtr="Cl.Cm.P2",
            redirect_uri=config.identity_redirect_uri
        )

        mock_build_redirect.assert_called_once_with(
            signed_
        )


def test_build_authentication_redirect_url(self):
    pass

def test_create_signed_auth_request(self):
    pass