from flask import g
from flask_babel import lazy_gettext as _l
from .base import BaseConstants
from grc.utils.link_builder import LinkBuilder


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

    @staticmethod
    def get_birth_cert_copy_link() -> str:
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = 'Anfonwch gopi gwreiddiol '
            link_text = 'neu ardystiedig (yn agor mewn tab newydd)'
            after_link_text = " o\'ch tystysgrif geni llawn neu dystysgrif mabwysiadu."
        else:
            before_link_text = 'Send an original or '
            link_text = 'certified copy (opens in a new tab)'
            after_link_text = ' of your full birth or adoption certificate.'
        anchor = '<a href="https://www.gov.uk/certifying-a-document" rel="external" target="_blank" class="govuk-link">'
        return LinkBuilder(anchor, link_text, before_link_text, after_link_text).get_link_with_text_safe()

    @staticmethod
    def get_birth_cert_uk_link() -> str:
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = 'Os cafodd eich genedigaeth neu eich mabwysiad ei chofrestru yn y DU, dewch o '
            link_text = 'hyd i wybodaeth am sut i archebu tystysgrif (yn agor mewn tab newydd)'
            after_link_text = ' os nad oes gennych un wrth law.'
        else:
            before_link_text = 'If your birth or adoption was registered in the UK, find out how to '
            link_text = 'order a certificate (opens in a new tab)'
            after_link_text = ' if you do not have it available.'
        anchor = '<a href="https://www.gov.uk/order-copy-birth-death-marriage-certificate" target="_blank" class="govuk-link">'
        return LinkBuilder(anchor, link_text, before_link_text, after_link_text).get_link_with_text_safe()

