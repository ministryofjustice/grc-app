from flask_wtf import FlaskForm
from grc.business_logic.data_structures.submit_and_pay_data import HelpWithFeesType
from grc.submit_and_pay.constants import SubmitAndPayConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired
from grc.utils.form_custom_validators import StrictRequiredIf, validate_hwf_reference_number
from wtforms import StringField, RadioField, BooleanField
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
    how_applying_for_fees = RadioField(
        choices=[
            (HelpWithFeesType.USING_ONLINE_SERVICE.name, 'Using the online service'),
            (HelpWithFeesType.USING_EX160_FORM.name, 'Using the EX160 form')
        ],
        validators=[DataRequired(message='Select how are you applying for help paying the fee')]
    )

    help_with_fees_reference_number = StringField(
        validators=[
            StrictRequiredIf(
                'how_applying_for_fees',
                HelpWithFeesType.USING_ONLINE_SERVICE.name,
                message='Enter your Help with Fees reference number'
            ),
            validate_hwf_reference_number
        ]
    )


class CheckYourAnswers(FlaskForm):
    certify = BooleanField(
        validators=[DataRequired(message='You must certify that all information given in this application is correct and that you understand making a false application is an offence.')]
    )
