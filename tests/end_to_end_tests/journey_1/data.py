from datetime import date
from dateutil.relativedelta import relativedelta
import os

DEFAULT_TIMEOUT = 3 * 1000  # Wait a maximum of 3 seconds
TIMEOUT_FOR_SLOW_OPERATIONS = 30 * 1000  # For slow operations, wait a maximum of 30 seconds


EMAIL_ADDRESS = 'ivan.touloumbadjian@hmcts.net'
DIFFERENT_EMAIL_ADDRESS = os.environ.get('DEFAULT_ADMIN_USER', 'matthew.sellings@hmcts.net')

TITLE = 'Mr'
FIRST_NAME = 'Joseph'
MIDDLE_NAMES = 'Adam Brian'
LAST_NAME = 'Bloggs'

ADDRESS_LINE_ONE = '16-20'
ADDRESS_LINE_ONE_INVALID = '16-20$'
ADDRESS_LINE_TWO = 'Great Smith Street'
TOWN = 'London'
POSTCODE = 'SW1P 3BT'

TRANSITION_DATE_MONTH = '3'
TRANSITION_DATE_YEAR = str((date.today() - relativedelta(years=3)).year)

# These 2 ensure invalid date is created for this journey
invalid_date = date.today() - relativedelta(years=1, months=11)
TRANSITION_DATE_MONTH_ERROR = str(invalid_date.month)
TRANSITION_DATE_YEAR_ERROR = str(invalid_date.year)

TRANSITION_DATE_FORMATTED = f'March {TRANSITION_DATE_YEAR}'

# Valid date after transition date
STATUTORY_DECLARATION_DATE_DAY = '5'
STATUTORY_DECLARATION_DATE_MONTH = '3'
STATUTORY_DECLARATION_DATE_YEAR = str((date.today() - relativedelta(years=1)).year)

# This ensure invalid date is created before transition date
TRANSITION_DATE_MONTH_MINUS_ONE = '2'

STATUTORY_DECLARATION_DATE_FORMATTED = f'05 March {STATUTORY_DECLARATION_DATE_YEAR}'

CONTACT_DATE_SINGLE_DAY = '5'
CONTACT_DATE_SINGLE_MONTH = '5'
CONTACT_DATE_SINGLE_YEAR = str((date.today() + relativedelta(years=1)).year)

CONTACT_DATE_RANGE_1_FROM_DAY = '5'
CONTACT_DATE_RANGE_1_FROM_MONTH = '5'
CONTACT_DATE_RANGE_1_FROM_YEAR = str((date.today() + relativedelta(years=1)).year)

CONTACT_DATE_RANGE_1_TO_DAY = '5'
CONTACT_DATE_RANGE_1_TO_MONTH = '6'
CONTACT_DATE_RANGE_1_TO_YEAR = str((date.today() + relativedelta(years=1)).year)

CONTACT_DATE_RANGE_2_FROM_DAY = '6'
CONTACT_DATE_RANGE_2_FROM_MONTH = '6'
CONTACT_DATE_RANGE_2_FROM_YEAR = str((date.today() + relativedelta(years=1)).year)

CONTACT_DATE_RANGE_2_TO_DAY = '6'
CONTACT_DATE_RANGE_2_TO_MONTH = '7'
CONTACT_DATE_RANGE_2_TO_YEAR = str((date.today() + relativedelta(years=1)).year)

# DATES_TO_AVOID = '1st June - 2nd July\n3rd August - 4th September'
DATES_TO_AVOID = f'From 05/05/{CONTACT_DATE_RANGE_1_FROM_YEAR} to 05/06/{CONTACT_DATE_RANGE_1_TO_YEAR}'

PHONE_NUMBER = '07700900000'

NATIONAL_INSURANCE_NUMBER = 'AB123456C'

BIRTH_FIRST_NAME = 'Joanna'
BIRTH_MIDDLE_NAME = 'Mary'
BIRTH_LAST_NAME = 'Bloggs'

DATE_OF_BIRTH_DAY = '3'
DATE_OF_BIRTH_MONTH = '4'
DATE_OF_BIRTH_YEAR = '1956'
DATE_OF_BIRTH_FORMATTED = '03 April 1956'

BIRTH_COUNTRY = 'France'
BIRTH_TOWN = 'London'

MOTHERS_FIRST_NAME = 'Margaret'
MOTHERS_LAST_NAME = 'Bloggs'
MOTHERS_MAIDEN_NAME = 'Jones'

FATHERS_FIRST_NAME = 'Norman'
FATHERS_LAST_NAME = 'Bloggs'

PARTNER_TITLE = 'Ms'
PARTNER_FIRST_NAME = 'Sam'
PARTNER_LAST_NAME = 'Jones'
PARTNER_POSTAL_ADDRESS = '10 Victoria Street\nLondon\nSW1H 0NB'

HELP_WITH_FEES_REFERENCE_NUMBER = 'HWF-123-ABC'
