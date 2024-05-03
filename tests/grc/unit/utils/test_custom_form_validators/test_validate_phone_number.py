import pytest
from grc.personal_details.forms import ContactPreferencesForm
from grc.utils.form_custom_validators import validate_phone_number
from wtforms.validators import ValidationError


class TestValidatePhoneNumber:

    def test_validate_phone_number_valid(self, app):
        with app.test_request_context():
            form = ContactPreferencesForm()
            form.contact_options.data = 'PHONE'
            valid_numbers = ['0', '123', '34324', '07111111111', '07123456789', '31341432131432143124']
            for number in valid_numbers:
                form.phone.data = number
                assert validate_phone_number(form, form.phone) is None

    def test_validate_phone_number_invalid_non_numeric(self, app):
        with app.test_request_context():
            form = ContactPreferencesForm()
            form.contact_options.data = 'PHONE'
            invalid_numbers = ['0A', '12dad3', '34DSAD324', '07111ddsaDQ111dW111d', '071234SADDQD', '432DSAD143124']
            for number in invalid_numbers:
                form.phone.data = number
                with pytest.raises(ValidationError, match='Enter a valid phone number'):
                    validate_phone_number(form, form.phone)

    def test_validate_phone_number_invalid_special_char(self, app):
        with app.test_request_context():
            form = ContactPreferencesForm()
            form.contact_options.data = 'PHONE'
            invalid_numbers = ['0£', '1$23', '34*(324', '07.111111111', '071234+56789', '+3134143213', '+447788991122']
            for number in invalid_numbers:
                form.phone.data = number
                with pytest.raises(ValidationError, match='Enter a valid phone number'):
                    validate_phone_number(form, form.phone)
