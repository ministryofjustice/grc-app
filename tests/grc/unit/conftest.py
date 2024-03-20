import pytest
from grc import create_app
from grc.config import TestConfig
from grc.models import db, SecurityCode
from grc.utils.security_code import security_code_generator


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def security_code(app) -> SecurityCode:
    with app.app_context():
        code = security_code_generator(app.config['TEST_PUBLIC_USER'])
        security_code_ = SecurityCode.query.filter(
            SecurityCode.email == app.config['TEST_PUBLIC_USER'],
            SecurityCode.code == code
        ).first()
        yield security_code_
