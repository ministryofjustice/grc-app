import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from admin import create_app
from admin.config import TestConfig
from grc.models import Application, db, ApplicationStatus, SecurityCode
from grc.utils.security_code import generate_security_code_and_expiry
from tests.jobs.helpers.application_data import ApplicationDataHelpers


@pytest.fixture()
def app():
    yield create_app(TestConfig)


@pytest.fixture()
def public_user_email():
    yield 'test.public.email@example.com'


@pytest.fixture()
def test_started_and_expired_applications(app, public_user_email):
    with app.test_request_context():
        test_inactive_apps = []
        for _ in range(3):
            app = ApplicationDataHelpers.create_new_application(public_user_email)
            new_app = Application.query.filter_by(
                reference_number=app.reference_number,
                email=app.email_address
            ).first()
            new_app.status = ApplicationStatus.STARTED
            new_app.updated = datetime.now() - relativedelta(days=200)
            db.session.commit()
            print(f'Test Inactive App Ref - {new_app.reference_number}', flush=True)
            test_inactive_apps.append(new_app)

        yield test_inactive_apps

        for app in test_inactive_apps:
            db.session.delete(app)
        db.session.commit()


@pytest.fixture()
def test_completed_applications(app, public_user_email):
    with app.test_request_context():
        test_completed_apps = []
        for _ in range(3):
            app = ApplicationDataHelpers.create_new_application(public_user_email)
            db.session.commit()
            new_app = Application.query.filter_by(
                reference_number=app.reference_number,
                email=app.email_address
            ).first()
            new_app.status = ApplicationStatus.COMPLETED
            new_app.completed = datetime.now() - relativedelta(days=7)
            db.session.commit()
            print(f'Test Completed App Ref - {new_app.reference_number}', flush=True)
            test_completed_apps.append(new_app)

        yield test_completed_apps

        for app in test_completed_apps:
            db.session.delete(app)
        db.session.commit()


@pytest.fixture()
def test_started_applications(request, app, public_user_email):
    with app.test_request_context():
        last_updated_days_ago = request.param
        test_inactive_apps = []
        for _ in range(3):
            app = ApplicationDataHelpers.create_new_application(public_user_email)
            new_app = Application.query.filter_by(
                reference_number=app.reference_number,
                email=app.email_address
            ).first()
            new_app.status = ApplicationStatus.STARTED
            new_app.updated = datetime.now() - relativedelta(days=last_updated_days_ago)
            db.session.commit()
            print(f'Test Inactive App Ref - {new_app.reference_number}', flush=True)
            test_inactive_apps.append(new_app)

        yield test_inactive_apps

        for app in test_inactive_apps:
            db.session.delete(app)
        db.session.commit()


@pytest.fixture
def test_emails(request):
    number_of_emails = request.param
    return [f'user{i}@test_email.com' for i in range(number_of_emails)]


@pytest.fixture
def expired_security_codes(app, test_emails):
    with app.app_context():
        codes = [generate_security_code_and_expiry(email)[0] for email in test_emails]
        print(f'codes = {codes}', flush=True)

        security_codes = SecurityCode.query.filter(SecurityCode.code.in_(codes)).all()
        print(f'security_codes = {security_codes}', flush=True)

        if security_codes:
            for security_code in security_codes:
                print(f'code = {security_code.code} for user = {security_code.email}', flush=True)
                security_code.created = datetime.now() - relativedelta(days=7)
            db.session.commit()

        yield security_codes
