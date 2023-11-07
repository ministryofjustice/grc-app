from playwright.async_api import Page
from tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_3.data as data


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):
    # ------------------------------------------------
    # ---- Homepage / Email address page
    # ------------------------------------------------
    await asserts.url('/')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__link--service-name') == 'Apply for a Gender Recognition Certificate'
    await asserts.h1('Email address')
    await asserts.a("applying for a Gender Recognition Certificate (opens in a new tab)")
    await asserts.number_of_errors(0)

    # Don't enter an Email Address, click Continue button, see an error message
    await helpers.fill_textbox(field='email', value='')
    await helpers.click_button('Continue')
    await asserts.url('/')
    await asserts.accessibility(page_description='No email address entered')
    await asserts.h1('Email address')
    await asserts.number_of_errors(1)
    await asserts.error(field='email', message='Enter your email address')

    # Enter an invalid Email Address, click Continue button, see an error message
    await helpers.fill_textbox(field='email', value=data.INVALID_EMAIL_ADDRESS)
    await helpers.click_button('Continue')
    await asserts.url('/')
    await asserts.accessibility(page_description='Invalid email address entered')
    await asserts.h1('Email address')
    await asserts.number_of_errors(1)
    await asserts.error(field='email', message='Enter a valid email address')

    # Enter a valid Email Address, click Continue button, see the Security Code page
    await helpers.fill_textbox(field='email', value=data.EMAIL_ADDRESS)
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Security Code page
    # ------------------------------------------------
    await asserts.url('/security-code')
    await asserts.accessibility()
    await asserts.h1('Enter security code')
    await asserts.number_of_errors(0)

    # Don't enter a Security Code, click Continue button, see an error message
    await helpers.fill_textbox(field='security_code', value='')
    await helpers.click_button('Continue')
    await asserts.url('/security-code')
    await asserts.accessibility(page_description='No security code entered')
    await asserts.h1('Enter security code')
    await asserts.number_of_errors(1)
    await asserts.error(field='security_code', message='Enter a security code')

    # Enter an invalid Security Code, click Continue button, see an error message
    await helpers.fill_textbox(field='security_code', value='ABCD')  # Note: Don't use a 5-digit code, otherwise this test will break once every 10,000 runs!
    await helpers.click_button('Continue')
    await asserts.url('/security-code')
    await asserts.accessibility(page_description='Invalid security code entered')
    await asserts.h1('Enter security code')
    await asserts.number_of_errors(1)
    await asserts.error(field='security_code', message='Enter the security code that we emailed you')

    # Enter a valid Security Code, click Continue button
    await helpers.fill_textbox(field='security_code', value='11111')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Is First Visit page
    # ------------------------------------------------
    await asserts.url('/is-first-visit')
    await asserts.accessibility()
    await asserts.h1('Have you already started an application?')
    await asserts.find_radio_input(field='isFirstVisit', value='FIRST_VISIT')
    await asserts.find_radio_input(field='isFirstVisit', value='HAS_REFERENCE')
    await asserts.find_radio_input(field='isFirstVisit', value='LOST_REFERENCE')
    await asserts.number_of_errors(0)

    # Choose the "No" (this is my first visit) option
    await helpers.check_radio(field='isFirstVisit', value='FIRST_VISIT')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Reference Number page
    # ------------------------------------------------
    await asserts.url('/reference-number')
    await asserts.accessibility()
    await asserts.h1('Your reference number')
    await asserts.number_of_errors(0)