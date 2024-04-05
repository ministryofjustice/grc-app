from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.data.uploads import UploadsHelpers
from unittest.mock import patch


class TestCreateOrDownloadAttachments:

    @patch('grc.utils.application_files.AwsS3Client')
    def test_create_or_download_attachments_(self, mock_s3_client, app, test_application):
        with app.test_request_context():
            medical_reports_docs = UploadsHelpers('medical_reports', mock_s3_client)
            gender_evidence_docs = UploadsHelpers('gender_evidence', mock_s3_client)
            marriage_docs = UploadsHelpers('marriage_documents', mock_s3_client)
            data = test_application.application_data()
            data.uploads_data.medical_reports = medical_reports_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            data.uploads_data.evidence_of_living_in_gender = gender_evidence_docs.get_uploads_object_data_pdf(2)
            marriage_documents_non_pdfs = marriage_docs.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
            marriage_documents_pdfs = marriage_docs.get_uploads_object_data_pdf(2, 1)
            data.uploads_data.partnership_documents = marriage_documents_pdfs + marriage_documents_non_pdfs
            print(mock_s3_client.download_object('aws_medical_reports_name_1_original.jpeg'))
            print(ApplicationFiles().create_or_download_attachments(
                reference_number=data.reference_number,
                application_data=data,
                download=False
            ))
            pass

