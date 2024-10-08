import pytest
from flask import session
from admin.admin.forms import SecurityCodeForm as AdminSecurityCodeForm
from grc.start_application.forms import SecurityCodeForm as PublicSecurityCodeForm
from grc.utils.form_custom_validators import validate_security_code, validate_security_code_admin
from unittest.mock import patch
from wtforms.validators import ValidationError


class TestValidateSecurityCode:

    def test_validate_security_code_test_or_local(self, app, client):
        with app.app_context():

            form = PublicSecurityCodeForm()
            form.security_code.data = '11111'

            assert validate_security_code(form, form.security_code) is None

    @patch('grc.utils.form_custom_validators.is_security_code_valid')
    def test_validate_security_code_valid_public_user(self, mock_is_security_code_valid,  app, client):
        with app.app_context():

            form = PublicSecurityCodeForm()
            form.security_code.data = '12345'

            with app.test_request_context():
                session['email'] = 'test.email@example.com'
                mock_is_security_code_valid.return_value = True
                assert validate_security_code(form, form.security_code) is None

    @patch('grc.utils.form_custom_validators.is_security_code_valid')
    def test_validate_security_code_valid_admin_user(self, mock_is_security_code_valid,  app, client):
        with app.app_context():

            form = AdminSecurityCodeForm()
            form.security_code.data = '12345'

            with app.test_request_context():
                session['email'] = 'test.email@example.com'
                mock_is_security_code_valid.return_value = True
                assert validate_security_code_admin(form, form.security_code) is None

    @patch('grc.utils.form_custom_validators.is_security_code_valid')
    def test_validate_security_code_invalid(self, mock_is_security_code_valid,  app, client):
        with app.app_context():

            form = PublicSecurityCodeForm()
            form.security_code.data = '12345'

            with app.test_request_context():
                session['email'] = 'test.email@example.com'
                mock_is_security_code_valid.return_value = False

                with pytest.raises(ValidationError, match='Enter the security code that we emailed you'):
                    validate_security_code(form, form.security_code)

    @patch('grc.utils.form_custom_validators.is_security_code_valid')
    def test_validate_security_code_invalid_admin_user(self, mock_is_security_code_valid,  app, client):
        with app.app_context():

            form = AdminSecurityCodeForm()
            form.security_code.data = '12345'

            with app.test_request_context():
                session['email'] = 'test.email@example.com'
                mock_is_security_code_valid.return_value = False
                with pytest.raises(ValidationError, match='Enter the security code that we emailed you'):
                    validate_security_code_admin(form, form.security_code)
