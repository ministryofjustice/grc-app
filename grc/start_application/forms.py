from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l, gettext as _
from wtforms import EmailField, StringField, RadioField, BooleanField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import validateSecurityCode, validateReferenceNumber, StrictRequiredIf, LazyDataRequired, LazyEmail


class EmailAddressForm(FlaskForm):

    email = EmailField(
        validators=[
            LazyDataRequired(lazy_message=_l('Enter your email address')),
            LazyEmail(lazy_message=_l('Enter a valid email address'))
        ]
    )


class SecurityCodeForm(FlaskForm):
    security_code = StringField(
        validators=[LazyDataRequired(lazy_message=_l('Enter a security code')),
                    validateSecurityCode]
    )


class IsFirstVisitForm(FlaskForm):
    isFirstVisit = RadioField(
        choices=[
            ('FIRST_VISIT', "No"),
            ('HAS_REFERENCE', "Yes, and I have my reference number"),
            ('LOST_REFERENCE', "Yes, but I have lost my reference number")
        ],
        validators=[LazyDataRequired(message='Select if you have already started an application',
                                     lazy_message=_l('Select if you have already started an application'))]
    )

    reference = StringField(
        validators=[StrictRequiredIf('isFirstVisit', 'HAS_REFERENCE', message=_('Enter a reference number'), validators=[validateReferenceNumber])]
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
