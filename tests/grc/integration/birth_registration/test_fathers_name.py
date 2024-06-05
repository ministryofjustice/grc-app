from tests.grc.integration.conftest import save_test_data, load_test_data


class TestFathersName:

    def test_fathers_name_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/fathers-name')
            assert response.status_code == 200
            assert "What is your father's name as listed on your birth or adoption certificate?" in response.text

    def test_fathers_name_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/fathers-name')
            assert response.status_code == 302
            assert response.location == '/'

    def test_fathers_name_post_fathers_name_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.fathers_first_name = 'Fathers first name'
            test_app_data.birth_registration_data.fathers_last_name = 'Fathers last name'
            save_test_data(test_app_data)
            response = client.get('/birth-registration/fathers-name')
            assert response.status_code == 200
            assert 'Fathers first name' in response.text
            assert 'Fathers last name' in response.text

    def test_fathers_name_post_fathers_name(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'first_name': 'Fathers first name', 'last_name': 'Fathers last name'}
            response = client.post('/birth-registration/fathers-name', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/adopted'
            assert test_app_data.birth_registration_data.fathers_first_name == 'Fathers first name'
            assert test_app_data.birth_registration_data.fathers_last_name == 'Fathers last name'

    def test_fathers_name_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/fathers-name', data={})
            assert response.status_code == 200
            assert "What is your father's name as listed on your birth or adoption certificate?" in response.text
            assert "Enter your father's first name" in response.text
            assert "Enter your father's last name" in response.text
