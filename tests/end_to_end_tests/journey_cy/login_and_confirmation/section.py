from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):
    # ------------------------------------------------
    # ---- Homepage / Email address page
    # ------------------------------------------------
    await asserts.url('/')
    await asserts.accessibility()
    assert await page.inner_text('a.govuk-header__link.govuk-header__link--service-name') == 'Apply for a Gender Recognition Certificate'
    await asserts.h1('Email address')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/')
    await asserts.accessibility()
    await helpers.click_button('Cymraeg')
    assert await page.inner_text('a.govuk-header__link.govuk-header__link--service-name') == 'Gwneud cais am Dystysgrif Cydnabod Rhywedd'
    await asserts.h1('Cyfeiriad e-bost')

    # Enter a valid Email Address, click Continue button, see the Security Code page
    await helpers.fill_textbox(field='email', value=data.EMAIL_ADDRESS)
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Security Code page
    # ------------------------------------------------
    await asserts.url('/security-code')
    await asserts.accessibility()
    await asserts.h1('Rhowch cod diogelwch')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/security-code')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Enter security code')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Rhowch cod diogelwch')

    # Enter a valid Security Code, click Continue button
    await helpers.fill_textbox(field='security_code', value='11111')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Is First Visit page
    # ------------------------------------------------
    await asserts.url('/is-first-visit')
    await asserts.accessibility()
    await asserts.h1('Ydych chi eisoes wedi cychwyn gwneud cais?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/is-first-visit')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Have you already started an application?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Ydych chi eisoes wedi cychwyn gwneud cais?')

    # Choose the "No" (this is my first visit) option
    await helpers.check_radio(field='isFirstVisit', value='FIRST_VISIT')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Reference Number page
    # ------------------------------------------------
    await asserts.url('/reference-number')
    await asserts.accessibility()
    await asserts.h1('Eich cyfeirnod')
    await asserts.number_of_errors(0)

    # Copy reference number so we can use it later
    reference_number = await page.inner_text('#reference-number')

    # Change language
    await asserts.url('/reference-number')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Your reference number')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Eich cyfeirnod')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Overseas Check page
    # ------------------------------------------------
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Ydych chi erioed wedi cael Tystysgrif Cydnabod Rhywedd (neu dystysgrif cyfwerth) mewn gwlad arall?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Have you ever been issued a Gender Recognition Certificate (or its equivalent) in another country?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Ydych chi erioed wedi cael Tystysgrif Cydnabod Rhywedd (neu dystysgrif cyfwerth) mewn gwlad arall?')

    # Choose the "No" option - this should take you straight to the Declaration page
    # i.e. you should skip the Overseas Approved Check page
    await helpers.check_radio(field='overseasCheck', value='False')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Declaration page
    # ------------------------------------------------
    await asserts.url('/declaration')
    await asserts.accessibility()
    await asserts.h1('Hysbysu’r Swyddfa Gofrestru Gyffredinol')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/declaration')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Notifying the General Register Office')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Hysbysu’r Swyddfa Gofrestru Gyffredinol')

    # Click "Back" to return to the Overseas Check page
    await helpers.click_button('Yn ôl')

    # ------------------------------------------------
    # ---- Overseas Check page
    # ------------------------------------------------
    await asserts.url('/overseas-check')
    await asserts.accessibility()
    await asserts.h1('Ydych chi erioed wedi cael Tystysgrif Cydnabod Rhywedd (neu dystysgrif cyfwerth) mewn gwlad arall?')
    await asserts.number_of_errors(0)

    # Choose the "Yes" radio option
    # This should take us to the Overseas Approved Check page
    await helpers.check_radio(field='overseasCheck', value='True')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Overseas Approved Check page
    # ------------------------------------------------
    await asserts.url('/overseas-approved-check')
    await asserts.accessibility()
    await asserts.h1('Cydnabod rhywedd mewn gwledydd a thiriogaethau cymeradwy')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/overseas-approved-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Gender recognition in approved countries and territories')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Cydnabod rhywedd mewn gwledydd a thiriogaethau cymeradwy')

    # Choose the "Yes" radio option
    await helpers.check_radio(field='overseasApprovedCheck', value='True')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Declaration page
    # ------------------------------------------------
    await asserts.url('/declaration')
    await asserts.accessibility()
    await asserts.h1('Hysbysu’r Swyddfa Gofrestru Gyffredinol')
    await asserts.number_of_errors(0)

    # Check the checkbox
    await helpers.check_checkbox(field='consent')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/task-list')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Your application')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Eich cais')

    # Status of "Confirmation" section should be "COMPLETED"
    await asserts.task_list_sections(7)
    await asserts.task_list_section(section='Cadarnhau', expected_status="WEDI'I GWBLHAU")
    await asserts.task_list_section(section='Eich manylion personol', expected_status='HEB DDECHRAU')
    await asserts.task_list_section(section='Gwybodaeth am gofrestru eich genedigaeth', expected_status='HEB DDECHRAU')
    await asserts.task_list_section(section='Manylion eich priodas neu bartneriaeth sifil', expected_status='HEB DDECHRAU')
    await asserts.task_list_section(section='Dogfennau Tystysgrif o Dramor', expected_status='HEB DDECHRAU')
    await asserts.task_list_section(section='Datganiadau statudol', expected_status='HEB DDECHRAU')
    await asserts.task_list_section(section='Cyflwyno a thalu', expected_status='METHU DECHRAU ETO')
