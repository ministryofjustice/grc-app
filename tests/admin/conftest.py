import pytest
from admin import create_app
from admin.config import TestConfig
from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc.models import db, AdminUser, SecurityCode
from grc.utils.security_code import generate_security_code_and_expiry
from werkzeug.security import generate_password_hash


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def default_admin(app):
    with app.app_context():
        test_admin = AdminUser(email=app.config['DEFAULT_ADMIN_USER'],
                               password=generate_password_hash('123ABC'), userType='ADMIN')
        db.session.add(test_admin)
        db.session.commit()
        yield test_admin

        db.session.delete(test_admin)
        db.session.commit()


@pytest.fixture()
def new_admin(app):
    with app.app_context():
        test_admin = AdminUser(email=app.config['DEFAULT_ADMIN_USER'], password=generate_password_hash('password'),
                               userType='ADMIN', passwordResetRequired=False)
        db.session.add(test_admin)
        db.session.commit()
        yield test_admin

        db.session.delete(test_admin)
        db.session.commit()


@pytest.fixture()
def admin(app):
    with app.app_context():
        twenty_five_hours_ago = datetime.now() - relativedelta(hours=25)
        last_logged_datetime = datetime.strftime(twenty_five_hours_ago, '%d/%m/%Y %H:%M:%S')
        test_admin = AdminUser(email=app.config['DEFAULT_ADMIN_USER'], password=generate_password_hash('password'),
                               userType='ADMIN', passwordResetRequired=False, dateLastLogin=last_logged_datetime)
        db.session.add(test_admin)
        db.session.commit()
        yield test_admin

        db.session.delete(test_admin)
        db.session.commit()


@pytest.fixture()
def security_code(app):
    with app.app_context():
        code, _ = generate_security_code_and_expiry(app.config['DEFAULT_ADMIN_USER'])
        security_code_ = SecurityCode.query.filter(
            SecurityCode.email == app.config['DEFAULT_ADMIN_USER'],
            SecurityCode.code == code
        ).first()
        yield security_code_

        db.session.delete(security_code_)
        db.session.commit()


@pytest.fixture()
def expired_security_code(app):
    with app.app_context():
        security_code_ = SecurityCode(code='123456', email=app.config['DEFAULT_ADMIN_USER'])
        db.session.add(security_code_)
        now = datetime.now()
        expired_code_date = now - relativedelta(hours=25)
        security_code_.created = expired_code_date
        db.session.commit()
        yield security_code_

        db.session.delete(security_code_)
        db.session.commit()
