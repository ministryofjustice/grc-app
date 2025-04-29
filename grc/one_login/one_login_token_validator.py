from grc.one_login import OneLoginConfig
from flask import session
from grc.one_login.one_login_jwt_handler import JWTHandler
from grc.utils.logger import Logger, LogLevel
from typing import Dict
from time import time
import base64
import hashlib

logger = Logger()

class OneLoginTokenValidator:

    def __init__(self, config: OneLoginConfig):
        self.config = config

    def validate_tokens(self, access_token: str, id_token: str):
        id_token_claims = JWTHandler.decode_jwt_token(jwt_token=id_token, jwks_uri=self.config.jwks_uri, client_id=self.config.client_id, issuer=self.config.issuer)
        self._validate_id_token(id_token_claims=id_token_claims, expected_iss=self.config.issuer, expected_aud=self.config.client_id)
        self._validate_access_token(id_token_claims, access_token)

    @staticmethod
    def _validate_id_token(id_token_claims: Dict[str, str], expected_iss: str, expected_aud: str):
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
    def _validate_access_token(id_token_claims:Dict[str, str], access_token):
        at_hash = id_token_claims.get('at_hash')
        if not at_hash:
            raise Exception("Missing 'at_hash' claim in ID token")

        digest = hashlib.sha256(access_token.encode('utf-8')).digest()

        left_most = digest[:16]

        recomputed_at_hash = base64.urlsafe_b64encode(left_most).rstrip(b'=').decode('utf-8')

        if recomputed_at_hash != at_hash:
            raise Exception("Access token hash does not match 'at_hash' in ID token")

