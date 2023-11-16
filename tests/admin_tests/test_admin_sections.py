import re
import os
import pytest
from playwright.async_api import Page
from playwright.async_api import async_playwright
from tests.helpers.e2e_assert_helpers import AssertHelpers
from tests.helpers.e2e_page_helpers import PageHelpers
import tests.admin_tests.data as data
from grc.models import AdminUser, SecurityCode, db



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

        with app.app_context():
            with app.test_request_context():
                # Clearing existing users with test creds
                test_users_present = AdminUser.query.filter_by(email=data.EMAIL_ADDRESS).all()
                print('Existing users present:', test_users_present)
                if test_users_present:
                    for user in test_users_present:
                        db.session.delete(user)
                        db.session.commit()
                print('Pre-existing users removed')

                # Create test user in database
                test_admin_user = AdminUser(
                    email=data.EMAIL_ADDRESS,
                    password=data.HASH_PASSWORD,
                    passwordResetRequired=False,
                    dateLastLogin=data.LOCAL_PLUS_ONE_HOUR
                )
                db.session.add(test_admin_user)
                db.session.commit()

                await page.goto(TEST_URL)
                await page.fill('input[name="email_address"]', data.EMAIL_ADDRESS)
                await page.fill('input[name="password"]', data.PASSWORD)
                await helpers.click_button('Login')
                await asserts.number_of_errors(0)

                # await asserts.url('/sign-in-with-security_code')
                #
                # await asserts.h1('Check your email')
                # security_code = SecurityCode.query.filter_by(email=data.EMAIL_ADDRESS).first().code
                # await page.fill('input[name="security_code"]', security_code)
                # await helpers.click_button('Continue')

                await asserts.number_of_errors(0)
                await asserts.url('/applications')
                await asserts.h1('View and download GRC applications')

            # await asserts.number_of_errors(1)
            # await asserts.error("password", "Your password was incorrect. Please try re-entering your password")




