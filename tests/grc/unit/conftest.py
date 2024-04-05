import pytest
import grc
import admin
from datetime import datetime
from dateutil.relativedelta import relativedelta
from admin.config import TestConfig as AdminTestConfig
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.config import TestConfig as GRCTestConfig
from grc.models import db, SecurityCode, Application, ApplicationStatus
from grc.utils.security_code import security_code_generator
from tests.grc.helpers.data.application_data import ApplicationDataHelpers
from unittest.mock import patch


@pytest.fixture()
def admin_app():
    yield admin.create_app(AdminTestConfig)


@pytest.fixture()
def app():
    yield grc.create_app(GRCTestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def public_user_email(app):
    return app.config['TEST_PUBLIC_USER']


@pytest.fixture()
def security_code_(app, public_user_email) -> SecurityCode:
    with app.app_context():
        code = security_code_generator(public_user_email)
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
            email=public_user_email
        )
        db.session.add(application_record)
        db.session.commit()

        data = ApplicationData()
        data.reference_number = application_record.reference_number
        data.email_address = application_record.email
        ApplicationDataHelpers.save_test_data(data)

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


@pytest.fixture()
def test_submitted_application(app, public_user_email):
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


@pytest.fixture()
def test_downloaded_application(app, public_user_email):
    with app.app_context():
        application_record = Application(
            reference_number='ABCD1234',
            email=public_user_email,
            status=ApplicationStatus.DOWNLOADED
        )
        db.session.add(application_record)
        db.session.commit()

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


@pytest.fixture()
def test_completed_application(app, public_user_email):
    with app.app_context():
        application_record = Application(
            reference_number='ABCD1234',
            email=public_user_email,
            status=ApplicationStatus.COMPLETED
        )
        db.session.add(application_record)
        db.session.commit()

        yield application_record

        db.session.delete(application_record)
        db.session.commit()


# @pytest.fixture()
# def mock_s3_client(app):
#     with app.app_context():
#         with patch('grc.external_services.aws_s3_client.AwsS3Client') as MockAwsS3Client:
#             mock_s3_client = MockAwsS3Client.return_value
#             mock_s3_client.upload_fileobj.return_value = True
#             yield MockAwsS3Client.return_value
