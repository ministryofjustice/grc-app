from playwright.async_api import Page
from tests.end_to_end_tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers
import tests.end_to_end_tests.journey_cy.data as data
import os

TEST_URL = os.getenv('TEST_URL', 'http://localhost:5000')


async def run_checks_on_section(page: Page, asserts: AssertHelpers, helpers: PageHelpers):

    # ------------------------------------------------
    # ---- Task List page
    # ------------------------------------------------
    await asserts.url('/task-list')
    await asserts.accessibility()
    await asserts.h1('Eich cais')
    await asserts.number_of_errors(0)

    # Click "Your personal details"
    await helpers.click_button('Eich manylion personol')

    # ------------------------------------------------
    # ---- Your Name page
    # ------------------------------------------------
    await asserts.url('/personal-details')
    await asserts.accessibility()
    await asserts.h1('Beth yw eich enw?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your name?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw eich enw?')

    # Enter valid details, click Save and continue
    await helpers.fill_textbox(field='title', value=data.TITLE)
    await helpers.fill_textbox(field='first_name', value=data.FIRST_NAME)
    await helpers.fill_textbox(field='middle_names', value=data.MIDDLE_NAMES)
    await helpers.fill_textbox(field='last_name', value=data.LAST_NAME)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Affirmed Gender page
    # ------------------------------------------------
    await asserts.url('/personal-details/affirmed-gender')
    await asserts.accessibility()
    await asserts.h1('Beth yw eich rhywedd a gadarnhawyd?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/affirmed-gender')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your affirmed gender?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw eich rhywedd a gadarnhawyd?')

    # Choose an option, click Save and continue
    await helpers.check_radio(field='affirmedGender', value='MALE')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Transition Date page
    # ------------------------------------------------
    await asserts.url('/personal-details/transition-date')
    await asserts.accessibility()
    await asserts.h1('Pryd wnaethoch chi drawsnewid o un rhywedd i’r llall?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/transition-date')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('When did you transition?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Pryd wnaethoch chi drawsnewid o un rhywedd i’r llall?')

    # Enter a valid date
    await helpers.fill_textbox(field='transition_date_month', value=data.TRANSITION_DATE_MONTH)
    await helpers.fill_textbox(field='transition_date_year', value=data.TRANSITION_DATE_YEAR)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Statutory Declaration Date page
    # ------------------------------------------------
    await asserts.url('/personal-details/statutory-declaration-date')
    await asserts.accessibility()
    await asserts.h1('Pryd wnaethoch chi arwyddo eich Datganiad Statudol?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/statutory-declaration-date')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('When did you sign your statutory declaration?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Pryd wnaethoch chi arwyddo eich Datganiad Statudol?')

    # Enter a valid date
    await helpers.fill_textbox(field='statutory_declaration_date_day', value=data.STATUTORY_DECLARATION_DATE_DAY)
    await helpers.fill_textbox(field='statutory_declaration_date_month', value=data.STATUTORY_DECLARATION_DATE_MONTH)
    await helpers.fill_textbox(field='statutory_declaration_date_year', value=data.STATUTORY_DECLARATION_DATE_YEAR)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Previous Name Check page
    # ------------------------------------------------
    await asserts.url('/personal-details/previous-names-check')
    await asserts.accessibility()
    await asserts.h1('Os ydych chi erioed wedi newid eich enw i adlewyrchu eich rhywedd')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/previous-names-check')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('If you have ever changed your name to reflect your gender')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Os ydych chi erioed wedi newid eich enw i adlewyrchu eich rhywedd')

    # Choose an option, click Save and continue
    await helpers.check_radio(field='previousNameCheck', value='True')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Address page
    # ------------------------------------------------
    await asserts.url('/personal-details/address')
    await asserts.accessibility()
    await asserts.h1('Beth yw eich cyfeiriad?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/address')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('What is your address?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Beth yw eich cyfeiriad?')

    # Enter valid values, click Save and continue
    await helpers.fill_textbox(field='address_line_one', value=data.ADDRESS_LINE_ONE)
    await helpers.fill_textbox(field='address_line_two', value=data.ADDRESS_LINE_TWO)
    await helpers.fill_textbox(field='town', value=data.TOWN)
    await helpers.fill_textbox(field='postcode', value=data.POSTCODE)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Contact Dates page
    # ------------------------------------------------
    await asserts.url('/personal-details/contact-dates')
    await asserts.accessibility()
    await asserts.h1('Os bydd arnom angen cysylltu â chi drwy’r post yn y 6 mis nesaf, a oes unrhyw ddyddiadau y dylid eu hosgoi?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/contact-dates')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('If we need to contact you by post in the next 6 months, are there any dates we should avoid?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Os bydd arnom angen cysylltu â chi drwy’r post yn y 6 mis nesaf, a oes unrhyw ddyddiadau y dylid eu hosgoi?')

    # Enter a valid date range
    await helpers.check_radio(field='contactDatesCheck', value='DATE_RANGE')
    await helpers.fill_textbox(field='date_ranges-0-from_date_day', value=data.CONTACT_DATE_RANGE_1_FROM_DAY)
    await helpers.fill_textbox(field='date_ranges-0-from_date_month', value=data.CONTACT_DATE_RANGE_1_FROM_MONTH)
    await helpers.fill_textbox(field='date_ranges-0-from_date_year', value=data.CONTACT_DATE_RANGE_1_FROM_YEAR)
    await helpers.fill_textbox(field='date_ranges-0-to_date_day', value=data.CONTACT_DATE_RANGE_1_TO_DAY)
    await helpers.fill_textbox(field='date_ranges-0-to_date_month', value=data.CONTACT_DATE_RANGE_1_TO_MONTH)
    await helpers.fill_textbox(field='date_ranges-0-to_date_year', value=data.CONTACT_DATE_RANGE_1_TO_YEAR)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Contact Preferences page
    # ------------------------------------------------
    await asserts.url('/personal-details/contact-preferences')
    await asserts.accessibility()
    await asserts.h1('Sut yr hoffech i ni gysylltu â chi ynghylch eich cais?')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/contact-preferences')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('How would you like to be contacted if we have any questions about your application?')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Sut yr hoffech i ni gysylltu â chi ynghylch eich cais?')

    # Choose all the options and enter a valid email address and phone number
    await helpers.check_checkbox(field='contact_options', value='EMAIL')
    await helpers.fill_textbox(field='email', value=data.EMAIL_ADDRESS)
    await helpers.check_checkbox(field='contact_options', value='PHONE')
    await helpers.fill_textbox(field='phone', value=data.PHONE_NUMBER)
    await helpers.check_checkbox(field='contact_options', value='POST')
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Notify HMRC page
    # ------------------------------------------------
    await asserts.url('/personal-details/hmrc')
    await asserts.accessibility()
    await asserts.h1('Hysbysu HMRC')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/hmrc')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Notifying HMRC')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Hysbysu HMRC')

    # Enter a valid National Insurance number
    await helpers.check_radio(field='tell_hmrc', value='True')
    await helpers.fill_textbox(field='national_insurance_number', value=data.NATIONAL_INSURANCE_NUMBER)
    await helpers.click_button('Cadw a pharhau')

    # ------------------------------------------------
    # ---- Check Your Answers page
    # ------------------------------------------------
    await asserts.url('/personal-details/check-your-answers')
    await asserts.accessibility()
    await asserts.h1('Gwiriwch eich atebion: Eich manylion personol')
    await asserts.number_of_errors(0)

    # Change language
    await asserts.url('/personal-details/check-your-answers')
    await asserts.accessibility()
    await helpers.click_button('English')
    await asserts.h1('Check your answers: Your personal details')
    await helpers.click_button('Cymraeg')
    await asserts.h1('Gwiriwch eich atebion: Eich manylion personol')

    # Click Save and continue to return to Task List page
    await helpers.click_button('Cadw a pharhau')
