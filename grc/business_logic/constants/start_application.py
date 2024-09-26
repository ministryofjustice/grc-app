from flask_babel import lazy_gettext as _l
from .base import BaseConstants


class StartApplicationConstants(BaseConstants):
    YES_WITH_REFERENCE_NUMBER = _l('Yes, and I have my reference number')
    YES_LOST_REFERENCE_NUMBER = _l('Yes, but I have lost my reference number')