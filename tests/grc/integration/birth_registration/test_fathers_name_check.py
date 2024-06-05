from tests.grc.integration.conftest import save_test_data, load_test_data


class TestFathersNameCheck:

    def test_fathers_name_check_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/fathers-name-check')
            assert response.status_code == 200
            assert "Is your father's name listed on the certificate?" in response.text

    def test_fathers_name_check_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/fathers-name-check')
            assert response.status_code == 302
            assert response.location == '/'

    def test_fathers_name_check_post_fathers_name_on_cert(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'fathers_name_on_certificate': 'True'}
            response = client.post('/birth-registration/fathers-name-check', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/fathers-name'
            assert test_app_data.birth_registration_data.fathers_name_on_birth_certificate is True

    def test_fathers_name_check_post_fathers_name_not_on_cert(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.fathers_first_name = 'Fathers first name'
            test_app_data.birth_registration_data.fathers_last_name = 'Fathers last name'
            save_test_data(test_app_data)
            data = {'fathers_name_on_certificate': 'False'}
            response = client.post('/birth-registration/fathers-name-check', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/adopted'
            assert test_app_data.birth_registration_data.fathers_name_on_birth_certificate is False
            assert test_app_data.birth_registration_data.fathers_last_name is None
            assert test_app_data.birth_registration_data.fathers_first_name is None

    def test_fathers_name_check_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/fathers-name-check', data={})
            assert response.status_code == 200
            assert "Is your father's name listed on the certificate?" in response.text
            assert "Select if your father&#39;s name is listed on the certificate" in response.text
