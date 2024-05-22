from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch


class TestIsFirstVisit:

    def test_is_first_visit_get(self, app, client, public_user_email):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            response = client.get('/is-first-visit')
            assert response.status_code == 200
            assert 'Have you already started an application?' in response.text

    @patch('grc.start_application.DataStore')
    def test_is_first_visit_post_first_visit(self, mock_data_store, app, client, public_user_email, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            mock_data_store.create_new_application.return_value = test_application
            mock_data_store.increment_application_sessions.return_value = None
            response = client.post('/is-first-visit', data={'isFirstVisit': 'FIRST_VISIT'})
            assert response.status_code == 302
            assert response.location == '/reference-number'
            with client.session_transaction() as session:
                assert session['reference_number'] == 'ABCD1234'
                assert session.get('validatedEmail') is None

    @patch('grc.start_application.DataStore')
    def test_is_first_visit_post_lost_reference_number(self, mock_data_store, app, client, public_user_email,
                                                       test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            mock_data_store.create_new_application.return_value = test_application
            mock_data_store.increment_application_sessions.return_value = None
            response = client.post('/is-first-visit', data={'isFirstVisit': 'LOST_REFERENCE'})
            assert response.status_code == 302
            assert response.location == '/reference-number'
            with client.session_transaction() as session:
                assert session['reference_number'] == 'ABCD1234'
                assert session.get('validatedEmail') is None

    @patch('grc.start_application.DataStore')
    def test_is_first_visit_post_first_visit_error_creating_app(self, mock_data_store, app, client, public_user_email,
                                                                test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            mock_data_store.create_new_application.side_effect = SQLAlchemyError
            response = client.post('/is-first-visit', data={'isFirstVisit': 'FIRST_VISIT'})
            assert response.status_code == 200
            assert 'There is a problem creating a new application' in response.text
            assert 'Have you already started an application?' in response.text

    def test_is_first_visit_post_has_reference_number_invalid_ref_number(self, app, client, public_user_email,
                                                                         test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            form_data = {'isFirstVisit': 'HAS_REFERENCE', 'reference': 'INVALID_REF'}
            response = client.post('/is-first-visit', data=form_data)
            assert response.status_code == 200
            assert 'Enter a valid reference number' in response.text

    def test_is_first_visit_post_has_reference_number_no_email_address(self, app, client, public_user_email,
                                                                       test_application_no_email):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            form_data = {'isFirstVisit': 'HAS_REFERENCE', 'reference': f'{test_application_no_email.reference_number}'}
            response = client.post('/is-first-visit', data=form_data)
            print(response.text)
            assert response.status_code == 200
            assert 'Enter a valid reference number' in response.text

    def test_is_first_visit_post_has_reference_number_anonymised_app(self, app, client, public_user_email,
                                                                     test_application_deleted):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            form_data = {'isFirstVisit': 'HAS_REFERENCE', 'reference': f'{test_application_deleted.reference_number}'}
            response = client.post('/is-first-visit', data=form_data)
            assert response.status_code == 200
            assert 'This application cannot be accessed' in response.text

    def test_is_first_visit_post_has_reference_number_already_submitted(self, app, client, public_user_email,
                                                                        test_application_submitted):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            form_data = {'isFirstVisit': 'HAS_REFERENCE',
                         'reference': f'{test_application_submitted.reference_number}'}
            response = client.post('/is-first-visit', data=form_data)
            assert response.status_code == 200
            assert 'This application has already been submitted' in response.text

    def test_is_first_visit_post_has_reference_access_different_users_application(self, app, client, public_user_email,
                                                                                  test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = 'different.email@test.com'
            form_data = {'isFirstVisit': 'HAS_REFERENCE', 'reference': f'{test_application.reference_number}'}
            response = client.post('/is-first-visit', data=form_data)
            assert response.status_code == 200
            assert 'Enter a valid reference number' in response.text

    @patch('grc.start_application.DataStore.increment_application_sessions')
    def test_is_first_visit_post_has_reference_valid(self, mock_inc_app_session, app, client, public_user_email,
                                                     test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['validatedEmail'] = public_user_email
            mock_inc_app_session.return_value = None
            form_data = {'isFirstVisit': 'HAS_REFERENCE', 'reference': f'{test_application.reference_number}'}
            response = client.post('/is-first-visit', data=form_data)
            assert response.status_code == 302
            assert response.location == '/task-list'
            with client.session_transaction() as session:
                assert session['reference_number'] == 'ABCD1234'
                assert session.get('validatedEmail') is None
