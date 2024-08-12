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

    # Click "Marriage or civil partnership details" to go to the "Are You Married" page
    await helpers.click_button('Manylion eich priodas neu bartneriaeth sifil')

    # ------------------------------------------------
    # ---- Are You Married page
    # ------------------------------------------------
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await asserts.h1('Priodasau a phartneriaethau sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Marriages and civil partnerships')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Priodasau a phartneriaethau sifil')

    # Select "Married" option and proceed down this route until the "Check you answers" page
    # Then, re-trace our steps back here and choose the "Civil partnership" and then "Neither" options
    await helpers.check_radio(field='currently_married', value='MARRIED')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Stay Together page
    # ------------------------------------------------
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await asserts.h1("Ydych chi’n bwriadu aros yn briod ar ôl cael eich Tystysgrif Cydnabod Rhywedd?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Do you plan to remain married after you receive your Gender Recognition Certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1("Ydych chi’n bwriadu aros yn briod ar ôl cael eich Tystysgrif Cydnabod Rhywedd?")

    # Select the "Yes" option, go down that route
    # Then backtrack and choose "No"
    await helpers.check_radio(field='stay_together', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Partner Agrees page
    # ------------------------------------------------
    await asserts.url('/partnership-details/partner-agrees')
    await asserts.accessibility()
    await asserts.h1('Datganiad o gydsyniad')
    await asserts.fieldset_legend('Allwch chi ddarparu datganiad statudol gan eich priod?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/partner-agrees')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Declaration of consent')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Datganiad o gydsyniad')

    # Select the "Yes" option, go down that route
    # Then backtrack and choose "No"
    await helpers.check_radio(field='partner_agrees', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Your spouse's details page
    # ------------------------------------------------
    await asserts.url('/partnership-details/partner-details')
    await asserts.accessibility()
    await asserts.h1("Manylion eich priod")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/partner-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Your spouse's details")
    await helpers.click_button('Cymraeg')
    await asserts.h1("Manylion eich priod")

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='partner_title', value=data.PARTNER_TITLE)
    await helpers.fill_textbox(field='partner_first_name', value=data.PARTNER_FIRST_NAME)
    await helpers.fill_textbox(field='partner_last_name', value=data.PARTNER_LAST_NAME)
    await helpers.fill_textbox(field='partner_postal_address', value=data.PARTNER_POSTAL_ADDRESS)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Marriage details: Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/partnership-details/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion eich priodas neu bartneriaeth sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Check your answers: Marriage or civil partnership details')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Gwiriwch eich atebion: Manylion eich priodas neu bartneriaeth sifil')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details/partner-details')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details/partner-agrees')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details/stay-together')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details')

    # ------------------------------------------------
    # ---- Are You Married page
    # ------------------------------------------------
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await asserts.h1('Priodasau a phartneriaethau sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Marriages and civil partnerships')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Priodasau a phartneriaethau sifil')

    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.check_radio(field='currently_married', value='CIVIL_PARTNERSHIP')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Stay Together page
    # ------------------------------------------------
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await asserts.h1("Ydych chi'n bwriadu aros yn eich partneriaeth sifil ar ôl i chi gael eich Tystysgrif Cydnabod Rhywedd?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Do you plan to remain in your civil partnership after you receive your Gender Recognition Certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1("Ydych chi'n bwriadu aros yn eich partneriaeth sifil ar ôl i chi gael eich Tystysgrif Cydnabod Rhywedd?")

    # Select the "Yes" option, go down that route
    # Then backtrack and choose "No"
    await helpers.check_radio(field='stay_together', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Partner Agrees page
    # ------------------------------------------------
    await asserts.url('/partnership-details/partner-agrees')
    await asserts.accessibility()
    await asserts.h1('Datganiad o gydsyniad')
    await asserts.fieldset_legend('Allwch chi ddarparu datganiad statudol gan eich partner sifil?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/partner-agrees')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Declaration of consent')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Datganiad o gydsyniad')

    # Select the "Yes" option, go down that route
    # Then backtrack and choose "No"
    await helpers.check_radio(field='partner_agrees', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Your spouse's details page
    # ------------------------------------------------
    await asserts.url('/partnership-details/partner-details')
    await asserts.accessibility()
    await asserts.h1("Manylion eich partner sifil")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/partner-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Your civil partner's details")
    await helpers.click_button('Cymraeg')
    await asserts.h1("Manylion eich partner sifil")

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='partner_title', value=data.PARTNER_TITLE)
    await helpers.fill_textbox(field='partner_first_name', value=data.PARTNER_FIRST_NAME)
    await helpers.fill_textbox(field='partner_last_name', value=data.PARTNER_LAST_NAME)
    await helpers.fill_textbox(field='partner_postal_address', value=data.PARTNER_POSTAL_ADDRESS)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Marriage details: Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/partnership-details/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion eich priodas neu bartneriaeth sifil')
    await asserts.number_of_errors(0)

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details/partner-details')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details/partner-agrees')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details/stay-together')

    # REWIND!
    # Go all the way back to the "Are you married" page,
    # Select the "Civil partnership" option
    # Go through all the same journeys, checking the text has changed from "married" to "in a civil partnership"
    await helpers.click_button('Yn ôl')
    await asserts.url('/partnership-details')

    # ------------------------------------------------
    # ---- Are You Married page
    # ------------------------------------------------
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await asserts.h1('Priodasau a phartneriaethau sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Marriages and civil partnerships')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Priodasau a phartneriaethau sifil')

    # Select the "Married" option
    await helpers.check_radio(field='currently_married', value='MARRIED')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Stay Together page
    # ------------------------------------------------
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await asserts.h1("Ydych chi’n bwriadu aros yn briod ar ôl cael eich Tystysgrif Cydnabod Rhywedd?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/stay-together')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Do you plan to remain married after you receive your Gender Recognition Certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1("Ydych chi’n bwriadu aros yn briod ar ôl cael eich Tystysgrif Cydnabod Rhywedd?")

    # Select the "No" option, go down that route
    # Then backtrack and choose "No"
    await helpers.check_radio(field='stay_together', value='False')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Interim GRC page
    # ------------------------------------------------
    await asserts.url('/partnership-details/interim-check')
    await asserts.accessibility()
    await asserts.h1('Tystysgrif Cydnabod Rhywedd Interim')
    await asserts.page_does_not_contain_text('partner sifil', 'partneriaeth sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/interim-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Interim Gender Recognition Certificate')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Tystysgrif Cydnabod Rhywedd Interim')
    await helpers.click_button('Parhau')

    # ------------------------------------------------
    # ---- Marriage details: Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/partnership-details/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion eich priodas neu bartneriaeth sifil')
    await asserts.number_of_errors(0)

    # Click "Change" to get back to the "Are You Married" page, then choose "Neither"
    await helpers.click_button('Newid if you are currently married or in a civil partnership')

    # ------------------------------------------------
    # ---- Are You Married page
    # ------------------------------------------------
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await asserts.h1('Priodasau a phartneriaethau sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Marriages and civil partnerships')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Priodasau a phartneriaethau sifil')

    # Select the "Married" option
    await helpers.check_radio(field='currently_married', value='NEITHER')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Partner Died page
    # ------------------------------------------------
    await asserts.url('/partnership-details/partner-died')
    await asserts.accessibility()
    await asserts.h1('A oeddech chi’n arfer bod yn briod neu mewn partneriaeth sifil, ond bod eich priod neu bartner sifil wedi marw?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/partner-died')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Were you previously married or in a civil partnership and your spouse or partner died?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('A oeddech chi’n arfer bod yn briod neu mewn partneriaeth sifil, ond bod eich priod neu bartner sifil wedi marw?')

    # Select a valid option, click "Save and continue"
    await helpers.check_radio(field='partner_died', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Partnership Ended page
    # ------------------------------------------------
    await asserts.url('/partnership-details/ended-check')
    await asserts.accessibility()
    await asserts.h1('A ydych chi erioed wedi bod yn briod neu mewn partneriaeth sifil a ddaeth i ben?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/partnership-details/ended-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Have you ever been married or in a civil partnership that ended?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('A ydych chi erioed wedi bod yn briod neu mewn partneriaeth sifil a ddaeth i ben?')

    # Select a valid option, click "Save and continue"
    await helpers.check_radio(field='previous_partnership_ended', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Marriage details: Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/partnership-details/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion eich priodas neu bartneriaeth sifil')
    await asserts.number_of_errors(0)

    # Click "Save and continue"
    await helpers.click_button('Cadw a pharhau')
