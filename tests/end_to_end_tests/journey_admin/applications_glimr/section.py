from playwright.async_api import Page

from grc.start_application import reference
from grc.utils.reference_number import reference_number_is_valid
from tests.end_to_end_tests.helpers.e2e_admin_helpers import AdminHelpers
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_admin.data as data



async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers, admin_helpers: AdminHelpers):

    # ------------------------------------------------
    # ---- Applications page
    # ------------------------------------------------
    await asserts.url('/applications')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'
    await asserts.h1('View and download GRC applications')
    await asserts.number_of_errors(0)

    # ------------------------------------------------
    # ---- Extract top three table applications
    # ------------------------------------------------
    await page.wait_for_selector("table")

    top_two_rows = await admin_helpers.get_top_rows(2)
    first_row, second_row = top_two_rows

    first_row_reference_number = await admin_helpers.get_row_reference_number(first_row)
    second_row_reference_number = await admin_helpers.get_row_reference_number(second_row)

    # ------------------------------------------------
    # ---- Ensure all are not GLiMR case registered
    # ------------------------------------------------
    await asserts.check_case_is_not_registered(reference_number=first_row_reference_number)
    await asserts.not_checked(field=first_row_reference_number)

    await asserts.check_case_is_not_registered(reference_number=second_row_reference_number)
    await asserts.not_checked(field=second_row_reference_number)

    await asserts.button_disabled(field="submit-selected-apps-btn-new")

    # ------------------------------------------------
    # ---- Select all for new case registration
    # ------------------------------------------------
    await helpers.click_button(link_text="Select all for new case registration")
    await asserts.is_checked(field=first_row_reference_number)
    await asserts.is_checked(field=second_row_reference_number)
    await asserts.button_enabled(field="submit-selected-apps-btn-new")

    # ------------------------------------------------
    # ---- Clear all for new case registration
    # ------------------------------------------------
    await helpers.click_button(link_text="Clear all for new case registration")
    await asserts.not_checked(field=first_row_reference_number)
    await asserts.not_checked(field=second_row_reference_number)
    await asserts.button_disabled(field="submit-selected-apps-btn-new")

    # ------------------------------------------------
    # ---- Select and deselect for case registration
    # ------------------------------------------------
    for row_reference_number in [first_row_reference_number, second_row_reference_number]:
        await helpers.check_checkbox(field=row_reference_number)
        await asserts.is_checked(field=row_reference_number)
        await asserts.button_enabled(field="submit-selected-apps-btn-new")
        await helpers.uncheck_checkbox(field=row_reference_number)
        await asserts.not_checked(field=row_reference_number)
        await asserts.button_disabled(field="submit-selected-apps-btn-new")

    # ------------------------------------------------
    # ---- Submit applications to GLiMR
    # ------------------------------------------------
    await helpers.check_checkbox(field=first_row_reference_number)
    await helpers.check_checkbox(field=second_row_reference_number)
    await asserts.is_checked(field=first_row_reference_number)
    await asserts.is_checked(field=second_row_reference_number)
    await asserts.button_enabled(field="submit-selected-apps-btn-new")

    async with page.expect_response("**/glimr/submit") as response_info:
        await helpers.click_button(link_text="Apply new case registration")

    response = await response_info.value
    assert response.status == 200

    await asserts.check_case_is_registered(reference_number=first_row_reference_number)
    await asserts.check_case_is_registered(reference_number=second_row_reference_number)
    await asserts.button_disabled(field="submit-selected-apps-btn-new")

    # ------------------------------------------------
    # ---- Clear all cases doesn't uncheck registered
    # ------------------------------------------------
    await helpers.click_button(link_text="Clear all for new case registration")
    await asserts.is_checked(field=first_row_reference_number)
    await asserts.is_checked(field=second_row_reference_number)









