from grc.one_login import OneLoginTokenStorage
from grc.one_login.one_login_config import OneLoginConfig
from grc.utils.logger import LogLevel, Logger
import requests

logger = Logger()

class OneLoginUserInfoRequest:

    def __init__(self, config: OneLoginConfig):
        self.config = config

    def fetch_user_info(self):
        try:
            access_token = OneLoginTokenStorage.get_access_token()
            headers = self._build_user_info_request_headers(access_token=access_token)
            response = requests.get(url=self.config.user_info_endpoint, headers=headers)

            if response.status_code != 200:
                error_message = f"Token request failed: {response.status_code} - {response.text}"
                logger.log(LogLevel.ERROR, error_message)
                raise Exception(error_message)

            user_info = response.json()
            logger.log(LogLevel.DEBUG, str(user_info))
            return user_info

        except Exception as e:
            error_message = f"Failed to fetch user information due to: {str(e)}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

    @staticmethod
    def _build_user_info_request_headers(access_token:str):
        return {
            'Authorization': f'Bearer {access_token}'
        }
