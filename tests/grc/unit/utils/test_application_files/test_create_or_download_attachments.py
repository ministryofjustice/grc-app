import pytest
from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.mock_aws_client import MockAWSClientHelper
from tests.grc.helpers.data.uploads import UploadsHelpers
from unittest.mock import patch, call, MagicMock


class TestCreateOrDownloadAttachments:

    @pytest.fixture
    def app_files(self):
        yield ApplicationFiles()

    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_or_download_attachments_create_attachment_zip(self, mock_s3_client, app, test_application,
                                                                  app_files):
        with app.test_request_context():
            # Set up evidence doc data
            medical_reports_docs = UploadsHelpers('medical_reports')
            gender_evidence_docs = UploadsHelpers('gender_evidence')
            statutory_declaration_docs = UploadsHelpers('statutory_declaration')

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            stat_dec_documents_non_pdfs = statutory_declaration_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            stat_dec_documents_pdfs = statutory_declaration_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.statutory_declarations = stat_dec_documents_non_pdfs + stat_dec_documents_pdfs

            mock_s3_client_helper = MockAWSClientHelper(mock_s3_client)
            mock_s3_client_helper.mock_s3_client.return_value.download_object.return_value = 'downloaded file'

            expected = (None, 'ABCD1234.zip')
            assert app_files.create_or_download_attachments(data.reference_number, data, False) == expected

    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_or_download_attachments_create_attachment_zip_correct_files_uploaded(
            self, mock_s3_client: MagicMock, app, test_application, app_files):
        with app.test_request_context():
            # Set up evidence doc data
            medical_reports_docs = UploadsHelpers('medical_reports')
            gender_evidence_docs = UploadsHelpers('gender_evidence')
            statutory_declaration_docs = UploadsHelpers('statutory_declaration')

            # Load evidence files data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            stat_dec_documents_non_pdfs = statutory_declaration_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            stat_dec_documents_pdfs = statutory_declaration_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.partnership_documents = stat_dec_documents_non_pdfs + stat_dec_documents_pdfs

            # Mock file content data and get args used in download_object call
            mock_s3 = MockAWSClientHelper(mock_s3_client, False)

            expected_downloads_objects_calls = [
                # medical docs
                call('aws_medical_reports_name_1.jpeg'),
                call('aws_medical_reports_name_1_original.jpeg'),
                call('aws_medical_reports_name_1.tiff'),
                call('aws_medical_reports_name_1_original.tiff'),

                # gender evidence docs
                call('aws_gender_evidence_name_1.pdf'),
                call('aws_gender_evidence_name_2.pdf'),

                # stat dec docs
                call('aws_statutory_declaration_name_1.jpeg'),
                call('aws_statutory_declaration_name_1_original.jpeg'),
                call('aws_statutory_declaration_name_1.tiff'),
                call('aws_statutory_declaration_name_1_original.tiff'),
                call('aws_statutory_declaration_name_1.pdf'),
                call('aws_statutory_declaration_name_2.pdf'),

                # application pdf
                call('ABCD1234.pdf')
            ]

            expected_return = (None, 'ABCD1234.zip')
            assert app_files.create_or_download_attachments(data.reference_number, data, False) == expected_return
            mock_s3_client.return_value.download_object.assert_has_calls(expected_downloads_objects_calls)
