from flask_wtf import FlaskForm
from grc.business_logic.data_structures.partnership_details_data import CurrentlyInAPartnershipEnum
from grc.business_logic.constants import BaseConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired


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
    stay_together = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you plan to remain married or in your civil partnership after receiving your Gender Recognition Certificate')]
    )


class PartnerAgreesForm(FlaskForm):
    partner_agrees = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you can provide a declaration of consent from your spouse or civil partner')]
    )


class PartnerDetailsForm(FlaskForm):
    partner_title = StringField(
        validators=[DataRequired(message="Enter your spouse or civil partner's title")]
    )

    partner_first_name = StringField(
        validators=[DataRequired(message="Enter your spouse or civil partner's first name")]
    )

    partner_last_name = StringField(
        validators=[DataRequired(message="Enter your spouse or civil partner's last name")]
    )

    partner_postal_address = StringField(
        validators=[DataRequired(message="Enter your spouse or civil partner's postal address")]
    )


class PartnerDiedForm(FlaskForm):
    partner_died = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you were previously married or in a civil partnership, and your spouse or partner died')]
    )


class PreviousPartnershipEndedForm(FlaskForm):
    previous_partnership_ended = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you have ever been married or in a civil partnership that has ended')]
    )


class InterimCheckForm(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass


class CheckYourAnswers(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass
