from .one_login_config import OneLoginConfig
from flask import session
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import Logger, LogLevel
from typing import Dict
from time import time
import base64
import hashlib

logger = Logger()

class OneLoginTokenValidator:
    """
    Validates ID and Access tokens received from the One Login service.
    Checks signature, claims, expiration, and hash integrity.
    """

    def __init__(self, config: OneLoginConfig):
        """
        Initializes the validator with configuration for expected issuer, client, and JWKS URI.

        :param config: OneLoginConfig object containing necessary settings.
        """
        self.config = config

    def validate_tokens(self, access_token: str, id_token: str):
        """
        Validates the structure and integrity of both the ID token and access token.

        :param access_token: The OAuth access token.
        :param id_token: The OpenID Connect ID token (JWT).
        :raises Exception: If any validation check fails.
        """
        public_key = JWTHandler.get_public_key_from_jwks(jwks_uri=self.config.jwks_uri, jwt_token=id_token)
        id_token_claims = JWTHandler.decode_jwt_with_key(jwt_token=id_token, public_key=public_key, algorithm="RS256")

        self._validate_id_token(
            id_token_claims=id_token_claims,
            expected_iss=self.config.issuer,
            expected_aud=self.config.client_id
        )
        self._validate_access_token(id_token_claims, access_token)

    @staticmethod
    def _validate_id_token(id_token_claims: Dict[str, str], expected_iss: str, expected_aud: str):
        """
        Validates key claims in the ID token including issuer, audience, expiration, issue time, nonce, and vot.

        :param id_token_claims: Decoded JWT claims from the ID token.
        :param expected_iss: Expected issuer value.
        :param expected_aud: Expected audience/client_id value.
        :raises Exception: If any claim is missing or invalid.
        """
        if id_token_claims.get("iss") != expected_iss:
            error_message = f"Invalid iss. Expected {expected_iss}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        if id_token_claims.get("aud") != expected_aud:
            error_message = f"Invalid aud. Expected {expected_aud}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        time_now = int(time())
        if int(id_token_claims.get('exp')) < time_now:
            error_message = "Id token is expired."
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        if int(id_token_claims.get('iat')) > time_now:
            error_message = "Id token's issued at time is after the current time."
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        expected_nonce = session.get('nonce')
        if id_token_claims.get('nonce') != expected_nonce:
            error_message = "Invalid nonce."
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        expected_vot = "Cl.Cm"
        if id_token_claims.get("vot") != expected_vot:
            error_message = f"Invalid vot claim. Expected {expected_vot}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_access_token(id_token_claims: Dict[str, str], access_token: str):
        """
        Verifies the access token against the 'at_hash' claim in the ID token.

        :param id_token_claims: Decoded JWT claims from the ID token.
        :param access_token: The access token to validate.
        :raises Exception: If the 'at_hash' is missing or does not match.
        """
        at_hash = id_token_claims.get('at_hash')
        if not at_hash:
            raise Exception("Missing 'at_hash' claim in ID token")

        digest = hashlib.sha256(access_token.encode('utf-8')).digest()
        left_most = digest[:16]

        recomputed_at_hash = base64.urlsafe_b64encode(left_most).rstrip(b'=').decode('utf-8')

        if recomputed_at_hash != at_hash:
            raise Exception("Access token hash does not match 'at_hash' in ID token")