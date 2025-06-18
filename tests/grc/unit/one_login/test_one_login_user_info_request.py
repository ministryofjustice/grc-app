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


def test_get_names_dob_from_context_jwt_success(app, user_info_request):
    with app.test_request_context():
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        expected_name = {
            "first_name": "Bilbo",
            "middle_names": "Rings",
            "last_name": "Baggins"
        }
        expected_dob = date(1990, 1, 1)

        test_jwt_payload = {
            "vc": {
                "credentialSubject": {
                    "name": [
                        {
                            "validUntil": None,
                            "nameParts": [
                                {"type": "GivenName", "value": "Bilbo"},
                                {"type": "GivenName", "value": "Rings"},
                                {"type": "FamilyName", "value": "Baggins"}
                            ]
                        }
                    ],
                    "birthDate": [
                        {"value": "1990-01-01"}
                    ]
                }
            }
        }

        with patch("grc.one_login.one_login_user_info_request.JWTHandler.get_public_key_from_did") as mock_get_key:
            with patch("grc.one_login.one_login_user_info_request.JWTHandler.decode_jwt_with_key") as mock_decode:
                mock_get_key.return_value = "test-public-key"
                mock_decode.return_value = test_jwt_payload

                name, dob = user_info_request.get_names_dob_from_context_jwt(jwt_token)

                assert name == expected_name
                assert dob == expected_dob

                mock_get_key.assert_called_once_with(
                    did_url="https://onelogin.gov.uk/.well-known/did.json", jwt_token=jwt_token
                )
                mock_decode.assert_called_once_with(
                    jwt_token=jwt_token, public_key="test-public-key", algorithm="ES256"
                )



def test_get_names_dob_from_context_jwt_throws_exception(app, user_info_request):
    with app.test_request_context():
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        test_jwt_payload = {
            "vc": {}
        }
        expected_response = "Could not get credentials from context JWT."

        with patch("grc.one_login.one_login_user_info_request.JWTHandler.get_public_key_from_did") as mock_get_key:
            with patch("grc.one_login.one_login_user_info_request.JWTHandler.decode_jwt_with_key") as mock_decode:
                mock_get_key.return_value = "test-public-key"
                mock_decode.return_value = test_jwt_payload

                with pytest.raises(Exception) as exc_info:
                    user_info_request.get_names_dob_from_context_jwt(jwt_token)

                assert expected_response in str(exc_info.value)
                mock_get_key.assert_called_once_with(
                    did_url="https://onelogin.gov.uk/.well-known/did.json", jwt_token=jwt_token
                )
                mock_decode.assert_called_once_with(
                    jwt_token=jwt_token, public_key="test-public-key", algorithm="ES256"
                )


def test_store_user_info_redis_mapping(app, user_info_request):
    with app.test_request_context():
        mock_sub = "test-sub"
        mock_session_id = "test-session-id"
        app.config['SESSION_REDIS'] = MagicMock()

        with patch("grc.one_login.one_login_user_info_request.request") as mock_request:
            mock_request.cookies = {"session": mock_session_id}

            user_info_request.store_user_info_redis_mapping(mock_sub)

            app.config['SESSION_REDIS'].set.assert_called_once_with(f"user_sub:{mock_sub}", mock_session_id)


def test_extract_current_name_no_middle_name(user_info_request):
    names = [
        {
            "validUntil": None,
            "nameParts": [
                {"type": "GivenName", "value": "Bilbo"},
                {"type": "FamilyName", "value": "Baggins"}
            ]
        }
    ]

    expected = {"first_name": "Bilbo", "middle_names": "", "last_name": "Baggins"}
    result = user_info_request._extract_current_name(names)
    assert expected == result


def test_extract_current_name_with_middle_name(user_info_request):
    names = [
        {
            "validUntil": None,
            "nameParts": [
                {"type": "GivenName", "value": "Bilbo"},
                {"type": "GivenName", "value": "Lord"},
                {"type": "FamilyName", "value": "Baggins"}
            ]
        }
    ]

    expected = {"first_name": "Bilbo", "middle_names": "Lord", "last_name": "Baggins"}
    result = user_info_request._extract_current_name(names)
    assert expected == result


def test_format_into_datetime_date(user_info_request):
    test_date = "2025-06-06"
    expected_date = date(2025, 6, 6)

    result = user_info_request._format_date_into_datetime_date(test_date)
    assert expected_date == result

