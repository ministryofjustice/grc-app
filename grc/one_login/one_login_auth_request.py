from flask import session
from secrets import token_urlsafe
from jwt import encode
from urllib.parse import urlencode
from grc.one_login.one_login_config import OneLoginConfig

class OneLoginAuthorizationRequest:

    def __init__(self, config: OneLoginConfig):
        self.config = config

    def build_identity_redirect_url(self):
        vtr = "Cl.Cm.P2"
        signed_request = self._create_signed_auth_request(vtr=vtr, redirect_uri=self.config.identity_redirect_uri)
        redirect_url = self._build_redirect_url(signed_jwt=signed_request)
        return redirect_url

    def build_authentication_redirect_url(self):
        vtr = "Cl.Cm"
        signed_request = self._create_signed_auth_request(vtr=vtr, redirect_uri=self.config.auth_redirect_uri)
        redirect_url = self._build_redirect_url(signed_jwt=signed_request)
        return redirect_url

    def _create_signed_auth_request(self, vtr: str, redirect_uri:str):
        state, nonce = self.generate_and_store_state_nonce()
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

        return encode(request_payload, self.config.private_key, algorithm="RS256")

    def _build_redirect_url(self, signed_jwt: str):
        params = {
            "response_type": "code",
            "scope": self.config.scope,
            "client_id": self.config.client_id,
            "request": signed_jwt
        }
        return f"{self.config.authorization_endpoint}?{urlencode(params)}"

    @staticmethod
    def generate_and_store_state_nonce():
        state = token_urlsafe(16)
        nonce = token_urlsafe(16)
        session["state"] = state
        session["nonce"] = nonce
        return state, nonce