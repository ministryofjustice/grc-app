import pytest
import jsonpickle
from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc import create_app
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.config import TestConfig
from grc.models import db, SecurityCode, Application, ApplicationStatus
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
def security_code(app, public_user_email) -> SecurityCode:
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


@pytest.fixture()
def test_application(app, public_user_email):
    with app.app_context():
        application_record = Application(
            reference_number='ABCD1234',
            email=public_user_email,
        )

        db.session.add(application_record)
        db.session.commit()

        data = ApplicationData()
        data.reference_number = application_record.reference_number
        data.email_address = application_record.email
        save_test_data(data)

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


@pytest.fixture()
def test_application_no_email(app, public_user_email):
    with app.app_context():
        application_record = Application(
            reference_number='ABCD1234',
            email=''
        )
        db.session.add(application_record)
        db.session.commit()

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


@pytest.fixture()
def test_application_deleted(app, public_user_email):
    with app.app_context():
        application_record = Application(
            reference_number='ABCD1234',
            email=public_user_email,
            status=ApplicationStatus.DELETED
        )
        db.session.add(application_record)
        db.session.commit()

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


@pytest.fixture()
def test_application_submitted(app, public_user_email):
    with app.app_context():
        application_record = Application(
            reference_number='ABCD1234',
            email=public_user_email,
            status=ApplicationStatus.SUBMITTED
        )
        db.session.add(application_record)
        db.session.commit()

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


def load_test_data(reference_number):
    application_record: Application = Application.query.filter_by(
        reference_number=reference_number
    ).first()
    return application_record.application_data()


def save_test_data(data):
    application_record: Application = Application.query.filter_by(
        reference_number=data.reference_number
    ).first()
    user_input: str = jsonpickle.encode(data)
    application_record.user_input = user_input
    application_record.updated = datetime.now()
    db.session.commit()
