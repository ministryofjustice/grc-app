from admin import create_app
from admin.config import TestConfig
from .data import create_test_applications
from grc.models import ApplicationStatus, Application


def create_test_app():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    flask_app = create_app(TestConfig)
    flask_app.config['WTF_CSRF_ENABLED'] = False
    return flask_app


def test_bulk_delete_applications():
    flask_app = create_test_app()

    with flask_app.test_client() as test_client:
        with test_client.session_transaction() as session:
            session['signedIn'] = 'ivan.touloumbadjian@hmcts.net'
        _ = test_client.get('/')
        app_one, app_two, app_three = create_test_applications(ApplicationStatus.COMPLETED)
        response = test_client.post("/applications/delete", data={
            f'{app_one.reference_number}': app_one.reference_number,
            f'{app_two.reference_number}': app_two.reference_number,
            f'{app_three.reference_number}': app_three.reference_number
        })
        assert response._status_code == 302
        assert response.location == "/applications#completed"
        deleted_applications = Application.query.filter(
            Application.reference_number.in_([app_one.reference_number, app_two.reference_number,
                                              app_three.reference_number])
            ).filter_by(email='ivan.touloumbadjian@hmcts.net')
        for app in deleted_applications:
            assert app.status == ApplicationStatus.DELETED
