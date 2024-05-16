from flask import g
from flask_babel import lazy_gettext as _l
from .base import BaseConstants
from grc.utils.link_builder import LinkBuilder


class SubmitAndPayConstants(BaseConstants):
    NO_PAY_NOW = _l('No, I will pay now')
    ONLINE_SERVICE = _l('Using the online service')
    EX160_FORM = _l('Using the EX160 form')
    HELP = _l('Help')
    ONLINE = _l('Online')
    GOV_PAY_SERVICE_DESCRIPTION = _l('Pay for Gender Recognition Certificate')

    # Errors
    HWF_ERROR = _l('Select if you are applying for help paying the fee')
    HWF_OPTION_ERROR = _l('Select how are you applying for help paying the fee')
    HWF_REFERENCE_NUMBER_ERROR = _l('Enter your Help with Fees reference number')
    CORRECT_INFO_DECLARATION_ERROR = _l('You must certify that all information given in this application is correct'
                                        ' and that you understand making a false application is an offence.')

    @staticmethod
    def get_birth_cert_copy_link() -> str:
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = 'copi gwreiddiol neu '
            link_text = 'gopi ardystiedig (yn agor mewn tab newydd)'
            after_link_text = ' o’ch tystysgrif geni llawn neu dystysgrif mabwysiadu'
        else:
            before_link_text = 'your original or a '
            link_text = 'certified copy (opens in a new tab)'
            after_link_text = ' of your full birth or adoption certificate'
        anchor = '<a href="https://www.gov.uk/certifying-a-document" rel="external" target="_blank" class="govuk-link">'
        return LinkBuilder(anchor, link_text, before_link_text, after_link_text).get_link_with_text_safe()

    @staticmethod
    def get_ex160_link():
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = ''
            link_text = 'ffurflen EX160 (yn agor mewn tab newydd)'
        else:
            before_link_text = 'an'
            link_text = 'EX160 form (opens in a new tab)'
        anchor = ('<a href="https://www.gov.uk/government/publications/apply-for-help-with-court-and-tribunal-fees '
                  'rel="external" target="_blank" class="govuk-link">')
        return LinkBuilder(anchor, link_text, before_link_text).get_link_with_text_safe()
