from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import InputRequired
from grc.utils.form_custom_validators import StrictRequiredIf, validate_reference_number
from grc.lazy.lazy_fields import LazyRadioField
from grc.business_logic.constants.one_login import OneLoginConstants as c
from grc.lazy.lazy_form_custom_validators import LazyDataRequired

class NewExistingApplicationForm(FlaskForm):
    new_application = LazyRadioField(
        lazy_choices=[
            (True, c.NEW_APPLICATION),
            (False, c.EXISTING_APPLICATION),
        ],
        validators=[LazyDataRequired(lazy_message=c.IS_FIRST_VISIT_ERROR)]
    )

class ReferenceCheckForm(FlaskForm):
    has_reference = LazyRadioField(
        lazy_choices=[
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