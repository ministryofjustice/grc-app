from flask_wtf import FlaskForm
from grc.business_logic.constants import BaseConstants as c
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyEmail
from wtforms import EmailField, StringField, RadioField, BooleanField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import validate_security_code, validate_reference_number, StrictRequiredIf


class EmailAddressForm(FlaskForm):
    email = EmailField(
        validators=[
            LazyDataRequired(lazy_message=c.NO_EMAIL_ADDRESS_ERROR),
            LazyEmail(message=c.EMAIL_ADDRESS_INVALID_ERROR)
        ]
    )


class SecurityCodeForm(FlaskForm):
    security_code = StringField(
        validators=[LazyDataRequired(lazy_message=c.NO_SECURITY_CODE), validate_security_code]
    )


class IsFirstVisitForm(FlaskForm):
    isFirstVisit = RadioField(
        choices=[
            ('FIRST_VISIT', "No"),
            ('HAS_REFERENCE', "Yes, and I have my reference number"),
            ('LOST_REFERENCE', "Yes, but I have lost my reference number")
        ],
        validators=[DataRequired(message='Select if you have already started an application')]
    )

    reference = StringField(
        validators=[StrictRequiredIf('isFirstVisit', 'HAS_REFERENCE',
                                     message='Enter a reference number', validators=[validate_reference_number])]
    )


class OverseasCheckForm(FlaskForm):
    overseasCheck = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you ever been issued a Gender Recognition Certificate')]
    )


class OverseasApprovedCheckForm(FlaskForm):
    overseasApprovedCheck = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you have official documentation')]
    )


class DeclerationForm(FlaskForm):
    consent = BooleanField(
        validators=[DataRequired(message='You must consent to the General Register Office contacting you')]
    )
