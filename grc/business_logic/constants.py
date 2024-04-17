from flask_babel import lazy_gettext as _l


class BaseConstants:
    YES = _l('Yes')
    NO = _l('No')
    MARRIED = _l('Married')
    CIVIL_PARTNERSHIP = _l('Civil partnership')
    NEITHER = _l('Neither')

    # Questions
    PLAN_TO_REMAIN_MARRIED = _l('Do you plan to remain married after you receive your Gender Recognition Certificate?')
    PLAN_TO_REMAIN_IN_CIVIL_PARTNERSHIP = _l(
        'Do you plan to remain in your civil partnership after you receive your Gender Recognition Certificate?')

    # Flash messages
    RESEND_SECURITY_CODE = _l("We’ve resent you a security code. This can take a few minutes to arrive")

    # Error messages
    PREVIOUS_NAME_CHECK_ERROR = _l('Select if you have ever changed your name to reflect your gender')
    CURRENTLY_MARRIED_OR_CIVIL_PARTNERSHIP_ERROR = _l('Select if you are currently married or in a civil partnership')
    PREVIOUS_PARTNER_DIED_ERROR = _l(
        'Select if you have ever been married or in a civil partnership where your spouse or partner died')
    MARRIED_OR_CIVIL_PARTNERSHIP_ENDED_ERROR = _l(
        'Select if you have ever been married or in a civil partnership that has ended')
    GENDER_RECOGNITION_IN_COUNTRY_ERROR = _l(
        'Select if you have received gender recognition in one of these countries or territories')
    PLAN_TO_REMAIN_MARRIED_ERROR = _l(
        'Select if you plan to remain married after receiving your Gender Recognition Certificate')
    NO_EMAIL_ADDRESS_ERROR = _l('Enter your email address')
    EMAIL_ADDRESS_INVALID_ERROR = _l('Enter a valid email address')
    NO_SECURITY_CODE = _l('Enter a security code')
    INVALID_SECURITY_CODE = _l('Enter the security code that we emailed you')
    IS_FIRST_VISIT_ERROR = _l('Select if you have already started an application')
    NO_REFERENCE_NUMBER_ERROR = _l('Enter a reference number')
    INVALID_REFERENCE_NUMBER_ERROR = _l('Enter a valid reference number')
    GENDER_RECOGNITION_OUTSIDE_UK_ERROR = _l('Select if you ever been issued a Gender Recognition Certificate')
