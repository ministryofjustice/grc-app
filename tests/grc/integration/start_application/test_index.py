import pytest
from flask.sessions import SecureCookieSessionInterface


@pytest.fixture()
def client(app):
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.session_interface = SecureCookieSessionInterface()
    return app.test_client()


class TestIndex:
    def assert_english_digital_support_content(self, response):
        assert 'Get help applying online' in response.text
        assert (
            'If you do not have access to the internet or do not feel confident using it, contact We Are Group.'
            in response.text
        )
        assert 'We Are Group' in response.text
        assert 'support@wearegroup.com' in response.text
        assert 'Telephone:' in response.text
        assert '03300 160 051' in response.text
        assert 'Monday to Friday, 9am to 5pm' in response.text
        assert 'Closed on bank holidays' in response.text
        assert 'Text FORM to 60777 and someone will call you back' in response.text
        assert 'Find out about call charges' in response.text

    def assert_digital_support_links(self, response, call_charges_url='https://www.gov.uk/call-charges'):
        digital_support_html = response.text.split('<section id="digital-support"')[1].split('</section>')[0]
        assert (
            '<a href="https://www.wearegroup.com/digital_support" class="govuk-link">We Are Group</a>'
            in digital_support_html
        )
        assert (
            '<a href="mailto:support@wearegroup.com" class="govuk-link">support@wearegroup.com</a>'
            in digital_support_html
        )
        assert (
            '<a href="tel:+443300160051" class="govuk-link">03300 160 051</a>'
            in digital_support_html
        )
        assert f'<a href="{call_charges_url}" class="govuk-link">' in digital_support_html
        assert 'target=' not in digital_support_html

    def assert_welsh_digital_support_content(self, response):
        assert 'Cael cymorth i wneud cais ar-lein' in response.text
        assert (
            "Os nad oes gennych fynediad i'r rhyngrwyd neu os nad ydych yn teimlo'n hyderus yn ei ddefnyddio, "
            'cysylltwch â We Are Group.' in response.text
        )
        assert 'Rhif ffôn:' in response.text
        assert 'Monday to Friday, 9am to 5pm' in response.text
        assert 'dydd Gwener 9am i 4.30pm' not in response.text
        assert 'Ar gau ar wyliau banc' in response.text
        assert "Tecstiwch FORM i 60777 a bydd rhywun yn eich ffonio'n ôl" in response.text
        assert 'Rhagor o wybodaeth am gostau galwadau' in response.text

    def test_index(self, app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200
            assert 'Start or return to an application' in response.text
            self.assert_english_digital_support_content(response)
            self.assert_digital_support_links(response)

    def test_index_welsh_uses_language_neutral_support_values_and_welsh_call_charges(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['lang_code'] = 'cy'

            response = client.get('/')

            assert response.status_code == 200
            self.assert_welsh_digital_support_content(response)
            assert 'We Are Group' in response.text
            assert 'support@wearegroup.com' in response.text
            assert '03300 160 051' in response.text
            self.assert_digital_support_links(response, call_charges_url='https://www.gov.uk/costau-galwadau')

    def test_index_post_no_choice(self, app, client):
        with app.app_context():
            form_data = {'new_application': None}
            response = client.post('/', data=form_data)
            assert response.status_code == 200
            assert 'Start or return to an application' in response.text
            self.assert_english_digital_support_content(response)
            self.assert_digital_support_links(response)
            assert 'Select if you have already started an application' in response.text

    def test_index_start_application(self, app, client):
        with app.app_context():
            form_data = {'new_application': True}
            response = client.post('/', data=form_data)
            assert response.status_code == 302
            assert response.location == '/one-login/authenticate'

    def test_index_post_valid_email(self, app, client):
        with app.app_context():
            form_data = {'new_application': False}
            response = client.post('/', data=form_data)
            assert response.status_code == 302
            assert response.location == '/your-reference-number'
