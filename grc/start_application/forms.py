from flask_wtf import FlaskForm
from grc.start_application.constants import StartApplicationConstants as c
from grc.lazy.lazy_fields import LazyRadioField
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
    isFirstVisit = LazyRadioField(
        lazy_choices=[
            ('FIRST_VISIT', c.NO),
            ('HAS_REFERENCE', c.YES_WITH_REFERENCE_NUMBER),
            ('LOST_REFERENCE', c.YES_LOST_REFERENCE_NUMBER)
        ],
        validators=[LazyDataRequired(lazy_message=c.IS_FIRST_VISIT_ERROR)]
    )

    reference = StringField(
        validators=[StrictRequiredIf('isFirstVisit', 'HAS_REFERENCE',
                                     message=c.NO_REFERENCE_NUMBER_ERROR, validators=[validate_reference_number])]
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
