import jsonpickle
from datetime import date
from flask.sessions import SecureCookieSessionInterface

from grc.business_logic.data_structures.uploads_data import (
    EvidenceFile,
    MEDICAL_REPORT_SLOT_FIRST,
    MEDICAL_REPORT_SLOT_SECOND,
)
from grc.models import db


def medical_file(name, slot):
    file = EvidenceFile()
    file.original_file_name = name
    file.aws_file_name = name
    file.medical_report_slot = slot
    return file


def test_view_groups_medical_reports_once(app, client, submitted_application_unregistered):
    app.session_interface = SecureCookieSessionInterface()
    with app.app_context():
        data = submitted_application_unregistered.application_data()
        data.confirmation_data.gender_recognition_outside_uk = False
        details = data.personal_details_data
        details.title = 'Mx'
        details.first_name = 'Alex'
        details.last_name = 'Example'
        details.transition_date = date(2020, 1, 1)
        details.statutory_declaration_date = date(2021, 1, 1)
        details.address_line_one = '1 Example Street'
        details.address_town_city = 'London'
        details.address_country = 'United Kingdom'
        details.address_postcode = 'SW1A 1AA'
        birth = data.birth_registration_data
        birth.first_name = 'Alex'
        birth.last_name = 'Example'
        birth.date_of_birth = date(1990, 1, 1)
        data.uploads_data.medical_reports.extend([
            medical_file('first.pdf', MEDICAL_REPORT_SLOT_FIRST),
            medical_file('second.pdf', MEDICAL_REPORT_SLOT_SECOND),
        ])
        submitted_application_unregistered.user_input = jsonpickle.encode(data)
        db.session.commit()

    with client.session_transaction() as session:
        session['signedIn'] = 'admin@example.com'

    response = client.get('/applications/ABCD1234')

    assert response.status_code == 200
    assert response.data.count(b'Your medical reports') == 1
    assert response.data.count(b'First medical report') == 1
    assert response.data.count(b'Second medical report') == 1
    assert b'first.pdf' in response.data
    assert b'second.pdf' in response.data
