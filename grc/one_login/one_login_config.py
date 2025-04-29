from flask import current_app
import requests
from typing import Dict, Any
from cryptography.hazmat.primitives import serialization

class OneLoginConfig:

    def __init__(self):
        self.client_id: str = current_app.config['ONE_LOGIN_CLIENT_ID']
        self.redirect_uri: str = current_app.config['ONE_LOGIN_REDIRECT_URI']
        self.scope: str = "openid phone email"
        self.claims: Dict[str, Dict[str, None]] = self.build_claims()
        self.public_key: bytes = self.load_public_key()
        self.private_key: bytes = self.load_private_key()
        self.metadata: Dict[str, Any] = self.get_discovery_metadata()
        self.issuer: str = self.metadata['issuer']
        self.authorization_endpoint: str = self.metadata['authorization_endpoint']
        self.user_info_endpoint: str = self.metadata['userinfo_endpoint']
        self.token_endpoint: str = self.metadata['token_endpoint']
        self.registration_endpoint: str = self.metadata['registration_endpoint']
        self.jwks_uri: str = self.metadata['jwks_uri']

    @staticmethod
    def get_discovery_metadata() -> Dict[str, Any]:
        url = current_app.config['ONE_LOGIN_DISCOVERY_URL']
        return requests.get(url).json()

    @staticmethod
    def load_public_key() -> bytes:
        with open('grc/one_login/keys/public_key.pem', "rb") as f:
            return f.read()

    @staticmethod
    def load_private_key() -> bytes:
        with open('grc/one_login/keys/private_key.pem', "rb") as f:
            return f.read()

    @staticmethod
    def build_claims() -> Dict[str, Dict[str, None]]:
        return {
            "userinfo": {
                "https://vocab.account.gov.uk/v1/coreIdentityJWT": None,
                "https://vocab.account.gov.uk/v1/address": None,
                "https://vocab.account.gov.uk/v1/returnCode": None
            }
        }