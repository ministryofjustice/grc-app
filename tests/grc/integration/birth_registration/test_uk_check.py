from tests.grc.integration.conftest import save_test_data, load_test_data


class TestUKCheck:

    def test_uk_check_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.get('/birth-registration/uk-check')
            assert response.status_code == 200
            assert 'Was your birth registered in the UK?' in response.text

    def test_uk_check_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/uk-check')
            assert response.status_code == 302
            assert response.location == '/'

    def test_uk_check_post_birth_registered_in_uk_redirect_place_of_birth(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            data = {'birth_registered_in_uk': 'True'}
            response = client.post('/birth-registration/uk-check', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/place-of-birth'
            assert test_app_data.birth_registration_data.birth_registered_in_uk is True

    def test_uk_check_post_birth_registered_in_uk_nullify_country_of_birth(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.country_of_birth = 'France'
            save_test_data(test_app_data)
            request_data = {'birth_registered_in_uk': 'True'}
            response = client.post('/birth-registration/uk-check', data=request_data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/place-of-birth'
            assert test_app_data.birth_registration_data.birth_registered_in_uk is True
            assert test_app_data.birth_registration_data.country_of_birth is None

    def test_uk_check_post_birth_registered_outside_uk_redirect_country(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            data = {'birth_registered_in_uk': 'False'}
            response = client.post('/birth-registration/uk-check', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/country'
            assert test_app_data.birth_registration_data.birth_registered_in_uk is False

    def test_uk_check_post_birth_registered_outside_uk_nullify_birth_reg_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.town_city_of_birth = 'London'
            test_app_data.birth_registration_data.mothers_first_name = 'Mothers first name'
            test_app_data.birth_registration_data.mothers_last_name = 'Mothers last name'
            test_app_data.birth_registration_data.mothers_maiden_name = 'Mothers maiden name'
            test_app_data.birth_registration_data.fathers_name_on_birth_certificate = True
            test_app_data.birth_registration_data.fathers_first_name = 'Fathers first name'
            test_app_data.birth_registration_data.fathers_last_name = 'Fathers last name'
            test_app_data.birth_registration_data.adopted = True
            test_app_data.birth_registration_data.adopted_in_the_uk = 'ADOPTED_IN_THE_UK_YES'
            test_app_data.birth_registration_data.forces_registration = True
            save_test_data(test_app_data)
            request_data = {'birth_registered_in_uk': 'False'}
            response = client.post('/birth-registration/uk-check', data=request_data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/country'
            assert test_app_data.birth_registration_data.birth_registered_in_uk is False
            assert test_app_data.birth_registration_data.town_city_of_birth is None
            assert test_app_data.birth_registration_data.mothers_first_name is None
            assert test_app_data.birth_registration_data.mothers_last_name is None
            assert test_app_data.birth_registration_data.mothers_maiden_name is None
            assert test_app_data.birth_registration_data.fathers_name_on_birth_certificate is None
            assert test_app_data.birth_registration_data.fathers_first_name is None
            assert test_app_data.birth_registration_data.fathers_last_name is None
            assert test_app_data.birth_registration_data.adopted is None
            assert test_app_data.birth_registration_data.adopted_in_the_uk is None
            assert test_app_data.birth_registration_data.forces_registration is None

    def test_uk_check_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.post('/birth-registration/uk-check', data={})
            assert response.status_code == 200
            assert 'Was your birth registered in the UK?' in response.text
            assert 'Select if your birth was registered in the UK' in response.text
