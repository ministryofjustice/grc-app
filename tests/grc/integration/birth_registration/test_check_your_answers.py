import datetime
import pytest
from grc.business_logic.data_structures.birth_registration_data import AdoptedInTheUkEnum as AdoptEnum
from tests.grc.integration.conftest import load_test_data, save_test_data


class TestCheckYourAnswers:

    @pytest.fixture
    def completed_section_application_data(self, test_application):
        test_app_data = test_application.application_data()
        test_app_data.birth_registration_data.first_name = 'First name'
        test_app_data.birth_registration_data.last_name = 'Last name'
        test_app_data.birth_registration_data.date_of_birth = datetime.date(1990, 1, 1)
        test_app_data.birth_registration_data.birth_registered_in_uk = True
        test_app_data.birth_registration_data.town_city_of_birth = 'London'
        test_app_data.birth_registration_data.mothers_first_name = 'Mothers first name'
        test_app_data.birth_registration_data.mothers_last_name = 'Mothers last name'
        test_app_data.birth_registration_data.mothers_maiden_name = 'Mothers maiden name'
        test_app_data.birth_registration_data.fathers_name_on_birth_certificate = False
        test_app_data.birth_registration_data.adopted = True
        test_app_data.birth_registration_data.adopted_in_the_uk = AdoptEnum.ADOPTED_IN_THE_UK_YES
        test_app_data.birth_registration_data.forces_registration = False
        save_test_data(test_app_data)

    def test_cya_get(self, app, client, test_application, completed_section_application_data):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.get('/birth-registration/check-your-answers')
            assert response.status_code == 200
            assert "Check your answers: Birth registration details" in response.text

    def test_cya_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/check-your-answers')
            assert response.status_code == 302
            assert response.location == '/'

    def test_cya_post_section_unfinished(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            test_app_data = test_application.application_data()
            test_app_data.birth_registration_data.first_name = 'First name'
            test_app_data.birth_registration_data.last_name = 'Last name'
            test_app_data.birth_registration_data.date_of_birth = datetime.date(1990, 1, 1)
            test_app_data.birth_registration_data.birth_registered_in_uk = True
            test_app_data.birth_registration_data.town_city_of_birth = 'London'
            test_app_data.birth_registration_data.mothers_first_name = 'Mothers first name'
            test_app_data.birth_registration_data.mothers_last_name = 'Mothers last name'

            # Unfinished part of section
            test_app_data.birth_registration_data.mothers_maiden_name = None

            test_app_data.birth_registration_data.fathers_name_on_birth_certificate = False
            test_app_data.birth_registration_data.adopted = True
            test_app_data.birth_registration_data.adopted_in_the_uk = AdoptEnum.ADOPTED_IN_THE_UK_YES
            test_app_data.birth_registration_data.forces_registration = False
            save_test_data(test_app_data)
            response = client.get('/birth-registration/check-your-answers')
            assert response.status_code == 302
            assert response.location == '/task-list'

    def test_cya_post_section_finished(self, app, client, test_application, completed_section_application_data):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.post('/birth-registration/check-your-answers')
            assert response.status_code == 302
            assert response.location == '/task-list'
