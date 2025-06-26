from grc.one_login.one_login_jwt_handler import JWTHandler
from unittest.mock import patch

from tests.grc.unit.one_login.conftest import token_request


@patch.object(JWTHandler, "get_public_key_from_jwks")
@patch.object(JWTHandler, "decode_jwt_with_key")
def test_validate_access_id_tokens(mock_decode_jwt, mock_get_public_key, app, token_request):
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

        with patch.object(token_request, '_validate_access_token') as mock_validate_access_token, \
                patch.object(token_request, '_validate_id_token_claims') as mock_validate_id_token_claims:

            token_request.validate_access_id_tokens(access_token, id_token)

            mock_validate_id_token_claims.assert_called_once_with(
                id_token_claims=mock_claims,
                expected_iss="https://onelogin.gov.uk",
                expected_aud="client-123ABC",
                expected_vot="Cl.Cm"
            )
            mock_validate_access_token.assert_called_once_with(mock_claims, access_token)
