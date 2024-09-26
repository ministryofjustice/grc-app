from flask_wtf import FlaskForm
from wtforms import EmailField
from grc.business_logic.constants.document_checker import DocumentCheckerConstants as c
from grc.document_checker.doc_checker_state import CurrentlyInAPartnershipEnum
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyEmail


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
    plan_to_remain_in_a_partnership = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.PLAN_TO_REMAIN_MARRIED_ERROR)]
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
    gender_recognition_outside_uk = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.GENDER_RECOGNITION_IN_COUNTRY_ERROR)]
    )


class EmailForm(FlaskForm):
    email_address = EmailField(
        validators=[
            LazyDataRequired(lazy_message=c.NO_EMAIL_ADDRESS_ERROR),
            LazyEmail(lazy_message=c.EMAIL_ADDRESS_INVALID_ERROR)
        ]
    )
