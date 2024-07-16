import pytest
from grc.models import SecurityCode, db, Application, ApplicationStatus, ApplicationData
from unittest.mock import patch, MagicMock, call


@pytest.mark.parametrize('test_emails', [3], indirect=True)
def test_notify_applicants_inactive_applications_returns_200(app, test_started_and_expired_applications, test_emails,
                                                             test_completed_applications, expired_security_codes):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        assert result.exit_code == 0


@pytest.mark.parametrize('test_emails', [3], indirect=True)
def test_notify_applicants_inactive_applications_deletes_expired_security_codes(app, expired_security_codes,
                                                                                test_emails):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        assert result.exit_code == 0

        deleted_security_codes = db.session.query(SecurityCode).filter(SecurityCode.email.in_(test_emails)).all()
        assert len(deleted_security_codes) == 0


def test_notify_applicants_inactive_apps_abandon_application_after_period_of_inactivity(app, public_user_email,
                                                                                        test_started_and_expired_applications):
    with app.app_context():
        runner = app.test_cli_runner()
        test_app_references = [application.reference_number for application in test_started_and_expired_applications]
        result = runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        assert result.exit_code == 0

        inactivated_applications_after_job = db.session.query(Application).filter(
            Application.reference_number.in_(test_app_references)).all()
        assert len(inactivated_applications_after_job) == 3
        for application in inactivated_applications_after_job:
            assert application.status == ApplicationStatus.ABANDONED
            assert application.email == ''
            assert application.user_input == ''


def test_notify_applicants_inactive_apps_mark_completed_application_as_deleted(app, public_user_email,
                                                                               test_completed_applications):
    with app.app_context():
        runner = app.test_cli_runner()
        test_app_references = [application.reference_number for application in test_completed_applications]
        result = runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        assert result.exit_code == 0

        inactivated_applications_after_job = db.session.query(Application).filter(
            Application.reference_number.in_(test_app_references)).all()
        assert len(inactivated_applications_after_job) == 3
        for application in inactivated_applications_after_job:
            assert application.status == ApplicationStatus.DELETED
            assert application.email == ''
            assert application.user_input == ''


@pytest.mark.parametrize('test_started_applications', [(183-90)], indirect=True)
@patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_unfinished_application')
def test_notify_applicants_inactive_send_reminder_email_3_months(mock_send_email_unfinished_application: MagicMock,
                                                                 app, public_user_email, test_started_applications):
    with app.app_context():
        runner = app.test_cli_runner()
        runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        expected_calls = [
            call(email_address='test.public.email@example.com', expiry_days='3 months'),
            call(email_address='test.public.email@example.com', expiry_days='3 months'),
            call(email_address='test.public.email@example.com', expiry_days='3 months')
        ]
        mock_send_email_unfinished_application.assert_has_calls(expected_calls)


@pytest.mark.parametrize('test_started_applications', [(183-30)], indirect=True)
@patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_unfinished_application')
def test_notify_applicants_inactive_send_reminder_email_1_month(mock_send_email_unfinished_application: MagicMock,
                                                                app, public_user_email, test_started_applications):
    with app.app_context():
        runner = app.test_cli_runner()
        runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        expected_calls = [
            call(email_address='test.public.email@example.com', expiry_days='1 month'),
            call(email_address='test.public.email@example.com', expiry_days='1 month'),
            call(email_address='test.public.email@example.com', expiry_days='1 month')
        ]
        mock_send_email_unfinished_application.assert_has_calls(expected_calls)


@pytest.mark.parametrize('test_started_applications', [(183-7)], indirect=True)
@patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_unfinished_application')
def test_notify_applicants_inactive_send_reminder_email_1_week(mock_send_email_unfinished_application: MagicMock,
                                                               app, public_user_email, test_started_applications):
    with app.app_context():
        runner = app.test_cli_runner()
        runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        expected_calls = [
            call(email_address='test.public.email@example.com', expiry_days='1 week'),
            call(email_address='test.public.email@example.com', expiry_days='1 week'),
            call(email_address='test.public.email@example.com', expiry_days='1 week')
        ]
        mock_send_email_unfinished_application.assert_has_calls(expected_calls)


def test_notify_applicants_inactive_invalid_app_data_still_abandons_applications(app, test_started_and_expired_applications):
    with app.app_context():
        app_record: Application = Application.query.filter_by(
            reference_number=test_started_and_expired_applications[0].reference_number
        ).first()
        app_record.user_input = "{'invalid': 'json_data'}"
        db.session.commit()
        test_app_references = [application.reference_number for application in test_started_and_expired_applications]
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        assert result.exit_code == 0

        inactivated_applications_after_job = db.session.query(Application).filter(
            Application.reference_number.in_(test_app_references)).all()
        for application in inactivated_applications_after_job:
            assert application.status == ApplicationStatus.ABANDONED
            assert application.email == ''
            assert application.user_input == ''
