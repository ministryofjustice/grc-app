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
