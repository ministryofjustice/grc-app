import io
import zipfile
import pytest
from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.mock_aws_client import MockAWSClientHelper
from tests.grc.helpers.data.uploads import UploadsHelpers
from unittest.mock import patch, call, MagicMock


class TestCreateAndDownloadAttachments:

    @pytest.fixture
    def app_files(self):
        yield ApplicationFiles()

    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_application_zip(self, mock_s3_client: MagicMock, app, test_application, app_files):
        with (app.test_request_context()):
            # Set up evidence doc data
            medical_reports_docs = UploadsHelpers('medicalReports')
            gender_evidence_docs = UploadsHelpers('genderEvidence')
            statutory_declaration_docs = UploadsHelpers('statutoryDeclarations')

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            stat_dec_documents_non_pdfs = statutory_declaration_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            stat_dec_documents_pdfs = statutory_declaration_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.statutory_declarations = stat_dec_documents_non_pdfs + stat_dec_documents_pdfs

            # Mock file content data and get args used in download_object call
            MockAWSClientHelper(mock_s3_client)

            expected_downloads_objects_calls = [
                # medical docs
                call('aws_medicalreports_name_1.jpeg'),
                call('aws_medicalreports_name_1_original.jpeg'),
                call('aws_medicalreports_name_1.tiff'),
                call('aws_medicalreports_name_1_original.tiff'),

                # gender evidence docs
                call('aws_genderevidence_name_1.pdf'),
                call('aws_genderevidence_name_2.pdf'),

                # stat dec docs
                call('aws_statutorydeclarations_name_1.jpeg'),
                call('aws_statutorydeclarations_name_1_original.jpeg'),
                call('aws_statutorydeclarations_name_1.tiff'),
                call('aws_statutorydeclarations_name_1_original.tiff'),
                call('aws_statutorydeclarations_name_1.pdf'),
                call('aws_statutorydeclarations_name_2.pdf'),

                # application pdf
                call('ABCD1234.pdf')
            ]

            expected_zip_files_content = {
                # medical reports file content
                "ABCD1234__medicalReports__1_original_medicalreports_name_1.jpeg": b'aws_medicalreports_name_1.jpeg file content',
                "ABCD1234__medicalReports__1_original_medicalreports_name_1_original.jpeg": b'aws_medicalreports_name_1_original.jpeg file content',
                "ABCD1234__medicalReports__2_original_medicalreports_name_1.tiff": b'aws_medicalreports_name_1.tiff file content',
                "ABCD1234__medicalReports__2_original_medicalreports_name_1_original.tiff": b'aws_medicalreports_name_1_original.tiff file content',

                # gender evidence file content
                "ABCD1234__genderEvidence__1_original_genderevidence_name_1.pdf": b'aws_genderevidence_name_1.pdf file content',
                "ABCD1234__genderEvidence__2_original_genderevidence_name_2.pdf": b'aws_genderevidence_name_2.pdf file content',

                # stat dec file content
                "ABCD1234__statutoryDeclarations__1_original_statutorydeclarations_name_1.jpeg": b'aws_statutorydeclarations_name_1.jpeg file content',
                "ABCD1234__statutoryDeclarations__1_original_statutorydeclarations_name_1_original.jpeg": b'aws_statutorydeclarations_name_1_original.jpeg file content',
                "ABCD1234__statutoryDeclarations__2_original_statutorydeclarations_name_1.tiff": b'aws_statutorydeclarations_name_1.tiff file content',
                "ABCD1234__statutoryDeclarations__2_original_statutorydeclarations_name_1_original.tiff": b'aws_statutorydeclarations_name_1_original.tiff file content',
                "ABCD1234__statutoryDeclarations__3_original_statutorydeclarations_name_1.pdf": b'aws_statutorydeclarations_name_1.pdf file content',
                "ABCD1234__statutoryDeclarations__4_original_statutorydeclarations_name_2.pdf": b'aws_statutorydeclarations_name_2.pdf file content',
            }

            application_file_zip: io.BytesIO = app_files._create_application_zip(data)
            with zipfile.ZipFile(application_file_zip, 'r') as test_application_zip_file:
                for file, data in expected_zip_files_content.items():
                    file_content = test_application_zip_file.read(file)
                    # assert that the data in the downloaded file is the same in the zip file
                    assert file_content == data

                application_pdf = test_application_zip_file.read('application.pdf')
                # assert that the application pdf has been attached
                assert len(application_pdf) > 0

            # assert the correct files are downloaded from s3
            mock_s3_client.return_value.download_object.assert_has_calls(expected_downloads_objects_calls)

    @patch('grc.utils.application_files.ApplicationFiles._create_application_zip')
    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_and_upload_attachment(self, mock_s3_client: MagicMock, mock_create_app_zip, app, test_application,
                                          app_files):
        with app.test_request_context():
            # Set up evidence doc data
            medical_reports_docs = UploadsHelpers('medicalReports')
            gender_evidence_docs = UploadsHelpers('genderEvidence')
            statutory_declaration_docs = UploadsHelpers('statutoryDeclarations')

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'bmp': 1, 'png': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            stat_dec_documents_non_pdfs = statutory_declaration_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            stat_dec_documents_pdfs = statutory_declaration_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.statutory_declarations = stat_dec_documents_non_pdfs + stat_dec_documents_pdfs

            # Mock file content data and get args used in download_object call
            MockAWSClientHelper(mock_s3_client, upload=True)

            # mock create application zip
            test_zipe_files = io.BytesIO('test zip files'.encode('utf-8'))
            mock_create_app_zip.return_value = test_zipe_files

            # assert the correct zip is uploaded to s3
            assert app_files.create_and_upload_attachments(data.reference_number, data) is True
            mock_s3_client.return_value.upload_fileobj.assert_called_once_with(test_zipe_files, 'ABCD1234.zip')

    @patch('grc.utils.application_files.AwsS3Client')
    def test_download_attachments_zip_exists(self, mock_s3_client: MagicMock, app, test_application, app_files):
        with app.test_request_context():
            # Set up evidence doc data
            medical_reports_docs = UploadsHelpers('medicalReports')
            gender_evidence_docs = UploadsHelpers('genderEvidence')
            statutory_declaration_docs = UploadsHelpers('statutoryDeclarations')

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'bmp': 1, 'png': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            stat_dec_documents_non_pdfs = statutory_declaration_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            stat_dec_documents_pdfs = statutory_declaration_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.statutory_declarations = stat_dec_documents_non_pdfs + stat_dec_documents_pdfs

            # Mock file content data and get args used in download_object call
            MockAWSClientHelper(mock_s3_client)

            assert app_files.download_attachments(data.reference_number, data) == (b'ABCD1234.zip file content', 'ABCD1234.zip')

    @patch('grc.utils.application_files.ApplicationFiles._create_application_zip')
    @patch('grc.utils.application_files.AwsS3Client')
    def test_download_attachments_zip_does_not_exist(self, mock_s3_client: MagicMock, mock_create_app_zip: MagicMock,
                                                     app, test_application, app_files):
        with app.test_request_context():
            # Set up evidence doc data
            medical_reports_docs = UploadsHelpers('medicalReports')
            gender_evidence_docs = UploadsHelpers('genderEvidence')
            statutory_declaration_docs = UploadsHelpers('statutoryDeclarations')

            # Load uploads data
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'bmp': 1, 'png': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            stat_dec_documents_non_pdfs = statutory_declaration_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            stat_dec_documents_pdfs = statutory_declaration_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.statutory_declarations = stat_dec_documents_non_pdfs + stat_dec_documents_pdfs

            # Mock file content data and get args used in download_object call
            MockAWSClientHelper(mock_s3_client, zip_exists=False)

            # mock create application zip
            test_zipe_files = io.BytesIO('test zip files'.encode('utf-8'))
            mock_create_app_zip.return_value = test_zipe_files

            assert app_files.download_attachments(data.reference_number, data) == (b'test zip files', 'ABCD1234.zip')
            mock_create_app_zip.assert_called_once_with(data)
