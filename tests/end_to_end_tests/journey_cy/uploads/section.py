from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.uploads.page_overseas_documents as page_overseas_documents
import tests.end_to_end_tests.journey_cy.uploads.page_statutory_declarations as page_statutory_declarations


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Overseas Documents page
    # ------------------------------------------------
    await page_overseas_documents.run_checks_on_page(page, asserts, helpers)

    # ------------------------------------------------
    # ---- Statutory Declarations page
    # ------------------------------------------------
    await page_statutory_declarations.run_checks_on_page(page, asserts, helpers)
