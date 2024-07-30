from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Click "Submit and pay"
    await helpers.click_button('Cyflwyno a thalu')

    # ------------------------------------------------
    # ---- Payment page
    # ------------------------------------------------
    await asserts.url('/submit-and-pay')
    await asserts.accessibility()
    await asserts.h1('Talu')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/submit-and-pay')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Payment')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Talu')

    # Choose "Yes", option, click Save and continue
    await helpers.check_radio(field='applying_for_help_with_fee', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Applying For Help page
    # ------------------------------------------------
    await asserts.url('/submit-and-pay/help-type')
    await asserts.accessibility()
    await asserts.h1('Gwneud cais am help i dalu’r ffi')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/submit-and-pay/help-type')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Applying for help with the fee')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Gwneud cais am help i dalu’r ffi')

    # Enter a valid Help with Fees reference number
    await helpers.check_radio(field='how_applying_for_fees', value='USING_ONLINE_SERVICE')
    await helpers.fill_textbox(field='help_with_fees_reference_number', value=data.HELP_WITH_FEES_REFERENCE_NUMBER)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/submit-and-pay/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion cyn anfon eich cais')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/submit-and-pay/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Check your answers before sending your application')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Gwiriwch eich atebion cyn anfon eich cais')

    # Check the values in the summary table
    await asserts.check_your_answers_rows(33)
    await asserts.check_your_answers_row(row_name='Ydych chi erioed wedi cael Tystysgrif Cydnabod Rhywedd (neu dystysgrif cyfwerth) mewn gwlad arall?', expected_value='Ydw')
    await asserts.check_your_answers_row(row_name="A oes gennych chi ddogfennaeth swyddogol sy'n dangos eich bod wedi cael Tystysgrif Cydnabod Rhywedd (neu dystysgrif cyfwerth) yn un o'r gwledydd neu diriogaethau a ganiateir?", expected_value='Ydw')
    await asserts.check_your_answers_row(row_name="Ydych chi’n rhoi caniatâd i’r Swyddfa Gofrestru Gyffredinol gysylltu â chi ynglŷn â’ch cais?", expected_value='Ydw')

    await asserts.check_your_answers_row(row_name='Enw (fel yr hoffech iddo ymddangos ar eich Tystysgrif Cydnabod Rhywedd)', expected_value=f"{data.TITLE} {data.FIRST_NAME} {data.MIDDLE_NAMES} {data.LAST_NAME}")
    await asserts.check_your_answers_row(row_name='Rhywedd a gadarnhawyd', expected_value='Gwryw')
    await asserts.check_your_answers_row(row_name='Pan wnaethoch drawsnewid', expected_value=data.TRANSITION_DATE_FORMATTED)
    await asserts.check_your_answers_row(row_name='Pan wnaethoch lofnodi eich datganiad statudol', expected_value=data.STATUTORY_DECLARATION_DATE_FORMATTED)
    await asserts.check_your_answers_row(row_name='Erioed wedi newid enw', expected_value='Ydw')
    await asserts.check_your_answers_row(row_name='Cyfeiriad', expected_value=f"{data.ADDRESS_LINE_ONE}\n{data.ADDRESS_LINE_TWO}\n{data.TOWN}\n{data.POSTCODE}")
    await asserts.check_your_answers_row(row_name='Dewisiadau cyswllt', expected_value=f"E-bost: {data.EMAIL_ADDRESS}\nFfôn: {data.PHONE_NUMBER}\nPost: {data.ADDRESS_LINE_ONE}, {data.ADDRESS_LINE_TWO}, {data.TOWN}, {data.POSTCODE}")
    await asserts.check_your_answers_row(row_name='Ddim ar gael yn y 6 mis nesaf', expected_value=f"Ydw\n{data.DATES_TO_AVOID}")
    await asserts.check_your_answers_row(row_name='Hysbysu HMRC', expected_value='Ydw')
    await asserts.check_your_answers_row(row_name='Rhif Yswiriant Gwladol', expected_value=data.NATIONAL_INSURANCE_NUMBER)

    await asserts.check_your_answers_row(row_name='Enw adeg geni', expected_value=f"{data.BIRTH_FIRST_NAME} {data.BIRTH_MIDDLE_NAME} {data.BIRTH_LAST_NAME}")
    await asserts.check_your_answers_row(row_name='Dyddiad geni', expected_value=data.DATE_OF_BIRTH_FORMATTED)
    await asserts.check_your_answers_row(row_name='Genedigaeth a gofrestrwyd yn y DU', expected_value='Ydw')
    await asserts.check_your_answers_row(row_name='Tref neu ddinas geni', expected_value=data.BIRTH_TOWN)
    await asserts.check_your_answers_row(row_name="Enw’r fam", expected_value=f"{data.MOTHERS_FIRST_NAME} {data.MOTHERS_LAST_NAME}\n(Enw cyn priodi: {data.MOTHERS_MAIDEN_NAME})")
    await asserts.check_your_answers_row(row_name="Enw’r tad a restrwyd", expected_value='Ydw')
    await asserts.check_your_answers_row(row_name="Enw’r tad", expected_value=f"{data.FATHERS_FIRST_NAME} {data.FATHERS_LAST_NAME}")
    await asserts.check_your_answers_row(row_name='Mabwysiadwyd', expected_value='Ydw')
    await asserts.check_your_answers_row(row_name='Mabwysiadwyd yn y DU', expected_value="Dydw i ddim yn gwybod")
    await asserts.check_your_answers_row(row_name="Gwasanaeth cofrestru’r Lluoedd, Conswl Prydeinig neu Uchel Gomisiwn, neu dan ddarpariaethau Llongau Masnach neu Hedfan Sifil", expected_value='Nac ydw')

    await asserts.check_your_answers_row(row_name='Wedi priodi neu mewn partneriaeth sifil ar hyn o bryd', expected_value='Ddim un ohonynt')
    await asserts.check_your_answers_row(row_name='Mae fy mhriod neu fy mhartner wedi marw', expected_value='Ydw')
    await asserts.check_your_answers_row(row_name='Mae ein priodas neu bartneriaeth sifil wedi dod i ben', expected_value='Ydw')

    await asserts.check_your_answers_row(row_name='Dogfennau newid enw', expected_value='document_1.bmp')
    await asserts.check_your_answers_row(row_name='Dogfennau priodas', expected_value='document_1.bmp')
    await asserts.check_your_answers_row(row_name='Dogfennau Tystysgrif o Dramor', expected_value='document_1.bmp')
    await asserts.check_your_answers_row(row_name='Datganiadau statudol', expected_value='document_1.bmp')

    await asserts.check_your_answers_row(row_name='Dull talu', expected_value='Help')
    await asserts.check_your_answers_row(row_name='Math o help', expected_value='Defnyddio’r gwasanaeth ar-lein')
    await asserts.check_your_answers_row(row_name='Cyfeirnod Help i Dalu Ffioedd', expected_value=data.HELP_WITH_FEES_REFERENCE_NUMBER)

    # Check the checkbox, click Save and continue
    await helpers.check_checkbox(field='certify')
    await helpers.click_button('Cyflwyno’r cais')

    # ------------------------------------------------
    # ---- Confirmation page
    # ------------------------------------------------
    await asserts.url('/submit-and-pay/confirmation')
    await asserts.accessibility()
    await asserts.h1("Cais wedi'i gyflwyno")
    await asserts.number_of_errors(0)
