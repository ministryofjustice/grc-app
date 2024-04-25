import jsonpickle
from datetime import datetime
from grc.models import Application, db


class ApplicationDataHelpers:

    @staticmethod
    def load_test_data(reference_number):
        application_record: Application = Application.query.filter_by(
            reference_number=reference_number
        ).first()
        return application_record.application_data()

    @staticmethod
    def save_test_data(data):
        application_record: Application = Application.query.filter_by(
            reference_number=data.reference_number
        ).first()
        user_input: str = jsonpickle.encode(data)
        application_record.user_input = user_input
        application_record.updated = datetime.now()
        db.session.commit()
