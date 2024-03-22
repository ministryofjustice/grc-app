from tests.admin.helpers.data import create_test_applications, delete_test_applications
from grc.models import ApplicationStatus, Application


def test_bulk_delete_applications(app, client):
    with app.app_context():

        with client.session_transaction() as session:
            session['signedIn'] = 'test.email@example.com'

        with app.test_request_context():
            app_one, app_two, app_three = create_test_applications(status=ApplicationStatus.COMPLETED,
                                                                   number_of_applications=3)
            app_to_ignore_one, app_to_ignore_two = create_test_applications(status=ApplicationStatus.COMPLETED,
                                                                            number_of_applications=2)

        response = client.post("/applications/delete", data={
            f'{app_one.reference_number}': app_one.reference_number,
            f'{app_two.reference_number}': app_two.reference_number,
            f'{app_three.reference_number}': app_three.reference_number
        })

        assert response._status_code == 302
        assert response.location == "/applications#completed"

        deleted_application_references = [app_one.reference_number, app_two.reference_number,
                                          app_three.reference_number]

        ignored_applications_references = [app_to_ignore_one.reference_number, app_to_ignore_two.reference_number]

        deleted_applications = Application.query.filter(
            Application.reference_number.in_(deleted_application_references)
            ).filter_by(email='test.email@example.com')

        ignored_applications = Application.query.filter(
            Application.reference_number.in_(ignored_applications_references)
            ).filter_by(email='test.email@example.com')

        for app in deleted_applications:
            assert app.status == ApplicationStatus.DELETED

        for app in ignored_applications:
            assert app.status == ApplicationStatus.COMPLETED

        delete_test_applications(deleted_application_references, ignored_applications_references)
