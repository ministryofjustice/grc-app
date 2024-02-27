import re
import os
import pytest
from playwright.async_api import Page
from playwright.async_api import async_playwright
from tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.helpers.e2e_page_helpers import PageHelpers
import tests.admin_tests.data as data


@pytest.mark.asyncio
async def test_admin_login_app_sections(app, client):
    TEST_URL = os.getenv('TEST_URL_ADMIN', 'http://localhost:3001')
    print('Running tests on %s' % TEST_URL)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.set_default_timeout(data.DEFAULT_TIMEOUT)

        helpers = PageHelpers(page)
        asserts = AssertHelpers(page, helpers, TEST_URL)

        await page.goto(TEST_URL)

        await asserts.url('/')
        await asserts.accessibility()
        await asserts.h1('Login to download GRC applications')
        await asserts.number_of_errors(0)
        await asserts.a('Forgot password?')

        # Enter a valid email, click Login button, see error
        await helpers.fill_textbox(field='email_address', value=data.EMAIL_ADDRESS)
        await helpers.click_button('Login')
        await asserts.url('/')
        await asserts.number_of_errors(1)
        await asserts.error(field='password', message='Enter your password')
