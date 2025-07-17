from tests.grc.integration.conftest import save_test_data, load_test_data


class TestMothersName:

    def test_mothers_name_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/mothers-name')
            assert response.status_code == 200
            assert "What is your first parent's name as listed on your birth or adoption certificate?" in response.text

    def test_mothers_name_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/mothers-name')
            assert response.status_code == 302
            assert response.location == '/'

    def test_mothers_name_get_name_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.mothers_first_name = 'Mothers first name'
            test_app_data.birth_registration_data.mothers_last_name = 'Mothers last name'
            test_app_data.birth_registration_data.mothers_maiden_name = 'Mothers maiden name'
            save_test_data(test_app_data)
            response = client.get('/birth-registration/mothers-name')
            assert response.status_code == 200
            assert "What is your first parent's name as listed on your birth or adoption certificate?" in response.text
            assert 'Mothers first name' in response.text
            assert 'Mothers last name' in response.text
            assert 'Mothers maiden name' in response.text

    def test_mothers_name_post(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {
                'first_name': 'Mothers first name',
                'last_name': 'Mothers last name',
                'maiden_name': 'Mothers maiden name'
            }
            response = client.post('/birth-registration/mothers-name', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/fathers-name-check'
            assert test_app_data.birth_registration_data.mothers_first_name == 'Mothers first name'
            assert test_app_data.birth_registration_data.mothers_last_name == 'Mothers last name'
            assert test_app_data.birth_registration_data.mothers_maiden_name == 'Mothers maiden name'

    def test_mothers_name_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/mothers-name', data={})
            assert response.status_code == 200
            assert "Enter your mother's first name" in response.text
            assert "Enter your mother's last name" in response.text
            assert "Enter your mother's maiden name" in response.text
