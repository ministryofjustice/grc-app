from .data import create_test_applications
from .fixtures import client
from grc.models import ApplicationStatus, Application


def test_bulk_delete_applications():
    app_one, app_two, app_three = create_test_applications(ApplicationStatus.COMPLETED)
    response = client.post("/applications/delete", data={
        f'{app_one.reference_number}': app_one.reference_number,
        f'{app_two.reference_number}': app_two.reference_number,
        f'{app_three.reference_number}': app_three.reference_number
    })
    assert response.status == 200
    deleted_applications = Application.query.filter_by(
        Application.reference_number.in_([app_one.reference_number, app_two.reference_number,
                                          app_three.reference_number]),
        email='ivan.touloumbadjian@hmcts.net')
    for app in deleted_applications:
        assert app.status == ApplicationStatus.DELETED
