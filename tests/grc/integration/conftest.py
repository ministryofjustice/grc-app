import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc import create_app
from grc.config import TestConfig
from grc.models import db, SecurityCode
from grc.utils.security_code import generate_security_code_and_expiry


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def public_user_email(app):
    return app.config['TEST_PUBLIC_USER']


@pytest.fixture()
def security_code_(app, public_user_email) -> SecurityCode:
    with app.app_context():
        code, _ = generate_security_code_and_expiry(public_user_email)
        security_code_ = SecurityCode.query.filter(
            SecurityCode.email == public_user_email,
            SecurityCode.code == code
        ).first()
        yield security_code_


@pytest.fixture()
def expired_security_code(app, public_user_email):
    with app.app_context():
        security_code_ = SecurityCode(code='123456', email=public_user_email)
        db.session.add(security_code_)
        now = datetime.now()
        expired_code_date = now - relativedelta(hours=25)
        security_code_.created = expired_code_date
        db.session.commit()
        yield security_code_

        db.session.delete(security_code_)
        db.session.commit()
