from flask import session
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import LogLevel, Logger
import requests
from typing import Tuple, List

logger = Logger()

class OneLoginUserInfoRequest:

    def __init__(self, config: OneLoginConfig):
        self.config = config

    def create_auth_session(self, access_token: str, id_token: str):
        user_info = self._fetch_user_info(access_token)
        session["user"] = {
            "sub": user_info.get("sub"),
            "email": user_info.get("email"),
            "phone_number": user_info.get("phone_number"),
            "identity_verified": False,
            "id_token": id_token
        }

    def update_auth_session_with_identity(self, access_token: str, id_token:str):
        user_info = self._fetch_user_info(access_token)

        if "user" not in session:
            session["user"] = {
                "sub": user_info.get("sub"),
                "email": user_info.get("email"),
                "phone_number": user_info.get("phone_number"),
                "id_token": id_token
            }

        context_jwt = user_info.get("https://vocab.account.gov.uk/v1/coreIdentityJWT")
        name, dob = self._get_names_dob_from_context_jwt(context_jwt)

        updates = {
            "name": name,
            "dob": dob,
            "address": user_info.get("https://vocab.account.gov.uk/v1/address"),
            "driving_permit": user_info.get("https://vocab.account.gov.uk/v1/drivingPermit"),
            "passport": user_info.get("https://vocab.account.gov.uk/v1/passport"),
            "identity_verified": True
        }
        session["user"].update(updates)
        session.modified = True

    def _fetch_user_info(self, access_token:str):
        try:
            headers = OneLoginUserInfoRequest._build_user_info_request_headers(access_token=access_token)
            response = requests.get(url=self.config.user_info_endpoint, headers=headers)

            if response.status_code != 200:
                error_message = f"Token request failed: {response.status_code} - {response.text}"
                logger.log(LogLevel.ERROR, error_message)
                raise Exception(error_message)

            user_info = response.json()
            return user_info

        except Exception as e:
            error_message = f"Failed to fetch user information due to: {str(e)}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    def _get_names_dob_from_context_jwt(self, context_jwt_token:str) -> Tuple[str, str]:
        public_key = JWTHandler.get_public_key_from_did(did_url=self.config.did_url, jwt_token=context_jwt_token)
        decoded_context_token = JWTHandler.decode_jwt_with_key(jwt_token=context_jwt_token, public_key=public_key, algorithm="ES256")
        credentialSubject = decoded_context_token.get('vc', {}).get('credentialSubject')

        if credentialSubject:
            names = credentialSubject.get('name')
            name = OneLoginUserInfoRequest._extract_current_name(names)
            dob_list = credentialSubject.get("birthDate", [])
            dob = dob_list[0]["value"] if dob_list else None
            return name, dob

        raise Exception('Could not get credentials from context JWT.')

    @staticmethod
    def _extract_current_name(names) -> str:
        for name_entry in names:
            if name_entry.get('validUntil') is None:
                name_parts = name_entry.get('nameParts', [])

                given_names = [part['value'] for part in name_parts if part['type'] == 'GivenName']
                family_name = next((part['value'] for part in name_parts if part['type'] == 'FamilyName'), "")

                full_name = " ".join(given_names) + " " + family_name
                return full_name.strip()
        raise Exception('No valid name present')


    @staticmethod
    def _build_user_info_request_headers(access_token:str):
        return {
            'Authorization': f'Bearer {access_token}'
        }
