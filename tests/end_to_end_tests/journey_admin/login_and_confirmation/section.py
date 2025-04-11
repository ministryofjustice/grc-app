from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_admin.data as data



async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Login page
    # ------------------------------------------------
    await asserts.url('/')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'
    await asserts.h1('Login to download GRC applications')
    await asserts.number_of_errors(0)

    # Don't enter an Email Address or password, click Continue button, see an error message
    await helpers.fill_textbox(field='email_address', value='')
    await helpers.fill_textbox(field='password', value='')
    await helpers.click_button('Login')
    await asserts.url('/')
    await asserts.accessibility(page_description='No email address or password entered')
    await asserts.h1('Login to download GRC applications')
    await asserts.number_of_errors(2)
    await asserts.error(field='email_address', message='Enter your email address')
    await asserts.error(field='password', message='Enter your password')

    # Enter a valid Email Address, click Continue button, see the Security Code page
    await helpers.fill_textbox(field='email_address', value=data.EMAIL_ADDRESS)
    await helpers.fill_textbox(field='password', value=data.PASSWORD)
    await helpers.click_button('Login')

    # ------------------------------------------------
    # ---- Security Code page
    # ------------------------------------------------
    await asserts.url('/sign-in-with-security_code')
    await asserts.accessibility()
    await asserts.h1('Check your email')
    await asserts.number_of_errors(0)

# Don't enter a Security Code, click Continue button, see an error message
    await helpers.fill_textbox(field='security_code', value='')
    await helpers.click_button('Continue')
    await asserts.url('/sign-in-with-security_code')
    await asserts.accessibility(page_description='No security code entered')
    await asserts.h1('Check your email')
    await asserts.number_of_errors(1)
    await asserts.error(field='security_code', message='Enter a security code')

    # Enter an invalid Security Code, click Continue button, see an error message
    await helpers.fill_textbox(field='security_code', value='4444')  # Note: Don't use a 5-digit code, otherwise this test will break once every 10,000 runs!
    await helpers.click_button('Continue')
    await asserts.url('/sign-in-with-security_code')
    await asserts.accessibility(page_description='Invalid security code entered')
    await asserts.h1('Check your email')
    await asserts.number_of_errors(1)
    await asserts.error(field='security_code', message='Enter the security code that we emailed you')

    # Enter a valid Security Code, click Continue button
    await helpers.fill_textbox(field='security_code', value='11111')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Is First Visit page
    # ------------------------------------------------
    await asserts.url('/applications')
    await asserts.accessibility()
    await asserts.h1('View and download GRC applications')
    await asserts.number_of_errors(0)