import pytest
import io
import fitz
from flask.sessions import SecureCookieSessionInterface

import grc.upload as upload_module
from grc.list_status import ListStatus
from tests.grc.integration.conftest import load_test_data


@pytest.fixture()
def client(app):
    app.secret_key = 'test-secret-key'
    app.config['AV_API'] = None
    app.session_interface = SecureCookieSessionInterface()
    return app.test_client()


class FakeAwsS3Client:
    def __init__(self):
        self.objects = {}
        self.upload_results = []

    def upload_fileobj(self, file_object, object_name):
        if self.upload_results and self.upload_results.pop(0) is False:
            return False
        file_object.seek(0)
        self.objects[object_name] = file_object.read()
        return True

@pytest.fixture()
def fake_s3(monkeypatch):
    client = FakeAwsS3Client()
    monkeypatch.setattr(upload_module, 'AwsS3Client', lambda: client)
    return client


def create_pdf_bytes(password=None):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), 'Birth certificate')
    if password:
        data = document.tobytes(
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw='owner-password',
            user_pw=password
        )
    else:
        data = document.tobytes()
    document.close()
    return data


def sign_in(client, reference_number):
    with client.session_transaction() as session:
        session['reference_number'] = reference_number
        session['identity_verified'] = True


def test_birth_or_adoption_certificate_upload_page(app, client, test_application):
    with app.app_context():
        with client.session_transaction() as session:
            session['reference_number'] = test_application.reference_number
            session['identity_verified'] = True

        response = client.get('/upload/birth-or-adoption-certificate')

        assert response.status_code == 200
        assert 'Upload your birth or adoption certificate' in response.text
        assert 'The files must be a JPG, BMP, PNG, TIF or PDF and smaller than 10MB' in response.text


def test_birth_or_adoption_certificate_upload_page_requires_login(app, client):
    with app.app_context():
        response = client.get('/upload/birth-or-adoption-certificate')

        assert response.status_code == 302
        assert response.location == '/'


def test_birth_or_adoption_certificate_supported_file_saves(app, client, test_application, fake_s3):
    with app.app_context():
        sign_in(client, test_application.reference_number)

        response = client.post(
            '/upload/birth-or-adoption-certificate',
            data={
                'button_clicked': 'UPLOAD_FILE',
                'documents': (io.BytesIO(create_pdf_bytes()), 'birth-certificate.pdf')
            },
            content_type='multipart/form-data'
        )

        application_data = load_test_data(test_application.reference_number)

        assert response.status_code == 302
        assert response.location == '/upload/birth-or-adoption-certificate#file-upload-section'
        assert len(application_data.uploads_data.birth_or_adoption_certificates) == 1
        evidence_file = application_data.uploads_data.birth_or_adoption_certificates[0]
        assert evidence_file.original_file_name == 'birth-certificate.pdf'
        assert fake_s3.objects[evidence_file.aws_file_name].startswith(b'%PDF-')


def test_birth_or_adoption_certificate_malformed_pdf_is_not_saved(app, client, test_application, fake_s3):
    with app.app_context():
        sign_in(client, test_application.reference_number)

        response = client.post(
            '/upload/birth-or-adoption-certificate',
            data={
                'button_clicked': 'UPLOAD_FILE',
                'documents': (io.BytesIO(b'%PDF-1.4 malformed'), 'birth-certificate.pdf')
            },
            content_type='multipart/form-data'
        )

        application_data = load_test_data(test_application.reference_number)

        assert response.status_code == 200
        assert 'Sorry, there is a problem with the service' in response.text
        assert 'Please try again later.' in response.text
        assert application_data.uploads_data.birth_or_adoption_certificates == []
        assert fake_s3.objects == {}


def test_birth_or_adoption_certificate_storage_failure_is_not_saved(app, client, test_application, fake_s3):
    fake_s3.upload_results = [False]

    with app.app_context():
        sign_in(client, test_application.reference_number)

        response = client.post(
            '/upload/birth-or-adoption-certificate',
            data={
                'button_clicked': 'UPLOAD_FILE',
                'documents': (io.BytesIO(create_pdf_bytes()), 'birth-certificate.pdf')
            },
            content_type='multipart/form-data'
        )

        application_data = load_test_data(test_application.reference_number)

        assert response.status_code == 200
        assert 'Sorry, there is a problem with the service' in response.text
        assert application_data.uploads_data.birth_or_adoption_certificates == []
        assert fake_s3.objects == {}


def test_password_protected_certificate_is_stored_as_error_state(
    app, client, test_application, fake_s3
):
    with app.app_context():
        sign_in(client, test_application.reference_number)

        response = client.post(
            '/upload/birth-or-adoption-certificate',
            data={
                'button_clicked': 'UPLOAD_FILE',
                'documents': (
                    io.BytesIO(create_pdf_bytes(password='birth-password')),
                    'birth-certificate.pdf'
                )
            },
            content_type='multipart/form-data'
        )

        application_data = load_test_data(test_application.reference_number)
        evidence_file = application_data.uploads_data.birth_or_adoption_certificates[0]

        assert response.status_code == 302
        assert response.location == '/upload/birth-or-adoption-certificate/document-password'
        assert evidence_file.password_required is True
        assert application_data.section_status_birth_or_adoption_certificates == ListStatus.ERROR
        assert evidence_file.aws_file_name in fake_s3.objects


def test_birth_or_adoption_certificate_unsupported_file_is_rejected(app, client, test_application):
    with app.app_context():
        with client.session_transaction() as session:
            session['reference_number'] = test_application.reference_number
            session['identity_verified'] = True

        response = client.post(
            '/upload/birth-or-adoption-certificate',
            data={
                'button_clicked': 'UPLOAD_FILE',
                'documents': (io.BytesIO(b'not a supported file'), 'birth-certificate.txt')
            },
            content_type='multipart/form-data'
        )

        application_data = load_test_data(test_application.reference_number)

        assert response.status_code == 200
        assert 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB' in response.text
        assert application_data.uploads_data.birth_or_adoption_certificates == []


def test_task_list_shows_birth_or_adoption_certificate_upload(app, client, test_application):
    with app.app_context():
        with client.session_transaction() as session:
            session['reference_number'] = test_application.reference_number
            session['identity_verified'] = True

        response = client.get('/task-list')

        assert response.status_code == 200
        assert 'Your birth or adoption certificate' in response.text
        assert '/upload/birth-or-adoption-certificate' in response.text
        assert 'You can also post your birth or adoption certificate to us if you cannot upload it' in response.text
