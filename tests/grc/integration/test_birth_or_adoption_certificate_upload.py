import pytest
import io
from flask.sessions import SecureCookieSessionInterface

import grc.upload as upload_module
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.models import Application, db
from tests.grc.integration.conftest import load_test_data, save_test_data


@pytest.fixture()
def client(app):
    app.secret_key = 'test-secret-key'
    app.config['AV_API'] = None
    app.session_interface = SecureCookieSessionInterface()
    return app.test_client()


@pytest.fixture()
def test_application(app, public_user_email):
    with app.app_context():
        db.create_all()

        application_record = Application(
            reference_number='ABCD1234',
            email=public_user_email
        )

        db.session.add(application_record)
        db.session.commit()

        data = ApplicationData()
        data.reference_number = application_record.reference_number
        data.email_address = application_record.email
        save_test_data(data)

        yield application_record

        db.session.remove()
        db.drop_all()


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


def test_birth_or_adoption_certificate_supported_file_saves(app, client, test_application, monkeypatch):
    class FakeAwsS3Client:
        def upload_fileobj(self, file_object, object_name):
            pass

    monkeypatch.setattr(upload_module, 'AwsS3Client', lambda: FakeAwsS3Client())

    with app.app_context():
        with client.session_transaction() as session:
            session['reference_number'] = test_application.reference_number
            session['identity_verified'] = True

        response = client.post(
            '/upload/birth-or-adoption-certificate',
            data={
                'button_clicked': 'UPLOAD_FILE',
                'documents': (io.BytesIO(b'%PDF-1.4 test file'), 'birth-certificate.pdf')
            },
            content_type='multipart/form-data'
        )

        application_data = load_test_data(test_application.reference_number)

        assert response.status_code == 302
        assert response.location == '/upload/birth-or-adoption-certificate#file-upload-section'
        assert len(application_data.uploads_data.birth_or_adoption_certificates) == 1
        assert application_data.uploads_data.birth_or_adoption_certificates[0].original_file_name == 'birth-certificate.pdf'


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
