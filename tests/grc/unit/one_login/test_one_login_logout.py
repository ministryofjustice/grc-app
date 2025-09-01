import pytest
from unittest.mock import patch, MagicMock

def test_logout_redirect_url_to_confirmation_page(logout, app):
    with app.test_request_context():
        id_token = "test-id-token"
        expected_url = "https://onelogin.gov.uk/logout?id_token_hint=test-id-token&post_logout_redirect_uri=https://app.gov.uk/submit-and-pay/confirmation"

        result = logout.logout_redirect_url_to_confirmation_page(id_token)

        assert result == expected_url


def test_logout_redirect_url_to_save_page(logout, app):
    with app.test_request_context():
        id_token = "test-id-token"
        expected_url = "https://onelogin.gov.uk/logout?id_token_hint=test-id-token&post_logout_redirect_uri=https://app.gov.uk/save-and-return/exit-application"

        result = logout.logout_redirect_url_to_save_page(id_token)

        assert result == expected_url


def test_logout_redirect_url_to_reference_check_page(logout, app):
    with app.test_request_context():
        id_token = "test-id-token"
        expected_url = "https://onelogin.gov.uk/logout?id_token_hint=test-id-token&post_logout_redirect_uri=https://app.gov.uk/your-reference-number"

        result = logout.logout_redirect_url_to_reference_check_page(id_token)

        assert result == expected_url


def test_redirect_url_to_start_page(logout, app):
    with app.test_request_context():
        id_token = "test-id-token"
        expected_url = "https://onelogin.gov.uk/logout?id_token_hint=test-id-token&post_logout_redirect_uri=https://app.gov.uk/"

        result = logout.logout_redirect_url_to_start_page(id_token)

        assert result == expected_url


def test_end_user_session(logout, app):
    with app.test_request_context():
        with patch("grc.one_login.one_login_logout.session") as mock_session:

            logout.end_user_session()

            mock_session.clear.assert_called_once()


def test_end_user_session_throws_exception(logout, app):
    expected_error_message = "Session clear failed"
    with app.test_request_context():
        with patch("grc.one_login.one_login_logout.session") as mock_session:
            mock_session.clear = MagicMock(side_effect=Exception("Session clear failed"))

            with pytest.raises(Exception) as exc_info:
                logout.end_user_session()

            assert expected_error_message in str(exc_info.value)
            mock_session.clear.assert_called_once()
