from flask_wtf import FlaskForm
from grc.business_logic.constants import BaseConstants as c
from grc.utils.form_custom_validators import validate_security_code
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email_address = EmailField(
        validators=[
            DataRequired(message='Enter your email address'),
            Email(message='Enter a valid email address')
        ]
    )

    password = PasswordField(
        validators=[DataRequired(message='Enter your password')]
    )


class SecurityCodeForm(FlaskForm):
    is_admin = True
    security_code = StringField(
        validators=[DataRequired(message='Enter a security code'), validate_security_code]
    )
