import pytest
from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.data.uploads import UploadsHelpers
from unittest.mock import patch, call, MagicMock


class TestCreateOrDownloadAttachments:

    @pytest.fixture
    def app_files(self):
        yield ApplicationFiles()

    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_or_download_attachments_create_attachment_zip(self, mock_s3_client, app, test_application, app_files):
        with app.test_request_context():

            # Set up evidence doc data and mock file download calls
            medical_reports_docs = UploadsHelpers('medical_reports', mock_s3_client)
            gender_evidence_docs = UploadsHelpers('gender_evidence', mock_s3_client)
            marriage_docs = UploadsHelpers('marriage_documents', mock_s3_client)

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            marriage_documents_non_pdfs = marriage_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            marriage_documents_pdfs = marriage_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.partnership_documents = marriage_documents_non_pdfs + marriage_documents_pdfs

            expected = (None, 'ABCD1234.zip')
            assert app_files.create_or_download_attachments(data.reference_number, data, False) == expected

    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_or_download_attachments_create_attachment_zip_correct_files_uploaded(
            self, mock_s3_client: MagicMock, app, test_application, app_files):
        with app.test_request_context():
            # Set up evidence doc data and mock file data
            sections = ['medical_reports', 'gender_evidence', 'marriage_documents']
            medical_reports_docs = UploadsHelpers(sections[0], mock_s3_client)
            gender_evidence_docs = UploadsHelpers(sections[1], mock_s3_client)
            marriage_docs = UploadsHelpers(sections[2], mock_s3_client)

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            marriage_documents_non_pdfs = marriage_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            marriage_documents_pdfs = marriage_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.partnership_documents = marriage_documents_non_pdfs + marriage_documents_pdfs

            expected_return = (None, 'ABCD1234.zip')
            assert app_files.create_or_download_attachments(data.reference_number, data, False) == expected_return
            mock_s3_client.return_value.download_object.assert_has_calls(medical_reports_docs.calls, any_order=True)
            mock_s3_client.return_value.download_object.assert_has_calls(gender_evidence_docs.calls, any_order=True)
            mock_s3_client.return_value.download_object.assert_has_calls(marriage_docs.calls, any_order=True)


