import pytest
from grc import create_app
from grc.config import TestConfig


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()
