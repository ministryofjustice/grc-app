from unittest.mock import patch

from werkzeug.security import check_password_hash

from grc.models import AdminUser

class TestForgotPassword:

    def test_forgot_password_get(self, app, client):
        with app.app_context():
            response = client.get('/forgot_password')

            assert response.status_code == 200
            assert 'Reset your password' in response.text

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_forgot_password')
    def test_forgot_password_existing_user_redirects_and_sends_email(self, mock_send_email, app, client, admin):
        with app.app_context():
            response = client.post('/forgot_password', data={
                'email_address': 'test.email@example.com'
            })

            mock_send_email.assert_called_once_with(email_address='test.email@example.com')
            assert response.status_code == 302
            assert response.location == '/reset-password-with-security-code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_forgot_password')
    def test_forgot_password_unknown_user_redirects_without_sending_email(self, mock_send_email, app, client):
        with app.app_context():
            response = client.post('/forgot_password', data={
                'email_address': 'unknown.email@example.com'
            })

            mock_send_email.assert_not_called()
            assert response.status_code == 302
            assert response.location == '/reset-password-with-security-code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_forgot_password')
    def test_forgot_password_existing_user_redirects_when_email_send_fails(self, mock_send_email, app, client, admin):
        with app.app_context():
            mock_send_email.side_effect = Exception('Notify unavailable')

            response = client.post('/forgot_password', data={
                'email_address': 'test.email@example.com'
            })

            mock_send_email.assert_called_once_with(email_address='test.email@example.com')
            assert response.status_code == 302
            assert response.location == '/reset-password-with-security-code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_forgot_password')
    def test_forgot_password_invalid_email_does_not_redirect_or_send_email(self, mock_send_email, app, client):
        with app.app_context():
            response = client.post('/forgot_password', data={
                'email_address': 'not-an-email-address'
            })

            mock_send_email.assert_not_called()
            assert response.status_code == 200
            assert 'Enter a valid email address' in response.text

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_forgot_password')
    def test_password_reset_resend_existing_user_sends_email(self, mock_send_email, app, client, admin):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.get('/reset-password-with-security-code', query_string={'resend': 'true'})

            mock_send_email.assert_called_once_with(email_address='test.email@example.com')
            assert response.status_code == 200
            assert 'If an account exists' in response.text

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_forgot_password')
    def test_password_reset_resend_unknown_user_does_not_send_email(self, mock_send_email, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'unknown.email@example.com'

            response = client.get('/reset-password-with-security-code', query_string={'resend': 'true'})

            mock_send_email.assert_not_called()
            assert response.status_code == 200
            assert 'If an account exists' in response.text

    def test_password_reset_security_code_redirects_to_forgot_password_without_session(self, app, client):
        with app.app_context():
            response = client.get('/reset-password-with-security-code')

            assert response.status_code == 302
            assert response.location == '/forgot_password'

    def test_password_reset_security_code_get_with_session(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.get('/reset-password-with-security-code')

            assert response.status_code == 200
            assert 'If an account exists, a security code has been sent to the email address you entered' in response.text

    def test_password_reset_security_code_post_valid_code_redirects_to_password_reset(self, app, client, admin):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.post('/reset-password-with-security-code', data={
                'security_code': '11111'
            })

            assert response.status_code == 302
            assert response.location == '/password_reset'

    def test_password_reset_security_code_post_valid_code_unknown_user_shows_error(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'unknown.email@example.com'

            response = client.post('/reset-password-with-security-code', data={
                'security_code': '11111'
            })

            assert response.status_code == 200
            assert 'We could not find your user details. Please try resetting your password again' in response.text

    def test_password_reset_redirects_to_forgot_password_without_session(self, app, client):
        with app.app_context():
            response = client.get('/password_reset')

            assert response.status_code == 302
            assert response.location == '/forgot_password'

    def test_password_reset_get_with_session(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.get('/password_reset')

            assert response.status_code == 200
            assert 'Reset your password' in response.text

    def test_password_reset_post_valid_password_updates_password(self, app, client, admin):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.post('/password_reset', data={
                'password': 'New-password-123',
                'confirmPassword': 'New-password-123'
            })

            user = AdminUser.query.filter_by(email='test.email@example.com').first()
            assert response.status_code == 200
            assert 'Your password has been reset' in response.text
            assert user.passwordResetRequired is False
            assert check_password_hash(user.password, 'New-password-123')

    def test_password_reset_post_passwords_do_not_match(self, app, client, admin):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.post('/password_reset', data={
                'password': 'New-password-123',
                'confirmPassword': 'Different-password-123'
            })

            assert response.status_code == 200
            assert 'Passwords must match' in response.text
