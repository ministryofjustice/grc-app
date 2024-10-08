import os
import asyncio
from playwright.async_api import async_playwright
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data
import tests.end_to_end_tests.journey_cy.login_and_confirmation.section as section_login_and_confirmation
import tests.end_to_end_tests.journey_cy.personal_details.section as section_personal_details
import tests.end_to_end_tests.journey_cy.birth_registration.section as section_birth_registration
import tests.end_to_end_tests.journey_cy.partnership_details.section as section_partnership_details
import tests.end_to_end_tests.journey_cy.uploads.section as section_uploads
import tests.end_to_end_tests.journey_cy.submit_and_pay.section as section_submit_and_pay



"""
Happy path to test the welsh content is present when language is toggled.
"""

TEST_URL = os.getenv('TEST_URL', 'http://localhost:5000')
print('Running tests on %s' % TEST_URL)


async def run_script_for_browser(browser_type):
    browser = await browser_type.launch()
    page = await browser.new_page()
    page.set_default_timeout(data.DEFAULT_TIMEOUT)

    helpers = PageHelpers(page)
    asserts = AssertHelpers(page, helpers, TEST_URL)

    # Open homepage ("Email address")
    await page.goto(TEST_URL)

    # ------------------------------------------------
    # ---- LOGIN / CONFIRMATION section
    # ------------------------------------------------
    await section_login_and_confirmation.run_checks_on_section(page, asserts, helpers)

    # ------------------------------------------------
    # ---- PERSONAL DETAILS section
    # ------------------------------------------------
    await section_personal_details.run_checks_on_section(page, asserts, helpers)

    # ------------------------------------------------
    # ---- BIRTH REGISTRATION section
    # ------------------------------------------------
    await section_birth_registration.run_checks_on_section(page, asserts, helpers)

    # ------------------------------------------------
    # ---- PARTNERSHIP DETAILS section
    # ------------------------------------------------
    await section_partnership_details.run_checks_on_section(page, asserts, helpers)

    # ------------------------------------------------
    # ---- UPLOADS section
    # ------------------------------------------------
    await section_uploads.run_checks_on_section(page, asserts, helpers)

    # ------------------------------------------------
    # ---- SUBMIT AND PAY section
    # ------------------------------------------------
    await section_submit_and_pay.run_checks_on_section(page, asserts, helpers)

    # Tidy up
    await browser.close()
    asserts.run_final_accessibility_checks()


async def e2e_main():
    print("")  # Blank line to improve formatting
    async with async_playwright() as p:
        for browser_type in [p.chromium]: #, p.firefox, p.webkit]:
            await run_script_for_browser(browser_type)


def test_e2e_journey_cy():
    asyncio.run(e2e_main())
