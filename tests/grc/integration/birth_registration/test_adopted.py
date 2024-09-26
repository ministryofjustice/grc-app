from tests.grc.integration.conftest import load_test_data


class TestAdopted:

    def test_adopted_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/adopted')
            assert response.status_code == 200
            assert "Were you adopted?" in response.text

    def test_adopted_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/adopted')
            assert response.status_code == 302
            assert response.location == '/'

    def test_adopted_post_adopted(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'adopted': 'True'}
            response = client.post('/birth-registration/adopted', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/adopted-uk'
            assert test_app_data.birth_registration_data.adopted is True

    def test_adopted_post_not_adopted(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'adopted': 'False'}
            response = client.post('/birth-registration/adopted', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/forces'
            assert test_app_data.birth_registration_data.adopted is False

    def test_adopted_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/adopted', data={})
            assert response.status_code == 200
            assert "Were you adopted?" in response.text
            assert "Select if you were you adopted" in response.text
