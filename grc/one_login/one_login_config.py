from flask import current_app
import requests
from typing import Dict, Any
from functools import lru_cache

class OneLoginConfig:
    """
    Loads and holds configuration and metadata for integrating with GOV.UK One Login.
    Includes credentials, endpoints, keys, and requested claims.
    """

    def __init__(self):
        """
        Initializes OneLoginConfig with Flask app settings and discovery metadata.
        """
        self.client_id: str = current_app.config['ONE_LOGIN_CLIENT_ID']
        self.auth_redirect_uri: str = current_app.config['ONE_LOGIN_AUTH_REDIRECT_URI']
        self.identity_redirect_uri: str = current_app.config['ONE_LOGIN_IDENTITY_REDIRECT_URI']
        self.did_url: str = current_app.config['ONE_LOGIN_DID_URL']
        self.post_logout_redirect_uri = current_app.config['ONE_LOGIN_POST_LOGOUT_REDIRECT_URI']
        self.scope: str = "openid phone email"
        self.claims: Dict[str, Dict[str, None]] = self.build_claims()
        self.public_key: bytes = self.load_public_key()
        self.private_key: bytes = self.load_private_key()
        self.metadata: Dict[str, Any] = self.get_discovery_metadata()
        self.issuer: str = self.metadata['issuer']
        self.authorization_endpoint: str = self.metadata['authorization_endpoint']
        self.user_info_endpoint: str = self.metadata['userinfo_endpoint']
        self.token_endpoint: str = self.metadata['token_endpoint']
        self.end_session_endpoint = self.metadata['end_session_endpoint']
        self.registration_endpoint: str = self.metadata['registration_endpoint']
        self.jwks_uri: str = self.metadata['jwks_uri']

    @staticmethod
    def get_discovery_metadata() -> Dict[str, Any]:
        """
        Retrieves OpenID Connect discovery metadata from configured URL.

        :return: A dictionary containing the provider's discovery metadata.
        """
        url = current_app.config['ONE_LOGIN_DISCOVERY_URL']
        return requests.get(url).json()

    @staticmethod
    def load_public_key() -> bytes:
        """
        Loads the One Login public key from the PEM file.

        :return: Public key in bytes.
        """
        with open('grc/one_login/keys/public_key.pem', "rb") as f:
            return f.read()

    @staticmethod
    def load_private_key() -> bytes:
        """
        Loads the One Login private key from the PEM file.

        :return: Private key in bytes.
        """
        with open('grc/one_login/keys/private_key.pem', "rb") as f:
            return f.read()

    @staticmethod
    def build_claims() -> Dict[str, Dict[str, None]]:
        """
        Builds the set of claims to request from One Login.

        :return: Dictionary specifying requested userinfo claims.
        """
        return {
            "userinfo": {
                "https://vocab.account.gov.uk/v1/coreIdentityJWT": None,
                "https://vocab.account.gov.uk/v1/address": None,
                "https://vocab.account.gov.uk/v1/returnCode": None,
                "https://vocab.account.gov.uk/v1/passport": None,
                "https://vocab.account.gov.uk/v1/drivingPermit": None
            }
        }

@lru_cache(maxsize=1)
def get_onelogin_config() -> OneLoginConfig:
    """
    Lazily instantiates and caches OneLoginConfig instance.

    :return: Cached OneLoginConfig instance.
    """
    return OneLoginConfig()