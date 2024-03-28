import pytest
from grc.personal_details.forms import AddressForm
from grc.utils.form_custom_validators import validate_address_field
from wtforms.validators import ValidationError


class TestValidateAddressField:

    def test_validate_address_field_valid(self, app):
        with app.app_context():
            form = AddressForm()
            form.address_line_one.data = '12 valid address line'
            assert validate_address_field(form, form.address_line_one) is None

    def test_validate_address_field_no_data(self, app):
        with app.app_context():
            form = AddressForm()
            form.address_line_one.data = None
            assert validate_address_field(form, form.address_line_one) is None

    def test_validate_address_field_invalid_address_line_one(self, app):
        with app.app_context():
            form = AddressForm()
            form.address_line_one.data = '12 in^al(id a££ress line'
            with pytest.raises(ValidationError, match='Enter a valid address line one'):
                validate_address_field(form, form.address_line_one)

    def test_validate_address_field_invalid_address_line_two(self, app):
        with app.app_context():
            form = AddressForm()
            form.address_line_one.data = '12 valid address line'
            form.address_line_two.data = '12 in^al(id a££ress line'
            with pytest.raises(ValidationError, match='Enter a valid address line two'):
                validate_address_field(form, form.address_line_two)

