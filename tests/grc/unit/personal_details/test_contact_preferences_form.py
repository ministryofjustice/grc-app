from grc.personal_details.forms import ContactPreferencesForm


class TestContactPreferencesForm:

    def test_email_required_when_email_contact_option_not_selected(self, app):
        with app.test_request_context():
            form = ContactPreferencesForm()
            form.contact_options.data = ['POST']

            assert not form.validate()
            assert form.errors['email'][0] == 'Enter your email address'

    def test_email_format_validated_when_email_contact_option_not_selected(self, app):
        with app.test_request_context():
            form = ContactPreferencesForm()
            form.contact_options.data = ['POST']
            form.email.data = 'not-an-email'

            assert not form.validate()
            assert form.errors['email'][0] == 'Enter a valid email address'

    def test_phone_still_required_when_phone_contact_option_selected(self, app):
        with app.test_request_context():
            form = ContactPreferencesForm()
            form.contact_options.data = ['PHONE']
            form.email.data = 'alex.example@example.com'

            assert not form.validate()
            assert form.errors['phone'][0] == 'Enter your phone number'
