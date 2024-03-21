from unittest.mock import patch


class TestAdminSignInWithSecurityCode:

    def test_sign_in_with_security_code_get(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.get('/sign-in-with-security_code')
            assert response.status_code == 200

    @patch('admin.admin.send_security_code_admin')
    def test_sign_in_with_security_code_resend_code(self, mock_resend_security_code, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.get('/sign-in-with-security_code', query_string={'resend': 'true'})
            mock_resend_security_code.assert_called_once()
            assert response.status_code == 200
            assert 'Success' in response.text
            assert 'We’ve resent you a security code. This can take a few minutes to arrive' in response.text

    def test_sign_in_with_security_code_post_valid_code(self, app, client, admin, security_code):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'

            response = client.post('/sign-in-with-security_code', data={'security_code': f'{security_code.code}'})

            assert response.status_code == 302
            assert response.location == '/applications'

            with client.session_transaction() as session:
                assert session['signedIn'] == 'test.email@example.com'
                assert session['userType'] == 'ADMIN'

    def test_sign_in_with_security_code_post_invalid_code(self, app, client, admin, security_code):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.post('/sign-in-with-security_code', data={'security_code': 'INVALID CODE'})

            assert response.status_code == 200
            assert 'Enter the security code that we emailed you' in response.text

    def test_sign_in_with_security_code_post_expired_code(self, app, client, admin, expired_security_code):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'

            response = client.post('/sign-in-with-security_code',
                                   data={'security_code': f'{expired_security_code.code}'})

            assert response.status_code == 200
            assert 'Enter the security code that we emailed you' in response.text

    def test_sign_in_with_security_code_post_valid_code_admin_not_found(self, app, client, security_code):
        with app.app_context():
            with client.session_transaction() as session:
                session['email'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'

            response = client.post('/sign-in-with-security_code', data={'security_code': f'{security_code.code}'})

            assert response.status_code == 200
            assert 'We could not find your user details. Please try logging in again' in response.text
