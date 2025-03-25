import logging
import os
from os.path import dirname


class Config:
    BASE_DIRECTORY = dirname(dirname(os.path.abspath(__file__)))
    ENVIRONMENT = os.environ.get("FLASK_ENV", "local")
    FLASK_APP = os.environ.get("FLASK_APP", "admin")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_KEY = os.environ.get("SQLALCHEMY_KEY")
    DEFAULT_ADMIN_USER = os.environ.get("DEFAULT_ADMIN_USER")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")
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
    SESSION_COOKIE_SAMESITE = "Strict"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Stops the CSRF token expiring (before the lifetime of the session). This was an accessibility problem
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION")
    AWS_S3_REGION_NAME = os.environ.get("AWS_REGION")
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    EXTERNAL_S3_AWS_ACCESS_KEY_ID = os.environ.get("EXTERNAL_S3_AWS_ACCESS_KEY_ID")
    EXTERNAL_S3_AWS_SECRET_ACCESS_KEY = os.environ.get("EXTERNAL_S3_AWS_SECRET_ACCESS_KEY")
    EXTERNAL_S3_AWS_REGION = os.environ.get("EXTERNAL_S3_AWS_REGION")
    EXTERNAL_S3_AWS_BUCKET_NAME = os.environ.get("EXTERNAL_S3_AWS_BUCKET_NAME")
    JOB_TOKEN = os.environ.get("JOB_TOKEN")
    BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")
    SENTRY_URL = os.environ.get("SENTRY_URL")
    MEMORY_STORAGE_URL = os.environ.get('MEMORY_STORAGE_URL')
    GLIMR_API_KEY = os.environ.get('GLIMR_API_KEY')
    GLIMR_BASE_URL = os.environ.get('GLIMR_BASE_URL')

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    DEFAULT_ADMIN_USER = "test.email@example.com"
    TEST_URL = os.environ.get('TEST_URL', 'http://localhost')
    FLASK_APP = "admin"