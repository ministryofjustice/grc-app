import io
from unittest.mock import MagicMock


class MockAWSClientHelper:

    def __init__(self, mock_s3_client: MagicMock, upload=False, zip_exists=True):
        self.mock_s3_client = mock_s3_client
        self.mock_s3_client.return_value.download_object.side_effect = self._mock_download_object
        self.upload = upload
        if self.upload:
            self.mock_s3_client.return_value.upload_fileobj.return_value = True
        self.zip_exists = zip_exists

    def _mock_download_object(self, aws_file_name):
        if not self.zip_exists and aws_file_name == 'ABCD1234.zip':
            return None

        test_file_content_string = f"{aws_file_name} file content"
        return io.BytesIO(test_file_content_string.encode("utf-8"))

