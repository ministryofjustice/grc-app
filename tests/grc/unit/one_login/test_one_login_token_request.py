import pytest
from unittest.mock import patch, MagicMock
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.one_login.one_login_token_request import OneLoginTokenRequest


@patch.object(OneLoginTokenRequest, "_fetch_tokens")
def test_fetch_tokens_identity_request(mock_fetch_tokens, app, token_request):
    with app.test_request_context():
        mock_fetch_tokens.return_value = ("mock_access_token", "mock_id_token")

        code = "code"
        tokens = token_request.fetch_tokens_identity_request(code)

        mock_fetch_tokens.assert_called_once_with(
            code="code",
            redirect_uri="https://app.gov.uk/identity/callback"
        )

        assert tokens == ("mock_access_token", "mock_id_token")


@patch.object(OneLoginTokenRequest, "_fetch_tokens")
def test_fetch_tokens_auth_request(mock_fetch_tokens, app, token_request):
    with app.test_request_context():
        mock_fetch_tokens.return_value = ("mock_access_token", "mock_id_token")

        code = "code"
        tokens = token_request.fetch_tokens_auth_request(code)

        mock_fetch_tokens.assert_called_once_with(
            code="code",
            redirect_uri="https://app.gov.uk/auth/callback"
        )

        assert tokens == ("mock_access_token", "mock_id_token")


@patch.object(OneLoginTokenRequest, "_build_token_request_data")
@patch.object(OneLoginTokenRequest, "_build_token_request_headers")
def test_fetch_tokens_successful(mock_build_token_request_headers, mock_build_token_request_data, app, token_request):
    with app.test_request_context():
        code = "code"
        redirect_uri = "https://app.gov.uk/auth/callback"

        mock_build_token_request_headers.return_value = {"Content-Type": "application/x-www-form-urlencoded"}
        mock_build_token_request_data.return_value = {"payload": "123ABC"}

        with patch("grc.one_login.one_login_token_request.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'access_token': 'mock-access-token', 'id_token': 'mock-id-token'}
            mock_post.return_value = mock_response

            access_token, id_token = token_request._fetch_tokens(code=code, redirect_uri=redirect_uri)

            mock_build_token_request_headers.assert_called_once_with()

            mock_build_token_request_data.assert_called_once_with(
                code="code",
                redirect_uri="https://app.gov.uk/auth/callback"
            )

            mock_post.assert_called_once_with(
                url="https://onelogin.gov.uk/token",
                data={'payload': '123ABC'},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            assert access_token == 'mock-access-token'
            assert id_token == 'mock-id-token'


@patch.object(OneLoginTokenRequest, "_build_token_request_data")
@patch.object(OneLoginTokenRequest, "_build_token_request_headers")
def test_fetch_tokens_error(mock_build_token_request_headers, mock_build_token_request_data, app, token_request):
    with app.test_request_context():
        code = "code"
        redirect_uri = "https://app.gov.uk/auth/callback"

        mock_build_token_request_headers.return_value = {"Content-Type": "application/x-www-form-urlencoded"}
        mock_build_token_request_data.return_value = {"payload": "123ABC"}

        with patch("grc.one_login.one_login_token_request.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response

            with pytest.raises(Exception, match="Failed to fetch tokens due to: Token request failed: 400 - Bad Request"):
                token_request._fetch_tokens(code=code, redirect_uri=redirect_uri)

                mock_build_token_request_headers.assert_called_once_with()

                mock_build_token_request_data.assert_called_once_with(
                    code="code",
                    redirect_uri="https://app.gov.uk/auth/callback"
                )

                mock_post.assert_called_once_with(
                    url="https://onelogin.gov.uk/token",
                    data={'payload': '123ABC'},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )


@patch.object(OneLoginTokenRequest, "_build_token_request_data")
@patch.object(OneLoginTokenRequest, "_build_token_request_headers")
def test_fetch_tokens_missing_access_id(mock_build_token_request_headers, mock_build_token_request_data, app, token_request):
    with app.test_request_context():
        code = "code"
        redirect_uri = "https://app.gov.uk/auth/callback"

        mock_build_token_request_headers.return_value = {"Content-Type": "application/x-www-form-urlencoded"}
        mock_build_token_request_data.return_value = {"payload": "123ABC"}

        with patch("grc.one_login.one_login_token_request.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_post.return_value = mock_response

            with pytest.raises(Exception, match="Failed to fetch tokens due to: Access or Id token does not exist."):
                token_request._fetch_tokens(code=code, redirect_uri=redirect_uri)

                mock_build_token_request_headers.assert_called_once_with()

                mock_build_token_request_data.assert_called_once_with(
                    code="code",
                    redirect_uri="https://app.gov.uk/auth/callback"
                )

                mock_post.assert_called_once_with(
                    url="https://onelogin.gov.uk/token",
                    data={'payload': '123ABC'},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )


@patch.object(JWTHandler, "build_jwt_assertion")
def test_build_token_request_data(mock_build_jwt_assertion, app, token_request):
    with app.test_request_context():
        mock_build_jwt_assertion.return_value = "mocked-jwt-assertion"
        code = "code"
        redirect_uri = "https://app.gov.uk/identity/callback"

        result = token_request._build_token_request_data(code=code, redirect_uri=redirect_uri)

        mock_build_jwt_assertion.assert_called_once_with(
            private_key=b"fake-private-key",
            algorithm="RS256",
            aud="https://onelogin.gov.uk/token",
            iss="client-123ABC",
            sub="client-123ABC",
            exp_length=300
        )

        assert result == {
            "grant_type": "authorization_code",
            "code": "code",
            "redirect_uri": "https://app.gov.uk/identity/callback",
            "client_assertion": "mocked-jwt-assertion",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        }


def test_build_token_request_headers(app, token_request):
    with app.test_request_context():
        result = token_request._build_token_request_headers()

        assert result == {
            "Content-Type": "application/x-www-form-urlencoded"
        }









