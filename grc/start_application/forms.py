from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l, gettext as _, LazyString
from typing import Tuple, List, Any
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


class LazyRadioField(RadioField):
    def __init__(self, lazy_choices: List[Tuple[Any, LazyString]], choices=None, validators=None, **kwargs):
        super().__init__(validators=validators, choices=choices, **kwargs)
        self.lazy_choices = lazy_choices
        self.choices = choices if choices else self._stringify_lazy_choices()

    def _stringify_lazy_choices(self) -> List[Tuple[str, str]]:
        return [(choice_id, _(choice_label)) for choice_id, choice_label in self.lazy_choices]


class IsFirstVisitForm(FlaskForm):
    isFirstVisit = LazyRadioField(
        lazy_choices=[
            ('FIRST_VISIT', _l("No")),
            ('HAS_REFERENCE', _l("Yes, and I have my reference number")),
            ('LOST_REFERENCE', _l("Yes, but I have lost my reference number"))
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
