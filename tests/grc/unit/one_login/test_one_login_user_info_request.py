import pytest
from unittest.mock import patch, MagicMock
from datetime import date


def test_request_user_info_is_successful(user_info_request, app):
    with app.test_request_context():
        with patch("grc.one_login.one_login_config.requests.get") as mock_get:
            mock_access_token = "testing123"
            expected_response = {"firstName": "Test", "lastName": "User", "age": "20"}

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            result = user_info_request.request_user_info(mock_access_token)

            assert result == expected_response
            mock_get.assert_called_once_with(
                url="https://onelogin.gov.uk/userinfo",
                headers={"Authorization": f"Bearer {mock_access_token}"}
            )


def test_request_user_info_is_throws_exception(user_info_request, app):
    with app.test_request_context():
        with patch("grc.one_login.one_login_config.requests.get") as mock_get:
            mock_access_token = "testing123"
            expected_response = "User Info request failed: 404 - Not Found"

            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = expected_response
            mock_get.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                user_info_request.request_user_info(mock_access_token)

            assert expected_response in str(exc_info.value)
            mock_get.assert_called_once_with(
                url="https://onelogin.gov.uk/userinfo",
                headers={"Authorization": f"Bearer {mock_access_token}"}
            )
