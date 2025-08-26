from playwright.async_api import Page

from tests.end_to_end_tests.helpers.e2e_admin_helpers import AdminHelpers
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers, get_url_path
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers


async def run_checks_on_downloaded_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers,
                                           admin_helpers: AdminHelpers):
    # ------------------------------------------------
    # ---- Land on New Applications Tab
    # ------------------------------------------------
    await asserts.url('/applications')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'
    await asserts.h1('View and download GRC applications')

    # ------------------------------------------------
    # ---- Extract top table applications from new applications table
    # ------------------------------------------------
    await page.wait_for_selector("table.new-table")

    top_two_rows = await admin_helpers.get_top_rows(2, ".new-table")
    first_row, second_row = top_two_rows

    first_row_reference_number = await admin_helpers.get_row_reference_number(first_row)
    # first_row_reference_number = first_row_reference_number.replace("-", "")
    second_row_reference_number = await admin_helpers.get_row_reference_number(second_row)
    # second_row_reference_number = second_row_reference_number.replace("-", "")

    # ------------------------------------------------
    # ---- Click on View Application for first application and assert details
    # ------------------------------------------------
    href1 = "/applications"
    href_first_row = f"{href1}/{first_row_reference_number}"
    await helpers.click_link_by_exact_href(href_value=href_first_row)
    await page.wait_for_load_state()
    actual_url = page.url
    print("Actual URL in  view applications - ", actual_url)
    assert first_row_reference_number in actual_url

    # ------------------------------------------------
    # ---- Download Application from details page
    # ------------------------------------------------
    await helpers.click_button(link_text='Download application (PDF)')
    await helpers.click_button(link_text='Download attachments (ZIP file)')
    await page.wait_for_load_state()
    assert first_row_reference_number in actual_url
    await page.go_back()
    current_url = page.url
    print("Current URL:", current_url)
    await page.click("#tab_new")
    await page.wait_for_load_state("load")
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'

    # ------------------------------------------------
    # ---- Click on View Application for second application and assert details
    # ------------------------------------------------
    href1 = "/applications"
    href_second_row = f"{href1}/{second_row_reference_number}"
    await helpers.click_link_by_exact_href(href_value=href_second_row)
    await page.wait_for_load_state()
    actual_url = page.url
    print("Actual URL in  view applications - ", actual_url)
    assert second_row_reference_number in actual_url

    # ------------------------------------------------
    # ---- Download Application from details page
    # ------------------------------------------------
    await helpers.click_button(link_text='Download application (PDF)')
    await helpers.click_button(link_text='Download attachments (ZIP file)')
    await page.wait_for_load_state()
    assert second_row_reference_number in actual_url
    await page.go_back()
    current_url = page.url
    print("Current URL:", current_url)
    await page.click("#tab_new")
    await page.wait_for_load_state("load")
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Download GRC applications'

    # ------------------------------------------------
    # ---- Click Downloaded Applications Tab
    # ------------------------------------------------
    await page.click("#tab_downloaded")
    # await page.wait_for_load_state("load")
    await asserts.accessibility()
    actual_url_download = page.url
    print("actual_url_download -", actual_url_download)
    download_tab_text = "applications#downloaded"
    print("download_tab_text - ", download_tab_text)
    # assert download_tab_text in actual_url_download

    # ------------------------------------------------
    # ---- Get Table details and verify the Downloaded
    # application is displayed (first application)
    # ------------------------------------------------

    await helpers.click_link_by_exact_href(href_value=href_first_row)
    await page.wait_for_load_state()
    actual_url_downloadedTab = page.url
    assert first_row_reference_number in actual_url_downloadedTab
    await page.go_back()
    await page.reload()
    await page.wait_for_load_state("load")
    page_details = page.url
    print("page URL after coming back is - ", page_details)

    # ------------------------------------------------
    # ---- Get Table details and verify the Downloaded
    # application is displayed (second application)
    # ------------------------------------------------

    await helpers.click_link_by_exact_href(href_value=href_second_row)
    await page.wait_for_load_state()
    actual_url_downloadedTab = page.url
    assert second_row_reference_number in actual_url_downloadedTab
    await page.go_back()
    await page.reload()
    await page.wait_for_load_state("load")
    page_details = page.url
    print("page URL after coming back is - ", page_details)

    # ------------------------------------------------
    # ---- Select all for applications marking as complete
    # ------------------------------------------------
    await helpers.click_button(link_text="Select all as completed")
    await asserts.is_checked(field=first_row_reference_number)
    await asserts.is_checked(field=second_row_reference_number)
    await asserts.button_enabled(field="submit-selected-apps-btn-downloaded")

    # ------------------------------------------------
    # ---- Deselect all the applications for unmarking as complete
    # ------------------------------------------------
    await helpers.click_button(link_text="Clear all as completed")
    await asserts.not_checked(field=first_row_reference_number)
    await asserts.not_checked(field=second_row_reference_number)
    await asserts.button_disabled(field="submit-selected-apps-btn-downloaded")

    # ------------------------------------------------
    # ---- Select and deselect application for marking as complete
    # ------------------------------------------------
    for row_reference_number in [first_row_reference_number, second_row_reference_number]:
        await helpers.check_checkbox(field=row_reference_number)
        await asserts.is_checked(field=row_reference_number)
        await asserts.button_enabled(field="submit-selected-apps-btn-downloaded")
        await helpers.uncheck_checkbox(field=row_reference_number)
        await asserts.not_checked(field=row_reference_number)
        await asserts.button_disabled(field="submit-selected-apps-btn-downloaded")

    # ------------------------------------------------
    # ---- Mark first application as complete on
    # Downloads page
    # ------------------------------------------------
    await helpers.check_checkbox(first_row_reference_number)
    await helpers.click_button("Apply applications completed")
    await page.wait_for_load_state("load")
    completed_applications_url = page.url
    print("completed applications url in code download page is - ", completed_applications_url)

    # ------------------------------------------------
    # ---- by default we land on completed applications
    # tab click on first view application and assert
    # the reference number
    # ------------------------------------------------
