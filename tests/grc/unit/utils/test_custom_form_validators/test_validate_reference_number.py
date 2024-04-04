import pytest
from flask import session
from grc.start_application.forms import IsFirstVisitForm
from grc.utils.form_custom_validators import validate_reference_number
from wtforms.validators import ValidationError


class TestValidateReferenceNumber:

    def test_validate_reference_number_valid(self, app, client, test_application):
        with app.test_request_context():
            session['validatedEmail'] = 'test.public.email@example.com'
            form = IsFirstVisitForm()
            form.isFirstVisit.data = 'HAS_REFERENCE'
            form.reference.data = test_application.reference_number
            assert validate_reference_number(form, form.reference) is None

    def test_validate_reference_number_invalid(self, app, test_application):
        with app.test_request_context():
            session['validatedEmail'] = 'test.public.email@example.com'
            form = IsFirstVisitForm()
            form.isFirstVisit.data = 'HAS_REFERENCE'
            form.reference.data = 'INVALID-REF'
            with pytest.raises(ValidationError, match='Enter a valid reference number'):
                validate_reference_number(form, form.reference)

    def test_validate_reference_number_invalid_unauth_public_user(self, app, test_application):
        with app.test_request_context():
            session['validatedEmail'] = 'different.public.email@example.com'
            form = IsFirstVisitForm()
            form.isFirstVisit.data = 'HAS_REFERENCE'
            form.reference.data = test_application.reference_number
            with pytest.raises(ValidationError, match='Enter a valid reference number'):
                validate_reference_number(form, form.reference)

