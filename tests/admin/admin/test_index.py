from unittest.mock import patch


class TestAdminIndex:

    @patch('admin.admin.add_default_admin_user_to_database_if_there_are_no_users')
    def test_index(self, mock_add_admin_user, app, client):
        with app.app_context():
            response = client.get('/')
            assert mock_add_admin_user.called
            assert response.status_code == 200

    @patch('grc.models.db.session')
    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_new_user')
    def test_index_add_default_admin_not_required(self, mock_send_email, mock_db_session, app, client):
        with app.app_context():
            mock_db_session.query.return_value.count.return_value = 1
            response = client.get('/')
            mock_send_email.assert_not_called()
            assert response.status_code == 200

    @patch('admin.admin.generate_temporary_password')
    @patch('grc.models.db.session')
    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_new_user')
    def test_index_add_default_admin_required(self, mock_send_email, mock_db_session, mock_temp_password, app, client):
        with app.app_context():
            mock_db_session.query.return_value.count.return_value = 0
            mock_temp_password.return_value = '123ABC'
            response = client.get('/')
            assert mock_db_session.add.called
            assert mock_db_session.commit.called
            assert mock_send_email.called
            assert response.status_code == 200

    def test_index_user_signed_in(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/')
            assert response.status_code == 302
            assert response.location == '/applications'

    def test_index_post_email_valid_password_password_reset_required(self, app, client, default_admin):
        with app.app_context():
            form_data = {'email_address': 'test.email@example.com', 'password': '123ABC'}
            response = client.post('/', data=form_data)

            with client.session_transaction() as session:
                assert session['email'] == 'test.email@example.com'
                assert session['userType'] == 'ADMIN'

            assert response.status_code == 302
            assert response.location == '/password_reset'

    def test_index_post_email_invalid_password(self, app, client, admin):
        with app.app_context():
            form_data = {'email_address': 'test.email@example.com', 'password': 'INVALID_PASSWORD'}
            response = client.post('/', data=form_data)
            assert 'Your password was incorrect. Please try re-entering your password' in response.text
            assert response.status_code == 200

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_login_security_code')
    def test_index_post_email_valid_password_security_code_required(self, mock_send_security_code_email, app, client,
                                                                    admin):
        with app.app_context():
            form_data = {'email_address': 'test.email@example.com', 'password': 'password'}
            response = client.post('/', data=form_data)
            mock_send_security_code_email.assert_called_once_with(email_address='test.email@example.com')
            assert response.status_code == 302
            assert response.location == '/sign-in-with-security_code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_login_security_code')
    def test_index_post_email_valid_password_security_code_required_first_time_login(self,
                                                                                     mock_send_security_code_email,
                                                                                     app, client, new_admin):
        with app.app_context():
            form_data = {'email_address': 'test.email@example.com', 'password': 'password'}
            response = client.post('/', data=form_data)
            mock_send_security_code_email.assert_called_once_with(email_address='test.email@example.com')
            assert response.status_code == 302
            assert response.location == '/sign-in-with-security_code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_login_security_code')
    def test_index_post_email_valid_password_security_code_expired_and_required(self, mock_send_security_code_email,
                                                                                app, client, admin,
                                                                                expired_security_code):
        with app.app_context():
            form_data = {'email_address': 'test.email@example.com', 'password': 'password'}
            response = client.post('/', data=form_data)
            mock_send_security_code_email.assert_called_with(email_address='test.email@example.com')
            assert response.status_code == 302
            assert response.location == '/sign-in-with-security_code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_login_security_code')
    @patch('admin.admin.has_last_security_code_been_used')
    def test_index_post_email_valid_password_security_code_valid_not_expired_and_previous_code_not_used_code_required(
            self, mock_last_security_code_been_used, mock_send_security_code_email, app,
            client, admin, security_code
    ):
        with app.app_context():
            mock_last_security_code_been_used.return_value = False
            form_data = {'email_address': 'test.email@example.com', 'password': 'password'}
            response = client.post('/', data=form_data)
            mock_send_security_code_email.assert_called_with(email_address='test.email@example.com')
            assert response.status_code == 302
            assert response.location == '/sign-in-with-security_code'

    @patch('grc.external_services.gov_uk_notify.GovUkNotify.send_email_admin_login_security_code')
    @patch('admin.admin.has_last_security_code_been_used')
    def test_index_post_email_valid_password_security_code_valid_not_expired_and_previous_code_used(
            self, mock_last_security_code_been_used, mock_send_security_code_email, app,
            client, admin, security_code
    ):
        with app.app_context():
            mock_last_security_code_been_used.return_value = True
            form_data = {'email_address': 'test.email@example.com', 'password': 'password'}
            response = client.post('/', data=form_data)
            mock_send_security_code_email.assert_not_called()
            assert response.status_code == 302
            assert response.location == '/applications'
            assert admin.dateLastLogin is not None

            with client.session_transaction() as session:
                assert session['signedIn'] == 'test.email@example.com'
