from flask import session
from secrets import token_urlsafe
from jwt import encode
from urllib.parse import urlencode
from grc.one_login.one_login_config import OneLoginConfig


class OneLoginAuthorizationRequest:
    """
    Handles creation of signed authorization requests for GOV.UK One Login.
    Generates redirect URLs for identity and authentication flows.
    """

    def __init__(self, config: OneLoginConfig):
        """
        Initializes the authorization request handler with configuration.

        :param config: OneLoginConfig object with necessary keys and endpoints.
        """
        self.config = config

    def build_authentication_redirect_url(self) -> str:
        """
        Builds the authentication redirect URL for One Login.

        :return: URL to redirect the user to for authentication only.
        """
        vtr = "Cl.Cm"
        signed_request = self._create_signed_auth_request(vtr=vtr, redirect_uri=self.config.auth_redirect_uri)
        redirect_url = self._build_redirect_url(signed_jwt=signed_request)
        return redirect_url

    def _create_signed_auth_request(self, vtr: str, redirect_uri: str) -> str:
        """
        Creates and signs a JWT authorization request for One Login.

        :param vtr: Vector of Trust requirement (e.g., 'Cl.Cm' or 'Cl.Cm.P2').
        :param redirect_uri: Callback URI to redirect to after authentication.
        :return: Signed JWT as a string.
        """
        state, nonce = self._generate_and_store_state_nonce()
        request_payload = {
            "response_type": "code",
            "scope": self.config.scope,
            "client_id": self.config.client_id,
            "state": state,
            "redirect_uri": redirect_uri,
            "nonce": nonce,
            "aud": self.config.authorization_endpoint,
            "iss": self.config.client_id,
            "ui_locales": "en",
            "vtr": [vtr],
            "claims": self.config.claims
        }

        return encode(request_payload, self.config.private_key, algorithm="RS256", headers={"kid": self.config.kid})

    def _build_redirect_url(self, signed_jwt: str) -> str:
        """
        Constructs the full redirect URL using the signed request JWT.

        :param signed_jwt: The signed JWT to embed in the request parameter.
        :return: Full redirect URL for One Login authorization.
        """
        params = {
            "response_type": "code",
            "scope": self.config.scope,
            "client_id": self.config.client_id,
            "request": signed_jwt
        }
        return f"{self.config.authorization_endpoint}?{urlencode(params)}"

    @staticmethod
    def _generate_and_store_state_nonce() -> tuple:
        """
        Generates and stores `state` and `nonce` values in session for security.

        :return: Tuple of (state, nonce).
        """
        state = token_urlsafe(16)
        nonce = token_urlsafe(16)
        session["state"] = state
        session["nonce"] = nonce
        return state, nonce