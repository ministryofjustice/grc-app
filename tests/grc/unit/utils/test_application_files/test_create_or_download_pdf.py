import io
import fitz
from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.mock_aws_client import MockAWSClientHelper
from unittest.mock import patch, MagicMock


class TestCreateOrCreateDownloadPDF:

    @staticmethod
    def mock_create_coversheet(*args, **kwargs):
        bytes_buffer = io.BytesIO()
        pdf_document = fitz.open()
        content_page = pdf_document.new_page(width=595, height=842)
        content_page.insert_text((100, 100), f"Coversheet", fontsize=12)
        pdf_document.save(bytes_buffer)
        bytes_buffer.seek(0)
        return bytes_buffer

    @staticmethod
    def mock_create_output_pdf_document_files_attached(*args, **kwargs):
        bytes_buffer = io.BytesIO()
        pdf_document = fitz.open()
        try:
            coversheet = fitz.open(stream=args[1][0], filetype='pdf')
            pdf_document.insert_pdf(coversheet)
        except IndexError:
            pass
        content_page = pdf_document.new_page(width=595, height=842)
        content_page.insert_text((100, 100), f"PDF with application data and attached files", fontsize=12)
        pdf_document.save(bytes_buffer)
        bytes_buffer.seek(0)
        return bytes_buffer

    @staticmethod
    def mock_create_output_pdf_document_with_filenames(*args, **kwargs):
        bytes_buffer = io.BytesIO()
        pdf_document = fitz.open()
        try:
            coversheet = fitz.open(stream=args[1][0], filetype='pdf')
            pdf_document.insert_pdf(coversheet)
        except IndexError:
            pass
        content_page = pdf_document.new_page(width=595, height=842)
        content_page.insert_text((100, 100), f"PDF with application data with uploaded file names", fontsize=12)
        pdf_document.save(bytes_buffer)
        bytes_buffer.seek(0)
        return bytes_buffer

    @staticmethod
    def mock_attach_files_method(pdfs, *args):
        for i in range(1, 4):
            bytes_buffer = io.BytesIO()
            pdf_document = fitz.open()
            content_page = pdf_document.new_page(width=595, height=842)
            content_page.insert_text((100, 100), f"Uploaded doc {i} to attach to application pdf", fontsize=12)
            pdf_document.save(bytes_buffer)
            bytes_buffer.seek(0)
            pdfs.append(bytes_buffer)

    @staticmethod
    def mock_attach_filenames_method(sections, *args):
        bytes_buffer = io.BytesIO()
        pdf_document = fitz.open()
        content_page = pdf_document.new_page(width=595, height=842)
        text = ''
        for section in sections:
            text += f'{section}\n'
            for i in range(1, 3):
                text += f'Uploaded doc {i} for section {section} to attach to application pdf\n'
        content_page.insert_text((100, 100), text, fontsize=12)
        pdf_document.save(bytes_buffer)
        bytes_buffer.seek(0)
        return bytes_buffer

    def test_download_pdf_admin(self, app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            app_files.s3_client = MockAWSClientHelper().mock_s3_client
            assert app_files.download_pdf_admin(test_application.application_data()).read() ==  b'ABCD1234.pdf file content'
            app_files.s3_client.download_object.assert_called_once_with('ABCD1234.pdf')

    def test_download_pdf_admin_file_not_found(self, app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            app_files.s3_client = MockAWSClientHelper(file_exists=False).mock_s3_client
            assert app_files.download_pdf_admin(test_application.application_data()) is None
            app_files.s3_client.download_object.assert_called_once_with('ABCD1234.pdf')

    @patch('grc.utils.application_files.ApplicationFiles.attach_all_files')
    def test_create_pdf_attach_files(self, mock_attach_files: MagicMock, app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            mock_attach_files.side_effect = self.mock_attach_files_method
            pdf_data = app_files._create_pdf_attach_files(test_application.application_data(), [], app_files.sections)
            pdf_document = fitz.open(stream=pdf_data)
            page_1, page_2, page_3 = pdf_document
            assert 'Uploaded doc 1 to attach to application pdf' in page_1.get_text()
            assert 'Uploaded doc 2 to attach to application pdf' in page_2.get_text()
            assert 'Uploaded doc 3 to attach to application pdf' in page_3.get_text()
            pdf_document.close()

    @patch('grc.utils.application_files.ApplicationFiles.create_attachment_names_pdf')
    def test_create_pdf_attach_filenames(self, mock_attach_filenames: MagicMock, app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            mock_attach_filenames.side_effect = self.mock_attach_filenames_method
            test_sections = ['statutoryDeclarations', 'marriageDocuments', 'nameChange']
            pdf_data = app_files._create_pdf_attach_filenames(test_application.application_data(), [], test_sections)
            pdf_document = fitz.open(stream=pdf_data)
            page_with_filenames = pdf_document[0].get_text()
            assert 'statutoryDeclarations' in page_with_filenames
            assert 'Uploaded doc 1 for section statutoryDeclarations to attach to application pdf' in page_with_filenames
            assert 'Uploaded doc 2 for section statutoryDeclarations to attach to application pdf' in page_with_filenames
            assert 'marriageDocuments' in page_with_filenames
            assert 'Uploaded doc 1 for section marriageDocuments to attach to application pdf' in page_with_filenames
            assert 'Uploaded doc 2 for section marriageDocuments to attach to application pdf' in page_with_filenames
            assert 'nameChange' in page_with_filenames
            assert 'Uploaded doc 1 for section nameChange to attach to application pdf' in page_with_filenames
            assert 'Uploaded doc 2 for section nameChange to attach to application pdf' in page_with_filenames
            pdf_document.close()

    @patch('grc.utils.application_files.ApplicationFiles._create_pdf_attach_files')
    @patch('grc.utils.application_files.ApplicationFiles.create_application_cover_sheet_pdf')
    def test_create_pdf_public(self, mock_create_coversheet: MagicMock, mock_pdf_attach_files: MagicMock, app,
                               test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            mock_create_coversheet.return_value = self.mock_create_coversheet()
            mock_pdf_attach_files.side_effect = self.mock_create_output_pdf_document_files_attached
            pdf, filename = app_files.create_pdf_public(test_application.application_data())
            assert filename == 'grc_test_public_email_example_com.pdf'
            pdf_document = fitz.open(stream=pdf)
            page_1, page_2 = pdf_document
            assert 'Coversheet' in page_1.get_text()
            assert 'PDF with application data and attached files' in page_2.get_text()
            pdf_document.close()

    @patch('grc.utils.application_files.ApplicationFiles._create_pdf_attach_files')
    @patch('grc.utils.application_files.ApplicationFiles.create_application_cover_sheet_pdf')
    def test_create_pdf_admin_with_files_attached(self, mock_create_coversheet: MagicMock,
                                                  mock_pdf_attach_files: MagicMock, app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            mock_create_coversheet.return_value = self.mock_create_coversheet()
            mock_pdf_attach_files.side_effect = self.mock_create_output_pdf_document_files_attached
            pdf, filename = app_files.create_pdf_admin_with_files_attached(test_application.application_data())
            assert filename == 'ABCD1234.pdf'
            pdf_document = fitz.open(stream=pdf)
            page_1, page_2 = pdf_document
            assert 'Coversheet' in page_1.get_text()
            assert 'PDF with application data and attached files' in page_2.get_text()
            pdf_document.close()

    @patch('grc.utils.application_files.ApplicationFiles._create_pdf_attach_filenames')
    @patch('grc.utils.application_files.ApplicationFiles.create_application_cover_sheet_pdf')
    def test_create_pdf_admin_with_filenames(self, mock_create_coversheet: MagicMock,
                                             mock_pdf_attach_filenames: MagicMock, app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            mock_create_coversheet.return_value = self.mock_create_coversheet()
            mock_pdf_attach_filenames.side_effect = self.mock_create_output_pdf_document_with_filenames
            pdf, filename = app_files.create_pdf_admin_with_filenames(test_application.application_data())
            assert filename == 'ABCD1234.pdf'
            pdf_document = fitz.open(stream=pdf)
            page_1, page_2 = pdf_document
            assert 'Coversheet' in page_1.get_text()
            assert 'PDF with application data with uploaded file names' in page_2.get_text()
            pdf_document.close()

    @patch('grc.utils.application_files.ApplicationFiles.create_pdf_admin_with_filenames')
    @patch('grc.utils.application_files.AwsS3Client')
    def test_upload_pdf_admin_with_file_names_attached(self, mock_s3_client: MagicMock, mock_create_pdf: MagicMock,
                                                       app, test_application):
        with app.test_request_context():
            app_files = ApplicationFiles()
            upload_object_mock: MagicMock = mock_s3_client.return_value.upload_fileobj
            upload_object_mock.return_value = True
            mock_application_pdf_to_upload = self.mock_create_output_pdf_document_with_filenames()
            mock_create_pdf.return_value = mock_application_pdf_to_upload
            assert app_files.upload_pdf_admin_with_file_names_attached(test_application.application_data()) is True
            upload_object_mock.assert_called_once_with(mock_application_pdf_to_upload, 'ABCD1234.pdf')




