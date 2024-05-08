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
    PARTNER_AGREES_CP_QUESTION = _l('Can you provide a statutory declaration from your civil partner?')
    PARTNER_AGREES_MARRIED_QUESTION = _l('Can you provide a statutory declaration from your spouse?')

    PARTNER_DETAILS_CP_HEADER = _l("Your civil partner's details")
    PARTNER_DETAILS_MARRIED_HEADER = _l("Your spouse's details")
    PARTNER_DETAILS_CP_PARAGRAPH = _l("We will contact them about what to do if they change their mind about staying in"
                                      " a civil partnership.")
    PARTNER_DETAILS_MARRIED_PARAGRAPH = _l("We will contact them about what to do if they change their mind about"
                                           " staying married.")
    PARTNER_DETAILS_PARAGRAPH_2 = _l(" We will also let them know how their pensions and benefits may be affected if "
                                     "you receive a Gender Recognition Certificate.")

    PARTNER_DETAILS_CYA_STAY_TOGETHER_MARRIED = _l("Remain married")
    PARTNER_DETAILS_CYA_STAY_TOGETHER_CP = _l("Remain in your civil partnership")
    PARTNER_DETAILS_CYA_PARTNER_MARRIED_CAPITALISED = _l("Spouse's name")
    PARTNER_DETAILS_CYA_PARTNER_CP_CAPITALISED = _l("Civil partner's name")
    PARTNER_DETAILS_CYA_PARTNER_MARRIED_CAPITALISED_ADDRESS = _l("Spouse's postal address")
    PARTNER_DETAILS_CYA_PARTNER_CP_CAPITALISED_ADDRESS = _l("Civil partner's postal address")
    PARTNER_DETAILS_CYA_PARTNER_MARRIED_AGREES = _l("Can provide a declaration of consent from your spouse")
    PARTNER_DETAILS_CYA_PARTNER_CP_AGREES = _l("Can provide a declaration of consent from your civil partner")

    INTERIM_P1_CP = _l('When you apply for a certificate, your civil partner needs to sign a document if you want to'
                       ' stay in a civil partnership.')
    INTERIM_P2_CP = _l("If they do not sign the document, or you’re ending the civil partnership, you will get an"
                       " ‘interim’ certificate if you continue with your application.")
    INTERIM_P3_CP = _l("You can only use the interim certificate to end your civil partnership.")
    INTERIM_P5_CP = _l("You will get a full certificate once you’re no longer in a civil partnership.")
    INTERIM_P1_MARRIED = _l('When you apply for a certificate, your spouse needs tosign a document if you want to'
                            ' stay married.')
    INTERIM_P2_MARRIED = _l("If they do not sign the document, or you’re ending the marriage, you will get an ‘interim’"
                            " certificate if you continue with your application.")
    INTERIM_P3_MARRIED = _l("You can only use the interim certificate to end your marriage.")
    INTERIM_P5_MARRIED = _l("You will get a full certificate once you’re no longer married.")
    INTERIM_P4 = _l("You have 6 months to apply for an annulment, divorce or dissolution from when you get your"
                    " interim certificate.")

    # Errors
    STAY_MARRIED_OR_IN_CIVIL_PARTNERSHIP_ERROR = _l('Select if you plan to remain married or in your civil partnership'
                                                    ' after receiving your Gender Recognition Certificate')
    PARTNER_AGREES_ERROR = _l('Select if you can provide a declaration of consent from your spouse or civil partner')
    PARTNER_TITLE_ERROR = _l("Enter your spouse or civil partner's title")
    PARTNER_FIRST_NAME_ERROR = _l("Enter your spouse or civil partner's first name")
    PARTNER_LAST_NAME_ERROR = _l("Enter your spouse or civil partner's last name")
    PARTNER_POSTCODE_ERROR = _l("Enter your spouse or civil partner's postal address")

    PARTNER_DIED_ERROR = _l('Select if you were previously married or in a civil partnership, and your spouse or'
                            ' partner died')

    PARTNERSHIP_ENDED_ERROR = _l('Select if you have ever been married or in a civil partnership that has ended')
