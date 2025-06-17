import pytest
from unittest.mock import patch, MagicMock
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest

@pytest.fixture
def fake_discovery_metadata():
    return {
        "issuer": "https://onelogin.gov.uk",
        "authorization_endpoint": "https://onelogin.gov.uk/auth",
        "userinfo_endpoint": "https://onelogin.gov.uk/userinfo",
        "token_endpoint": "https://onelogin.gov.uk/token",
        "end_session_endpoint": "https://onelogin.gov.uk/logout",
        "registration_endpoint": "https://onelogin.gov.uk/register",
        "jwks_uri": "https://onelogin.gov.uk/jwks"
    }


@pytest.fixture
def config(app, fake_discovery_metadata):
    with app.app_context():
        with patch("grc.one_login.one_login_config.requests.get") as mock_get, \
             patch("grc.one_login.one_login_config.OneLoginConfig.load_private_key") as mock_key:
            mock_response = MagicMock()
            mock_response.json.return_value = fake_discovery_metadata
            mock_get.return_value = mock_response
            mock_key.return_value = b"fake-private-key"
            return OneLoginConfig()


@pytest.fixture
def auth_request(config):
    return OneLoginAuthorizationRequest(config)