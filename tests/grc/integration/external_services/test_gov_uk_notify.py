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
            response = GovUkNotify().send_email_unfinished_application(public_user_email, '30', 'http://return-link')
            print(response)
            assert 'Your Gender Recognition Certificate application expires in 30' in response['content']['subject']
            # assert 'until 12:45 on 29 Mar 2024' in response['content']['body']
