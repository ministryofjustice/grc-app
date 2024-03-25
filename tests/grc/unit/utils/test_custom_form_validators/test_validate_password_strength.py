import pytest
from admin.password_reset.forms import PasswordResetForm
from grc.utils.form_custom_validators import validate_password_strength
from wtforms.validators import ValidationError


class TestValidatePasswordStrength:

    def test_validate_password_strength_valid(self, app):
        with app.app_context():
            form = PasswordResetForm()
            form.password.data = 'Akj_42fadHJ)(ce35DSA'
            assert validate_password_strength(form, form.password) is None

    def test_validate_password_strength_too_short(self, app):
        with app.app_context():
            with app.test_request_context():
                form = PasswordResetForm()
                form.password.data = 'AbC12_'
                with pytest.raises(ValidationError, match='Your password needs to contain 8 or more characters, a lower'
                                                          ' case letter, an upper case letter, a number and a special '
                                                          'character'):

                    validate_password_strength(form, form.password)

    def test_validate_password_strength_missing_number(self, app):
        with app.app_context():
            with app.test_request_context():
                form = PasswordResetForm()
                form.password.data = 'Akj_fadHJ)(ceDSA'
                with pytest.raises(ValidationError, match='Your password needs to contain 8 or more characters, a lower'
                                                          ' case letter, an upper case letter, a number and a special '
                                                          'character'):

                    validate_password_strength(form, form.password)

    def test_validate_password_strength_no_uppercase(self, app):
        with app.app_context():
            with app.test_request_context():
                form = PasswordResetForm()
                form.password.data = 'ab3_dqwr&daa543vu'
                with pytest.raises(ValidationError, match='Your password needs to contain 8 or more characters, a lower'
                                                          ' case letter, an upper case letter, a number and a special '
                                                          'character'):
                    validate_password_strength(form, form.password)

    def test_validate_password_strength_no_lowercase(self, app):
        with app.app_context():
            with app.test_request_context():
                form = PasswordResetForm()
                form.password.data = 'AB3_DG&EWFAD(VXC3'
                with pytest.raises(ValidationError, match='Your password needs to contain 8 or more characters, a lower'
                                                          ' case letter, an upper case letter, a number and a special '
                                                          'character'):
                    validate_password_strength(form, form.password)

    def test_validate_password_strength_no_special_char(self, app):
        with app.app_context():
            with app.test_request_context():
                form = PasswordResetForm()
                form.password.data = 'AB3DsadFaD6VXC3'
                with pytest.raises(ValidationError, match='Your password needs to contain 8 or more characters, a lower'
                                                          ' case letter, an upper case letter, a number and a special '
                                                          'character'):
                    validate_password_strength(form, form.password)