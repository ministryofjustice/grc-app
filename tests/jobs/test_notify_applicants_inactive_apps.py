import pytest
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
