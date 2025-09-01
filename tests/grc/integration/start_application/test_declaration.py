from tests.grc.integration.conftest import save_test_data, load_test_data


class TestDeclaration:

    def test_declaration_get_reference_number_in_session(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.get('/declaration')
            assert response.status_code == 200
            assert 'Notifying the General Register Office' in response.text

    def test_declaration_get_reference_number_not_in_session(self, app, client):
        with app.app_context():
            response = client.get('/declaration')
            assert response.status_code == 302
            assert response.location == '/'

    def test_declaration_get_consent_to_gro_contact_data_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True

            pre_request_data = test_application.application_data()
            pre_request_data.confirmation_data.consent_to_GRO_contact = True
            save_test_data(pre_request_data)
            response = client.get('/declaration')
            after_request_data = load_test_data(test_application.reference_number)
            assert response.status_code == 200
            assert 'Notifying the General Register Office' in response.text
            assert after_request_data.confirmation_data.consent_to_GRO_contact is True

    def test_declaration_post_make_declaration(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True

            response = client.post('/declaration', data={'consent': True})
            after_request_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/task-list'
            assert after_request_data.confirmation_data.consent_to_GRO_contact is True
