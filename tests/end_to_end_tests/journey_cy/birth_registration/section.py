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
    await helpers.fill_textbox(field='last_name', value=data.BIRTH_LAST_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Dob page
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
    await helpers.fill_textbox(field='day', value='1')
    await helpers.fill_textbox(field='month', value='1')
    await helpers.fill_textbox(field='year', value='1999')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- UK Check page
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
    await asserts.h1('Beth yw’r dref neu’r ddinas ar nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/place-of-birth')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is the town or city of birth on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw’r dref neu’r ddinas ar nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='place_of_birth', value=data.TOWN_OR_CITY)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Mothers Name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/mothers-name')
    await asserts.accessibility()
    await asserts.h1('Beth yw enw eich mam fel y nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/mothers-name')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your mother’s name as listed on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw enw eich mam fel y nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.MOTHER_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.MOTHER_LAST_NAME)
    await helpers.fill_textbox(field='maiden_name', value=data.MOTHER_MAIDEN_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Fathers Name Check page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name-check')
    await asserts.accessibility()
    await asserts.h1("A yw enw eich tad wedi'i nodi ar y dystysgrif?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Is your father's name listed on the certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1("A yw enw eich tad wedi'i nodi ar y dystysgrif?")

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='fathers_name_on_certificate', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Fathers Name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name')
    await asserts.accessibility()
    await asserts.h1('Beth yw enw eich tad fel y nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("What is your father's name as listed on your birth or adoption certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw enw eich tad fel y nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.FATHER_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.FATHER_LAST_NAME)
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
    await asserts.h1('Manylion Cofrestru Genedigaeth')
    await asserts.dt('Enw adeg geni')
    await asserts.dt('Dyddiad geni')
    await asserts.dt('Genedigaeth a gofrestrwyd yn y DU')
    await asserts.dt('Tref neu ddinas geni')
    await asserts.dt('Enw’r fam')
    await asserts.dt('Enw’r tad a restrwyd')
    await asserts.dt('Enw’r tad')
    await asserts.dt('Mabwysiadwyd')
    await asserts.dt('Mabwysiadwyd yn y DU')
    await asserts.dt('Gwasanaeth cofrestru’r Lluoedd, Conswl Prydeinig neu Uchel Gomisiwn, neu dan ddarpariaethau '
                     'Llongau Masnach neu Hedfan Sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Birth registration details")
    await asserts.dt('Birth name')
    await asserts.dt('Date of birth')
    await asserts.dt('Birth registered in UK')
    await asserts.dt('Town or city of birth')
    await asserts.dt("Mother's name")
    await asserts.dt("Father's name listed")
    await asserts.dt("Father's name")
    await asserts.dt('Adopted')
    await asserts.dt('Adopted in UK')
    await asserts.dt('Forces registering service, British Consul or High Commission, or under Merchant Shipping or '
                     'Civil Aviation provisions')

    await helpers.click_button('Change whether your birth was registered in the UK')

    # ------------------------------------------------
    # ---- UK Check page
    # ------------------------------------------------
    await asserts.url('/birth-registration/uk-check?check_source=section&pages_from_check=1')
    await helpers.click_button('Cymraeg')
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
    await asserts.url('/birth-registration/country?check_source=section&pages_from_check=2')
    await asserts.accessibility()
    await asserts.h1('Ym mha wlad cafodd eich genedigaeth ei chofrestru?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/country?check_source=section&pages_from_check=2')
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
    await asserts.h1('Manylion Cofrestru Genedigaeth')
    await asserts.dt('Enw adeg geni')
    await asserts.dt('Dyddiad geni')
    await asserts.dt('Genedigaeth a gofrestrwyd yn y DU')
    await asserts.dt('Gwlad enedigol gofrestredig')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Birth registration details")
    await asserts.dt('Birth name')
    await asserts.dt('Date of birth')
    await asserts.dt('Birth registered in UK')
    await asserts.dt('Registered birth country')

    await helpers.click_button('Change whether your birth was registered in the UK')

    # ------------------------------------------------
    # ---- UK Check page
    # ------------------------------------------------
    await asserts.url('/birth-registration/uk-check?check_source=section&pages_from_check=1')
    await helpers.click_button('Cymraeg')
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
    await asserts.url('/birth-registration/place-of-birth?check_source=section&pages_from_check=2')
    await asserts.accessibility()
    await asserts.h1('Beth yw’r dref neu’r ddinas ar nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/place-of-birth?check_source=section&pages_from_check=2')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is the town or city of birth on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw’r dref neu’r ddinas ar nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='place_of_birth', value=data.TOWN_OR_CITY)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Mothers Name page
    # ------------------------------------------------
    await asserts.url('/birth-registration/mothers-name?check_source=section&pages_from_check=3')
    await asserts.accessibility()
    await asserts.h1('Beth yw enw eich mam fel y nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/mothers-name?check_source=section&pages_from_check=3')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your mother’s name as listed on your birth or adoption certificate?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw enw eich mam fel y nodir ar eich tystysgrif geni neu dystysgrif mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='first_name', value=data.MOTHER_FIRST_NAME)
    await helpers.fill_textbox(field='last_name', value=data.MOTHER_LAST_NAME)
    await helpers.fill_textbox(field='maiden_name', value=data.MOTHER_MAIDEN_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Fathers Name Check page
    # ------------------------------------------------
    await asserts.url('/birth-registration/fathers-name-check?check_source=section&pages_from_check=4')
    await asserts.accessibility()
    await asserts.h1("A yw enw eich tad wedi'i nodi ar y dystysgrif?")
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/fathers-name-check?check_source=section&pages_from_check=4')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Is your father's name listed on the certificate?")
    await helpers.click_button('Cymraeg')
    await asserts.h1("A yw enw eich tad wedi'i nodi ar y dystysgrif?")

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='fathers_name_on_certificate', value='False')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Adopted page
    # ------------------------------------------------
    await asserts.url('/birth-registration/adopted?check_source=section&pages_from_check=5')
    await asserts.accessibility()
    await asserts.h1('A gawsoch chi eich mabwysiadu?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/adopted?check_source=section&pages_from_check=5')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Were you adopted?")
    await helpers.click_button('Cymraeg')
    await asserts.h1('A gawsoch chi eich mabwysiadu?')

    # Enter valid details, click Save and continue
    await helpers.check_radio(field='adopted', value='False')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Forces page
    # ------------------------------------------------
    await asserts.url('/birth-registration/forces?check_source=section&pages_from_check=6')
    await asserts.accessibility()
    await asserts.h1('A oedd eich genedigaeth wedi’i chofrestru gan wasanaeth cofrestru y Lluoedd, neu gyda Chonswl '
                     'Prydeinig neu Uwch Gomisiwn, neu dan ddarpariaethau Llongau Masnach neu Hedfan Sifil?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/forces?check_source=section&pages_from_check=6')
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
    await asserts.h1('Manylion Cofrestru Genedigaeth')
    await asserts.dt('Enw adeg geni')
    await asserts.dt('Dyddiad geni')
    await asserts.dt('Genedigaeth a gofrestrwyd yn y DU')
    await asserts.dt('Tref neu ddinas geni')
    await asserts.dt('Enw’r fam')
    await asserts.dt('Enw’r tad a restrwyd')
    await asserts.dt('Mabwysiadwyd')
    await asserts.dt('Gwasanaeth cofrestru’r Lluoedd, Conswl Prydeinig neu Uchel Gomisiwn, neu dan ddarpariaethau '
                     'Llongau Masnach neu Hedfan Sifil')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/birth-registration/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1("Birth registration details")
    await asserts.dt('Birth name')
    await asserts.dt('Date of birth')
    await asserts.dt('Birth registered in UK')
    await asserts.dt('Town or city of birth')
    await asserts.dt("Mother's name")
    await asserts.dt("Father's name listed")
    await asserts.dt('Adopted')
    await asserts.dt('Forces registering service, British Consul or High Commission, or under Merchant Shipping or '
                     'Civil Aviation provisions')
    await helpers.click_button('Cymraeg')

    # Click Save and continue
    await helpers.click_button('Cadw a pharhau')
