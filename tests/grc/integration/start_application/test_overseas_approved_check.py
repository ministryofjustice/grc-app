from tests.grc.integration.conftest import save_test_data, load_test_data


class TestOverseasApprovedCheck:

    def test_overseas_approved_check_get_reference_number_in_session(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/overseas-approved-check')
            assert response.status_code == 200
            assert 'Gender recognition in approved countries and territories' in response.text

    def test_overseas_approved_check_get_reference_number_not_in_session(self, app, client):
        with app.app_context():
            response = client.get('/overseas-approved-check')
            assert response.status_code == 302
            assert response.location == '/'

    def test_overseas_approved_check_get_overseas_approve_check_data_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number

            pre_request_data = test_application.application_data()
            pre_request_data.confirmation_data.gender_recognition_from_approved_country = True
            save_test_data(pre_request_data)
            response = client.get('/overseas-approved-check')
            after_request_data = load_test_data(test_application.reference_number)
            assert response.status_code == 200
            assert 'Gender recognition in approved countries and territories' in response.text
            assert after_request_data.confirmation_data.gender_recognition_from_approved_country is True

    def test_overseas_approved_check_post_gender_recognised_in_approved_country(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number

            response = client.post('/overseas-approved-check', data={'overseasApprovedCheck': True})
            after_request_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/declaration'
            assert after_request_data.confirmation_data.gender_recognition_from_approved_country is True
