from flask import session
from grc.utils.logger import Logger, LogLevel
from typing import Dict

logger = Logger()

class OneLoginTokenStorage:

    @staticmethod
    def store_tokens(access_token:str, id_token:str):
        session["access_token"] = access_token
        session['id_token'] = id_token

    @staticmethod
    def clear_tokens():
        session.pop("access_token", None)
        session.pop("id_token", None)

    @staticmethod
    def get_access_token():
        access_token = session.get('access_token')
        if not access_token:
            error_message = "Access token does not exist in session"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)
        return access_token

    @staticmethod
    def get_id_token():
        id_token = session.get('id_token')
        if not id_token:
            error_message = "Id token does not exist in session"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)
        return id_token