from playwright.async_api import Page


class PageHelpers:
    def __init__(self, page: Page):
        self.page: Page = page

    async def click_button(self, link_text):
        links_and_buttons = self.page.locator('a, button, input[type="submit"]')
        number_of_links_and_buttons = await links_and_buttons.count()
        found_index = None
        for n in range(number_of_links_and_buttons):
            link_or_button = links_and_buttons.nth(n)
            tag_name: str = await link_or_button.evaluate('e => e.tagName')
            if tag_name.lower() == 'input':
                link_or_button_text = await link_or_button.get_attribute('value')
                print("link_or_button_text -", link_or_button_text)
            else:
                link_or_button_text = await link_or_button.inner_text()
            normalised_inner_text = clean_string(link_or_button_text)
            print("normalised_inner_text -", normalised_inner_text)
            if normalised_inner_text == link_text:
                if found_index is None:
                    found_index = n
                else:
                    print(f"Error: Link/button with text ({link_text}) was found more than once")
                    assert found_index is None  # found_index

        if found_index is None:
            print(f"Error: Link/button with text ({link_text}) was not found")
        assert found_index is not None
        await links_and_buttons.nth(found_index).click()
        print(f"clicked on the button/link")

    async def check_radio(self, field, value):
        await self.page.check(f"input[type=\"radio\"][name=\"{field}\"][value=\"{value}\"]")

    async def check_checkbox(self, field, value=None):
        if value:
            await self.page.check(f"input[type=\"checkbox\"][name=\"{field}\"][value=\"{value}\"]")
        else:
            await self.page.check(f"input[type=\"checkbox\"][name=\"{field}\"]")

    async def uncheck_checkbox(self, field, value=None):
        if value:
            await self.page.uncheck(f"input[type=\"checkbox\"][name=\"{field}\"][value=\"{value}\"]")
        else:
            await self.page.uncheck(f"input[type=\"checkbox\"][name=\"{field}\"]")

    async def fill_textbox(self, field, value):
        selector = f"input[type=\"text\"][name=\"{field}\"], input[type=\"tel\"][name=\"{field}\"], input[type=\"email\"][name=\"{field}\"], input[type=\"password\"][name=\"{field}\"], textarea[name=\"{field}\"]"
        await self.page.fill(selector, value)

    async def fill_textbox_byid(self, field, value):
        selector = f"input[type=\"text\"][id=\"{field}\"], input[type=\"tel\"][id=\"{field}\"], input[type=\"email\"][id=\"{field}\"], textarea[id=\"{field}\"]"
        await self.page.fill(selector, value)

    async def upload_file_invalid_file_type(self, field):
        file_content = '{ "message": "Hello World" }'
        files = [{
            'name': 'some_file.json',
            'mimeType': 'application/json',
            'buffer': (bytes('%s' % file_content, 'utf-8'))
        }]
        await self.page.set_input_files(f"input[type=\"file\"][name=\"{field}\"]", files)

    async def upload_file_invalid_zero_bytes(self, field):
        files = [{
            'name': 'zero_bytes.pdf',
            'mimeType': 'application/pdf',
            'buffer': (bytes())
        }]
        await self.page.set_input_files(f"input[type=\"file\"][name=\"{field}\"]", files)

    async def upload_file_invalid_too_large(self, field):
        file_size_in_bytes = 11 * 1024 * 1024
        file_content = ''.ljust(file_size_in_bytes, 'A')  # 11 MB of the letter 'A'
        files = [{
            'name': 'some_file.pdf',
            'mimeType': 'application/pdf',
            'buffer': (bytes(file_content, 'utf-8'))
        }]
        await self.page.set_input_files(f"input[type=\"file\"][name=\"{field}\"]", files)

    async def upload_file_valid(self, field, file_name):
        with open('tests/end_to_end_tests/helpers/TestDocument.png', mode='rb') as file:
            image_contents = file.read()

        files = [{
            'name': file_name,
            'mimeType': 'image/png',
            'buffer': image_contents
        }]
        await self.page.set_input_files(f"input[type=\"file\"][name=\"{field}\"]", files)

    async def go_to_page(self, page):
        await self.page.goto(page)

    async def click_link_by_exact_href(self, href_value: str):
        """
        Clicks the first <a> element where the href exactly matches the provided value.
        """
        links = self.page.locator('a[href]')
        total_links = await links.count()

        for n in range(total_links):
            link = links.nth(n)
            href = await link.get_attribute('href')
            if href == href_value:
                await link.click()
                return  # Exit after clicking the first match

        raise Exception(f"No link found with href exactly equal to '{href_value}'.")

    async def click_button_by_exact_text(self, text: str):
        locator = self.page.locator(f'xpath=//button[normalize-space(text())="{text}"]')
        if await locator.is_visible():
            await locator.click()
        else:
            raise Exception(f"Button with exact text '{text}' is not visible.")


# Removes multiple sequential whitespace characters from the string
def clean_string(value: str):
    return " ".join(value.split())
