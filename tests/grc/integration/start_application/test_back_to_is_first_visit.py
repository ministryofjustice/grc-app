

class TestBackToIsFirstVisit:

    def test_back_to_is_first_visit_get(self, app, client, public_user_email, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
            response = client.get('/back-to-is-first-visit')
            assert response.status_code == 302
            assert response.location == '/is-first-visit'
            with client.session_transaction() as session:
                assert session['validatedEmail'] == public_user_email
                assert session.get('reference_number') is None