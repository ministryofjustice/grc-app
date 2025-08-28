from tests.grc.integration.conftest import load_test_data


class TestForces:
    def test_forces_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.get('/birth-registration/forces')
            assert response.status_code == 200
            assert ("Was your birth registered by a Forces registering service, or with a British Consul or High"
                    " Commission, or under Merchant Shipping or Civil Aviation provisions?") in response.text

    def test_forces_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/forces')
            assert response.status_code == 302
            assert response.location == '/'

    def test_forces_post(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.post('/birth-registration/forces', data={'forces': 'True'})
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/check-your-answers'
            assert test_app_data.birth_registration_data.forces_registration is True

    def test_forces_post_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.post('/birth-registration/forces', data={})
            assert response.status_code == 200
            assert ("Was your birth registered by a Forces registering service, or with a British Consul or High"
                    " Commission, or under Merchant Shipping or Civil Aviation provisions?") in response.text
            assert ("Select if your birth was registered by a Forces registering service, or with a British Consul "
                    "or High Commission, or under Merchant Shipping or Civil Aviation provisions") in response.text
