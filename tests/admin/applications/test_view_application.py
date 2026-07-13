from datetime import date, datetime

import pytest
from flask import render_template_string

from grc.business_logic.data_store import DataStore
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.personal_details_data import AffirmedGender, ContactDatesAvoid
from grc.business_logic.data_structures.partnership_details_data import CurrentlyInAPartnershipEnum
from grc.business_logic.data_structures.uploads_data import EvidenceFile
from grc.models import db


def birth_or_adoption_certificate_file():
    evidence_file = EvidenceFile()
    evidence_file.original_file_name = 'birth-certificate.pdf'
    evidence_file.aws_file_name = 'ABCD1234__birthOrAdoptionCertificate__birth-certificate.pdf'
    return evidence_file


def populate_application_data_for_view(application_data):
    application_data.confirmation_data.gender_recognition_outside_uk = False
    application_data.confirmation_data.consent_to_GRO_contact = True

    personal_details = application_data.personal_details_data
    personal_details.title = 'Mx'
    personal_details.first_name = 'Alex'
    personal_details.last_name = 'Example'
    personal_details.affirmed_gender = AffirmedGender.MALE
    personal_details.transition_date = date(2020, 1, 1)
    personal_details.statutory_declaration_date = date(2024, 1, 1)
    personal_details.changed_name_to_reflect_gender = False
    personal_details.address_line_one = '1 Test Street'
    personal_details.address_town_city = 'Test Town'
    personal_details.address_country = 'United Kingdom'
    personal_details.address_postcode = 'TE1 1ST'
    personal_details.contact_email_address = 'alex@example.com'
    personal_details.contact_by_post = False
    personal_details.contact_dates_should_avoid = False
    personal_details.contact_dates_to_avoid_option = ContactDatesAvoid.NO_DATES
    personal_details.tell_hmrc = False

    birth_registration = application_data.birth_registration_data
    birth_registration.first_name = 'Alex'
    birth_registration.last_name = 'Example'
    birth_registration.date_of_birth = date(1990, 1, 1)
    birth_registration.birth_registered_in_uk = True
    birth_registration.town_city_of_birth = 'Test City'
    birth_registration.mothers_first_name = 'Pat'
    birth_registration.mothers_last_name = 'Example'
    birth_registration.mothers_maiden_name = 'Original'
    birth_registration.fathers_name_on_birth_certificate = False
    birth_registration.adopted = False
    birth_registration.forces_registration = False

    partnership_details = application_data.partnership_details_data
    partnership_details.currently_in_a_partnership = CurrentlyInAPartnershipEnum.NEITHER
    partnership_details.previous_partnership_partner_died = False
    partnership_details.previous_partnership_ended = False

    application_data.submit_and_pay_data.applying_for_help_with_fee = False


class TestAdminViewApplicationBirthOrAdoptionCertificate:

    @pytest.fixture(autouse=True)
    def _create_schema(self, app):
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_shows_uploaded_certificate_and_no_documents_to_post(self, app, client, submitted_application_unregistered):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            application_data = DataStore.load_application('ABCD1234')
            populate_application_data_for_view(application_data)
            application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]
            DataStore.save_application(application_data)

            response = client.get('/applications/ABCD1234')
            html = response.data.decode()

            assert response.status_code == 200
            assert 'Your birth or adoption certificate' in html
            assert 'birth-certificate.pdf' in html

            documents_to_post_section = html.split('Documents to post')[1]
            assert 'Yes' not in documents_to_post_section.split('An EX160 form')[0]
            assert 'No' in documents_to_post_section

    def test_keeps_documents_to_post_when_certificate_not_uploaded(self, app, client, submitted_application_unregistered):
        with app.app_context():
            with client.session_transaction() as session:
                session['signedIn'] = 'test.email@example.com'

            application_data = DataStore.load_application('ABCD1234')
            populate_application_data_for_view(application_data)
            DataStore.save_application(application_data)

            response = client.get('/applications/ABCD1234')
            html = response.data.decode()

            assert response.status_code == 200
            documents_to_post_section = html.split('Documents to post')[1]
            assert 'Yes' in documents_to_post_section.split('An EX160 form')[0]


class TestAdminGeneratedPdfBirthOrAdoptionCertificate:

    def test_admin_pdf_omits_certificate_from_documents_to_post_when_uploaded(self, app):
        with app.app_context():
            with app.test_request_context():
                application_data = ApplicationData()
                populate_application_data_for_view(application_data)
                application_data.updated = datetime(2024, 1, 1, 9)
                application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]

                response = render_template_string(
                    "{% from 'applications/application-pdfkit.html' import adminapplication %}"
                    "{{ adminapplication(application_data) }}",
                    application_data=application_data
                )

                documents_to_post_section = response.split('Documents to post')[1]
                assert 'your original or a certified copy of your full birth or adoption certificate' not in documents_to_post_section
                assert 'None' in documents_to_post_section

    def test_admin_pdf_keeps_certificate_in_documents_to_post_when_not_uploaded(self, app):
        with app.app_context():
            with app.test_request_context():
                application_data = ApplicationData()
                populate_application_data_for_view(application_data)
                application_data.updated = datetime(2024, 1, 1, 9)

                response = render_template_string(
                    "{% from 'applications/application-pdfkit.html' import adminapplication %}"
                    "{{ adminapplication(application_data) }}",
                    application_data=application_data
                )

                documents_to_post_section = response.split('Documents to post')[1]
                assert 'your original or a certified copy of your full birth or adoption certificate' in documents_to_post_section
