import pytest
from grc import create_app
from grc.config import TestConfig


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


def pytest_addoption(parser):
    parser.addoption("--max-retries", type=int, default=1, help="Add number of attempts to ping endpoint")
    parser.addoption("--timeout", type=int, default=3, help="Timeout in seconds between each ping")


@pytest.fixture
def max_retries(request):
    return request.config.getoption("--max-retries")


@pytest.fixture
def timeout(request):
    return request.config.getoption("--timeout")