import io
from grc.business_logic.data_structures.uploads_data import EvidenceFile


class UploadsHelpers:

    def __init__(self, section: str, mock_s3_client=None):
        self.mock_s3_client = mock_s3_client
        self.section = section

        if self.mock_s3_client:
            self.mock_s3_client.return_value.download_object.side_effect = self._mock_download_object
            self.mock_s3_client.return_value.upload_fileobj.side_effect = self.mock_upload_fileobj

    def get_uploads_object_data(self, extensions_and_number):
        uploads_file_data = []
        for extension, number in extensions_and_number.items():
            for i in range(1, number + 1):
                ef = EvidenceFile()
                ef.aws_file_name = f'aws_{self.section}_name_{i}_original.{extension}'
                ef.original_file_name = f'original_{self.section}_name_{i}.{extension}'
                uploads_file_data.append(ef)
        return uploads_file_data

    def get_uploads_object_data_pdf(self, number_of_files, number_passwords_required=0):
        if number_passwords_required > number_of_files:
            raise ValueError('Number of pdfs with passwords requested exceeds number of pdfs requested')
        uploads_file_data = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_{self.section}_name_{i}.pdf'
            ef.original_file_name = f'original_{self.section}_name_{i}.pdf'
            if number_passwords_required > 0:
                ef.password_required = True
                number_passwords_required -= 1
            uploads_file_data.append(ef)
        return uploads_file_data

    @staticmethod
    def _mock_download_object(aws_file_name):
        test_file_content_string = f"{aws_file_name} file content"
        return io.BytesIO(test_file_content_string.encode("utf-8"))

    @staticmethod
    def mock_upload_fileobj(zip_buffer, attachment_name):
        return zip_buffer, attachment_name


