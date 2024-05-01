from datetime import date
from dateutil.relativedelta import relativedelta

DEFAULT_TIMEOUT = 3 * 1000  # Wait a maximum of 3 seconds

EMAIL_ADDRESS = 'test.public.email@example.com'

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
