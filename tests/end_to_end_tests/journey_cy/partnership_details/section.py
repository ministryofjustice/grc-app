from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Click "Marriage or civil partnership details" to go to the "Are You Married" page
    await helpers.click_button('Manylion eich priodas neu bartneriaeth sifil')

    # ------------------------------------------------
    # ---- Are You Married page
    # ------------------------------------------------
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await asserts.h1('Priodasau a phartneriaethau sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Marriages and civil partnerships')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Priodasau a phartneriaethau sifil')

    # Select "Married" option and proceed down this route until the "Check you answers" page
    # Then, re-trace our steps back here and choose the "Civil partnership" and then "Neither" options
    await helpers.check_radio(field='currently_married', value='MARRIED')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Stay Together page
    # ------------------------------------------------
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await asserts.h1("Ydych chi'n bwriadu parhau i briodi ar ôl cael eich Tystysgrif Cydnabod Rhywedd?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Do you plan to remain married after you receive your Gender Recognition Certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1("Ydych chi'n bwriadu parhau i briodi ar ôl cael eich Tystysgrif Cydnabod Rhywedd?")

    # Select the "Yes" option, go down that route
    # Then backtrack and choose "No"
    await helpers.check_radio(field='stay_together', value='True')
    await helpers.click_button('Cadw a pharhau')
