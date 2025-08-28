import pytest
from grc.one_login.mock_api.generate_mock_keys import generate_and_write_keys

@pytest.fixture(scope="session", autouse=True)
def setup_mock_keys():
    generate_and_write_keys()