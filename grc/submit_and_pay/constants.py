from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class SubmitAndPayConstants(BaseConstants):
    NO_PAY_NOW = _l('No, I will pay now')
    ONLINE_SERVICE = _l('Using the online service')
    EX160_FORM = _l('Using the online service')

    # Errors
    HWF_ERROR = _l('Select if you are applying for help paying the fee')
    HWF_OPTION_ERROR = _l('Select how are you applying for help paying the fee')
    HWF_REFERENCE_NUMBER_ERROR = _l('Enter your Help with Fees reference number')
