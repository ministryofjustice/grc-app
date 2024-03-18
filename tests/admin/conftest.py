import pytest
from admin import create_app
from admin.config import TestConfig
from grc.models import db, AdminUser
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
def admin(app):
    with app.app_context():
        test_admin = AdminUser(email=app.config['DEFAULT_ADMIN_USER'], password=generate_password_hash('password'),
                               userType='ADMIN', passwordResetRequired=False)
        db.session.add(test_admin)
        db.session.commit()
        yield test_admin

        db.session.delete(test_admin)
        db.session.commit()
