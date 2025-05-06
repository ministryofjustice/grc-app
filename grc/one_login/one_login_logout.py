from grc.one_login.one_login_config import OneLoginConfig
from grc.utils.logger import Logger, LogLevel
from flask import session
import requests

logger = Logger()

class OneLoginLogout:
    """
    Handles user logout from GOV.UK One Login and local session termination.
    """

    def __init__(self, config: OneLoginConfig):
        """
        Initializes with configuration for logout endpoints and redirect URIs.

        :param config: OneLoginConfig instance with endpoint settings.
        """
        self.config = config

    def build_logout_redirect_url(self, id_token: str):
        """
        Logs the user out of the local session and initiates logout from One Login.

        :param id_token: ID token used for logout redirection.
        """
        return OneLoginLogout._build_logout_url(
            logout_endpoint=self.config.end_session_endpoint,
            id_token=id_token,
            post_logout_redirect_uri=self.config.post_logout_redirect_uri
        )

    @staticmethod
    def end_user_session():
        """
        Removes the user session from the Flask session store.
        """
        try:
            session.pop('user', None)
        except Exception as e:
            raise Exception(f'Failed to end user session due to {str(e)}.')

    @staticmethod
    def _build_logout_url(logout_endpoint: str, id_token: str, post_logout_redirect_uri: str) -> str:
        """
        Constructs the logout URL with required query parameters.

        :param logout_endpoint: Base logout endpoint URL.
        :param id_token: Token used as an ID token hint.
        :param post_logout_redirect_uri: URI to redirect the user after logout.
        :return: Fully constructed logout URL.
        """
        url_without_state = f"{logout_endpoint}?id_token_hint={id_token}&post_logout_redirect_uri={post_logout_redirect_uri}"
        state = session.get('state')
        if state:
            return url_without_state + f"&state={str(state)}"
        else:
            return url_without_state