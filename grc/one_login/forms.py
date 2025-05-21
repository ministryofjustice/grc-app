from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import InputRequired
from grc.utils.form_custom_validators import StrictRequiredIf, validate_reference_number
from grc.lazy.lazy_fields import LazyRadioField
from grc.business_logic.constants.start_application import StartApplicationConstants as c
from grc.lazy.lazy_form_custom_validators import LazyDataRequired


class ReferenceCheckForm(FlaskForm):
    has_reference = LazyRadioField(
        lazy_choices=[
            ('FIRST_VISIT', c.NO),
            ('HAS_REFERENCE', c.YES_WITH_REFERENCE_NUMBER),
            ('LOST_REFERENCE', c.YES_LOST_REFERENCE_NUMBER)
        ],
        validators=[LazyDataRequired(lazy_message=c.IS_FIRST_VISIT_ERROR)]
    )
    reference = StringField(
        validators=[
            StrictRequiredIf(
                'has_reference',
                'HAS_REFERENCE',
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