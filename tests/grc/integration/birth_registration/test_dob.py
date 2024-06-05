import datetime
from tests.grc.integration.conftest import save_test_data, load_test_data


class TestDob:

    def test_dob_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/dob')
            assert response.status_code == 200
            assert 'What is the date of birth on your birth or adoption certificate?' in response.text

    def test_dob_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/dob')
            assert response.status_code == 302
            assert response.location == '/'

    def test_dob_get_dob_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = test_application.application_data()
            data.birth_registration_data.date_of_birth = datetime.date(1990, 8, 23)
            save_test_data(data)
            response = client.get('/birth-registration/dob')
            assert response.status_code == 200
            assert '23' in response.text
            assert '8' in response.text
            assert '1990' in response.text

    def test_dob_post_dob_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'day': '3', 'month': '5', 'year': '1973'}
            response = client.post('/birth-registration/dob', data=data)

            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/uk-check'
            assert test_app_data.birth_registration_data.date_of_birth == datetime.date(1973, 5, 3)

    def test_dob_post_no_dob_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/dob', data={})
            assert response.status_code == 200
            assert 'Enter a day' in response.text
            assert 'Enter a month' in response.text
            assert 'Enter a year' in response.text

    def test_dob_post_invalid_dob_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'day': '48', 'month': '13', 'year': '123'}
            response = client.post('/birth-registration/dob', data=data)
            assert response.status_code == 200
            assert 'Enter a day as a number between 1 and 31' in response.text
            assert 'Enter a month as a number between 1 and 12' in response.text
            assert 'Enter a year as a 4-digit number, like 2000' in response.text
