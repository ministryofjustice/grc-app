from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):
    # ------------------------------------------------
    # ---- Homepage / Email address page
    # ------------------------------------------------
    await asserts.url('/')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__link--service-name') == 'Apply for a Gender Recognition Certificate'
    await asserts.h1('Email address')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/')
    await asserts.accessibility()
    await helpers.click_button('Cymraeg')
    assert await page.inner_text('a.govuk-header__link.govuk-header__link--service-name') == 'Gwneud cais am Dystysgrif Cydnabod Rhywedd'
    await asserts.h1('Cyfeiriad e-bost')

    # Enter a valid Email Address, click Continue button, see the Security Code page
    await helpers.fill_textbox(field='email', value=data.EMAIL_ADDRESS)
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Security Code page
    # ------------------------------------------------
    await asserts.url('/security-code')
    await asserts.accessibility()
    await asserts.h1('Rhowch cod diogelwch')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/security-code')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Enter security code')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Rhowch cod diogelwch')

    # Enter a valid Security Code, click Continue button
    await helpers.fill_textbox(field='security_code', value='11111')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Is First Visit page
    # ------------------------------------------------
    await asserts.url('/is-first-visit')
    await asserts.accessibility()
    await asserts.h1('Have you already started an application?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/is-first-visit')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Have you already started an application?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Have you already started an application?')

    # Choose the "No" (this is my first visit) option
    await helpers.check_radio(field='isFirstVisit', value='FIRST_VISIT')
    await helpers.click_button('Parhau')
