class TestAdminElements:

    def test_homepage_elements(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications')
            html = response.data.decode()
            assert 'Download GRC applications' in html

    def test_new_applications_present_unregistered(self, app, client, submitted_application_unregistered):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#new')
            html = response.data.decode()
            assert 'New applications' in html
            assert 'View application' in html
            assert 'Register new case' in html
            assert 'Reference number' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert '/applications/ABCD1234' in html
            assert 'ABCD1234' in html
            assert '01/01/2024 09:00' in html

    def test_new_applications_present_registered(self, app, client, submitted_application_registered):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#new')
            html = response.data.decode()
            assert 'New applications' in html
            assert 'View application' in html
            assert 'Registered new case' in html
            assert 'Reference number' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert '/applications/ABCD1234' in html
            assert 'ABCD1234' in html
            assert '01/01/2024 09:00' in html

    def test_downloaded_applications_present(self, app, client, downloaded_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#downloaded')
            html = response.data.decode()
            assert 'Downloaded applications' in html
            assert 'View application' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert 'Downloaded on' in html
            assert 'Downloaded by' in html
            assert '/applications/EFGH5678' in html
            assert 'EFGH5678' in html
            assert '01/01/2024 09:00' in html

    def test_completed_applications_present(self, app, client, completed_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#completed')
            html = response.data.decode()
            assert 'Completed applications' in html
            assert 'View application' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert 'Completed on' in html
            assert 'Completed by' in html
            assert '/applications/IJKL9012' in html
            assert 'IJKL9012' in html
            assert '01/01/2024 09:00' in html

    def test_invalid_applications_present(self, app, client, invalid_submitted_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            response = client.get('/applications#new')
            html = response.data.decode()
            assert 'New applications' in html
            assert 'Reference number' in html
            assert 'Applicant name' in html
            assert 'Submitted' in html
            assert 'Valid data not found for application MNOP3456 - test.email2@example.com' in html

