from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data
import os

TEST_URL = os.getenv('TEST_URL', 'http://localhost:5000')


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Click "Your personal details"
    await helpers.click_button('Eich manylion personol')

    # ------------------------------------------------
    # ---- Your Name page
    # ------------------------------------------------
    await asserts.url('/personal-details')
    await asserts.accessibility()
    await asserts.h1('Beth yw eich enw?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your name?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw eich enw?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='title', value=data.TITLE)
    await helpers.fill_textbox(field='first_name', value=data.FIRST_NAME)
    await helpers.fill_textbox(field='middle_names', value=data.MIDDLE_NAMES)
    await helpers.fill_textbox(field='last_name', value=data.LAST_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Affirmed Gender page
    # ------------------------------------------------
    await asserts.url('/personal-details/affirmed-gender')
    await asserts.accessibility()
    await asserts.h1('Beth yw eich rhywedd a gadarnhawyd?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/affirmed-gender')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your affirmed gender?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw eich rhywedd a gadarnhawyd?')

    # Choose an option, click Save and continue
    await helpers.check_radio(field='affirmedGender', value='MALE')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Transition Date page
    # ------------------------------------------------
    await asserts.url('/personal-details/transition-date')
    await asserts.accessibility()
    await asserts.h1('Pryd wnaethoch chi drawsnewid o un rhywedd i’r llall?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/transition-date')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('When did you transition?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Pryd wnaethoch chi drawsnewid o un rhywedd i’r llall?')

    # Enter a valid date
    await helpers.fill_textbox(field='transition_date_month', value=data.TRANSITION_DATE_MONTH)
    await helpers.fill_textbox(field='transition_date_year', value=data.TRANSITION_DATE_YEAR)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Statutory Declaration Date page
    # ------------------------------------------------
    await asserts.url('/personal-details/statutory-declaration-date')
    await asserts.accessibility()
    await asserts.h1('Pryd wnaethoch chi arwyddo eich Datganiad Statudol?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/statutory-declaration-date')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('When did you sign your statutory declaration?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Pryd wnaethoch chi arwyddo eich Datganiad Statudol?')

    # Enter a valid date
    await helpers.fill_textbox(field='statutory_declaration_date_day', value=data.STATUTORY_DECLARATION_DATE_DAY)
    await helpers.fill_textbox(field='statutory_declaration_date_month', value=data.STATUTORY_DECLARATION_DATE_MONTH)
    await helpers.fill_textbox(field='statutory_declaration_date_year', value=data.STATUTORY_DECLARATION_DATE_YEAR)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Previous Name Check page
    # ------------------------------------------------
    await asserts.url('/personal-details/previous-names-check')
    await asserts.accessibility()
    await asserts.h1('Os ydych chi erioed wedi newid eich enw i adlewyrchu eich rhywedd')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/previous-names-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('If you have ever changed your name to reflect your gender')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Os ydych chi erioed wedi newid eich enw i adlewyrchu eich rhywedd')

    # Choose an option, click Save and continue
    await helpers.check_radio(field='previousNameCheck', value='True')
    await helpers.click_button('Cadw a pharhau')
