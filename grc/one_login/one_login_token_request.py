from grc.one_login.one_login_config import OneLoginConfig
import requests
from typing import Dict, Any, Tuple

from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import LogLevel, Logger

logger = Logger()

class OneLoginTokenRequest:

    def __init__(self, config: OneLoginConfig):
        self.config = config

    def fetch_tokens(self, code:str) -> Tuple:
        try:
            token_url = self.config.token_endpoint
            data = self._build_token_request_data(code)
            headers = self.build_token_request_headers()

            response = requests.post(url=token_url, data=data, headers=headers)

            if response.status_code != 200:
                error_message = f"Token request failed: {response.status_code} - {response.text}"
                logger.log(LogLevel.ERROR, error_message)
                raise Exception(error_message)

            tokens = response.json()
            access_token = tokens['access_token']
            id_token = tokens['id_token']

            if not access_token or not id_token:
                error_message = "Access or Id token does not exist."
                logger.log(LogLevel.ERROR, error_message)
                raise Exception(error_message)

            return access_token, id_token

        except Exception as e:
            error_message = f"Failed to fetch tokens due to: {str(e)}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    def _build_token_request_data(self, code:str) -> Dict[str, Any]:
        assertion = JWTHandler.build_jwt_assertion(
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
            "redirect_uri": self.config.redirect_uri,
            "client_assertion": assertion,
            "client_assertion_type": assertion_type,
        }
        return data

    @staticmethod
    def build_token_request_headers() -> Dict[str, Any]:
        return {
            "Content-Type": "application/x-www-form-urlencoded"
        }


