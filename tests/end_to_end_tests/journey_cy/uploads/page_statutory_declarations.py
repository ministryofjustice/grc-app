from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_1.data as data


TASK_LIST_BUTTON_NAME = 'Datganiadau statudol'
PAGE_URL = '/upload/statutory-declarations'
PAGE_H1_EN = 'Statutory declarations documents'
PAGE_H1_CY = 'Dogfennau datganiadau statudol'


async def run_checks_on_page(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Click "Statutory declarations" to go to the "Statutory Declarations" page
    await helpers.click_button(TASK_LIST_BUTTON_NAME)

    # ------------------------------------------------
    # ---- Statutory Declarations page
    # ------------------------------------------------
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1_CY)
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1(PAGE_H1_EN)
    await helpers.click_button('Cymraeg')
    await asserts.h1(PAGE_H1_CY)

    DOCUMENT_ONE_NAME = 'document_1.bmp'

    # Upload a valid document
    await helpers.upload_file_valid(field='documents', file_name=DOCUMENT_ONE_NAME)
    page.set_default_timeout(data.TIMEOUT_FOR_SLOW_OPERATIONS)
    await helpers.click_button('Uwchlwytho 1 ffeil')
    await asserts.url(PAGE_URL)
    page.set_default_timeout(data.DEFAULT_TIMEOUT)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1_CY)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(1)
    await asserts.document_uploaded(file_name=DOCUMENT_ONE_NAME)

    # Remove the uploaded document
    await helpers.click_button(f"Dileu ffeil {DOCUMENT_ONE_NAME}")
    await asserts.url(PAGE_URL)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1_CY)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(0)

    # Upload a valid document
    await helpers.upload_file_valid(field='documents', file_name=DOCUMENT_ONE_NAME)
    page.set_default_timeout(data.TIMEOUT_FOR_SLOW_OPERATIONS)
    await helpers.click_button('Uwchlwytho 1 ffeil')
    await asserts.url(PAGE_URL)
    page.set_default_timeout(data.DEFAULT_TIMEOUT)
    await asserts.accessibility()
    await asserts.h1(PAGE_H1_CY)
    await asserts.number_of_errors(0)
    await asserts.documents_uploaded(1)
    await asserts.document_uploaded(file_name=DOCUMENT_ONE_NAME)

    # Return to Task List page
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Status of "Statutory declarations" section should be "COMPLETED"
    await asserts.task_list_sections(9)
    await asserts.task_list_section(section='Datganiadau statudol', expected_status="WEDI'I GWBLHAU")