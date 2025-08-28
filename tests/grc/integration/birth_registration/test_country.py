from tests.grc.integration.conftest import save_test_data, load_test_data


class TestCountry:

    def test_country_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.get('/birth-registration/country')
            assert response.status_code == 200
            assert 'What country was your birth registered in?' in response.text

    def test_country_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/country')
            assert response.status_code == 302
            assert response.location == '/'

    def test_country_get_country_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.country_of_birth = 'Belgium'
            save_test_data(test_app_data)
            response = client.get('/birth-registration/country')
            assert response.status_code == 200
            assert 'What country was your birth registered in?' in response.text
            assert 'Belgium' in response.text

    def test_country_post(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            data = {'country_of_birth': 'Ireland'}
            response = client.post('/birth-registration/country', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/check-your-answers'
            assert test_app_data.birth_registration_data.country_of_birth == 'Ireland'

    def test_country_no_country(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.post('/birth-registration/country', data={})
            assert response.status_code == 200
            assert 'What country was your birth registered in?' in response.text
            assert 'Enter your country of birth' in response.text
