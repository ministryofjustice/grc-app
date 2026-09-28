import jsonpickle
import zipfile
from io import BytesIO
from unittest.mock import patch, call
import fitz
from werkzeug.datastructures import FileStorage

from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.uploads_data import (
    EvidenceFile,
    MEDICAL_REPORT_SLOT_FIRST,
    MEDICAL_REPORT_SLOT_SECOND,
)
from grc.list_status import ListStatus
from grc.utils.application_files import ApplicationFiles
from grc.utils.pdf_utils import PDFUtils
from grc.upload.forms import MedicalReportsUploadForm


def evidence_file(slot=None, password_required=False):
    file = EvidenceFile()
    file.original_file_name = f'{slot or "legacy"}.pdf'
    file.aws_file_name = f'{slot or "legacy"}.pdf'
    file.medical_report_slot = slot
    file.password_required = password_required
    return file


def uk_application_data():
    data = ApplicationData()
    data.confirmation_data.gender_recognition_outside_uk = False
    return data


def test_legacy_evidence_file_decodes_with_empty_slot():
    file = evidence_file()
    del file.medical_report_slot

    decoded = jsonpickle.decode(jsonpickle.encode(file))

    assert decoded.medical_report_slot is None


def test_medical_report_status_requires_both_labelled_slots():
    data = uk_application_data()
    assert data.section_status_medical_reports == ListStatus.NOT_STARTED

    data.uploads_data.medical_reports.append(evidence_file(MEDICAL_REPORT_SLOT_FIRST))
    assert data.section_status_medical_reports == ListStatus.IN_PROGRESS

    data.uploads_data.medical_reports.append(evidence_file(MEDICAL_REPORT_SLOT_SECOND))
    assert data.section_status_medical_reports == ListStatus.COMPLETED


def test_legacy_medical_report_files_remain_completed():
    data = uk_application_data()
    data.uploads_data.medical_reports.append(evidence_file())

    assert data.section_status_medical_reports == ListStatus.COMPLETED


def test_unknown_medical_report_slot_is_treated_as_legacy():
    data = uk_application_data()
    data.uploads_data.medical_reports.append(evidence_file('future-slot'))

    assert data.section_status_medical_reports == ListStatus.COMPLETED


def test_empty_browser_file_parts_do_not_block_save_and_continue(app):
    with app.test_request_context(method='POST'):
        form = MedicalReportsUploadForm()
        form.button_clicked.data = form.UploadEnum.SAVE_AND_CONTINUE.name
        form.first_medical_report.data = [FileStorage(filename='')]
        form.second_medical_report.data = [FileStorage(filename='')]

        assert form.validate()


def test_empty_browser_file_parts_show_one_upload_error(app):
    with app.test_request_context(method='POST'):
        form = MedicalReportsUploadForm()
        form.button_clicked.data = form.UploadEnum.UPLOAD_FILE.name
        form.first_medical_report.data = [FileStorage(filename='')]
        form.second_medical_report.data = [FileStorage(filename='')]

        assert not form.validate()
        assert len(form.first_medical_report.errors) == 1
        assert form.second_medical_report.errors == []


def test_password_protected_medical_report_remains_error():
    data = uk_application_data()
    data.uploads_data.medical_reports.extend([
        evidence_file(MEDICAL_REPORT_SLOT_FIRST, password_required=True),
        evidence_file(MEDICAL_REPORT_SLOT_SECOND),
    ])

    assert data.section_status_medical_reports == ListStatus.ERROR


def test_application_files_groups_labelled_and_legacy_reports():
    data = uk_application_data()
    first = evidence_file(MEDICAL_REPORT_SLOT_FIRST)
    second = evidence_file(MEDICAL_REPORT_SLOT_SECOND)
    legacy = evidence_file()
    unknown = evidence_file('future-slot')
    data.uploads_data.medical_reports.extend([second, legacy, first, unknown])

    groups = ApplicationFiles()._get_file_groups_for_section('medicalReports', data)

    assert groups == [
        ('First Medical Report', MEDICAL_REPORT_SLOT_FIRST, [first]),
        ('Second Medical Report', MEDICAL_REPORT_SLOT_SECOND, [second]),
        ('Medical Reports', None, [legacy, unknown]),
    ]


def test_application_files_attaches_medical_groups_in_slot_order():
    data = uk_application_data()
    first = evidence_file(MEDICAL_REPORT_SLOT_FIRST)
    second = evidence_file(MEDICAL_REPORT_SLOT_SECOND)
    legacy = evidence_file()
    data.uploads_data.medical_reports.extend([second, legacy, first])
    application_files = ApplicationFiles()

    with patch.object(application_files, 'add_object') as add_object:
        application_files.attach_all_files([], ['medicalReports'], data)

    assert add_object.call_args_list == [
        call([], 'medicalReports', first.aws_file_name, first.original_file_name, 'First Medical Report'),
        call([], 'medicalReports', second.aws_file_name, second.original_file_name, 'Second Medical Report'),
        call([], 'medicalReports', legacy.aws_file_name, legacy.original_file_name, 'Medical Reports'),
    ]


@patch('grc.utils.application_files.PDFUtils')
def test_attachment_names_pdf_contains_medical_group_headings_in_order(mock_pdf_utils, app):
    data = uk_application_data()
    data.uploads_data.medical_reports.extend([
        evidence_file(MEDICAL_REPORT_SLOT_SECOND),
        evidence_file(MEDICAL_REPORT_SLOT_FIRST),
    ])
    mock_pdf_utils.return_value.create_pdf_from_html.return_value = b'pdf'

    with app.test_request_context():
        result = ApplicationFiles().create_attachment_names_pdf(['medicalReports'], data)

    assert result == b'pdf'
    html = mock_pdf_utils.return_value.create_pdf_from_html.call_args.args[0]
    assert html.index('First Medical Report') < html.index('Second Medical Report')
    mock_pdf_utils.return_value.create_pdf_from_html.assert_called_once_with(html, title='Attachments')


def test_labelled_zip_names_include_stable_slot_token():
    data = uk_application_data()
    data.reference_number = 'ABCD1234'
    first = evidence_file(MEDICAL_REPORT_SLOT_FIRST)

    assert ApplicationFiles()._zip_attachment_name(
        data, 'medicalReports', MEDICAL_REPORT_SLOT_FIRST, 0, first
    ) == 'ABCD1234__medicalReports__first__1_first.pdf'


@patch('grc.utils.application_files.AwsS3Client')
def test_labelled_medical_reports_are_separate_entries_in_real_zip(mock_s3_client):
    data = uk_application_data()
    data.reference_number = 'ABCD1234'
    first = evidence_file(MEDICAL_REPORT_SLOT_FIRST)
    second = evidence_file(MEDICAL_REPORT_SLOT_SECOND)
    data.uploads_data.medical_reports.extend([second, first])
    stored_files = {
        first.aws_file_name: b'first report',
        second.aws_file_name: b'second report',
    }
    mock_s3_client.return_value.download_object.side_effect = (
        lambda object_name: BytesIO(stored_files[object_name])
    )
    application_files = ApplicationFiles()

    with patch.object(application_files, 'download_pdf_admin', return_value=b'application'):
        zip_stream = application_files._create_application_zip(data)

    with zipfile.ZipFile(zip_stream) as archive:
        assert archive.namelist() == [
            'ABCD1234__medicalReports__first__1_first.pdf',
            'ABCD1234__medicalReports__second__1_second.pdf',
            'application.pdf',
        ]
        assert archive.read('ABCD1234__medicalReports__first__1_first.pdf') == b'first report'
        assert archive.read('ABCD1234__medicalReports__second__1_second.pdf') == b'second report'


def one_page_pdf(text):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    stream = BytesIO(document.tobytes())
    document.close()
    return stream


@patch('grc.utils.application_files.AwsS3Client')
def test_labelled_medical_reports_have_ordered_bookmarks_in_real_merged_pdf(mock_s3_client, app):
    data = uk_application_data()
    first = evidence_file(MEDICAL_REPORT_SLOT_FIRST)
    second = evidence_file(MEDICAL_REPORT_SLOT_SECOND)
    data.uploads_data.medical_reports.extend([second, first])
    mock_s3_client.return_value.download_object.side_effect = (
        lambda object_name: one_page_pdf(object_name)
    )
    application_files = ApplicationFiles()
    attachments = []

    with app.test_request_context():
        application_files.attach_all_files(attachments, ['medicalReports'], data)
        merged = PDFUtils().merge_pdfs(attachments)

    document = fitz.open(stream=merged, filetype='pdf')
    try:
        assert document.get_toc() == [
            [1, 'First Medical Report', 1],
            [2, 'first.pdf', 1],
            [1, 'Second Medical Report', 2],
            [2, 'second.pdf', 2],
        ]
        assert len(document) == 2
    finally:
        document.close()
