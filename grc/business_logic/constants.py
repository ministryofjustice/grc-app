from flask_babel import lazy_gettext as _l

YES = _l('Yes')
NO = _l('No')
MARRIED = _l('Married')
CIVIL_PARTNERSHIP = _l('Civil partnership')
NEITHER = _l('Neither')

# Questions
PLAN_TO_REMAIN_MARRIED = _l('Do you plan to remain married after you receive your Gender Recognition Certificate?')
PLAN_TO_REMAIN_IN_CIVIL_PARTNERSHIP = _l(
    'Do you plan to remain in your civil partnership after you receive your Gender Recognition Certificate?')

# Error messages
PREVIOUS_NAME_CHECK_ERROR = _l('Select if you have ever changed your name to reflect your gender')
CURRENTLY_MARRIED_OR_CIVIL_PARTNERSHIP_ERROR = _l('Select if you are currently married or in a civil partnership')
PREVIOUS_PARTNER_DIED_ERROR = _l(
    'Select if you ever been married or in a civil partnership where your spouse or partner died')
MARRIED_OR_CIVIL_PARTNERSHIP_ENDED_ERROR = _l(
    'Select if you have ever been married or in a civil partnership that has ended')
GENDER_RECOGNITION_IN_COUNTRY_ERROR = _l(
    'Select if you have received gender recognition in one of these countries or territories')
PLAN_TO_REMAIN_MARRIED_ERROR = _l(
    'Select if you plan to remain married after receiving your Gender Recognition Certificate')
