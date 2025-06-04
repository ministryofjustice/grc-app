from grc.one_login.one_login_config import OneLoginConfig
from grc.utils.logger import Logger, LogLevel
from flask import session, current_app

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

    def logout_redirect_url_to_confirmation_page(self, id_token: str):
        """
        Builds a logout redirect url to go to first page

        :param id_token: ID token used for logout redirection.
        """
        return self._build_logout_redirect_url(id_token=id_token, redirect_uri=self.config.confirmation_logout_redirect_uri)

    def logout_redirect_url_to_save_page(self, id_token: str):
        """
        Builds a logout redirect url to go to save reference number page

        :param id_token: ID token used for logout redirection.
        """
        return self._build_logout_redirect_url(id_token=id_token, redirect_uri=self.config.save_and_exit_redirect_uri)

    def logout_redirect_url_to_reference_check_page(self, id_token: str):
        """
        Builds a logout redirect url to go to reference number check page

        :param id_token: ID token used for logout redirection.
        """
        return self._build_logout_redirect_url(id_token=id_token, redirect_uri=self.config.reference_logout_redirect_uri)

    def _build_logout_redirect_url(self, id_token: str, redirect_uri:str):
        """
        Builds a logout redirect url a user will be directed to and then takes a redirect_uri a user will be taken back to in the app

        :param id_token: ID token used for logout redirection.
        :param redirect_uri: The uri a user will be taken to after one login logout
        """
        return OneLoginLogout._build_logout_url(
            logout_endpoint=self.config.end_session_endpoint,
            id_token=id_token,
            post_logout_redirect_uri=redirect_uri
        )

    @staticmethod
    def end_user_session():
        """
        Removes the user session from the Flask session store.
        """
        try:
            # session.pop('user')
            # session.pop('one_login_auth')
            session.clear()
        except Exception as e:
            raise Exception(f'Failed to end user session due to {str(e)}.')

    @staticmethod
    def end_user_session_with_sub(sub: str):
        """
        Removes the user session from the Flask session store.
        """
        try:
            redis_client = current_app.config['SESSION_REDIS']
            session_key = redis_client.get(f"user_sub:{sub}")
            if session_key:
                session_key = session_key.decode('utf-8')
                redis_client.delete(f"session:{session_key}")
                redis_client.delete(f"user_sub:{sub}")
                logger.log(LogLevel.INFO, f'User redis session id and mapping have been deleted.')

            else:
                logger.log(LogLevel.INFO, f"No session found for sub {sub}. User could already be logged out.")

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