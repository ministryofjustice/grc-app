from flask_wtf import FlaskForm
from grc.business_logic.data_structures.submit_and_pay_data import HelpWithFeesType
from grc.submit_and_pay.constants import SubmitAndPayConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired
from grc.utils.form_custom_validators import StrictRequiredIf, validate_hwf_reference_number
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class MethodCheckForm(FlaskForm):
    applying_for_help_with_fee = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO_PAY_NOW)
        ],
        validators=[LazyDataRequired(lazy_message=c.HWF_ERROR)]
    )


class HelpTypeForm(FlaskForm):
    how_applying_for_fees = LazyRadioField(
        lazy_choices=[
            (HelpWithFeesType.USING_ONLINE_SERVICE.name, c.ONLINE_SERVICE),
            (HelpWithFeesType.USING_EX160_FORM.name, c.EX160_FORM)
        ],
        validators=[LazyDataRequired(lazy_message=c.HWF_OPTION_ERROR)]
    )

    help_with_fees_reference_number = StringField(
        validators=[
            StrictRequiredIf(
                'how_applying_for_fees',
                HelpWithFeesType.USING_ONLINE_SERVICE.name,
                message=c.HWF_REFERENCE_NUMBER_ERROR
            ),
            validate_hwf_reference_number
        ]
    )


class CheckYourAnswers(FlaskForm):
    certify = BooleanField(
        validators=[LazyDataRequired(lazy_message=c.CORRECT_INFO_DECLARATION_ERROR)]
    )
