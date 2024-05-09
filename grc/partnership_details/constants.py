from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class PartnershipDetailsConstants(BaseConstants):
    HINT_TEXT_BEFORE_LINK = _l('If you are in a same-sex civil partnership and want ')
    HINT_TEXT_LINK = _l('convert your civil partnership to a marriage (opens in a new tab)')
    HINT_TEXT_AFTER_LINK = _l(', you must do that before you apply for a Gender Recognition Certificate.')

    # Errors
    STAY_MARRIED_OR_IN_CIVIL_PARTNERSHIP_ERROR = _l('Select if you plan to remain married or in your civil partnership'
                                                    ' after receiving your Gender Recognition Certificate')
