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
    def get_send_birth_cert_copy_link() -> str:
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = 'Anfonwch naill ai’r ddogfen wreiddiol neu '
            link_text = 'gopi ardystiedig (yn agor mewn tab newydd)'
            after_link_text = ' - bydd yn cael ei phostio’n ôl i chi.'
        else:
            before_link_text = 'Send either an original or a '
            link_text = 'certified copy (opens in a new tab)'
            after_link_text = ' – it will be posted back to you.'
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

    @staticmethod
    def get_send_ex160_link():
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = 'Mae hefyd angen i chi bostio '
            link_text = 'ffurflen EX160 (yn agor mewn tab newydd)'
        else:
            before_link_text = 'You also need to post an '
            link_text = 'EX160 form (opens in a new tab)'
        anchor = ('<a href="https://www.gov.uk/government/publications/apply-for-help-with-court-and-tribunal-fees '
                  'rel="external" target="_blank" class="govuk-link">')
        return LinkBuilder(anchor, link_text, before_link_text).get_link_with_text_safe()

    @staticmethod
    def get_copy_birth_death_marriage_cert_link():
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_link_text = 'Gallwch archebu '
            link_text = ('tystysgrif geni, tystysgrif marwolaeth, tystysgrif priodas neu dystysgrif partneriaeth sifil'
                         ' (yn agor mewn tab newydd)')
            after_link_text = ' ar-lein os ydych chi’n byw yng Nghymru a Lloegr.'
        else:
            before_link_text = 'You can '
            link_text = 'order a birth, death, marriage or civil partnership certificate (opens in a new tab)'
            after_link_text = 'online if you live in England and Wales.'
        anchor = ('<a href="https://www.gov.uk/order-copy-birth-death-marriage-certificate" target="_blank" '
                  'rel="external" class="govuk-link">')
        return LinkBuilder(anchor, link_text, before_link_text, after_link_text).get_link_with_text_safe()

    @staticmethod
    def get_scotland_and_northern_ireland_links():
        is_welsh = g.lang_code and g.lang_code == 'cy'
        if is_welsh:
            before_scotland_link_text = 'Mae’r broses ar gyfer cael '
            link_scotland_text = 'tystysgrifau yn wahanol yn yr Alban (yn agor mewn tab newydd)'
            after_scotland_link_text = ' ac '
            link_northern_ireland_text = 'yng Ngogledd Iwerddon (yn agor mewn tab newydd).'
        else:
            before_scotland_link_text = "There's a different process for "
            link_scotland_text = 'getting certificates in Scotland (opens in a new tab)'
            after_scotland_link_text = ' and '
            link_northern_ireland_text = 'getting certificates in Northern Ireland (opens in a new tab).'

        anchor_scotland = ('<a href="http://www.nrscotland.gov.uk/registration/how-to-order-an-official-extract-from-'
                           'the-registers" target="_blank" rel="external" class="govuk-link">')
        anchor_northern_ireland = ('<a href="http://www.nidirect.gov.uk/index/do-it-online/government-citizens-and-'
                                   'rights-online/order-a-birth-adoption-death-marriage-or-civil-partnership-certifica'
                                   'te.htm" target="_blank" rel="external" class="govuk-link">')

        link_scotland = LinkBuilder(
            anchor_scotland, link_scotland_text, before_scotland_link_text, after_scotland_link_text
        )
        link_northern_ireland = LinkBuilder(anchor_northern_ireland, link_northern_ireland_text)
        return link_scotland.get_link_with_text_safe() + link_northern_ireland.get_link_with_text_safe()
