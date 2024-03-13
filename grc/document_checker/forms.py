from flask_wtf import FlaskForm
from wtforms import EmailField, RadioField
from wtforms.validators import DataRequired, Email
from grc.business_logic import constants as c
from grc.document_checker.doc_checker_state import CurrentlyInAPartnershipEnum
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired


class PreviousNamesCheck(FlaskForm):
    changed_name_to_reflect_gender = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.PREVIOUS_NAME_CHECK_ERROR)]
    )


class MarriageCivilPartnershipForm(FlaskForm):
    currently_in_a_partnership = LazyRadioField(
        lazy_choices=[
            (CurrentlyInAPartnershipEnum.MARRIED.name, c.MARRIED),
            (CurrentlyInAPartnershipEnum.CIVIL_PARTNERSHIP.name, c.CIVIL_PARTNERSHIP),
            (CurrentlyInAPartnershipEnum.NEITHER.name, c.NEITHER)
        ],
        validators=[LazyDataRequired(lazy_message=c.CURRENTLY_MARRIED_OR_CIVIL_PARTNERSHIP_ERROR)]
    )


class PlanToRemainInAPartnershipForm(FlaskForm):
    plan_to_remain_in_a_partnership = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you plan to remain married after receiving your Gender Recognition Certificate')]
    )


class PartnerDiedForm(FlaskForm):
    previous_partnership_partner_died = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.PREVIOUS_PARTNER_DIED_ERROR)]
    )


class PreviousPartnershipEndedForm(FlaskForm):
    previous_partnership_ended = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.MARRIED_OR_CIVIL_PARTNERSHIP_ENDED_ERROR)]
    )


class GenderRecognitionOutsideUKForm(FlaskForm):
    gender_recognition_outside_uk = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you have received gender recognition in one of these countries or territories')]
    )


class EmailForm(FlaskForm):
    email_address = EmailField(
        validators=[
            DataRequired(message='Enter your email address'),
            Email(message='Enter a valid email address')
        ]
    )
