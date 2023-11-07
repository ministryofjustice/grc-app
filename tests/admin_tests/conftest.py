import pytest
from admin import create_app
from admin.config import TestConfig


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()
