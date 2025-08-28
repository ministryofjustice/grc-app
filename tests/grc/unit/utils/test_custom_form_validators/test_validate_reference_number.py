import pytest
from grc.one_login.forms import ReferenceCheckForm
from grc.utils.form_custom_validators import validate_reference_number
from wtforms.validators import ValidationError


class TestValidateReferenceNumber:

    def test_validate_reference_number_valid(self, app, client, test_application):
        with app.test_request_context():
            form = ReferenceCheckForm()
            form.has_reference.data = 'HAS_REFERENCE'
            form.reference.data = test_application.reference_number
            assert validate_reference_number(form, form.reference) is None

    def test_validate_reference_number_invalid(self, app, test_application):
        with app.test_request_context():
            form = ReferenceCheckForm()
            form.has_reference.data = 'HAS_REFERENCE'
            form.reference.data = 'INVALID-REF'
            with pytest.raises(ValidationError, match='Your application reference number has not been validated'):
                validate_reference_number(form, form.reference)


