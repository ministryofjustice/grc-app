import jsonpickle
import pytest
from admin import create_app
from admin.config import TestConfig
from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc.models import db, AdminUser, SecurityCode, Application, ApplicationStatus
from grc.utils.security_code import generate_security_code_and_expiry
from werkzeug.security import generate_password_hash
from grc.business_logic.data_store import DataStore, ApplicationData


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


@pytest.fixture()
def submitted_application(app):
    with app.app_context():
        with app.test_request_context():
            reference_number = 'ABCD1234'

            # Create the application record
            application_record = Application(
                reference_number=reference_number,
                email='test.email@example.com',
                status=ApplicationStatus.SUBMITTED,
                updated=datetime(2024, 1, 1, 9)
            )

            # Add the application to the database session
            db.session.add(application_record)

            # Add and encode user input
            application_data = ApplicationData()
            application_data.reference_number = reference_number
            application_data.email_address = 'test.email@example.com'
            application_data.updated = application_record.updated

            user_input: str = jsonpickle.encode(application_data)
            application_record.user_input = user_input

            # Commit the changes to the database
            db.session.commit()

            # Yield the application for use in the test
            yield application_record

            # Delete the application after the test
            db.session.delete(application_record)
            db.session.commit()


@pytest.fixture()
def downloaded_application(app):
    with app.app_context():
        with app.test_request_context():
            # Generate a unique reference number
            reference_number = 'EFGH5678'

            # Create the application record
            application_record = Application(
                reference_number=reference_number,
                email='test.email@example.com',
                status=ApplicationStatus.DOWNLOADED,
                downloaded=datetime(2024, 1, 1, 9)
            )

            # Add the application to the database session
            db.session.add(application_record)

            # Add and save user input
            application_data = ApplicationData()
            application_data.reference_number = reference_number
            application_data.email_address = 'test.email@example.com'
            DataStore.save_application(application_data)

            # Yield the application for use in the test
            yield application_record

            # Delete the application after the test
            db.session.delete(application_record)
            db.session.commit()


@pytest.fixture()
def completed_application(app):
    with app.app_context():
        with app.test_request_context():
            # Generate a unique reference number
            reference_number = 'IJKL9012'

            # Create the application record
            application_record = Application(
                reference_number=reference_number,
                email='test.email@example.com',
                status=ApplicationStatus.COMPLETED,
                completed=datetime(2024, 1, 1, 9)
            )

            # Add the application to the database session
            db.session.add(application_record)

            # Commit the changes to the database
            db.session.commit()

            # Add and save user input
            application_data = ApplicationData()
            application_data.reference_number = reference_number
            application_data.email_address = 'test.email@example.com'
            DataStore.save_application(application_data)

            # Yield the application for use in the test
            yield application_record

            # Delete the application after the test
            db.session.delete(application_record)
            db.session.commit()


@pytest.fixture()
def invalid_submitted_application(app):
    with app.app_context():
        with app.test_request_context():
            # Generate a unique reference number
            reference_number = 'MNOP3456'

            # Create the application record
            application_record = Application(
                reference_number=reference_number,
                email='test.email2@example.com',
                status=ApplicationStatus.SUBMITTED,
                completed=datetime(2024, 1, 1, 9)
            )

            # Add the application to the database session
            db.session.add(application_record)

            # Commit the changes to the database
            db.session.commit()

            # Yield the application for use in the test
            yield application_record

            # Delete the application after the test
            db.session.delete(application_record)
            db.session.commit()
