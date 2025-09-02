from playwright.async_api import Page

from grc.start_application import reference
from grc.utils.reference_number import reference_number_is_valid
from tests.end_to_end_tests.helpers.e2e_admin_helpers import AdminHelpers
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_admin.data as data


async def run_checks_on_completed_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers,
                                          admin_helpers: AdminHelpers):
    # ------------------------------------------------
    # ---- Completed Applications page
    # ------------------------------------------------
    await page.click("a[href*='#completed']")
    print("completed page url is  -", page.url)
    completed_page_url = page.url
    completed_text = '/applications#completed'
    print(completed_text)
    assert completed_text in completed_page_url
    # await asserts.url('/applications#completed')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'
    await asserts.h1('View and download GRC applications')
    await asserts.h2('Completed applications')
    # await asserts.check_heading(2, "Completed applications")
    # await page.click("#tab_completed")
    assert completed_text in completed_page_url

    # ------------------------------------------------
    # ---- Extract top table applications
    # ------------------------------------------------
    await page.wait_for_selector("table.completed-table")
    await page.locator("table.completed-table").wait_for(state="visible")

    top_two_rows = await admin_helpers.get_top_rows(2, ".completed-table")
    first_row_completed, second_row_completed = top_two_rows
    first_row_ref_num_completed = await admin_helpers.get_ref_num_complete_tab(first_row_completed)
    print("first row reference in completed page - ", first_row_ref_num_completed)
    # first_row_reference_number_no_hyphen = first_row_reference_number.replace("-", "")
    # second_row_reference_number_completed = await admin_helpers.get_row_reference_number(second_row)
    # print("second row reference in completed page - ", second_row_reference_number_completed)
    # second_row_reference_number_no_hyphen = second_row_reference_number.replace("-", "")

    # ----------------------------------------------------------------------
    # ---- Click on View Application and
    # ----assert details for first application
    # ----------------------------------------------------------------------

    href1 = "/applications"
    href_first_application_completed = f"{href1}/{first_row_ref_num_completed}"
    await helpers.click_link_by_exact_href(href_value=href_first_application_completed)
    await page.wait_for_load_state()
    actual_url = page.url
    print("Actual URL in  completed applications first_application- ", actual_url)
    assert first_row_ref_num_completed in actual_url

    # ------------------------------------------------
    # ---- Download Pdf and zip files of the first application and back to
    # completed tab
    # ------------------------------------------------
    await helpers.click_button(link_text='Download application (PDF)')
    await helpers.click_button(link_text='Download attachments (ZIP file)')
    # await page.wait_for_load_state()
    assert first_row_ref_num_completed in actual_url
    await page.go_back()
    current_url = page.url
    print("Current URL completed page first application :", current_url)
    await page.click("#tab_new")
    await page.wait_for_load_state("load")
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'
    await page.click("#tab_completed")

    # ----------------------------------------------------------------------
    # ---- Click on View Application and
    # ----assert details for second application
    # ----------------------------------------------------------------------
    # await page.click("#tab_completed")
    # href1 = "/applications"
    # href_second_application_completed = f"{href1}/{second_row_reference_number_completed}"
    # await helpers.click_link_by_exact_href(href_value=href_second_application_completed)
    # await page.wait_for_load_state()
    # actual_url = page.url
    # print("Actual URL in  completed applications second_application- ", actual_url)
    # assert second_row_reference_number_completed in actual_url

    # ------------------------------------------------
    # ---- Download Pdf and zip files of the second application and back to
    # completed tab
    # ------------------------------------------------
    # await helpers.click_button(link_text='Download application (PDF)')
    # await helpers.click_button(link_text='Download attachments (ZIP file)')
    # await page.wait_for_load_state()
    # assert second_row_reference_number_completed in actual_url
    # await page.go_back()
    # current_url = page.url
    # print("Current URL completed page second application :", current_url)
    # await page.click("#tab_completed")
    # await page.wait_for_load_state("load")
    # assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'

    # ------------------------------------------------
    # ---- Select all for deleting applications
    # ------------------------------------------------
    await helpers.click_button_by_exact_text("Select all applications")
    await asserts.is_checked(field=first_row_ref_num_completed)
    # await asserts.is_checked(field=second_row_reference_number_completed)
    await asserts.button_enabled(field="submit-selected-apps-btn-completed")

    # ------------------------------------------------
    # ---- Deselect all the selected applications
    # ------------------------------------------------
    await helpers.click_button(link_text="Deselect all applications")
    await asserts.not_checked(field=first_row_ref_num_completed)
    # await asserts.not_checked(field=second_row_reference_number_completed)
    await asserts.button_disabled(field="submit-selected-apps-btn-completed")

    # ------------------------------------------------
    # ---- Select and deselect for application deletion
    # ------------------------------------------------
    for row_reference_number in [first_row_ref_num_completed]:
        await helpers.check_checkbox(field=row_reference_number)
        await asserts.is_checked(field=row_reference_number)
        await asserts.button_enabled(field="submit-selected-apps-btn-completed")
        await helpers.uncheck_checkbox(field=row_reference_number)
        await asserts.not_checked(field=row_reference_number)
        await asserts.button_disabled(field="submit-selected-apps-btn-completed")

    # ------------------------------------------------
    # ---- Delete Selected application
    # ------------------------------------------------
    for row_reference_number in [first_row_ref_num_completed]:
        await helpers.check_checkbox(field=row_reference_number)
        await asserts.is_checked(field=row_reference_number)
        await helpers.click_button('Delete selected applications')
        await asserts.single_text_not_displayed(row_reference_number)


