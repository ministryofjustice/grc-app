import pytest
from grc.models import Application, db
from unittest.mock import patch, MagicMock, call


@pytest.mark.parametrize('test_emails', [3], indirect=True)
def test_notify_applicants_inactive_applications_returns_200(app, test_started_and_expired_applications, test_emails,
                                                             test_completed_applications, expired_security_codes):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        assert result.exit_code == 0


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


@pytest.mark.parametrize('test_started_applications', [(183-7)], indirect=True)
@patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_unfinished_application')
def test_notify_applicants_inactive_send_reminder_do_not_send_email_if_app_aleady_submitted(
        mock_send_email_unfinished_application: MagicMock, app, public_user_email, test_started_applications,
        test_submitted_application
):
    with (app.app_context()):
        # Change one of the started apps to have same email as submitted app
        app_record: Application = Application.query.filter_by(
            reference_number=test_started_applications[0].reference_number
        ).first()
        app_record.email = test_submitted_application.email
        db.session.commit()

        runner = app.test_cli_runner()
        runner.invoke(args=['jobs.notify_applicants_inactive_apps', 'run'])
        expected_calls = [
            call(email_address='test.public.email@example.com', expiry_days='1 week'),
            call(email_address='test.public.email@example.com', expiry_days='1 week')
        ]
        assert len(mock_send_email_unfinished_application.mock_calls) == 2
        mock_send_email_unfinished_application.assert_has_calls(expected_calls)
        assert call(email_address='different_email_address@example.com', expiry_days='1 week') \
            not in mock_send_email_unfinished_application.mock_calls
