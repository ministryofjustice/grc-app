import pytest
from tests.grc.integration.conftest import save_test_data, load_test_data
from unittest.mock import patch, MagicMock


class TestIndex:

    @pytest.fixture
    def mock_render_template(self):
        with patch('grc.birth_registration.render_template') as mock:
            yield mock

    def test_index(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration')
            assert response.status_code == 200
            assert 'What name was originally registered on your birth or adoption certificate?' in response.text

    def test_index_back_link(self, app, client, test_application, mock_render_template: MagicMock,):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration')
            _, kwargs = mock_render_template.call_args
            assert response.status_code == 200
            assert kwargs['back'] == '/task-list'

    def test_index_not_logged_in(self, app, client):
        with app.app_context():
            response = client.get('/birth-registration')
            assert response.status_code == 302
            assert response.location == '/'

    def test_index_get_birth_registration_name_persists(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = test_application.application_data()
            data.birth_registration_data.first_name = 'Test first name'
            data.birth_registration_data.middle_names = 'Test middle names'
            data.birth_registration_data.last_name = 'Test last name'
            save_test_data(data)
            response = client.get('/birth-registration')
            assert response.status_code == 200
            assert 'Test first name' in response.text
            assert 'Test middle names' in response.text
            assert 'Test last name' in response.text

    def test_index_post_name_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {
                'first_name': 'Test first name',
                'middle_names': 'Test middle names',
                'last_name': 'Test last name'
            }
            response = client.post('/birth-registration', data=data)

            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/dob'
            assert test_app_data.birth_registration_data.first_name == 'Test first name'
            assert test_app_data.birth_registration_data.middle_names == 'Test middle names'
            assert test_app_data.birth_registration_data.last_name == 'Test last name'

    def test_index_no_first_or_last_name(self, app, client, test_application):
        with client.session_transaction() as session:
            session['reference_number'] = test_application.reference_number
        response = client.post('/birth-registration', data={})
        assert response.status_code == 200
        assert 'Enter your first name, as originally registered on your birth or adoption certificate' in response.text
        assert 'Enter your last name, as originally registered on your birth or adoption certificate' in response.text
