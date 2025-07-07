from flask_babel import lazy_gettext as _l, pgettext, lazy_pgettext
from flask_babel.speaklater import LazyString
from .base import BaseConstants


class OneLoginConstants(BaseConstants):

    NEW_APPLICATION = _l('Start a new application')
    EXISTING_APPLICATION = _l('Return to your existing application')
    YES_WITH_REFERENCE_NUMBER = _l('I have my reference number')
    YES_LOST_REFERENCE_NUMBER = _l('I have lost my reference number')

    # Error messages
    FIRST_NAME_ERROR = _l('Enter your first name, as originally registered on your birth or adoption certificate')
