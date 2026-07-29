from io import BytesIO
from datetime import date
from unittest.mock import patch, PropertyMock, call
from flask.sessions import SecureCookieSessionInterface

from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.uploads_data import EvidenceFile, MEDICAL_REPORT_SLOT_FIRST
from grc.list_status import ListStatus
from tests.grc.integration.conftest import load_test_data, save_test_data


def sign_in(client, reference_number):
    with client.session_transaction() as session:
        session['reference_number'] = reference_number
        session['identity_verified'] = True


def use_welsh(client):
    response = client.get('/set_language/cy', headers={'Referer': 'http://localhost/'})
    assert response.status_code == 302


def configure_upload_test(app):
    app.config['AV_API'] = None
    app.session_interface = SecureCookieSessionInterface()


def test_medical_reports_page_renders_two_labelled_fields(app, client, test_application):
    configure_upload_test(app)
    sign_in(client, test_application.reference_number)

    response = client.get('/upload/medical-reports')

    assert response.status_code == 200
    assert response.data.count(b'First medical report') == 1
    assert response.data.count(b'Second medical report') == 1
    assert b'name="first_medical_report"' in response.data
    assert b'name="second_medical_report"' in response.data


def test_medical_reports_page_uses_approved_welsh_labels(app, client, test_application):
    configure_upload_test(app)
    sign_in(client, test_application.reference_number)
    use_welsh(client)

    response = client.get('/upload/medical-reports')

    assert response.status_code == 200
    assert 'Adroddiad meddygol cyntaf'.encode() in response.data
    assert 'Ail adroddiad meddygol'.encode() in response.data


def test_empty_upload_does_not_duplicate_error_summary_links(app, client, test_application):
    configure_upload_test(app)
    sign_in(client, test_application.reference_number)

    response = client.post('/upload/medical-reports', data={'button_clicked': 'UPLOAD_FILE'})

    assert response.status_code == 200
    assert response.data.count(b'href="#first_medical_report"') == 1
    assert response.data.count(b'href="#second_medical_report"') <= 1


@patch('grc.upload.create_aws_file_name', side_effect=['first.pdf', 'second.pdf'])
@patch('grc.upload.PDFUtils')
@patch('grc.upload.AwsS3Client')
def test_uploads_and_persists_both_medical_report_slots(
    mock_s3_client, mock_pdf_utils, _mock_file_name, app, client, test_application
):
    configure_upload_test(app)
    mock_s3_client.return_value.upload_fileobj.return_value = True
    mock_pdf_utils.return_value.is_pdf_form.return_value = False
    mock_pdf_utils.return_value.is_pdf_password_protected.return_value = False
    sign_in(client, test_application.reference_number)

    response = client.post(
        '/upload/medical-reports',
        data={
            'button_clicked': 'UPLOAD_FILE',
            'first_medical_report': (BytesIO(b'first report'), 'first.pdf'),
            'second_medical_report': (BytesIO(b'second report'), 'second.pdf'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 302
    with app.app_context():
        files = load_test_data(test_application.reference_number).uploads_data.medical_reports
        assert [(file.original_file_name, file.medical_report_slot) for file in files] == [
            ('first.pdf', 'first'),
            ('second.pdf', 'second'),
        ]


@patch('grc.upload.create_aws_file_name', side_effect=['first.pdf', 'second.pdf'])
@patch('grc.upload.PDFUtils')
@patch('grc.upload.AwsS3Client')
def test_rolls_back_new_batch_when_second_upload_fails(
    mock_s3_client, mock_pdf_utils, _mock_file_name, app, client, test_application
):
    configure_upload_test(app)
    mock_s3_client.return_value.upload_fileobj.side_effect = [True, False]
    mock_s3_client.return_value.delete_object.return_value = True
    mock_pdf_utils.return_value.is_pdf_form.return_value = False
    mock_pdf_utils.return_value.is_pdf_password_protected.return_value = False
    sign_in(client, test_application.reference_number)

    response = client.post(
        '/upload/medical-reports',
        data={
            'button_clicked': 'UPLOAD_FILE',
            'first_medical_report': (BytesIO(b'first report'), 'first.pdf'),
            'second_medical_report': (BytesIO(b'second report'), 'second.pdf'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 200
    assert b'Sorry, there is a problem with the service' in response.data
    assert b'Please try again later.' in response.data
    mock_s3_client.return_value.delete_object.assert_called_once_with('first.pdf')
    with app.app_context():
        assert load_test_data(test_application.reference_number).uploads_data.medical_reports == []


@patch('grc.upload.create_aws_file_name', return_value='first.pdf')
@patch('grc.upload.PDFUtils')
@patch('grc.upload.AwsS3Client')
def test_failed_upload_uses_existing_approved_welsh_errors(
    mock_s3_client, mock_pdf_utils, _mock_file_name, app, client, test_application
):
    configure_upload_test(app)
    mock_s3_client.return_value.upload_fileobj.return_value = False
    mock_pdf_utils.return_value.is_pdf_form.return_value = False
    mock_pdf_utils.return_value.is_pdf_password_protected.return_value = False
    sign_in(client, test_application.reference_number)
    use_welsh(client)

    response = client.post(
        '/upload/medical-reports',
        data={
            'button_clicked': 'UPLOAD_FILE',
            'first_medical_report': (BytesIO(b'first report'), 'first.pdf'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 200
    assert "Mae'n ddrwg gennym, mae problem gyda'r gwasanaeth".encode() in response.data
    assert 'Rhowch gynnig arall arni hwyrach ymlaen.'.encode() in response.data
    assert (
        b'aria-describedby="first_medical_report-hint first_medical_report-page-order-hint '
        b'first_medical_report-error-1 first_medical_report-error-2"'
    ) in response.data


@patch('grc.upload.DataStore.save_application', side_effect=RuntimeError('database unavailable'))
@patch('grc.upload.create_aws_file_name', side_effect=['first.pdf', 'second.pdf'])
@patch('grc.upload.PDFUtils')
@patch('grc.upload.AwsS3Client')
def test_rolls_back_uploaded_objects_when_application_save_fails(
    mock_s3_client, mock_pdf_utils, _mock_file_name, _mock_save, app, client, test_application
):
    configure_upload_test(app)
    mock_s3_client.return_value.upload_fileobj.return_value = True
    mock_s3_client.return_value.delete_object.return_value = True
    mock_pdf_utils.return_value.is_pdf_form.return_value = False
    mock_pdf_utils.return_value.is_pdf_password_protected.return_value = False
    sign_in(client, test_application.reference_number)

    response = client.post(
        '/upload/medical-reports',
        data={
            'button_clicked': 'UPLOAD_FILE',
            'first_medical_report': (BytesIO(b'first report'), 'first.pdf'),
            'second_medical_report': (BytesIO(b'second report'), 'second.pdf'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 200
    assert mock_s3_client.return_value.delete_object.call_args_list == [
        call('second.pdf'),
        call('first.pdf'),
    ]
    with app.app_context():
        assert load_test_data(test_application.reference_number).uploads_data.medical_reports == []


def test_save_requires_both_labelled_report_slots(app, client, test_application):
    configure_upload_test(app)
    with app.app_context():
        data = load_test_data(test_application.reference_number)
        file = EvidenceFile()
        file.original_file_name = 'first.pdf'
        file.aws_file_name = 'first.pdf'
        file.medical_report_slot = MEDICAL_REPORT_SLOT_FIRST
        data.uploads_data.medical_reports.append(file)
        save_test_data(data)
    sign_in(client, test_application.reference_number)

    response = client.post('/upload/medical-reports', data={'button_clicked': 'SAVE_AND_CONTINUE'})

    assert response.status_code == 200
    assert b'second_medical_report-error-1' in response.data
    assert b'href="#second_medical_report"' in response.data
    assert b'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB' in response.data


@patch('grc.upload.create_aws_file_name', return_value='name-change.pdf')
@patch('grc.upload.PDFUtils')
@patch('grc.upload.AwsS3Client')
def test_shared_upload_refactor_preserves_generic_uploads(
    mock_s3_client, mock_pdf_utils, _mock_file_name, app, client, test_application
):
    configure_upload_test(app)
    mock_s3_client.return_value.upload_fileobj.return_value = True
    mock_pdf_utils.return_value.is_pdf_form.return_value = False
    mock_pdf_utils.return_value.is_pdf_password_protected.return_value = False
    sign_in(client, test_application.reference_number)

    response = client.post(
        '/upload/name-change',
        data={
            'button_clicked': 'UPLOAD_FILE',
            'documents': (BytesIO(b'name change'), 'name-change.pdf'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 302
    with app.app_context():
        files = load_test_data(test_application.reference_number).uploads_data.name_change_documents
        assert len(files) == 1
        assert files[0].original_file_name == 'name-change.pdf'
        assert files[0].medical_report_slot is None


@patch('grc.upload.forms.BaseUploadForm.get_csrf_token', return_value='test-csrf-token')
@patch('grc.upload.create_aws_file_name', return_value='name-change.pdf')
@patch('grc.upload.PDFUtils')
@patch('grc.upload.AwsS3Client')
def test_shared_upload_refactor_handles_generic_storage_failure(
    mock_s3_client, mock_pdf_utils, _mock_file_name, _mock_csrf, app, client, test_application
):
    configure_upload_test(app)
    mock_s3_client.return_value.upload_fileobj.return_value = False
    mock_pdf_utils.return_value.is_pdf_form.return_value = False
    mock_pdf_utils.return_value.is_pdf_password_protected.return_value = False
    sign_in(client, test_application.reference_number)

    response = client.post(
        '/upload/name-change',
        data={
            'button_clicked': 'UPLOAD_FILE',
            'documents': (BytesIO(b'name change'), 'name-change.pdf'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 200
    assert b'Sorry, there is a problem with the service' in response.data
    assert b'Please try again later.' in response.data
    with app.app_context():
        assert load_test_data(test_application.reference_number).uploads_data.name_change_documents == []


def test_check_your_answers_groups_medical_report_files(app, client, test_application):
    configure_upload_test(app)
    with app.app_context():
        data = load_test_data(test_application.reference_number)
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
        for name, slot in [('first.pdf', 'first'), ('second.pdf', 'second')]:
            file = EvidenceFile()
            file.original_file_name = name
            file.aws_file_name = name
            file.medical_report_slot = slot
            data.uploads_data.medical_reports.append(file)
        save_test_data(data)
    sign_in(client, test_application.reference_number)
    use_welsh(client)

    with patch.object(
        ApplicationData,
        'section_status_submit_and_pay_data',
        new_callable=PropertyMock,
        return_value=ListStatus.IN_REVIEW,
    ), patch(
        'grc.submit_and_pay.DataStore.load_application_by_session_reference_number',
        return_value=data,
    ), patch('grc.submit_and_pay.get_previous_page', return_value='/task-list'):
        response = client.get('/submit-and-pay/check-your-answers')

    assert response.status_code == 200
    assert b'first.pdf' in response.data
    assert b'second.pdf' in response.data
    assert 'Adroddiad meddygol cyntaf'.encode() in response.data
    assert 'Ail adroddiad meddygol'.encode() in response.data
