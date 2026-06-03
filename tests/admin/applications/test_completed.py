from grc.models import Application, ApplicationStatus

class TestAdminApplicationsCompleted:
    def test_completed_marks_selected_application_as_completed(self, app, client, downloaded_application):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'
        response = client.post('/applications/completed', data={
            downloaded_application.reference_number: 'on'
        })

        updated_application = Application.query.filter_by(
            reference_number=downloaded_application.reference_number).first()

        assert response.status_code == 302
        assert response.location == '/applications#completed'
        assert updated_application.status == ApplicationStatus.COMPLETED
        assert updated_application.completed is not None
        assert updated_application.completedBy == 'test.email@example.com'

    def test_completed_with_no_selected_applications_redirects_to_downloaded(self, app, client):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'
                session['userType'] = 'ADMIN'

            response = client.post('/applications/completed', data={})

            assert response.status_code == 302
            assert response.location == '/applications#downloaded'
