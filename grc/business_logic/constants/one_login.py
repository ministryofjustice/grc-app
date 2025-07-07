from flask_babel import lazy_gettext as _l
from .base import BaseConstants


class OneLoginConstants(BaseConstants):

    NEW_APPLICATION = _l('Start a new application')
    EXISTING_APPLICATION = _l('Return to your existing application')
    YES_WITH_REFERENCE_NUMBER = _l('I have my reference number')
    YES_LOST_REFERENCE_NUMBER = _l('I have lost my reference number')

