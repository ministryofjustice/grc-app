class TestReferenceNumber:

    def test_reference_number(self, app, client, public_user_email, test_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['reference_number'] = test_application.reference_number
                session['identity_verified'] = True
            response = client.get('/reference-number')
            assert response.status_code == 200
            assert 'Your reference number' in response.text
            assert 'ABCD-1234' in response.text
