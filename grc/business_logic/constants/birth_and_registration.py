from flask_babel import lazy_gettext as _l, pgettext, lazy_pgettext
from flask_babel.speaklater import LazyString
from .base import BaseConstants


class BirthRegistrationConstants(BaseConstants):

    YES_ADOPTED_UK = lazy_pgettext('BIRTH_DETS_ADOPTED', 'Yes')
    NO_ADOPTED_UK = lazy_pgettext('BIRTH_DETS_ADOPTED', 'No')
    YES_FORCES_REGISTERED = lazy_pgettext('BIRTH_DETS_FORCES', 'Yes')
    NO_FORCES_REGISTERED = lazy_pgettext('BIRTH_DETS_FORCES', 'No')

    # Error messages
    FIRST_NAME_ERROR = _l('Enter your first name, as originally registered on your birth or adoption certificate')
    LAST_NAME_ERROR = _l('Enter your last name, as originally registered on your birth or adoption certificate')
    SELECT_BIRTH_REGISTERED_IN_UK_ERROR = _l('Select if your birth was registered in the UK')
    ENTER_COUNTRY_OF_BIRTH_ERROR = _l('Enter your country of birth')
    ENTER_PLACE_OF_BIRTH_ERROR = _l('Enter your town or city of birth')
    ENTER_MOTHERS_FIRST_NAME_ERROR = _l("Enter your first parent's first name")
    ENTER_MOTHERS_LAST_NAME_ERROR = _l("Enter your first parent's last name")
    ENTER_MOTHERS_MAIDEN_NAME_ERROR = _l("Enter your first parent's maiden name")
    SELECT_FATHERS_NAME_ON_CERTIFICATE_ERROR = _l("Select if your second parent's name is listed on the certificate")
    ENTER_FATHERS_FIRST_NAME_ERROR = _l("Enter your second parent's first name")
    ENTER_FATHERS_LAST_NAME_ERROR = _l("Enter your second parent's last name")
    ENTER_ADOPTED_ERROR = _l('Select if you were you adopted')
    SELECT_ADOPTED_UK_ERROR = _l('Select if you were adopted in the United Kingdom')
    SELECT_FORCES_ERROR = _l('Select if your birth was registered by a Forces registering service, or with a British '
                             'Consul or High Commission, or under Merchant Shipping or Civil Aviation provisions')
