from types import SimpleNamespace
from datetime import date, datetime

from flask import g, render_template, render_template_string

from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.personal_details_data import AffirmedGender, ContactDatesAvoid
from grc.business_logic.data_structures.partnership_details_data import CurrentlyInAPartnershipEnum
from grc.business_logic.data_structures.submit_and_pay_data import HelpWithFeesType
from grc.business_logic.data_structures.uploads_data import EvidenceFile
from grc.list_status import ListStatus
from grc.submit_and_pay.forms import CheckYourAnswers


def birth_or_adoption_certificate_file():
    evidence_file = EvidenceFile()
    evidence_file.original_file_name = 'birth-certificate.pdf'
    evidence_file.aws_file_name = 'ABCD1234__birthOrAdoptionCertificate__birth-certificate.pdf'
    return evidence_file


def password_protected_birth_or_adoption_certificate_file():
    evidence_file = birth_or_adoption_certificate_file()
    evidence_file.password_required = True
    return evidence_file


def populate_check_your_answers_data(application_data):
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


def test_birth_or_adoption_certificate_section_is_optional_and_visible(app):
    with app.app_context():
        application_data = ApplicationData()

        assert application_data.need_birth_or_adoption_certificate is True
        assert application_data.section_status_birth_or_adoption_certificates == ListStatus.NOT_STARTED
        assert application_data.has_usable_birth_or_adoption_certificate is False
        assert application_data.needs_to_post_birth_or_adoption_certificate is True
        assert application_data.needs_to_post_documents is True


def test_birth_or_adoption_certificate_section_is_completed_when_file_uploaded(app):
    with app.app_context():
        application_data = ApplicationData()
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]

        assert application_data.section_status_birth_or_adoption_certificates == ListStatus.COMPLETED
        assert application_data.has_usable_birth_or_adoption_certificate is True
        assert application_data.needs_to_post_birth_or_adoption_certificate is False
        assert application_data.needs_to_post_documents is False


def test_password_protected_certificate_requires_postal_fallback(app):
    with app.app_context():
        application_data = ApplicationData()
        application_data.uploads_data.birth_or_adoption_certificates = [
            password_protected_birth_or_adoption_certificate_file()
        ]

        assert application_data.section_status_birth_or_adoption_certificates == ListStatus.ERROR
        assert application_data.has_usable_birth_or_adoption_certificate is False
        assert application_data.needs_to_post_birth_or_adoption_certificate is True
        assert application_data.needs_to_post_documents is True


def test_confirmation_does_not_ask_for_posted_certificate_when_uploaded(app):
    with app.test_request_context():
        g.build_info = SimpleNamespace(git_commit='test')
        g.lang_code = 'en'
        application_data = ApplicationData()
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]
        context = {
            'birth_cert_copy_link': 'BIRTH_CERT_LINK',
            'ex160_link': 'EX160_LINK',
            'copy_birth_death_marriage_link': 'COPY_CERT_LINK',
            'scotland_norther_ireland_cert_link': 'SCOTLAND_NI_LINK'
        }

        response = render_template(
            'submit-and-pay/confirmation.html',
            application_data=application_data,
            context=context
        )

        assert 'You do not need to post any documents to us unless we ask you to' in response
        assert 'Post your birth or adoption certificate to us as soon as possible' not in response
        assert 'BIRTH_CERT_LINK' not in response


def test_confirmation_keeps_postal_guidance_when_no_certificate_uploaded(app):
    with app.test_request_context():
        g.build_info = SimpleNamespace(git_commit='test')
        g.lang_code = 'en'
        application_data = ApplicationData()
        context = {
            'birth_cert_copy_link': 'BIRTH_CERT_LINK',
            'ex160_link': 'EX160_LINK',
            'copy_birth_death_marriage_link': 'COPY_CERT_LINK',
            'scotland_norther_ireland_cert_link': 'SCOTLAND_NI_LINK'
        }

        response = render_template(
            'submit-and-pay/confirmation.html',
            application_data=application_data,
            context=context
        )

        assert 'Post your birth or adoption certificate to us as soon as possible' in response
        assert 'BIRTH_CERT_LINK' in response


def test_documents_email_omits_certificate_when_uploaded(app):
    with app.test_request_context():
        application_data = ApplicationData()
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]

        response = render_template('documents.html', application_data=application_data)

        assert 'birth certificate' not in response
        assert 'adoption certificate' not in response


def test_documents_email_keeps_ex160_when_certificate_uploaded(app):
    with app.test_request_context():
        application_data = ApplicationData()
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]
        application_data.submit_and_pay_data.how_applying_for_help_with_fees = HelpWithFeesType.USING_EX160_FORM

        response = render_template('documents.html', application_data=application_data)

        assert 'EX160 form' in response


def test_check_your_answers_shows_uploaded_certificate_and_omits_postal_certificate(app):
    with app.test_request_context():
        g.build_info = SimpleNamespace(git_commit='test')
        g.lang_code = 'en'
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]
        application_data.submit_and_pay_data.applying_for_help_with_fee = False
        context = {
            'birth_cert_copy_link': 'BIRTH_CERT_LINK',
            'ex160_link': 'EX160_LINK'
        }

        response = render_template(
            'submit-and-pay/check-your-answers.html',
            form=CheckYourAnswers(),
            application_data=application_data,
            context=context,
            back='taskList.index'
        )

        assert 'Your birth or adoption certificate' in response
        assert 'birth-certificate.pdf' in response
        assert 'BIRTH_CERT_LINK' not in response


def test_check_your_answers_keeps_postal_certificate_when_not_uploaded(app):
    with app.test_request_context():
        g.build_info = SimpleNamespace(git_commit='test')
        g.lang_code = 'en'
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.submit_and_pay_data.applying_for_help_with_fee = False
        context = {
            'birth_cert_copy_link': 'BIRTH_CERT_LINK',
            'ex160_link': 'EX160_LINK'
        }

        response = render_template(
            'submit-and-pay/check-your-answers.html',
            form=CheckYourAnswers(),
            application_data=application_data,
            context=context,
            back='taskList.index'
        )

        assert 'Your birth or adoption certificate' not in response
        assert 'BIRTH_CERT_LINK' in response


def test_admin_pdf_omits_certificate_from_documents_to_post_when_uploaded(app):
    with app.test_request_context():
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.updated = datetime(2024, 1, 1, 9)
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]

        response = render_template_string(
            "{% from 'applications/application.html' import adminapplication %}"
            "{{ adminapplication(application_data) }}",
            application_data=application_data
        )

        documents_to_post_section = response.split('Documents to post')[1]
        assert 'your original or a certified copy of your full birth or adoption certificate' not in documents_to_post_section
        assert 'None' in documents_to_post_section


def test_admin_pdf_keeps_certificate_in_documents_to_post_when_not_uploaded(app):
    with app.test_request_context():
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.updated = datetime(2024, 1, 1, 9)

        response = render_template_string(
            "{% from 'applications/application.html' import adminapplication %}"
            "{{ adminapplication(application_data) }}",
            application_data=application_data
        )

        documents_to_post_section = response.split('Documents to post')[1]
        assert 'your original or a certified copy of your full birth or adoption certificate' in documents_to_post_section


def test_applicant_pdf_omits_certificate_from_documents_to_post_when_uploaded(app):
    with app.test_request_context():
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.updated = datetime(2024, 1, 1, 9)
        application_data.uploads_data.birth_or_adoption_certificates = [birth_or_adoption_certificate_file()]

        response = render_template_string(
            "{% from 'applications/application_user-pdfkit.html' import userapplication %}"
            "{{ userapplication(application_data) }}",
            application_data=application_data
        )

        documents_to_post_section = response.split('Documents to post')[1]
        assert 'your original or a certified copy of your full birth or adoption certificate' not in documents_to_post_section
        assert 'None' in documents_to_post_section


def test_applicant_pdf_keeps_certificate_in_documents_to_post_when_not_uploaded(app):
    with app.test_request_context():
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.updated = datetime(2024, 1, 1, 9)

        response = render_template_string(
            "{% from 'applications/application_user-pdfkit.html' import userapplication %}"
            "{{ userapplication(application_data) }}",
            application_data=application_data
        )

        documents_to_post_section = response.split('Documents to post')[1]
        assert 'your original or a certified copy of your full birth or adoption certificate' in documents_to_post_section


def test_check_your_answers_treats_password_protected_evidence_as_not_supplied(app):
    with app.test_request_context():
        g.build_info = SimpleNamespace(git_commit='test')
        g.lang_code = 'en'
        application_data = ApplicationData()
        populate_check_your_answers_data(application_data)
        application_data.uploads_data.birth_or_adoption_certificates = [
            password_protected_birth_or_adoption_certificate_file()
        ]
        application_data.submit_and_pay_data.applying_for_help_with_fee = False

        response = render_template(
            'submit-and-pay/check-your-answers.html',
            form=CheckYourAnswers(),
            application_data=application_data,
            context={'birth_cert_copy_link': 'BIRTH_CERT_LINK', 'ex160_link': 'EX160_LINK'},
            back='taskList.index'
        )

        assert 'BIRTH_CERT_LINK' in response
        assert 'birth-certificate.pdf' not in response
        assert 'You have uploaded your birth or adoption certificate' not in response


def test_confirmation_treats_password_protected_evidence_as_not_supplied(app):
    with app.test_request_context():
        g.build_info = SimpleNamespace(git_commit='test')
        g.lang_code = 'en'
        application_data = ApplicationData()
        application_data.uploads_data.birth_or_adoption_certificates = [
            password_protected_birth_or_adoption_certificate_file()
        ]

        response = render_template(
            'submit-and-pay/confirmation.html',
            application_data=application_data,
            context={
                'birth_cert_copy_link': 'BIRTH_CERT_LINK',
                'ex160_link': 'EX160_LINK',
                'copy_birth_death_marriage_link': 'COPY_CERT_LINK',
                'scotland_norther_ireland_cert_link': 'SCOTLAND_NI_LINK'
            }
        )

        assert 'Post your birth or adoption certificate to us as soon as possible' in response
        assert 'BIRTH_CERT_LINK' in response
        assert 'You do not need to post any documents to us unless we ask you to' not in response
