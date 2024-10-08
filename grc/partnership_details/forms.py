from flask_wtf import FlaskForm
from grc.business_logic.data_structures.partnership_details_data import CurrentlyInAPartnershipEnum
from grc.business_logic.constants.partnership_details import PartnershipDetailsConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired
from wtforms import StringField


class MarriageCivilPartnershipForm(FlaskForm):
    currently_married = LazyRadioField(
        lazy_choices=[
            (CurrentlyInAPartnershipEnum.MARRIED.name, c.MARRIED),
            (CurrentlyInAPartnershipEnum.CIVIL_PARTNERSHIP.name, c.CIVIL_PARTNERSHIP),
            (CurrentlyInAPartnershipEnum.NEITHER.name, c.NEITHER)
        ],
        validators=[LazyDataRequired(lazy_message=c.CURRENTLY_MARRIED_OR_CIVIL_PARTNERSHIP_ERROR)]
    )


class StayTogetherForm(FlaskForm):
    stay_together = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.STAY_MARRIED_OR_IN_CIVIL_PARTNERSHIP_ERROR)]
    )


class PartnerAgreesForm(FlaskForm):
    partner_agrees = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.PARTNER_AGREES_ERROR)]
    )


class PartnerDetailsForm(FlaskForm):
    partner_title = StringField(
        validators=[LazyDataRequired(lazy_message=c.PARTNER_TITLE_ERROR)]
    )

    partner_first_name = StringField(
        validators=[LazyDataRequired(lazy_message=c.PARTNER_FIRST_NAME_ERROR)]
    )

    partner_last_name = StringField(
        validators=[LazyDataRequired(lazy_message=c.PARTNER_LAST_NAME_ERROR)]
    )

    partner_postal_address = StringField(
        validators=[LazyDataRequired(lazy_message=c.PARTNER_POSTCODE_ERROR)]
    )


class PartnerDiedForm(FlaskForm):
    partner_died = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.PARTNER_DIED_ERROR)]
    )


class PreviousPartnershipEndedForm(FlaskForm):
    previous_partnership_ended = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.MARRIED_OR_CIVIL_PARTNERSHIP_ENDED_ERROR)]
    )


class InterimCheckForm(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass


class CheckYourAnswers(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass
