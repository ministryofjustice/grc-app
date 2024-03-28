from grc.external_services.gov_uk_notify import GovUkNotify
from unittest.mock import patch


class TestGovNotifyEmails:

    @patch('grc.external_services.gov_uk_notify.generate_security_code')
    def test_send_email_security_code(self, mock_security_code, app, public_user_email):
        with app.app_context():
            mock_security_code.return_value = ('12345', '12:45 on 29 Mar 2024')
            response = GovUkNotify().send_email_security_code(public_user_email)
            assert 'Your security code: 12345' in response['content']['subject']
            assert 'until 12:45 on 29 Mar 2024' in response['content']['body']

    def test_send_email_unfinished_application(self, app, public_user_email):
        with app.app_context():
            response = GovUkNotify().send_email_unfinished_application(public_user_email, '30')
            assert 'Your Gender Recognition Certificate application expires in 30' in response['content']['subject']

    def test_send_email_completed_application(self, app, public_user_email):
        with app.app_context():
            response = GovUkNotify().send_email_completed_application(public_user_email, 'list of docs')
            assert 'Your application has been received' in response['content']['subject']
            assert 'list of docs' in response['content']['body']

    def test_send_email_feedback(self, app, public_user_email):
        with app.app_context():
            response = GovUkNotify().send_email_feedback(
                public_user_email,
                'difficult questions to answer',
                'list of questions which were difficult to answer',
                'needed to call admin team',
                'description of what I needed help with',
                'I used doc checker',
                'Good experience using doc checker',
                'No other suggestions'
            )
            assert 'Feedback received' in response['content']['subject']
            assert 'list of questions which were difficult to answer' in response['content']['body']
            assert 'needed to call admin team' in response['content']['body']
            assert 'description of what I needed help with' in response['content']['body']
            assert 'I used doc checker' in response['content']['body']
            assert 'Good experience using doc checker' in response['content']['body']
            assert 'No other suggestions' in response['content']['body']

    @patch('grc.external_services.gov_uk_notify.generate_security_code')
    def test_send_email_admin_login_security_code(self, mock_security_code, app, public_user_email):
        with app.app_context():
            mock_security_code.return_value = ('12345', '12:45 on 29 Mar 2024')
            response = GovUkNotify().send_email_admin_login_security_code(public_user_email)
            assert 'Your login link for GRC admin' in response['content']['subject']
            assert '12345' in response['content']['body']
            assert 'until 12:45 on 29 Mar 2024' in response['content']['body']
