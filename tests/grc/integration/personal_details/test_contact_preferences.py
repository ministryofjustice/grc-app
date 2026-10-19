from tests.grc.integration.conftest import save_test_data, load_test_data


def prepare_personal_details_data(test_application):
    data = test_application.application_data()
    data.personal_details_data.address_line_one = '1 Test Street'
    data.personal_details_data.address_town_city = 'London'
    data.personal_details_data.address_country = 'United Kingdom'
    data.personal_details_data.address_postcode = 'SW1H 9AJ'
    save_test_data(data)


def log_in(client, test_application):
    with client.session_transaction() as session:
        session['reference_number'] = test_application.reference_number
        session['identity_verified'] = True


class TestContactPreferences:

    def test_contact_preferences_post_without_email(self, app, client, test_application):
        with app.app_context():
            prepare_personal_details_data(test_application)
            log_in(client, test_application)

            response = client.post('/personal-details/contact-preferences', data={
                'contact_options': ['POST']
            })

            assert response.status_code == 200
            assert 'Enter your email address' in response.text

    def test_contact_preferences_post_invalid_email(self, app, client, test_application):
        with app.app_context():
            prepare_personal_details_data(test_application)
            log_in(client, test_application)

            response = client.post('/personal-details/contact-preferences', data={
                'contact_options': ['POST'],
                'email': 'not-an-email'
            })

            assert response.status_code == 200
            assert 'Enter a valid email address' in response.text

    def test_contact_preferences_post_post_only_saves_email_and_post_preference(self, app, client, test_application):
        with app.app_context():
            prepare_personal_details_data(test_application)
            log_in(client, test_application)

            response = client.post('/personal-details/contact-preferences', data={
                'contact_options': ['POST'],
                'email': 'alex.example@example.com'
            })
            test_app_data = load_test_data(test_application.reference_number)

            assert response.status_code == 302
            assert response.location == '/personal-details/hmrc'
            assert test_app_data.personal_details_data.contact_email_address == 'alex.example@example.com'
            assert test_app_data.personal_details_data.contact_phone_number == ''
            assert not test_app_data.personal_details_data.contact_by_email
            assert test_app_data.personal_details_data.contact_by_post

    def test_contact_preferences_post_email_preference_is_saved_separately_from_address(self, app, client, test_application):
        with app.app_context():
            prepare_personal_details_data(test_application)
            log_in(client, test_application)

            response = client.post('/personal-details/contact-preferences', data={
                'contact_options': ['EMAIL', 'PHONE'],
                'email': 'alex.example@example.com',
                'phone': '07123456789'
            })
            test_app_data = load_test_data(test_application.reference_number)

            assert response.status_code == 302
            assert test_app_data.personal_details_data.contact_email_address == 'alex.example@example.com'
            assert test_app_data.personal_details_data.contact_by_email
            assert test_app_data.personal_details_data.contact_phone_number == '07123456789'

    def test_contact_preferences_get_does_not_select_email_for_saved_email_address(self, app, client, test_application):
        with app.app_context():
            prepare_personal_details_data(test_application)
            data = load_test_data(test_application.reference_number)
            data.personal_details_data.contact_email_address = 'alex.example@example.com'
            data.personal_details_data.contact_phone_number = '07123456789'
            save_test_data(data)
            log_in(client, test_application)

            response = client.get('/personal-details/contact-preferences')

            assert response.status_code == 200
            assert 'value="alex.example@example.com"' in response.text
            assert 'value="EMAIL" class="govuk-checkboxes__input"' in response.text
            assert 'value="EMAIL" class="govuk-checkboxes__input" checked' not in response.text
            assert 'value="07123456789"' in response.text
