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

    # Change language
    await asserts.url('/task-list')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Your application')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Eich cais')

    await helpers.click_button('Gwybodaeth am gofrestru eich genedigaeth')

    # ------------------------------------------------
    # ---- Birth registration page
    # ------------------------------------------------
    await asserts.url('/birth-registration')
    await asserts.accessibility()
    await asserts.h1('Pa enw oedd wedi’i gofrestru’n wreiddiol ar eich tystysgrif geni neu’ch tystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What name was originally registered on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Pa enw oedd wedi’i gofrestru’n wreiddiol ar eich tystysgrif geni neu’ch tystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.BIRTH_FIRST_NAME)
    await helpers.fill_textbox(field='middle_names', value=data.BIRTH_MIDDLE_NAME)
    await helpers.fill_textbox(field='last_name', value=data.BIRTH_LAST_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Date of Birth page
    # ------------------------------------------------
    await asserts.url('/birth-registration/dob')
    await asserts.accessibility()
    await asserts.h1('Beth yw’r dyddiad geni ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/dob')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is the date of birth on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw’r dyddiad geni ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='day', value=data.DATE_OF_BIRTH_DAY)
    await helpers.fill_textbox(field='month', value=data.DATE_OF_BIRTH_MONTH)
    await helpers.fill_textbox(field='year', value=data.DATE_OF_BIRTH_YEAR)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Birth Registered in UK page
    # ------------------------------------------------
    await asserts.url('/birth-registration/uk-check')
    await asserts.accessibility()
    await asserts.h1('A gafodd eich genedigaeth ei chofrestru yn y DU?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/uk-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Was your birth registered in the UK?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('A gafodd eich genedigaeth ei chofrestru yn y DU?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='birth_registered_in_uk', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Place of Birth page
    # ------------------------------------------------
    await asserts.url('/birth-registration/place-of-birth')
    await asserts.accessibility()
    await asserts.h1('Beth yw’r dref neu’r ddinas a nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/place-of-birth')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is the town or city of birth on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw’r dref neu’r ddinas a nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='place_of_birth', value=data.BIRTH_TOWN)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Mothers Name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/mothers-name')
    await asserts.accessibility()
    await asserts.h1('Beth yw enw eich rhiant cyntaf fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/mothers-name')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("What is your first parent's name as listed on your birth or adoption certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw enw eich rhiant cyntaf fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.MOTHERS_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.MOTHERS_LAST_NAME)
    await helpers.fill_textbox(field='maiden_name', value=data.MOTHERS_MAIDEN_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Is Second parent's name On Certificate page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name-check')
    await asserts.accessibility()
    await asserts.h1("A yw enw eich ail riant wedi'i restru ar y dystysgrif?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Is your second parent's name listed on the certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1("A yw enw eich ail riant wedi'i restru ar y dystysgrif?")

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='fathers_name_on_certificate', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Fathers Name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name')
    await asserts.accessibility()
    await asserts.h1('Beth yw enw eich ail riant fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("What is your second parent's name as listed on your birth or adoption certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw enw eich ail riant fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.FATHERS_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.FATHERS_LAST_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Adopted page
    # ------------------------------------------------
    await asserts.url('/birth-registration/adopted')
    await asserts.accessibility()
    await asserts.h1('A gawsoch chi eich mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/adopted')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Were you adopted?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A gawsoch chi eich mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='adopted', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Adopted in UK page
    # ------------------------------------------------
    await asserts.url('/birth-registration/adopted-uk')
    await asserts.accessibility()
    await asserts.h1('A gawsoch chi eich mabwysiadu yn y Deyrnas Unedig?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/adopted-uk')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Were you adopted in the United Kingdom?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A gawsoch chi eich mabwysiadu yn y Deyrnas Unedig?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='adopted_uk', value='ADOPTED_IN_THE_UK_YES')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Forces page
    # ------------------------------------------------
    await asserts.url('/birth-registration/forces')
    await asserts.accessibility()
    await asserts.h1('A oedd eich genedigaeth wedi’i chofrestru gan wasanaeth cofrestru y Lluoedd, neu gyda Chonswl '
                     'Prydeinig neu Uwch Gomisiwn, neu dan ddarpariaethau Llongau Masnach neu Hedfan Sifil?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/forces')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Was your birth registered by a Forces registering service, or with a British Consul or High "
                     "Commission, or under Merchant Shipping or Civil Aviation provisions?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A oedd eich genedigaeth wedi’i chofrestru gan wasanaeth cofrestru y Lluoedd, neu gyda Chonswl '
                     'Prydeinig neu Uwch Gomisiwn, neu dan ddarpariaethau Llongau Masnach neu Hedfan Sifil?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='forces', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion Cofrestru Genedigaeth')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Check your answers: Birth registration details")
    await helpers.click_button('Cymraeg')

    await helpers.click_button('Newid whether your birth was registered in the UK')

    # ------------------------------------------------
    # ---- UK Check page
    # ------------------------------------------------
    await asserts.url('/birth-registration/uk-check')
    await asserts.accessibility()
    await asserts.h1('A gafodd eich genedigaeth ei chofrestru yn y DU?')
    await asserts.number_of_errors(0)
    await helpers.click_button('English')
    await asserts.h1('Was your birth registered in the UK?')
    await helpers.click_button('Cymraeg')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='birth_registered_in_uk', value='False')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Country page
    # ------------------------------------------------
    await asserts.url('/birth-registration/country')
    await asserts.accessibility()
    await asserts.h1('Ym mha wlad cafodd eich genedigaeth ei chofrestru?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/country')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("What country was your birth registered in?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('Ym mha wlad cafodd eich genedigaeth ei chofrestru?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='country_of_birth', value=data.COUNTRY_OF_BIRTH)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion Cofrestru Genedigaeth')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Check your answers: Birth registration details")
    await helpers.click_button('Cymraeg')

    await helpers.click_button('Newid whether your birth was registered in the UK')

    # ------------------------------------------------
    # ---- UK Check page
    # ------------------------------------------------
    await asserts.url('/birth-registration/uk-check')
    await asserts.accessibility()
    await asserts.h1('A gafodd eich genedigaeth ei chofrestru yn y DU?')
    await asserts.number_of_errors(0)
    await helpers.click_button('English')
    await asserts.h1('Was your birth registered in the UK?')
    await helpers.click_button('Cymraeg')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='birth_registered_in_uk', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Place of Birth page
    # ------------------------------------------------
    await asserts.url('/birth-registration/place-of-birth')
    await asserts.accessibility()
    await asserts.h1('Beth yw’r dref neu’r ddinas a nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/place-of-birth')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is the town or city of birth on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw’r dref neu’r ddinas a nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='place_of_birth', value=data.BIRTH_TOWN)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Mothers Name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/mothers-name')
    await asserts.accessibility()
    await asserts.h1('Beth yw enw eich rhiant cyntaf fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/mothers-name')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("What is your first parent's name as listed on your birth or adoption certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw enw eich rhiant cyntaf fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.MOTHERS_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.MOTHERS_LAST_NAME)
    await helpers.fill_textbox(field='maiden_name', value=data.MOTHERS_MAIDEN_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Is second parent's name On Certificate page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name-check')
    await asserts.accessibility()
    await asserts.h1("A yw enw eich ail riant wedi'i restru ar y dystysgrif?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Is your second parent's name listed on the certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1("A yw enw eich ail riant wedi'i restru ar y dystysgrif?")

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='fathers_name_on_certificate', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- second parent's name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name')
    await asserts.accessibility()
    await asserts.h1("Beth yw enw eich ail riant fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("What is your second parent's name as listed on your birth or adoption certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1("Beth yw enw eich ail riant fel y’i nodwyd ar eich tystysgrif geni neu fabwysiadu?")

    # Enter valid values, click "Save and continue"
    await helpers.fill_textbox(field='first_name', value=data.FATHERS_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.FATHERS_LAST_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Adopted page
    # ------------------------------------------------
    await asserts.url('/birth-registration/adopted')
    await asserts.accessibility()
    await asserts.h1('A gawsoch chi eich mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/adopted')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Were you adopted?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A gawsoch chi eich mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='adopted', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Adopted in UK page
    # ------------------------------------------------
    await asserts.url('/birth-registration/adopted-uk')
    await asserts.accessibility()
    await asserts.h1('A gawsoch chi eich mabwysiadu yn y Deyrnas Unedig?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/adopted-uk')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Were you adopted in the United Kingdom?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A gawsoch chi eich mabwysiadu yn y Deyrnas Unedig?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='adopted_uk', value='ADOPTED_IN_THE_UK_DO_NOT_KNOW')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Forces page
    # ------------------------------------------------
    await asserts.url('/birth-registration/forces')
    await asserts.accessibility()
    await asserts.h1('A oedd eich genedigaeth wedi’i chofrestru gan wasanaeth cofrestru y Lluoedd, neu gyda Chonswl '
                     'Prydeinig neu Uwch Gomisiwn, neu dan ddarpariaethau Llongau Masnach neu Hedfan Sifil?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/forces')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Was your birth registered by a Forces registering service, or with a British Consul or High "
                     "Commission, or under Merchant Shipping or Civil Aviation provisions?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A oedd eich genedigaeth wedi’i chofrestru gan wasanaeth cofrestru y Lluoedd, neu gyda Chonswl '
                     'Prydeinig neu Uwch Gomisiwn, neu dan ddarpariaethau Llongau Masnach neu Hedfan Sifil?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='forces', value='False')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Manylion Cofrestru Genedigaeth')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Check your answers: Birth registration details")
    await helpers.click_button('Cymraeg')

    # Click Save and continue
    await helpers.click_button('Cadw a pharhau')
