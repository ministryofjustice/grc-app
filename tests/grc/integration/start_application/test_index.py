from unittest.mock import patch


class TestIndex:
    def test_index(self, app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200
            assert 'What is your email address?' in response.text

    def test_index_post_no_email(self, app, client):
        with app.app_context():
            form_data = {'email': None}
            response = client.post('/', data=form_data)
            assert response.status_code == 200
            assert 'What is your email address?' in response.text
            assert 'Enter your email address' in response.text

    def test_index_post_invalid_email(self, app, client):
        with app.app_context():
            form_data = {'email': 'INVALID_EMAIL'}
            response = client.post('/', data=form_data)
            assert response.status_code == 200
            assert 'What is your email address?' in response.text
            assert 'Enter a valid email address' in response.text

    @patch('grc.start_application.send_security_code')
    def test_index_post_valid_email(self, mock_send_security_code, app, client):
        with app.app_context():
            form_data = {'email': app.config['TEST_PUBLIC_USER']}
            response = client.post('/', data=form_data)
            assert response.status_code == 302
            assert response.location == '/security-code'
            mock_send_security_code.assert_called_once_with('test.public.email@example.com')

    @patch('grc.start_application.send_security_code')
    def test_index_post_valid_email_clear_session(self, mock_send_security_code, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['session_key'] = 'test value'
                session['email'] = 'previous email logged in session'
            form_data = {'email': app.config['TEST_PUBLIC_USER']}
            response = client.post('/', data=form_data)
            assert response.status_code == 302
            assert response.location == '/security-code'
            mock_send_security_code.assert_called_once_with('test.public.email@example.com')
            with client.session_transaction() as session:
                assert session['email'] == 'test.public.email@example.com'
