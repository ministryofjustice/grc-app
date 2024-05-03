from datetime import date
from dateutil.relativedelta import relativedelta

DEFAULT_TIMEOUT = 3 * 1000  # Wait a maximum of 3 seconds

EMAIL_ADDRESS = 'test.public.email@example.com'
PHONE_NUMBER = '07700900000'

TITLE = 'Mr'
FIRST_NAME = 'Joseph'
MIDDLE_NAMES = 'Adam Brian'
LAST_NAME = 'Bloggs'

TRANSITION_DATE_MONTH = '3'
TRANSITION_DATE_YEAR = str((date.today() - relativedelta(years=3)).year)
TRANSITION_DATE_FORMATTED = f'March {TRANSITION_DATE_YEAR}'

STATUTORY_DECLARATION_DATE_DAY = '5'
STATUTORY_DECLARATION_DATE_MONTH = '3'
STATUTORY_DECLARATION_DATE_YEAR = str((date.today() - relativedelta(years=2)).year)
STATUTORY_DECLARATION_DATE_FORMATTED = f'05 March {STATUTORY_DECLARATION_DATE_YEAR}'

ADDRESS_LINE_ONE = '16-20'
ADDRESS_LINE_TWO = 'Great Smith Street'
TOWN = 'London'
POSTCODE = 'SW1P 3BT'

CONTACT_DATE_RANGE_1_FROM_DAY = '5'
CONTACT_DATE_RANGE_1_FROM_MONTH = '5'
CONTACT_DATE_RANGE_1_FROM_YEAR = str((date.today() + relativedelta(years=1)).year)

CONTACT_DATE_RANGE_1_TO_DAY = '5'
CONTACT_DATE_RANGE_1_TO_MONTH = '6'
CONTACT_DATE_RANGE_1_TO_YEAR = str((date.today() + relativedelta(years=1)).year)

NATIONAL_INSURANCE_NUMBER = 'AB123456C'
