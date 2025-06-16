import json
from .one_login_config import OneLoginConfig
from flask import session
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import Logger, LogLevel
from typing import Dict, Any
from time import time
import base64
import hashlib
from cachetools import TTLCache

logger = Logger()

jti_cache = TTLCache(maxsize=1000, ttl=180)


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

    def validate_access_id_tokens(self, access_token: str, id_token: str):
        """
        Validates the structure and integrity of both the ID token and access token.

        :param access_token: The OAuth access token.
        :param id_token: The OpenID Connect ID token (JWT).
        :raises Exception: If any validation check fails.
        """
        public_key = JWTHandler.get_public_key_from_jwks(jwks_uri=self.config.jwks_uri, jwt_token=id_token)
        id_token_claims = JWTHandler.decode_jwt_with_key(jwt_token=id_token, public_key=public_key, algorithm="RS256")

        self._validate_id_token_claims(
            id_token_claims=id_token_claims,
            expected_iss=self.config.issuer,
            expected_aud=self.config.client_id,
            expected_vot="Cl.Cm"
        )
        self._validate_access_token(id_token_claims, access_token)

    def validate_logout_token(self, logout_token: str) -> Dict[str, Any]:
        public_key = JWTHandler.get_public_key_from_jwks(jwks_uri=self.config.jwks_uri, jwt_token=logout_token)
        logout_token_claims = JWTHandler.decode_jwt_with_key(jwt_token=logout_token, public_key=public_key, algorithm="ES256")

        self._validate_logout_token_claims(
            logout_token_claims=logout_token_claims,
            expected_iss=self.config.issuer,
            expected_aud=self.config.client_id,
        )

        return logout_token_claims

    @staticmethod
    def _validate_id_token_claims(id_token_claims: Dict[str, str], expected_iss: str, expected_aud: str, expected_vot: str):
        """
        Validates key claims in the ID token including issuer, audience, expiration, issue time, nonce, and vot.

        :param id_token_claims: Decoded JWT claims from the ID token.
        :param expected_iss: Expected issuer value.
        :param expected_aud: Expected audience/client_id value.
        :param expected_vot: Expected vot value.
        :raises Exception: If any claim is missing or invalid.
        """
        OneLoginTokenValidator._validate_iss(token_iss=id_token_claims.get('iss'), expected_iss=expected_iss)
        OneLoginTokenValidator._validate_aud(token_aud=id_token_claims.get('aud'), expected_aud=expected_aud)
        OneLoginTokenValidator._validate_exp(token_exp=int(id_token_claims.get('exp')))
        OneLoginTokenValidator._validate_iat(token_iat=int(id_token_claims.get('iat')))
        OneLoginTokenValidator._validate_nonce(token_nonce=id_token_claims.get('nonce'))
        OneLoginTokenValidator._validate_vot(token_vot=id_token_claims.get('vot'), expected_vot=expected_vot)

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

    @staticmethod
    def _validate_logout_token_claims(logout_token_claims: Dict[str, str], expected_iss: str, expected_aud: str):
        """
        Validates key claims in the logout token including issuer, audience, expiration, issue time, subject identifier, jti, events.

        :param logout_token_claims: Decoded JWT claims from the ID token.
        :param expected_iss: Expected issuer value.
        :param expected_aud: Expected audience/client_id value.
        :raises Exception: If any claim is missing or invalid.
        """
        OneLoginTokenValidator._validate_iss(token_iss=logout_token_claims.get('iss'), expected_iss=expected_iss)
        OneLoginTokenValidator._validate_aud(token_aud=logout_token_claims.get('aud'), expected_aud=expected_aud)
        OneLoginTokenValidator._validate_exp(token_exp=int(logout_token_claims.get('exp')))
        OneLoginTokenValidator._validate_iat(token_iat=int(logout_token_claims.get('iat')))
        OneLoginTokenValidator._validate_sub_exists(token_sub=logout_token_claims.get('sub'))
        OneLoginTokenValidator._validate_jti(token_jti=logout_token_claims.get('jti'))
        OneLoginTokenValidator._validate_events(token_events=logout_token_claims.get('events'))

    @staticmethod
    def _validate_iss(token_iss: str, expected_iss: str):
        if token_iss is None:
            raise Exception("Missing iss in token.")

        if token_iss != expected_iss:
            error_message = f"Invalid iss. Expected {expected_iss}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_aud(token_aud: str, expected_aud: str):
        if token_aud is None:
            raise Exception("Missing aud in token.")

        if token_aud != expected_aud:
            error_message = f"Invalid aud. Expected {expected_aud}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_exp(token_exp: int):
        if token_exp is None:
            raise Exception("Missing exp in token.")

        time_now = int(time())
        if token_exp < time_now:
            error_message = "Token is expired."
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_iat(token_iat: int):
        if token_iat is None:
            raise Exception("Missing iat in token.")

        time_now = int(time())
        if token_iat > time_now:
            raise Exception("Id token's issued at time is after the current time.")

    @staticmethod
    def _validate_nonce(token_nonce: str):
        if token_nonce is None:
            raise Exception("Missing nonce in token.")

        expected_nonce = session.get('nonce')
        if token_nonce != expected_nonce:
            error_message = "Invalid nonce."
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_vot(token_vot: str, expected_vot: str):
        if token_vot is None:
            raise Exception("Missing vot in token.")

        if token_vot != expected_vot:
            error_message = f"Invalid vot claim. Expected {expected_vot}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_sub_exists(token_sub: str):
        if token_sub is None:
            raise Exception("Missing sub in token.")

    @staticmethod
    def _validate_events(token_events: dict):
        if token_events is None:
            raise Exception("Missing events in token.")

        expected_events = {
            "http://schemas.openid.net/event/backchannel-logout": {}
        }

        if token_events != expected_events:
            error_message = f"Invalid events claim. Expected {expected_events}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _validate_jti(token_jti: str):
        if token_jti is None:
            raise Exception("Missing jti in token.")

        if token_jti in jti_cache:
            raise Exception("JTI already used.")

        jti_cache[token_jti] = True



