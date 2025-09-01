from flask import session, current_app, request, g
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import LogLevel, Logger
import requests
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from grc.business_logic.data_store import DataStore


logger = Logger()

class OneLoginUserInfoRequest:
    """
    Handles the retrieval and parsing of user information from One Login,
    and populates the Flask session with user attributes for both authentication and identity verification.
    """

    def __init__(self, config: OneLoginConfig):
        """
        Initialize with OneLogin configuration.

        :param config: OneLoginConfig object with endpoint and key configuration.
        """
        self.config = config

    def request_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Makes a request to the user info endpoint to retrieve the user's attributes.

        :param access_token: OAuth access token for authorization.
        :return: Dictionary of user claims.
        :raises Exception: If the HTTP request fails or response is invalid.
        """
        try:
            headers = OneLoginUserInfoRequest._build_user_info_request_headers(access_token=access_token)
            response = requests.get(url=self.config.user_info_endpoint, headers=headers)

            if response.status_code != 200:
                error_message = f"User Info request failed: {response.status_code} - {response.text}"
                logger.log(LogLevel.ERROR, error_message)
                raise Exception(error_message)

            user_info = response.json()
            return user_info

        except Exception as e:
            raise Exception(f"Failed to fetch user information due to: {str(e)}")

    @staticmethod
    def store_user_info_redis_mapping(sub: str):
        current_app.config['SESSION_REDIS'].sadd(f"user_sub:{sub}", f"session:{request.cookies.get('session')}")

    @staticmethod
    def _build_user_info_request_headers(access_token: str):
        """
        Builds authorization headers for the user info endpoint request.

        :param access_token: OAuth access token.
        :return: Dictionary with Authorization header.
        """
        return {
            'Authorization': f'Bearer {access_token}'
        }
