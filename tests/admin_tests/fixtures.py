import pytest
from admin import create_app
from admin.config import Config


@pytest.fixture()
def app():
    app = create_app(Config)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
