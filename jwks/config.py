import os

class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV')
    FLASK_APP = os.environ.get('FLASK_APP')
    ONE_LOGIN_PUBLIC_KEY_PATH = os.environ.get('ONE_LOGIN_PUBLIC_KEY_PATH')