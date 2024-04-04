import pytest
from admin.users.forms import UsersForm
from grc.utils.form_custom_validators import validate_gov_uk_email_address
from wtforms.validators import ValidationError


class TestValidateGovUkEmailAddress:

    def test_validate_gov_uk_email_address_valid(self, app):
        with app.app_context():
            form = UsersForm()
            form.email_address.data = 'valid.justice.email@example.gov.uk'
            assert validate_gov_uk_email_address(form, form.email_address) is None

    def test_validate_gov_uk_email_address_invalid(self, app):
        with app.app_context():
            form = UsersForm()
            form.email_address.data = app.config['TEST_PUBLIC_USER']
            with pytest.raises(ValidationError, match='Enter a .gov.uk email address'):
                validate_gov_uk_email_address(form, form.email_address)
