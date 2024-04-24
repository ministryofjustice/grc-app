import pytest
from admin import create_app
from admin.config import TestConfig
from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc.models import db, AdminUser, SecurityCode
from grc.utils.security_code import security_code_generator
from werkzeug.security import generate_password_hash
from tests.admin.helpers.data import create_test_applications
from grc.models import db, Application, ApplicationStatus
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
        code = security_code_generator(app.config['DEFAULT_ADMIN_USER'])
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
            # Generate a unique reference number
            reference_number = DataStore.generate_unallocated_reference_number()

            # Create the application record
            application_record = Application(
                reference_number=reference_number,
                email='test.email@example.com',
                status=ApplicationStatus.SUBMITTED,
                completed=datetime.now() + relativedelta(hours=1)
            )

            # Add the application to the database session
            db.session.add(application_record)

            # Commit the changes to the database
            db.session.commit()

            # Add user input
            application_data = ApplicationData()
            application_data.reference_number = reference_number
            application_data.email_address = 'test.email@example.com'

            DataStore.save_application(application_data)

            # Retrieve the newly created application
            new_app = Application.query.filter_by(
                reference_number=reference_number,
                email='test.email@example.com'
            ).first()

            # Yield the application for use in the test
            yield new_app

            # Delete the application after the test
            db.session.delete(new_app)
            db.session.commit()


@pytest.fixture()
def downloaded_application(app):
    with app.app_context():
        with app.test_request_context():
            new_submitted_application = []

            app = DataStore.create_new_application('test.email@example.com')
            db.session.commit()
            new_app = Application.query.filter_by(
                reference_number=app.reference_number,
                email=app.email_address
            ).first()
            new_app.status = ApplicationStatus.DOWNLOADED
            new_app.completed = datetime.now()

            db.session.commit()

            new_submitted_application.append(new_app)
            new_submitted_application = new_submitted_application[0]

            yield new_submitted_application

            db.session.delete(new_submitted_application)
            db.session.commit()


@pytest.fixture()
def completed_application(app):
    with app.app_context():
        with app.test_request_context():
            new_submitted_application = []

            app = DataStore.create_new_application('test.email@example.com')
            db.session.commit()
            new_app = Application.query.filter_by(
                reference_number=app.reference_number,
                email=app.email_address
            ).first()
            new_app.status = ApplicationStatus.COMPLETED
            new_app.completed = datetime.now()

            db.session.commit()

            new_submitted_application.append(new_app)
            new_submitted_application = new_submitted_application[0]

            yield new_submitted_application

            db.session.delete(new_submitted_application)
            db.session.commit()
