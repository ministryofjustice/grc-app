import pytest
from unittest.mock import patch, MagicMock


def test_get_discovery_metadata(config, app):
    with app.test_request_context():
        fake_metadata = {
            "issuer": "https://onelogin.gov.uk",
            "authorization_endpoint": "https://onelogin.gov.uk/auth",
            "userinfo_endpoint": "https://onelogin.gov.uk/userinfo",
            "token_endpoint": "https://onelogin.gov.uk/token",
            "end_session_endpoint": "https://onelogin.gov.uk/logout",
            "registration_endpoint": "https://onelogin.gov.uk/register",
            "jwks_uri": "https://onelogin.gov.uk/jwks"
        }
        with patch("grc.one_login.one_login_config.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = fake_metadata
            mock_get.return_value = mock_response

            result_metadata = config.get_discovery_metadata()

            assert fake_metadata == result_metadata
