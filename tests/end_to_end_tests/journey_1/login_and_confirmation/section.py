from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_1.data as data


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):
    # ------------------------------------------------
    # ---- Homepage / Start or return to an application page
    # ------------------------------------------------
    await asserts.url('/')
    # await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__service-name') == 'Apply for a Gender Recognition Certificate'
    await asserts.h1('Start or return to an application')
    await asserts.number_of_errors(0)

    # Select no options, see error message
    await helpers.click_button('Continue')
    await asserts.url('/')
    await asserts.accessibility()
    await asserts.h1('Start or return to an application')
    await asserts.number_of_errors(1)
    await asserts.error(field='new_application', message='Select if you have already started an application')

    # Choose the "Start a new application" option
    await helpers.check_radio(field='new_application', value=True)
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Reference Number page
    # ------------------------------------------------
    await asserts.url('/reference-number')
    await asserts.accessibility()
    await asserts.h1('Your reference number')
    await asserts.number_of_errors(0)

    initial_reference_number_on_reference_number_page = await page.inner_text('#reference-number')

    # Clicking "Back" should take us to the start page
    await helpers.click_button('Back')

    # ------------------------------------------------
    # ---- Homepage / Start or return to an application page
    # ------------------------------------------------
    # Choose the "Start a new application" option
    await asserts.url('/')
    await asserts.accessibility()
    await helpers.check_radio(field='new_application', value=True)
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Reference Number page
    # ------------------------------------------------
    await asserts.url('/reference-number')
    await asserts.accessibility()
    await asserts.h1('Your reference number')
    await asserts.number_of_errors(0)

    # Copy reference number so we can use it later
    reference_number_on_reference_number_page = await page.inner_text('#reference-number')

    # The reference number should be different to the one we saw earlier
    assert reference_number_on_reference_number_page != initial_reference_number_on_reference_number_page

    # CLick "Continue"
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Overseas Check page
    # ------------------------------------------------
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Have you ever been issued a Gender Recognition Certificate (or its equivalent) in another country?')
    await asserts.number_of_errors(0)

    # Click "Back" to return to the Reference Number page
    await helpers.click_button('Back')

    # ------------------------------------------------
    # ---- Reference Number page
    # ------------------------------------------------
    await asserts.url('/reference-number')
    await asserts.accessibility()
    await asserts.h1('Your reference number')
    await asserts.number_of_errors(0)

    # Click "Continue" to return to the Overseas Check page
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Overseas Check page
    # ------------------------------------------------
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Have you ever been issued a Gender Recognition Certificate (or its equivalent) in another country?')
    await asserts.number_of_errors(0)

    # Don't choose any radio option
    await helpers.click_button('Continue')
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Have you ever been issued a Gender Recognition Certificate (or its equivalent) in another country?')
    await asserts.number_of_errors(1)
    await asserts.error(field='overseasCheck', message='Select if you have ever been issued a Gender Recognition Certificate')

    # Choose the "No" option - this should take you straight to the Declaration page
    # i.e. you should skip the Overseas Approved Check page
    await helpers.check_radio(field='overseasCheck', value='False')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Declaration page
    # ------------------------------------------------
    await asserts.url('/declaration')
    await asserts.accessibility()
    await asserts.h1('Notifying the General Register Office')
    await asserts.number_of_errors(0)

    # Click "Back" to return to the Overseas Check page
    await helpers.click_button('Back')

    # ------------------------------------------------
    # ---- Overseas Check page
    # ------------------------------------------------
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Have you ever been issued a Gender Recognition Certificate (or its equivalent) in another country?')
    await asserts.number_of_errors(0)

    # Selection of "No" should be remembered
    await asserts.is_checked(field='overseasCheck', value='False')
    await asserts.not_checked(field='overseasCheck', value='True')

    # Choose the "Yes" radio option
    # This should take us to the Overseas Approved Check page
    await helpers.check_radio(field='overseasCheck', value='True')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Overseas Approved Check page
    # ------------------------------------------------
    await asserts.url('/overseas-approved-check')
    await asserts.accessibility()
    await asserts.h1('Gender recognition in approved countries and territories')
    await asserts.number_of_errors(0)

    # Click "Back" to return to the Overseas Check page
    await helpers.click_button('Back')

    # ------------------------------------------------
    # ---- Overseas Check page
    # ------------------------------------------------
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Have you ever been issued a Gender Recognition Certificate (or its equivalent) in another country?')
    await asserts.number_of_errors(0)

    # Selection of "Yes" should be remembered
    await asserts.is_checked(field='overseasCheck', value='True')
    await asserts.not_checked(field='overseasCheck', value='False')

    # Go forward to the Overseas Approved Check page
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Overseas Approved Check page
    # ------------------------------------------------
    await asserts.url('/overseas-approved-check')
    await asserts.accessibility()
    await asserts.h1('Gender recognition in approved countries and territories')
    await asserts.number_of_errors(0)

    # Don't choose any radio option
    await helpers.click_button('Continue')
    await asserts.url('/overseas-approved-check')
    await asserts.accessibility()
    await asserts.h1('Gender recognition in approved countries and territories')
    await asserts.number_of_errors(1)
    await asserts.error(field='overseasApprovedCheck', message='Select if you have official documentation')

    # Choose the "Yes" radio option
    await helpers.check_radio(field='overseasApprovedCheck', value='True')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Declaration page
    # ------------------------------------------------
    await asserts.url('/declaration')
    await asserts.accessibility()
    await asserts.h1('Notifying the General Register Office')
    await asserts.number_of_errors(0)

    # Click "Back" to return to the Overseas Approved Check page
    await helpers.click_button('Back')

    # ------------------------------------------------
    # ---- Overseas Approved Check page
    # ------------------------------------------------
    await asserts.url('/overseas-approved-check')
    await asserts.accessibility()
    await asserts.h1('Gender recognition in approved countries and territories')
    await asserts.number_of_errors(0)

    # Selection of "Yes" should be remembered
    await asserts.is_checked(field='overseasApprovedCheck', value='True')
    await asserts.not_checked(field='overseasApprovedCheck', value='False')

    # Go forward to the Declaration page
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Declaration page
    # ------------------------------------------------
    await asserts.url('/declaration')
    await asserts.accessibility()
    await asserts.h1('Notifying the General Register Office')
    await asserts.number_of_errors(0)

    # Don't check the checkbox
    await helpers.click_button('Continue')
    await asserts.url('/declaration')
    await asserts.accessibility()
    await asserts.h1('Notifying the General Register Office')
    await asserts.number_of_errors(1)
    await asserts.error(field='consent', message='You must consent to the General Register Office contacting you')

    # Check the checkbox
    await helpers.check_checkbox(field='consent')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Your application')
    await asserts.number_of_errors(0)

    # # Click "save and exit"
    await helpers.click_button('save and exit')
    #
    # # ------------------------------------------------
    # # ---- Application Saved page
    # # ------------------------------------------------
    await asserts.url('/save-and-return/exit-application')
    await asserts.accessibility()
    await asserts.h1('Application saved')
    await asserts.number_of_errors(0)

    # # Check reference number matches that given on earlier page
    reference_number_on_application_saved_page = await page.inner_text('#reference-number')
    assert reference_number_on_application_saved_page == reference_number_on_reference_number_page

    # # Click "return to your application"
    await helpers.click_button('return to your application.')

    # ------------------------------------------------
    # ---- Homepage / Start or return to an application page
    # ------------------------------------------------
    await asserts.url('/')
    await asserts.h1('Start or return to an application')
    await asserts.number_of_errors(0)

    # Choose the "Return to your existing application" option
    await helpers.check_radio(field='new_application', value="False")
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Application reference number page
    # ------------------------------------------------
    await asserts.url('/your-reference-number')
    await asserts.accessibility()
    await asserts.h1('Application reference number')
    await asserts.number_of_errors(0)

    # Select no options, see error message
    await helpers.click_button('Continue')
    await asserts.url('/your-reference-number')
    await asserts.accessibility()
    await asserts.h1('Application reference number')
    await asserts.number_of_errors(1)
    await asserts.error(field='has_reference', message='Select if you have already started an application')

    # Choose the "I have lost my reference number" option
    await helpers.check_radio(field='has_reference', value="LOST_REFERENCE")
    await helpers.click_button('Continue')

    # Should return back to start page
    await asserts.url('/')
    await asserts.h1('Start or return to an application')
    await asserts.number_of_errors(0)

    # Choose the "Return to your existing application" option
    await helpers.check_radio(field='new_application', value="False")
    await helpers.click_button('Continue')

    await asserts.url('/your-reference-number')
    await asserts.h1('Application reference number')

    await helpers.check_radio(field='has_reference', value="HAS_REFERENCE")
    await helpers.fill_textbox(field='reference', value=reference_number_on_application_saved_page)
    await helpers.click_button('Continue')

    await asserts.url('/reference-number')
    await helpers.click_button('Continue')

    await asserts.url('/overseas-check')
    await helpers.check_radio(field='overseasCheck', value='True')
    await helpers.click_button('Continue')

    await asserts.url('/overseas-approved-check')
    await helpers.check_radio(field='overseasApprovedCheck', value='True')
    await helpers.click_button('Continue')

    await asserts.url('/declaration')
    await helpers.check_checkbox(field='consent')
    await helpers.click_button('Continue')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Your application')
    await asserts.number_of_errors(0)

    # Status of "Confirmation" section should be "COMPLETED"
    await asserts.task_list_sections(7)
    await asserts.task_list_section(section='Confirmation', expected_status='Completed')
    await asserts.task_list_section(section='Your personal details', expected_status='Not started')
    await asserts.task_list_section(section='Your birth registration information', expected_status='Not started')
    await asserts.task_list_section(section='Marriage or civil partnership details', expected_status='Not started')
    await asserts.task_list_section(section='Overseas certificate documents', expected_status='Not started')
    await asserts.task_list_section(section='Statutory declarations', expected_status='Not started')
    await asserts.task_list_section(section='Submit and pay', expected_status='Cannot start yet')