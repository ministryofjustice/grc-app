from flask_babel import lazy_gettext as _l, lazy_pgettext
from .base import BaseConstants


class PersonalDetailsConstants(BaseConstants):

    YES_CONTACT_HMRC = lazy_pgettext('CONTACT_HMRC', 'Yes')
    NO_CONTACT_HMRC = lazy_pgettext('CONTACT_HMRC', 'No')

    MALE = _l('Male')
    FEMALE = _l('Female')
    SINGLE_DATE = _l('A single date')
    DATE_RANGE = _l('A range of dates')
    NO_DATES = _l('No dates')
    EMAIL = _l('Email')
    PHONE = _l('Phone call')
    POST = _l('Post')

    # Error messages
    TITLE_ERROR = _l('Enter your title')
    FIRST_NAME_ERROR = _l('Enter your first name(s)')
    LAST_NAME_ERROR = _l('Enter your last name')
    NO_AFFIRMED_GENDER_ERROR = _l('Select your affirmed gender')
    NO_CONTACT_DATES_OPTION_ERROR = _l("Select if you don't want us to contact you at any point in the next 6 months")
    NO_CONTACT_PREFERENCES_ERROR = _l('Select how would you like to be contacted')
    NO_HMRC_OPTION_ERROR = _l('Select if you would like us to tell HMRC after you receive a Gender Recognition Certificate')
