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
        Fetches and returns user information from One Login.

        :param access_token: Access token used to fetch user info.
        """
        return self._fetch_user_info(access_token)

    def get_names_dob_from_context_jwt(self, context_jwt_token: str) -> Tuple[Dict, Optional[str]]:
        """
        Decodes the context JWT to extract the current name and date of birth.

        :param context_jwt_token: The JWT containing core identity attributes.
        :return: Tuple of (full name, date of birth).
        :raises Exception: If decoding fails or data is incomplete.
        """
        public_key = JWTHandler.get_public_key_from_did(did_url=self.config.did_url, jwt_token=context_jwt_token)
        decoded_context_token = JWTHandler.decode_jwt_with_key(jwt_token=context_jwt_token, public_key=public_key, algorithm="ES256")
        credentialSubject = decoded_context_token.get('vc', {}).get('credentialSubject')

        if credentialSubject is not None:
            names = credentialSubject.get('name')
            name = OneLoginUserInfoRequest._extract_current_name(names)
            dob_list = credentialSubject.get("birthDate", [])
            dob = dob_list[0]["value"] if dob_list else None

            if dob is not None:
                dob = OneLoginUserInfoRequest._format_date_into_datetime_date(dob)

            return name, dob

        raise Exception('Could not get credentials from context JWT.')

    @staticmethod
    def store_user_info_redis_mapping(sub: str):
        current_app.config['SESSION_REDIS'].set(f"user_sub:{sub}", request.cookies.get('session'))

    def _fetch_user_info(self, access_token: str):
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
    def _extract_current_name(names) -> Dict:
        """
        Extracts the full current name from the name entries based on `validUntil` field.

        :param names: List of name records.
        :return: The most current full name string.
        :raises Exception: If a valid name is not found.
        """
        for name_entry in names:
            if name_entry.get('validUntil') is None:
                nameParts = name_entry.get('nameParts', [])
                result = {
                    "first_name": "",
                    "middle_names": "",
                    "last_name": ""
                }

                given_names = [part["value"] for part in nameParts if part["type"] == "GivenName"]
                family_names = [part["value"] for part in nameParts if part["type"] == "FamilyName"]

                if given_names:
                    result["first_name"] = given_names[0]
                    if len(given_names) > 1:
                        result["middle_names"] = " ".join(given_names[1:])

                result["last_name"] = family_names[0]

                return result

        raise Exception('No valid name present')

    @staticmethod
    def _format_date_into_datetime_date(date: str):
        return datetime.strptime(date, "%Y-%m-%d").date()

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
