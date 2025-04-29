import logging
import os
from os.path import dirname


class Config:
    BASE_DIRECTORY = dirname(dirname(os.path.abspath(__file__)))
    ENVIRONMENT = os.environ.get("FLASK_ENV", "local")
    NON_LIVE_ENV = ["development", "local", "test"]
    FLASK_APP = os.environ.get("FLASK_APP", "grc")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_KEY = os.environ.get("SQLALCHEMY_KEY")
    LOG_LEVEL = (
        logging.getLevelName(os.environ.get("LOG_LEVEL"))
        if "LOG_LEVEL" in os.environ
        else logging.INFO
    )
    NOTIFY_OVERRIDE_EMAIL = (
        os.environ.get("NOTIFY_OVERRIDE_EMAIL")
        if "NOTIFY_OVERRIDE_EMAIL" in os.environ
        else False
    )
    NOTIFY_API = os.environ.get("NOTIFY_API")
    GOVUK_PAY_API = os.environ.get("GOVUK_PAY_API")
    GOVUK_PAY_API_KEY = os.environ.get("GOVUK_PAY_API_KEY")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Stops the CSRF token expiring (before the lifetime of the session). This was an accessibility problem
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION")
    AWS_S3_REGION_NAME = os.environ.get("AWS_REGION")
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE")
    AV_API = os.environ.get("AV_API")
    BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")
    SENTRY_URL = os.environ.get("SENTRY_URL")
    MEMORY_STORAGE_URL = os.environ.get('MEMORY_STORAGE_URL')

    #ONE LOGIN
    ONE_LOGIN_DISCOVERY_URL = os.environ.get("ONE_LOGIN_DISCOVERY_URL")
    ONE_LOGIN_CLIENT_ID = os.environ.get("ONE_LOGIN_CLIENT_ID")
    ONE_LOGIN_PRIVATE_KEY = os.environ.get("ONE_LOGIN_PRIVATE_KEY")
    ONE_LOGIN_REDIRECT_URI = os.environ.get("ONE_LOGIN_REDIRECT_URI")

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    TEST_PUBLIC_USER = 'test.public.email@example.com'
    AV_API = 'TEST CLAMAV API'
    NOTIFY_API = os.environ.get('NOTIFY_API')
    FLASK_APP = "grc"
