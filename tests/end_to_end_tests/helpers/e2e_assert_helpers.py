import re

from playwright.async_api import Page, expect

from tests.end_to_end_tests.accessibility.accessibility_checks import AccessibilityChecks
from tests.end_to_end_tests.helpers.e2e_page_helpers import PageHelpers, clean_string


class AssertHelpers:
    def __init__(self, page: Page, helpers: PageHelpers, base_url: str):
        self.page: Page = page
        self.helpers: PageHelpers = helpers
        self.base_url = base_url
        self.accessibility_checks = AccessibilityChecks()

    async def new_page(self, url: str, h1: str, errors: int):
        await self.url(expected_url=url)
        await self.accessibility()
        await self.h1(expected_h1_text=h1)
        await self.number_of_errors(expected_nuber_of_errors=errors)

    async def url(self, expected_url: str):
        await self.page.wait_for_load_state()
        actual_url = get_url_path(self.page.url)
        assert_equal(actual_url, expected_url)

    async def url_matches_regex(self, expected_url_regex: str):
        await self.page.wait_for_load_state()
        actual_url = get_url_path(self.page.url)
        assert_matches_regex(actual_url, expected_url_regex)

    async def error(self, field: str, message: str):
        error_summary_message = clean_string(
            await self.page.inner_text(f".govuk-error-summary__list a[href=\"#{field}\"]"))
        assert_equal(error_summary_message, message)

        field_error_message = clean_string(await self.page.inner_text(f"#{field}-error"))
        expected_field_error_message = f"Error: {message}"
        assert_equal(field_error_message, expected_field_error_message)

    async def number_of_errors(self, expected_nuber_of_errors: int):
        number_of_errors_in_error_summary = await self.page.locator('.govuk-error-summary__list li').count()
        # assert_equal(number_of_errors_in_error_summary, expected_nuber_of_errors)

        number_of_error_messages_on_page = await self.page.locator('.govuk-error-message').count()
        # assert_equal(number_of_error_messages_on_page, expected_nuber_of_errors)

        if expected_nuber_of_errors == 0:
            number_of_elements_with_error_class = await self.page.locator('*[class$="--error"]').count()
            assert_equal(number_of_elements_with_error_class, 0)

    async def h1(self, expected_h1_text: str):
        actual_h1_text = clean_string(await self.page.inner_text('h1'))
        assert_equal(actual_h1_text, expected_h1_text)

    async def fieldset_legend(self, expected_fieldset_legend_text: str):
        actual_fieldset_legend_text = clean_string(await self.page.inner_text('.govuk-fieldset__legend'))
        assert_equal(actual_fieldset_legend_text, expected_fieldset_legend_text)

    async def page_does_not_contain_text(self, *not_expected_text_list: str):
        page_text = await self.page.inner_text('body')
        page_text_lowercase = page_text.lower()
        for not_expected_text in not_expected_text_list:
            not_expected_text_lowercase = not_expected_text.lower()
            assert not_expected_text_lowercase not in page_text_lowercase

    async def accessibility(self, page_description: str = None):
        await self.accessibility_checks.run_checks_on_page(self.page, page_description)

    def run_final_accessibility_checks(self):
        self.accessibility_checks.run_final_checks()

    async def task_list_sections(self, expected_number_of_sections: int):
        sections = self.page.locator('.app-task-list__item')
        number_of_sections = await sections.count()
        if (number_of_sections != expected_number_of_sections):
            for n in range(number_of_sections):
                section = sections.nth(n)
                print(await section.inner_text())
        assert_equal(number_of_sections, expected_number_of_sections)

    async def task_list_section(self, section: str, expected_status: str):
        selector = f".app-task-list__item:has(.app-task-list__task-name:text-is(\"{section}\")) .app-task-list__tag, " \
                   f".app-task-list__item:has(.app-task-list__task-name a:text-is(\"{section}\")) .app-task-list__tag"
        status = await self.page.inner_text(selector)
        assert_equal(status, expected_status)

    async def field_value(self, field: str, expected_value: str):
        selector = f"input[name=\"{field}\"], textarea[name=\"{field}\"]"
        actual_value = await self.page.input_value(selector)
        assert_equal(actual_value, expected_value)

    async def field_not_visible(self, field):
        visible = await self.page.get_by_role('input', name=f'{field}').is_visible()
        assert_equal(visible, False)

    async def is_checked(self, field: str, value=None):
        if value:
            selector = f"input[type=\"radio\"][name=\"{field}\"][value=\"{value}\"], " \
                       f"input[type=\"checkbox\"][name=\"{field}\"][value=\"{value}\"] "
        else:
            selector = f"input[type=\"radio\"][name=\"{field}\"], " \
                       f"input[type=\"checkbox\"][name=\"{field}\"] "

        element_is_checked = await self.page.is_checked(selector)
        assert_equal(element_is_checked, True)

    async def not_checked(self, field: str, value=None):
        if value:
            selector = f"input[type=\"radio\"][name=\"{field}\"][value=\"{value}\"], " \
                       f"input[type=\"checkbox\"][name=\"{field}\"][value=\"{value}\"] "
        else:
            selector = f"input[type=\"radio\"][name=\"{field}\"], " \
                       f"input[type=\"checkbox\"][name=\"{field}\"] "

        element_is_checked = await self.page.is_checked(selector)
        assert_equal(element_is_checked, False)

    async def check_your_answers_rows(self, expected_number_of_rows: int):
        rows = self.page.locator('.govuk-summary-list__row')
        actual_number_of_rows = await rows.count()
        if (actual_number_of_rows != expected_number_of_rows):
            for n in range(actual_number_of_rows):
                row = rows.nth(n)
                print(await row.inner_text())
        assert_equal(actual_number_of_rows, expected_number_of_rows)

    async def check_your_answers_row(self, row_name: str, expected_value: str):
        selector = f".govuk-summary-list__row:has(.govuk-summary-list__key:text-is(\"{row_name}\")) .govuk-summary-list__value"
        status = await self.page.inner_text(selector)
        assert_equal(status, expected_value)

    async def check_your_answers_row_missing(self, row_name: str):
        selector = f".govuk-summary-list__key:text-is(\"{row_name}\")"
        number_of_matching_rows = await self.page.locator(selector).count()
        assert_equal(number_of_matching_rows, 0)

    async def change_links_to_url(self,
                                  link_text: str,
                                  expected_url: str,
                                  back_link_should_return_to_check_page: bool = True,
                                  save_button_should_return_to_check_page: bool = True,
                                  save_and_continue_button_text: str = 'Save and continue'):
        url_before = self.page.url

        if back_link_should_return_to_check_page:
            print_now(f"Clicking 'Change' then 'Back' expecting url:{expected_url}")
            # Click on the "Change" link
            await self.helpers.click_button(link_text)
            await self.url(expected_url)

            # Then click on the "Back" link
            await self.helpers.click_button('Back')
            await self.page.wait_for_load_state()
            url_after = self.page.url
            assert_equal(url_after, url_before)

        if save_button_should_return_to_check_page:
            print_now(f"Clicking 'Change' then '{save_and_continue_button_text}' expecting url:{expected_url}")
            # Click on the "Change" link
            await self.helpers.click_button(link_text)
            await self.url(expected_url)

            # Then click on the "Save and continue" button
            await self.helpers.click_button(save_and_continue_button_text)
            await self.page.wait_for_load_state()
            url_after = self.page.url
            assert_equal(url_after, url_before)

        if not back_link_should_return_to_check_page and not save_button_should_return_to_check_page:
            print_now(f"Clicking 'Change' then browser back button expecting url:{expected_url}")
            # Click on the "Change" link
            await self.helpers.click_button(link_text)
            await self.url(expected_url)

            # Really, we want to click on the "Back" link and/or the "Save and continue" button
            #  But, a few pages don't have the these actions wired up to return to the "Check your answers" page :-(
            #  So, instead, we use the browser's back button
            await self.page.go_back()  # <-- What we use instead

            await self.page.wait_for_load_state()
            url_after = self.page.url
            assert_equal(url_after, url_before)

        await self.page.wait_for_load_state()
        url_after = self.page.url
        assert_equal(url_after, url_before)

    async def documents_uploaded(self, expected_number_of_documents_already_uploaded):
        actual_number_of_documents_already_uploaded = await self.page.locator('.govuk-summary-list__row').count()
        assert_equal(actual_number_of_documents_already_uploaded, expected_number_of_documents_already_uploaded)

    async def document_uploaded(self, file_name):
        selector = f".govuk-summary-list__row:has(.govuk-summary-list__value:has-text(\"{file_name}\"))"
        matching_elements = await self.page.locator(selector).count()
        assert_equal(matching_elements, 1)

    async def no_button(self, link_text):
        links_and_buttons = self.page.locator('a, button, input[type="submit"]')
        number_of_links_and_buttons = await links_and_buttons.count()
        found_index = None
        for n in range(number_of_links_and_buttons):
            link_or_button = links_and_buttons.nth(n)
            tag_name: str = await link_or_button.evaluate('e => e.tagName')
            if tag_name.lower() == 'input':
                link_or_button_text = await link_or_button.get_attribute('value')
            else:
                link_or_button_text = await link_or_button.inner_text()
            normalised_inner_text = clean_string(link_or_button_text)
            if normalised_inner_text == link_text:
                if found_index is None:
                    found_index = n
                else:
                    print(f"Error: Link/button with text ({link_text}) was found more than once")
                    assert found_index is None  # found_index

        if found_index is not None:
            print(f"Error: Link/button with text ({link_text}) was found")
        assert found_index is None

    async def check_case_is_registered(self, reference_number: str):
        checkbox = f"input[type=\"checkbox\"][name=\"{reference_number}\"] "
        checkbox_label = f"label[name=label-{reference_number}] "

        checkbox_is_checked = await self.page.is_checked(checkbox)
        # checkbox_is_disabled = await self.page.locator(checkbox).is_disabled()
        checkbox_label_text = await self.page.locator(checkbox_label).inner_text()

        # assert_equal(checkbox_is_disabled, True)
        assert_equal(checkbox_is_checked, True)
        assert_equal(checkbox_label_text, "Registered new case")

    async def check_case_is_not_registered(self, reference_number: str):
        checkbox_label = f"label[id=\"label-{reference_number}\"]"
        checkbox_label_text = await self.page.locator(checkbox_label).inner_text()

        assert_equal(checkbox_label_text, "Register new case")

    async def button_disabled(self, field: str):
        button_locator = self.page.locator(f'button#{field}')

        class_attribute = await button_locator.get_attribute('class')

        is_disabled_by_class = class_attribute and "govuk-button--disabled" in class_attribute
        is_disabled_by_attribute = await button_locator.get_attribute('disabled') is not None

        is_disabled = is_disabled_by_class and is_disabled_by_attribute

        assert_equal(is_disabled, True)

    async def button_enabled(self, field: str):
        button_locator = self.page.locator(f'button#{field}')

        class_attribute = await button_locator.get_attribute('class')

        is_enabled_by_class = class_attribute and "govuk-button--disabled" not in class_attribute
        is_enabled_by_attribute = await button_locator.get_attribute('disabled') is None

        is_enabled = is_enabled_by_class and is_enabled_by_attribute

        assert_equal(is_enabled, True)

    # can be used for any h1 , h2 and h3
    # async def check_heading(self, level: int, expected_text: str):
    #     selector = f'h{level}'
    #     actual_text = clean_string(await self.page.inner_text(selector))
    #     assert_equal(actual_text, expected_text)

    async def h2(self, expected_h2_text: str):
        h2_elements = await self.page.query_selector_all('h2')
        actual_texts = [clean_string(await el.inner_text()) for el in h2_elements]
        assert expected_h2_text in actual_texts

    async def single_text_not_displayed(self, first_row_reference_number: str):
        elements = self.page.locator(f"text={first_row_reference_number}")
        expect(elements).not_to_be_visible()


def get_url_path(url: str):
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]

    first_slash_position = url.find('/')
    url = url[first_slash_position:]

    question_mark_position = url.find('?')
    if question_mark_position != -1:
        url = url[:question_mark_position]

    hash_position = url.find('#')
    if hash_position != -1:
        url = url[:hash_position]
    return url


# This method looks pointless, but helps give informative stack traces
# The parameter values are shown in the stack trace,
#   so it's really clear to see what the expected and actual values are
def assert_equal(actual_value, expected_value):
    if actual_value != expected_value:
        print(f"Actual value does not equal expected value\n"
              f"- actual value: ({actual_value})\n"
              f"- expected value: ({expected_value})", flush=True)
    assert actual_value == expected_value


def single_text_not_displayed(self, text: str, timeout: float = 5000):
    elements = self.page.locator(f"text={text}")
    expect(elements).not_to_be_visible(timeout=timeout)


def assert_matches_regex(actual_value, expected_regex):
    pattern = re.compile(expected_regex)
    matches = pattern.match(actual_value)
    if matches is None:
        print(f"Actual value does not match expected regex\n"
              f"- actual value: ({actual_value})\n"
              f"- expected regex: ({expected_regex})", flush=True)
    assert matches is not None


def print_now(message):
    print(message, flush=True)


async def url_contains_text(self, expected_value: str):
    await self.page.wait_for_load_state()
    actual_url = get_url_path(self.page.url)
    assert expected_value in actual_url
