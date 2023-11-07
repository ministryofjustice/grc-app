from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc.business_logic.data_store import DataStore
from grc.models import db, Application, ApplicationStatus


def create_test_applications(status: ApplicationStatus):
    test_completed_apps = []
    for _ in range(3):
        app = DataStore.create_new_application('ivan.touloumbadjian@hmcts.net')
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


def delete_test_applications(application_references: [Application.reference_number]):
    Application.query.filter(
        Application.reference_number.in_(application_references)
    ).filter_by(email='ivan.touloumbadjian@hmcts.net').delete()
    db.session.commit()
    print(f'applications - {application_references} deleted', flush=True)

