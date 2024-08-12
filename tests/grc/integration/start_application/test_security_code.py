from unittest.mock import patch


class TestSecurityCode:

    def test_security_code_get(self, app, client, public_user_email):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = public_user_email
            response = client.get('/security-code')
            assert response.status_code == 200
            assert 'Enter security code' in response.text

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_security_code')
    def test_security_code_resend_code(self, mock_send_security_code, app, client, public_user_email):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = public_user_email
            response = client.get('/security-code', query_string={'resend': 'true'})
            mock_send_security_code.assert_called_once_with('test.public.email@example.com')
            assert response.status_code == 200
            assert 'Enter security code' in response.text
            assert 'We’ve resent you a security code. This can take a few minutes to arrive' in response.text

    def test_security_code_post_valid(self, app, client, public_user_email, security_code):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = public_user_email
            response = client.post('/security-code', data={'security_code': f'{security_code.code}'})
            assert response.status_code == 302
            assert response.location == '/is-first-visit'
            with client.session_transaction() as session:
                assert session['validatedEmail'] == public_user_email
                assert session.get('email') is None

    def test_security_code_post_invalid_code(self, app, client, public_user_email, security_code):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = public_user_email
            response = client.post('/security-code', data={'security_code': 'INVALID CODE'})
            assert response.status_code == 200
            assert 'Enter the security code that we emailed you' in response.text
