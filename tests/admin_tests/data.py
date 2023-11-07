from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc.business_logic.data_store import DataStore
from grc.models import db, Application, ApplicationStatus


def create_test_applications(status: ApplicationStatus, number_of_applications: int):
    test_completed_apps = []
    for _ in range(number_of_applications):
        app = DataStore.create_new_application('test.email@example.com')
        db.session.commit()
        new_app = Application.query.filter_by(
            reference_number=app.reference_number,
            email=app.email_address
        ).first()
        new_app.status = status
        new_app.completed = datetime.now() - relativedelta(days=7)
        db.session.commit()
        print(f'Test ADMIN Completed App Ref - {new_app.reference_number}', flush=True)
        test_completed_apps.append(new_app)
    return test_completed_apps


def delete_test_applications(*application_references_lists: [Application.reference_number]):
    if application_references_lists:
        for app_refs in application_references_lists:
            Application.query.filter(
                Application.reference_number.in_(app_refs)
            ).filter_by(email='test.email@example.com').delete()
            db.session.commit()
            print(f'applications - {app_refs} deleted', flush=True)

