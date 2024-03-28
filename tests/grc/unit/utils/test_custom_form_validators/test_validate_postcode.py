import pytest
from grc.personal_details.forms import AddressForm
from grc.utils.form_custom_validators import validate_postcode
from wtforms.validators import ValidationError


class TestValidatePostcode:

    # https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes

    def test_validate_postcode_valid(self, app):
        with app.app_context():
            form = AddressForm()
            valid_postcodes = ['W1J 7NT', 'SW1H 9EX', 'W1J7NT', 'SW1H9EX', 'M25 1AB', 'W29CD']
            for postcode in valid_postcodes:
                form.postcode.data = postcode
                assert validate_postcode(form, form.postcode) is None

    def test_validate_postcode_invalid(self, app):
        with app.app_context():
            form = AddressForm()
            invalid_postcodes = ['W 1J 7NT', 'SW1H9 EX', 'W 1J7NT', 'aWC2H 7LT', 'a WC2H', '@^^£&@*', '123 456',
                                 '1234 313']
            for postcode in invalid_postcodes:
                form.postcode.data = postcode
                with pytest.raises(ValidationError, match='Enter a valid postcode'):
                    validate_postcode(form, form.postcode)
