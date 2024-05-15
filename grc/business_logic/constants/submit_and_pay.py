from flask_babel import lazy_gettext as _l
from .base import BaseConstants


class SubmitAndPayConstants(BaseConstants):
    NO_PAY_NOW = _l('No, I will pay now')
    ONLINE_SERVICE = _l('Using the online service')
    EX160_FORM = _l('Using the EX160 form')
    HELP = _l('Help')
    ONLINE = _l('Online')

    # Errors
    HWF_ERROR = _l('Select if you are applying for help paying the fee')
    HWF_OPTION_ERROR = _l('Select how are you applying for help paying the fee')
    HWF_REFERENCE_NUMBER_ERROR = _l('Enter your Help with Fees reference number')
    CORRECT_INFO_DECLARATION_ERROR = _l('You must certify that all information given in this application is correct'
                                        ' and that you understand making a false application is an offence.')


    # Errors
    HWF_ERROR = _l('Select if you are applying for help paying the fee')