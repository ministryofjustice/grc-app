from .data import create_test_applications, delete_test_applications
from grc.models import ApplicationStatus, Application


def test_bulk_delete_applications(app, client):
    with app.app_context():

        with client.session_transaction() as session:
            session['signedIn'] = 'test.email@example.com'

        with app.test_request_context():
            app_one, app_two, app_three = create_test_applications(status=ApplicationStatus.COMPLETED)

        response = client.post("/applications/delete", data={
            f'{app_one.reference_number}': app_one.reference_number,
            f'{app_two.reference_number}': app_two.reference_number,
            f'{app_three.reference_number}': app_three.reference_number
        })

        assert response._status_code == 302
        assert response.location == "/applications#completed"

        deleted_applications = Application.query.filter(
            Application.reference_number.in_([app_one.reference_number, app_two.reference_number,
                                              app_three.reference_number])
            ).filter_by(email='test.email@example.com')

        for app in deleted_applications:
            assert app.status == ApplicationStatus.DELETED

        delete_test_applications([app_one.reference_number, app_two.reference_number, app_three.reference_number])
