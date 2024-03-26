from flask_wtf import FlaskForm
from wtforms import EmailField, BooleanField
from wtforms.validators import DataRequired, Email
from grc.utils.form_custom_validators import validate_gov_uk_email_address


class UsersForm(FlaskForm):
    email_address = EmailField(
        validators=[
            DataRequired(message="Enter the new user's email address"),
            Email(message='Enter a valid email address'),
            validate_gov_uk_email_address
        ]
    )

    is_admin_user = BooleanField()
