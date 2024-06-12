import io
from unittest.mock import MagicMock


class MockAWSClientHelper:

    def __init__(self, upload=False, file_exists=True, zip_exists=True):
        self.mock_s3_client = MagicMock()
        self.mock_s3_client.download_object.side_effect = self._mock_download_object
        self.upload = upload
        if self.upload:
            self.mock_s3_client.upload_fileobj.return_value = True
        self.file_exists = file_exists
        self.zip_exists = zip_exists

    def _mock_download_object(self, aws_file_name):
        if not self.zip_exists and aws_file_name == 'ABCD1234.zip':
            return None

        if not self.file_exists and aws_file_name == 'ABCD1234.pdf':
            return None

        test_file_content_string = f"{aws_file_name} file content"
        return io.BytesIO(test_file_content_string.encode("utf-8"))

