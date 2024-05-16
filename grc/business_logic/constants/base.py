from flask_babel import lazy_gettext as _l


class BaseConstants:
    YES = _l('Yes')
    NO = _l('No')
    DONT_KNOW = _l("I don't know")
    MARRIED = _l('Married')
    CIVIL_PARTNERSHIP = _l('Civil partnership')
    NEITHER = _l('Neither')
    APPROVED_COUNTRIES = (
        _l('Australia – not including the external territories'),
        _l('Austria'),
        _l('Belgium'),
        _l('Bulgaria'),
        _l('Canada – not including Northwest Territories and Nunavut'),
        _l('Croatia'),
        _l('Cyprus'),
        _l('Czech Republic'),
        _l('Denmark'),
        _l('Estonia'),
        _l('Finland'),
        _l('France'),
        _l('Germany'),
        _l('Greece'),
        _l('Iceland'),
        _l('Italy'),
        _l('Japan'),
        _l('Liechtenstein'),
        _l('Luxembourg'),
        _l('Malta'),
        _l('Federal District of Mexico'),
        _l('Moldova'),
        _l('Netherlands'),
        _l('New Zealand'),
        _l('Norway'),
        _l('Poland'),
        _l('Romania'),
        _l('Russian Federation'),
        _l('Serbia'),
        _l('Singapore'),
        _l('Slovakia'),
        _l('Slovenia'),
        _l('South Africa'),
        _l('South Korea'),
        _l('Spain'),
        _l('Sweden'),
        _l('Switzerland'),
        _l('Turkey'),
        _l('Ukraine'),
        _l('United States of America – not including Idaho, Ohio, Tennessee and Texas'),
        _l('Uruguay')
    )

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
    GENDER_RECOGNITION_OUTSIDE_UK_ERROR = _l('Select if you have ever been issued a Gender Recognition Certificate')
    DECLARATION_ERROR = _l('You must consent to the General Register Office contacting you')
    GENDER_RECOGNITION_IN_APPROVED_COUNTRY_ERROR = _l('Select if you have official documentation')
    ENTER_DAY_ERROR = _l('Enter a day')
    ENTER_VALID_DAY_ERROR = _l('Enter a day as a number between 1 and 31')
    ENTER_MONTH_ERROR = _l('Enter a month')
    ENTER_VALID_MONTH_ERROR = _l('Enter a month as a number between 1 and 12')
    ENTER_YEAR_ERROR = _l('Enter a year')
    INVALID_YEAR_ERROR = _l('Enter a valid year')
    ENTER_VALID_DATE_ERROR = _l('Enter a valid date')
    ENTER_VALID_YEAR_ERROR = _l('Enter a year as a 4-digit number, like 2000')
    DATE_BEFORE_EARLIEST_ERROR = _l('Enter a date within the last 100 years')
    ENTER_DATE_IN_PAST_ERROR = _l('Enter a date in the past')
    ENTER_DATE_IN_FUTURE_ERROR = _l('Enter a date in the future')
    ENTER_DATE_2_YEARS_BEFORE_APP_CREATED_ERROR = _l('Enter a date at least 2 years before your application')
    ENTER_DAY_ERROR = _l('Enter a day')
    ENTER_VALID_DAY_ERROR = _l('Enter a day as a number between 1 and 31')
    STAT_DEC_DATE_BEFORE_TRANSITION_DATE_ERROR = _l('Enter a date that does not precede your transition date')
    CONTACT_FROM_DATE_IN_PAST_ERROR = _l("'From' date is in the past")
    CONTACT_TO_DATE_IN_PAST_ERROR = _l("'To' date is in the past")
    CONTACT_FROM_DATE_AFTER_TO_DATE_ERROR = _l("'From' date is after the 'To' date")
    ADDRESS_ERROR = _l('Enter your address')
    ADDRESS_NO_TOWN_ERROR = _l('Enter your town or city')
    ADDRESS_LINE_ONE_ERROR = _l('Enter a valid address line one')
    ADDRESS_LINE_TWO_ERROR = _l('Enter a valid address line two')
    ADDRESS_TOWN_OR_CITY_ERROR = _l('Enter a valid town')
    NO_POSTCODE_ERROR = _l('Enter your postcode')
    ENTER_VALID_POSTCODE_ERROR = _l('Enter a valid postcode')
    NO_PHONE_NUMBER_ERROR = _l('Enter your phone number')
    ENTER_VALID_PHONE_NUMBER_ERROR = _l('Enter a valid phone number')
    ENTER_NI_NUMBER_ERROR = _l('Enter your National Insurance number')
    ENTER_VALID_NI_NUMBER_ERROR = _l('Enter a valid National Insurance number')
    ABOVE_AGE_ERROR = _l('You need to be at least 18 years old to apply')
    BELOW_AGE_ERROR = _l('You need to be less than 110 years old to apply')
    DATE_OF_BIRTH_BEFORE_TRANSITION_ERROR = _l('Your date of birth must be before your transition date and statutory '
                                               'declaration date')
    FILE_EMPTY_ERROR = _l('The selected file is empty. Check that the file you are uploading has the content you expect')
    FILE_SIZE_LIMIT_ERROR = _l('The selected file must be smaller than 10MB')
    VIRUS_SCANNER_ERROR = _l('Unable to communicate with virus scanner')
    FILE_HAS_VIRUS_ERROR = _l('The selected file contains a virus')
    INVALID_HWF_REFERENCE_NUMBER = _l('Enter a valid \'Help with fees\' reference number')