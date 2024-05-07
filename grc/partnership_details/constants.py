from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class PartnershipDetailsConstants(BaseConstants):
    STAY_TOGETHER_HINT_TEXT_BEFORE_LINK = _l('If you are in a same-sex civil partnership and want ')
    STAY_TOGETHER_HINT_TEXT_LINK = _l('convert your civil partnership to a marriage (opens in a new tab)')
    STAY_TOGETHER_HINT_TEXT_AFTER_LINK = _l(', you must do that before you apply for a Gender Recognition Certificate.')

    PARTNER_AGREES_CP_TEXT_BEFORE_LINK = _l('If you intend to remain in a civil partnership, your civil partner '
                                            'needs to fill in a ')
    PARTNER_AGREES_MARRIED_TEXT_BEFORE_LINK = _l('If you intend to remain married, your spouse needs to fill in a ')
    PARTNER_AGREES_CP_LINK_TEXT = _l('statutory declaration for civil partners (opens in a new tab)')
    PARTNER_AGREES_MARRIED_LINK_TEXT = _l('statutory declaration for spouses (opens in a new tab)')
    PARTNER_AGREES_TEXT_AFTER_LINK = _l(', and sign it in front of someone authorised to administer oaths.')
    PARTNER_AGREES_CP_QUESTION = _l('Can you provide a statutory declaration from your civil partner')
    PARTNER_AGREES_MARRIED_QUESTION = _l('Can you provide a statutory declaration from your spouse')

    # Errors
    STAY_MARRIED_OR_IN_CIVIL_PARTNERSHIP_ERROR = _l('Select if you plan to remain married or in your civil partnership'
                                                    ' after receiving your Gender Recognition Certificate')
    PARTNER_AGREES_ERROR = _l('Select if you can provide a declaration of consent from your spouse or civil partner')
