from flask import session
from grc.one_login.one_login_config import OneLoginConfig
import requests
from typing import Dict, Any, Tuple
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import LogLevel, Logger

logger = Logger()

class OneLoginTokenRequest:
    """
    Handles token exchange with the One Login token endpoint.
    Supports fetching tokens for both identity and authentication flows.
    """

    def __init__(self, config: OneLoginConfig):
        """
        Initializes the token request handler with config values.

        :param config: OneLoginConfig containing endpoints and credentials.
        """
        self.config = config

    def fetch_tokens_identity_request(self, code: str) -> Tuple[str, str]:
        """
        Fetches tokens for an identity verification request.

        :param code: Authorization code returned from One Login.
        :return: Tuple of (access_token, id_token).
        """
        return self._fetch_tokens(code=code, redirect_uri=self.config.identity_redirect_uri)

    def fetch_tokens_auth_request(self, code: str) -> Tuple[str, str]:
        """
        Fetches tokens for an authentication request.

        :param code: Authorization code returned from One Login.
        :return: Tuple of (access_token, id_token).
        """
        return self._fetch_tokens(code=code, redirect_uri=self.config.auth_redirect_uri)

    def _fetch_tokens(self, code: str, redirect_uri: str) -> Tuple[str, str]:
        """
        Handles the token exchange by sending a POST request to One Login's token endpoint.

        :param code: Authorization code from One Login.
        :param redirect_uri: The redirect URI used in the initial request.
        :return: Tuple containing access_token and id_token.
        :raises Exception: If the request fails or required tokens are missing.
        """
        try:
            token_url = self.config.token_endpoint
            data = self._build_token_request_data(code=code, redirect_uri=redirect_uri)
            headers = self._build_token_request_headers()

            response = requests.post(url=token_url, data=data, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Token request failed: {response.status_code} - {response.text}")

            tokens = response.json()
            access_token = tokens.get('access_token')
            id_token = tokens.get('id_token')

            if not access_token or not id_token:
                raise Exception("Access or Id token does not exist.")

            return access_token, id_token

        except Exception as e:
            raise Exception(f"Failed to fetch tokens due to: {str(e)}")

    def _build_token_request_data(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Builds the data payload for the token request.

        :param code: Authorization code.
        :param redirect_uri: Redirect URI used in the flow.
        :return: Dictionary containing request parameters.
        """
        assertion = JWTHandler.build_jwt_assertion(
            kid=self.config.kid,
            private_key=self.config.private_key,
            algorithm="RS256",
            aud=self.config.token_endpoint,
            iss=self.config.client_id,
            sub=self.config.client_id,
            exp_length=300
        )
        assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_assertion": assertion,
            "client_assertion_type": assertion_type,
        }
        return data

    @staticmethod
    def _build_token_request_headers() -> Dict[str, Any]:
        """
        Returns the headers required for the token request.

        :return: Dictionary with content-type set for form submission.
        """
        return {
            "Content-Type": "application/x-www-form-urlencoded"
        }