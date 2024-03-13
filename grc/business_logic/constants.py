from flask_babel import lazy_gettext as _l


YES = _l('Yes')
NO = _l('No')
MARRIED = _l('Married')
CIVIL_PARTNERSHIP = _l('Civil partnership')
NEITHER = _l('Neither')

# Error messages
PREVIOUS_NAME_CHECK_ERROR = _l('Select if you have ever changed your name to reflect your gender')
CURRENTLY_MARRIED_OR_CIVIL_PARTNERSHIP_ERROR = _l('Select if you are currently married or in a civil partnership')
PREVIOUS_PARTNER_DIED_ERROR = _l('Select if you ever been married or in a civil partnership where '
                                 'your spouse or partner died')
