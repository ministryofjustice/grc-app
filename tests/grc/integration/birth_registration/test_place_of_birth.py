from tests.grc.integration.conftest import save_test_data, load_test_data


class TestPlaceOfBirth:

    def test_place_of_birth_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/place-of-birth')
            assert response.status_code == 200
            assert 'What is the town or city of birth on your birth or adoption certificate?' in response.text

    def test_place_of_birth_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/place-of-birth')
            assert response.status_code == 302
            assert response.location == '/'

    def test_place_of_birth_get_place_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.town_city_of_birth = 'London'
            save_test_data(test_app_data)
            response = client.get('/birth-registration/place-of-birth')
            assert response.status_code == 200
            assert 'What is the town or city of birth on your birth or adoption certificate?' in response.text
            assert 'London' in response.text

    def test_place_of_birth_post(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'place_of_birth': 'Manchester'}
            response = client.post('/birth-registration/place-of-birth', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/mothers-name'
            assert test_app_data.birth_registration_data.town_city_of_birth == 'Manchester'

    def test_place_of_birth_no_place(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/place-of-birth', data={})
            assert response.status_code == 200
            assert 'What is the town or city of birth on your birth or adoption certificate?' in response.text
            assert 'Enter your town or city of birth' in response.text
