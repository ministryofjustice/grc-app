from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo
from grc.utils.form_custom_validators import validate_password_strength


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        validators=[DataRequired(message='Enter a new password'), validate_password_strength]
    )

    confirmPassword = PasswordField(
        validators=[
            DataRequired(message='Confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )
