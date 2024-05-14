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

    # Click "Submit and pay"
    await helpers.click_button('Cyflwyno a thalu')

    # ------------------------------------------------
    # ---- Payment page
    # ------------------------------------------------
    await asserts.url('/submit-and-pay')
    await asserts.accessibility()
    await asserts.h1('Talu')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/submit-and-pay')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Payment')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Talu')

    # Choose "Yes", option, click Save and continue
    await helpers.check_radio(field='applying_for_help_with_fee', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Applying For Help page
    # ------------------------------------------------
    await asserts.url('/submit-and-pay/help-type')
    await asserts.accessibility()
    await asserts.h1('Gwneud cais am help i dalu’r ffi')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/submit-and-pay/help-type')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Applying for help with the fee')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Gwneud cais am help i dalu’r ffi')

    # Enter a valid Help with Fees reference number
    await helpers.check_radio(field='how_applying_for_fees', value='USING_ONLINE_SERVICE')
    await helpers.fill_textbox(field='help_with_fees_reference_number', value=data.HELP_WITH_FEES_REFERENCE_NUMBER)
    await helpers.click_button('Cadw a pharhau')
