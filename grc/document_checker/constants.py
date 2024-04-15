from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class DocumentCheckerConstants(BaseConstants):

    STAT_DEC_MARRIED_APPLICANTS_SUMMARY = _l('Statutory declaration for applicants who are married')
    STAT_DEC_APPLICANTS_CIVIL_PARTNERSHIP_SUMMARY = _l(
        'Statutory declaration for applicants who are in a civil partnership')
    STAT_DEC_SPOUSE_SUMMARY = _l('Your spouse’s statutory declaration')
    STAT_DEC_CIVIL_PARTNER_SUMMARY = _l('Your civil partner’s statutory declaration')
    STAT_DEC_SPOUSE_P1 = _l('If you intend to remain married, your spouse needs to fill in and sign a')
    STAT_DEC_SPOUSE_P2 = _l('If you are currently married and your spouse does not provide a statutory declaration of'
                            ' consent, or you do not plan to stay married, then you can still apply for a Gender'
                            ' Recognition Certificate without it, but you will be given an Interim Gender Recognition'
                            ' Certificate.')
    STAT_DEC_SPOUSE_P3 = _l('This can be used to end your marriage after which you’ll receive a full certificate')
    STAT_DEC_CIVIL_PARTNER_P1 = _l('If you intend to remain in a civil partnership, your civil partner needs to fill in'
                                   ' and sign a')
    STAT_DEC_CIVIL_PARTNER_P2 = _l('If you are currently in a civil partnership and your civil partner does not provide'
                                   ' a statutory declaration of consent, or you do not plan to stay in a civil'
                                   ' partnership, then you can still apply for a Gender Recognition Certificate without'
                                   ' it, but you will be given an Interim Gender Recognition Certificate.')
    STAT_DEC_CIVIL_PARTNER_P3 = _l('This can be used to end your civil partnership after which you’ll receive a full'
                                   ' certificate')
    PARTNER_MARRIAGE_CERT_SUMMARY = _l('Your marriage certificate')
    PARTNER_CP_CERT_SUMMARY = _l('Your civil partnership certificate')
    PARTNER_MARRIAGE_CERT_P1 = _l('Upload a scan or good quality photograph of your marriage certificate')
    PARTNER_CP_CERT_P1 = _l('Upload a scan or good quality photograph of your civil partnership certificate')

