from unittest.mock import patch


class TestIndex:
    def test_index(self, app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200
            assert 'Start or return to an application' in response.text

    def test_index_post_no_choice(self, app, client):
        with app.app_context():
            form_data = {'new_application': None}
            response = client.post('/', data=form_data)
            assert response.status_code == 200
            assert 'Start or return to an application' in response.text
            assert 'Select if you have already started an application' in response.text

    def test_index_start_application(self, app, client):
        with app.app_context():
            form_data = {'new_application': True}
            response = client.post('/', data=form_data)
            assert response.status_code == 302
            assert response.location == '/one-login/authenticate'

    def test_index_post_valid_email(self, app, client):
        with app.app_context():
            form_data = {'new_application': False}
            response = client.post('/', data=form_data)
            assert response.status_code == 302
            assert response.location == '/your-reference-number'
