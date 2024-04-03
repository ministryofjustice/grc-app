from tests.grc.integration.conftest import save_test_data, load_test_data


class TestOverseasCheck:
    def test_overseas_check_get_reference_number_in_session(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/overseas-check')
            assert response.status_code == 200
            assert ('Have you ever been issued a Gender Recognition Certificate (or its equivalent)'
                    ' in another country?') in response.text

    def test_overseas_check_get_reference_number_not_in_session(self, app, client):
        with app.app_context():
            response = client.get('/overseas-check')
            assert response.status_code == 302
            assert response.location == '/'

    def test_overseas_check_post_not_issued_in_another_country_declaration_next_page(self, app, client,
                                                                                     test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number

            with app.test_request_context():
                pre_request_data = test_application.application_data()
                pre_request_data.confirmation_data.gender_recognition_from_approved_country = True
                save_test_data(pre_request_data)
                response = client.post('/overseas-check', data={'overseasCheck': False})
                after_request_data = load_test_data(test_application.reference_number)
                assert response.status_code == 302
                assert response.location == '/declaration'
                assert after_request_data.confirmation_data.gender_recognition_from_approved_country is None
                assert after_request_data.confirmation_data.gender_recognition_outside_uk is False

    def test_overseas_check_post_issued_in_another_country_overseas_approved_check_next_page(self, app, client,
                                                                                             test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number

            pre_request_data = test_application.application_data()
            pre_request_data.confirmation_data.gender_recognition_from_approved_country = True
            save_test_data(pre_request_data)
            response = client.post('/overseas-check', data={'overseasCheck': True})
            after_request_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/overseas-approved-check'
            assert after_request_data.confirmation_data.gender_recognition_from_approved_country is True
            assert after_request_data.confirmation_data.gender_recognition_outside_uk is True

    def test_overseas_check_get_overseas_check_data_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number

            pre_request_data = test_application.application_data()
            pre_request_data.confirmation_data.gender_recognition_outside_uk = True
            save_test_data(pre_request_data)
            response = client.get('/overseas-check')
            after_request_data = load_test_data(test_application.reference_number)
            assert response.status_code == 200
            assert ('Have you ever been issued a Gender Recognition Certificate (or its equivalent)'
                    ' in another country?') in response.text
            assert after_request_data.confirmation_data.gender_recognition_outside_uk is True
