import logging
import os
from os.path import dirname


class Config:
    BASE_DIRECTORY = dirname(dirname(os.path.abspath(__file__)))
    ENVIRONMENT = os.environ.get("FLASK_ENV", "local")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_KEY = os.environ.get("SQLALCHEMY_KEY")
    LOG_LEVEL = (
        logging.getLevelName(os.environ.get("LOG_LEVEL"))
        if "LOG_LEVEL" in os.environ
        else logging.INFO
    )
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Stops the CSRF token expiring (before the lifetime of the session). This was an accessibility problem
    BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")
    IP_WHITELIST = os.environ.get("IP_WHITELIST")
    SENTRY_URL = os.environ.get("SENTRY_URL")
    MEMORY_STORAGE_URL = os.environ.get('MEMORY_STORAGE_URL')


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    TEST_URL = os.environ.get('TEST_URL', 'http://localhost')
    FLASK_APP = "dashboard"
