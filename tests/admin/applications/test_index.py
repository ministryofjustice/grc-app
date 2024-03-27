from tests.admin.helpers.data import create_test_applications
from grc.models import ApplicationStatus


class TestAdminElements:

    def test_homepage_elements(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications')
            html = response.data.decode()
            assert response.status_code == 200
            assert 'View and download GRC applications' in html
            assert 'Download GRC applications' in html
            assert 'New applications' in html
            assert 'Downloaded applications' in html
            assert 'Completed applications' in html

    def test_new_applications_present(self, app, client, submitted_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#new')
            html = response.data.decode()
            assert response.status_code == 200
            assert 'New applications' in html
            assert 'View application' in html
            assert 'Reference number' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html

    def test_downloaded_applications_present(self, app, client, downloadeded_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#downloaded')
            html = response.data.decode()
            assert response.status_code == 200
            assert 'Downloaded applications' in html
            assert 'View application' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert 'Downloaded on' in html
            assert 'Downloaded by' in html

    def test_completed_applications_present(self, app, client, completed_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#completed')
            html = response.data.decode()
            assert response.status_code == 200
            assert 'Completed applications' in html
            assert 'View application' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert 'Completed on' in html
            assert 'Completed by' in html
