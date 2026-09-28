from admin.glimr.glimr_new_case import GlimrNewCase
from grc.business_logic.data_structures.application_data import ApplicationData


class StubApplication:
    def __init__(self, data):
        self.data = data

    def application_data(self):
        return self.data


def test_glimr_params_keep_single_documents_url(app):
    app.config['BUCKET_NAME'] = 'test-bucket'
    data = ApplicationData()
    data.reference_number = 'ABCD1234'
    data.confirmation_data.gender_recognition_outside_uk = False
    details = data.personal_details_data
    details.title = 'Mx'
    details.first_name = 'Alex'
    details.middle_names = ''
    details.last_name = 'Example'
    details.contact_email_address = 'alex@example.com'
    details.contact_phone_number = '01234567890'
    details.address_line_one = '1 Example Street'
    details.address_line_two = None
    details.address_town_city = 'London'
    details.address_postcode = 'SW1A 1AA'
    details.address_country = 'United Kingdom'

    with app.app_context():
        params = GlimrNewCase(StubApplication(data)).params()

    assert params['jurisdictionId'] == 2000000
    assert params['track'] == 'GRP General'
    assert params['onlineMappingCode'] == 'GRP_STANDARD'
    assert params['documentsUrl'] == 'https://test-bucket.s3.eu-west-2.amazonaws.com/ABCD1234.pdf'
    assert 'firstMedicalReport' not in params
    assert 'secondMedicalReport' not in params
    assert 'documents' not in params
