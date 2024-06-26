from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email
from grc.utils.form_custom_validators import validate_security_code, validate_reference_number, StrictRequiredIf


class EmailAddressForm(FlaskForm):
    email = EmailField(
        validators=[
            DataRequired(message='Enter your email address'),
            Email(message='Enter a valid email address')
        ]
    )


class SecurityCodeForm(FlaskForm):
    security_code = StringField(
        validators=[DataRequired(message='Enter a security code'), validate_security_code]
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
