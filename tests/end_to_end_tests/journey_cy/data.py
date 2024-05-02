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

# birth_registration
BIRTH_FIRST_NAME = 'John'
BIRTH_LAST_NAME = 'Doe'
TOWN_OR_CITY = 'London'

MOTHER_FIRST_NAME = 'Ruby'
MOTHER_LAST_NAME = 'Gem'
MOTHER_MAIDEN_NAME = 'Amy'

FATHER_FIRST_NAME = 'Mark'
FATHER_LAST_NAME = 'Smith'

COUNTRY_OF_BIRTH = 'China'
