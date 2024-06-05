import datetime
from grc.business_logic.data_structures.birth_registration_data import AdoptedInTheUkEnum as AdoptEnum
from tests.grc.integration.conftest import save_test_data, load_test_data


class TestAdoptedUK:

    def test_adopted_uk_get(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/birth-registration/adopted-uk')
            assert response.status_code == 200
            assert "Were you adopted in the United Kingdom?" in response.text

    def test_adopted_uk_get_not_logged_in(self, app, client, test_application):
        with app.app_context():
            response = client.get('/birth-registration/adopted-uk')
            assert response.status_code == 302
            assert response.location == '/'

    def test_adopted_post_adopted_in_uk(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'adopted_uk': 'ADOPTED_IN_THE_UK_YES'}
            response = client.post('/birth-registration/adopted-uk', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/forces'
            assert test_app_data.birth_registration_data.adopted_in_the_uk == AdoptEnum.ADOPTED_IN_THE_UK_YES

    def test_adopted_post_adopted_outside_uk(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'adopted_uk': 'ADOPTED_IN_THE_UK_NO'}
            response = client.post('/birth-registration/adopted-uk', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/forces'
            assert test_app_data.birth_registration_data.adopted_in_the_uk == AdoptEnum.ADOPTED_IN_THE_UK_NO

    def test_adopted_post_adopted_not_sure_where(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            data = {'adopted_uk': 'ADOPTED_IN_THE_UK_DO_NOT_KNOW'}
            response = client.post('/birth-registration/adopted-uk', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/forces'
            assert test_app_data.birth_registration_data.adopted_in_the_uk == AdoptEnum.ADOPTED_IN_THE_UK_DO_NOT_KNOW

    def test_adopted_post_adopted_in_uk_section_completed_redirect_cya(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
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
            data = {'adopted_uk': 'ADOPTED_IN_THE_UK_YES'}
            response = client.post('/birth-registration/adopted-uk', data=data)
            test_app_data = load_test_data(test_application.reference_number)
            assert response.status_code == 302
            assert response.location == '/birth-registration/check-your-answers'
            assert test_app_data.birth_registration_data.section_status == 'COMPLETED'

    def test_adopted_uk_no_data(self, app, client, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.post('/birth-registration/adopted-uk', data={})
            assert response.status_code == 200
            assert "Were you adopted in the United Kingdom?" in response.text
            assert "Select if you were adopted in the United Kingdom" in response.text
