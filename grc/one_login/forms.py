from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import InputRequired
from grc.utils.form_custom_validators import StrictRequiredIf, validate_reference_number

class ReferenceCheckForm(FlaskForm):
    has_reference = RadioField(
        'Do you have a reference number?',
        choices=[('yes', 'Yes'), ('no', 'No')],
        validators=[InputRequired()]
    )
    reference = StringField(
        validators=[
            StrictRequiredIf(
                'has_reference',
                'yes',
                message='Please enter your reference number',
                validators=[validate_reference_number]
            )
        ]
    )

class IdentityEligibility(FlaskForm):
    identity_eligible = RadioField(
        'Are you able to prove your identity by use of xx? If you do not live in the United Kingdom do you have xxx?',
        choices=[('yes', 'Yes'), ('no', 'No')],
        validators=[InputRequired()]
    )