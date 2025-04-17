import os
import asyncio
from playwright.async_api import async_playwright

from tests.end_to_end_tests.helpers.e2e_admin_helpers import AdminHelpers
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_admin.login_and_confirmation.section as section_login_and_confirmation
import tests.end_to_end_tests.journey_admin.applications_glimr.section as section_applications_glimr
import tests.end_to_end_tests.journey_admin.data as data
from grc.utils.security_code import delete_all_user_codes

TEST_URL = os.getenv('ADMIN_TEST_URL', 'http://grc_admin:3001')

def e2e_test_prerequisites():
    # Require security code to be entered
    delete_all_user_codes(data.EMAIL_ADDRESS)


async def run_script_for_browser(browser_type):
    browser = await browser_type.launch()
    page = await browser.new_page()
    page.set_default_timeout(data.DEFAULT_TIMEOUT)

    helpers = PageHelpers(page)
    asserts = AssertHelpers(page, helpers, TEST_URL)
    admin_helpers = AdminHelpers(page)

    e2e_test_prerequisites()

    # Open login page
    await page.goto(TEST_URL)

    # ------------------------------------------------
    # ---- LOGIN / CONFIRMATION section
    # ------------------------------------------------
    await section_login_and_confirmation.run_checks_on_section(page, asserts, helpers)

    # ------------------------------------------------
    # ---- Applications section
    # ------------------------------------------------
    await section_applications_glimr.run_checks_on_section(page, asserts, helpers, admin_helpers)




async def e2e_main():
    print("")  # Blank line to improve formatting

    async with async_playwright() as p:
        for browser_type in [p.chromium]: #, p.firefox, p.webkit]:
            await run_script_for_browser(browser_type)

def test_e2e_journey_admin(app):
    with app.app_context():
        asyncio.run(e2e_main())

