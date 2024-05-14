from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class SubmitAndPayConstants(BaseConstants):
    NO_PAY_NOW = _l('No, I will pay now')

    # Errors
    HWF_ERROR = _l('Select if you are applying for help paying the fee')