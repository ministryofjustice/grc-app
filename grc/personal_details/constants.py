from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class PersonalDetailsConstants(BaseConstants):
    MALE = _l('Male')
    FEMALE = _l('Female')
    EMAIL = _l('Email')
    PHONE = _l('Phone call')
    POST = _l('Post')

    # Error messages
    TITLE_ERROR = _l('Enter your title')
    FIRST_NAME_ERROR = _l('Enter your first name(s)')
    LAST_NAME_ERROR = _l('Enter your last name')
    NO_AFFIRMED_GENDER_ERROR = _l('Select your affirmed gender')
    NO_CONTACT_PREFERENCES_ERROR = _l('Select how would you like to be contacted')
