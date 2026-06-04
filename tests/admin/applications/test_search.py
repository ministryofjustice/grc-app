
class TestAdminApplicationSearch:

    def test_search_get(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'

            response = client.get('/applications/search')

            assert response.status_code == 200
            assert 'Search' in response.text

    def test_search_by_reference_number_valid(self, app, client, submitted_application_unregistered):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'

            response = client.post('/applications/search-by-reference-number', data={
                'reference_number': 'abcd-1234'
            })

            assert response.status_code == 302
            assert response.location == '/applications/ABCD1234'

    def test_search_by_reference_number_invalid(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'

            response = client.post('/applications/search-by-reference-number', data={
                'reference_number': 'invalid'
            })

            assert response.status_code == 200
            assert 'invalid' in response.text
