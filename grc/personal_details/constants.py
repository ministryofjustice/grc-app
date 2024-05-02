from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class PersonalDetailsConstants(BaseConstants):
    MALE = _l('Male')
    FEMALE = _l('Female')
    SINGLE_DATE = _l('A single date')
    DATE_RANGE = _l('A range of dates')
    NO_DATES = _l('No dates')

    # Error messages
    TITLE_ERROR = _l('Enter your title')
    FIRST_NAME_ERROR = _l('Enter your first name(s)')
    LAST_NAME_ERROR = _l('Enter your last name')
    NO_AFFIRMED_GENDER_ERROR = _l('Select your affirmed gender')
    NO_CONTACT_DATES_OPTION_ERROR = _l("Select if you don't want us to contact you at any point in the next 6 months")
