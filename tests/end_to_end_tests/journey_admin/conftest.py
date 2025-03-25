import pytest
from admin import create_app
from admin.config import Config

@pytest.fixture()
def app():
    yield create_app(Config)