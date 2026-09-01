from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_1.data as data


TASK_LIST_BUTTON_NAME = 'Your birth or adoption certificate'
PAGE_URL = '/upload/birth-or-adoption-certificate'
PAGE_H1 = 'Upload your birth or adoption certificate'


async def run_checks_on_page(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Your application')
    await asserts.number_of_errors(0)

    # Click "Your birth or adoption certificate" to go to the upload page
    await helpers.click_button(TASK_LIST_BUTTON_NAME)

    # ------------------------------------------------
    # ---- Birth or Adoption Certificate page
    # ------------------------------------------------
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(0)

    # "Back" should take us to the Task List page
    await helpers.click_button('Back')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Your application')
    await asserts.number_of_errors(0)

    # Continue to the "Birth or Adoption Certificate" page again
    await helpers.click_button(TASK_LIST_BUTTON_NAME)

    # ------------------------------------------------
    # ---- Birth or Adoption Certificate page
    # ------------------------------------------------
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(0)

    # Try to upload a document of the wrong type
    await helpers.upload_file_invalid_file_type(field='documents')
    await helpers.click_button('Upload 1 file')
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(1)
    await asserts.error(field='documents', message='Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')
    await asserts.documents_uploaded(0)

    DOCUMENT_ONE_NAME = 'document_1.png'

    # Upload a valid document
    await helpers.upload_file_valid(field='documents', file_name=DOCUMENT_ONE_NAME)
    page.set_default_timeout(data.TIMEOUT_FOR_SLOW_OPERATIONS)
    await helpers.click_button('Upload 1 file')
    await asserts.url(PAGE_URL)
    page.set_default_timeout(data.DEFAULT_TIMEOUT)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(1)
    await asserts.document_uploaded(file_name=DOCUMENT_ONE_NAME)

    # Remove the uploaded document
    await helpers.click_button(f"Remove file {DOCUMENT_ONE_NAME}")
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(0)

    # Return to Task List page without uploading a file
    # Because this section is optional, this should be allowed even with no upload
    await helpers.click_button('Return to task list')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Your application')
    await asserts.number_of_errors(0)

    # Status of "Your birth or adoption certificate" section should be "NOT STARTED"
    await asserts.task_list_sections(10)
    await asserts.task_list_section(section='Confirmation', expected_status='Completed')
    await asserts.task_list_section(section='Your personal details', expected_status='Completed')
    await asserts.task_list_section(section='Your birth registration information', expected_status='Completed')
    await asserts.task_list_section(section='Marriage or civil partnership details', expected_status='Completed')
    await asserts.task_list_section(section='Name change documents', expected_status='Completed')
    await asserts.task_list_section(section='Marriage and civil partnership documents', expected_status='Completed')
    await asserts.task_list_section(section='Overseas certificate documents', expected_status='Completed')
    await asserts.task_list_section(section='Statutory declarations', expected_status='Completed')
    await asserts.task_list_section(section='Your birth or adoption certificate', expected_status='Not started')
    await asserts.task_list_section(section='Submit and pay', expected_status='Not started')

    # Click "Your birth or adoption certificate" to go back to the upload page
    await helpers.click_button(TASK_LIST_BUTTON_NAME)

    # ------------------------------------------------
    # ---- Birth or Adoption Certificate page
    # ------------------------------------------------
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(0)

    # Upload a valid document
    await helpers.upload_file_valid(field='documents', file_name=DOCUMENT_ONE_NAME)
    page.set_default_timeout(data.TIMEOUT_FOR_SLOW_OPERATIONS)
    await helpers.click_button('Upload 1 file')
    await asserts.url(PAGE_URL)
    page.set_default_timeout(data.DEFAULT_TIMEOUT)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(1)
    await asserts.document_uploaded(file_name=DOCUMENT_ONE_NAME)

    # Click "Save and continue"
    # Now that there is a file uploaded, we should be taken to the Task List page
    # "Your birth or adoption certificate" section should be marked as "COMPLETED"
    await helpers.click_button('Save and continue')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Your application')
    await asserts.number_of_errors(0)

    # Status of "Your birth or adoption certificate" section should be "COMPLETED"
    await asserts.task_list_sections(10)
    await asserts.task_list_section(section='Confirmation', expected_status='Completed')
    await asserts.task_list_section(section='Your personal details', expected_status='Completed')
    await asserts.task_list_section(section='Your birth registration information', expected_status='Completed')
    await asserts.task_list_section(section='Marriage or civil partnership details', expected_status='Completed')
    await asserts.task_list_section(section='Name change documents', expected_status='Completed')
    await asserts.task_list_section(section='Marriage and civil partnership documents', expected_status='Completed')
    await asserts.task_list_section(section='Overseas certificate documents', expected_status='Completed')
    await asserts.task_list_section(section='Statutory declarations', expected_status='Completed')
    await asserts.task_list_section(section='Your birth or adoption certificate', expected_status='Completed')
    await asserts.task_list_section(section='Submit and pay', expected_status='Not started')
