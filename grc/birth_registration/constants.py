from flask_babel import lazy_gettext as _l
from grc.business_logic.constants import BaseConstants


class BirthRegistrationConstants(BaseConstants):

    # Error messages
    FIRST_NAME_ERROR = _l('Enter your first name, as originally registered on your birth or adoption certificate')
    LAST_NAME_ERROR = _l('Enter your last name, as originally registered on your birth or adoption certificate')
    SELECT_BIRTH_REGISTERED_IN_UK_ERROR = _l('Select if your birth was registered in the UK')
    ENTER_COUNTRY_OF_BIRTH_ERROR = _l('Enter your country of birth')
    ENTER_PLACE_OF_BIRTH_ERROR = _l('Enter your town or city of birth')
    ENTER_MOTHERS_FIRST_NAME_ERROR = _l("Enter your mother's first name")
    ENTER_MOTHERS_LAST_NAME_ERROR = _l("Enter your mother's last name")
    ENTER_MOTHERS_MAIDEN_NAME_ERROR = _l("Enter your mother's maiden name")
    SELECT_FATHERS_NAME_ON_CERTIFICATE_ERROR = _l("Select if your father's name is listed on the certificate")
    ENTER_FATHERS_FIRST_NAME_ERROR = _l("Enter your father's first name")
    ENTER_FATHERS_LAST_NAME_ERROR = _l("Enter your father's last name")
    ENTER_ADOPTED_ERROR = _l('Select if you were you adopted')
    SELECT_ADOPTED_UK_ERROR = _l('Select if you were adopted in the United Kingdom')
    SELECT_FORCES_ERROR = _l('Select if your birth was registered by a Forces registering service, or with a British '
                             'Consul or High Commission, or under Merchant Shipping or Civil Aviation provisions')
    ABOVE_AGE_ERROR = _l('You need to be at least 18 years old to apply')
    BELOW_AGE_ERROR = _l('You need to be less than 110 years old to apply')
    DATE_OF_BIRTH_BEFORE_TRANSITION_ERROR = _l('Your date of birth must be before your transition date and statutory '
                                               'declaration date')
