from grc.one_login.one_login_config import OneLoginConfig
from grc.utils.logger import Logger, LogLevel
from flask import session
import requests

logger = Logger()

class OneLoginLogout:

    def __init__(self, config: OneLoginConfig):
        self.config = config

    def logout(self, id_token: str):
        OneLoginLogout._end_user_session()
        OneLoginLogout._logout_one_login(logout_endpoint=self.config.end_session_endpoint, id_token=id_token, post_logout_redirect_uri=self.config.post_logout_redirect_uri)

    @staticmethod
    def _end_user_session():
        try:
            session.pop('user', None)
        except Exception as e:
            raise Exception(f'Failed to end user session due to {str(e)}.')

    @staticmethod
    def _logout_one_login(logout_endpoint: str, id_token: str, post_logout_redirect_uri:str):
        try:
            request_url = OneLoginLogout._build_logout_url(logout_endpoint=logout_endpoint, id_token=id_token, post_logout_redirect_uri=post_logout_redirect_uri)
            response = requests.get(request_url)
            response.raise_for_status()

        except Exception as e:
            raise Exception(f'Failed to log user out of one login due to {str(e)}.')

    @staticmethod
    def _build_logout_url(logout_endpoint: str, id_token: str, post_logout_redirect_uri: str):
        url_without_state = f"{logout_endpoint}?id_token_hint={id_token}&post_logout_redirect_uri={post_logout_redirect_uri}"
        state = session.get('state')
        if state:
            return url_without_state+f"&state={str(state)}"
        else:
            return url_without_state


