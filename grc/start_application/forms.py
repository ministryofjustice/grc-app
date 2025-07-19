from flask_wtf import FlaskForm
from grc.business_logic.constants.base import BaseConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyEmail
from wtforms import EmailField, StringField, BooleanField
from grc.utils.form_custom_validators import validate_security_code, validate_reference_number, StrictRequiredIf, validate_email_matches_application


class EmailAddressForm(FlaskForm):
    email = EmailField(
        validators=[
            LazyDataRequired(lazy_message=c.NO_EMAIL_ADDRESS_ERROR),
            LazyEmail(message=c.EMAIL_ADDRESS_INVALID_ERROR),
            validate_email_matches_application
        ]
    )


class SecurityCodeForm(FlaskForm):
    security_code = StringField(
        validators=[LazyDataRequired(lazy_message=c.NO_SECURITY_CODE), validate_security_code]
    )


class OverseasCheckForm(FlaskForm):
    overseasCheck = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.GENDER_RECOGNITION_OUTSIDE_UK_ERROR)]
    )


class OverseasApprovedCheckForm(FlaskForm):
    overseasApprovedCheck = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.GENDER_RECOGNITION_IN_APPROVED_COUNTRY_ERROR)]
    )


class DeclarationForm(FlaskForm):
    consent = BooleanField(
        validators=[LazyDataRequired(lazy_message=c.DECLARATION_ERROR)]
    )
