import io
from unittest.mock import MagicMock


class MockAWSClientHelper:

    def __init__(self, mock_s3_client: MagicMock, download=False):
        self.download = download
        self.mock_s3_client = mock_s3_client
        self.mock_s3_client.return_value.download_object.side_effect = self._mock_download_object

    def _mock_download_object(self, aws_file_name):
        if aws_file_name == 'ABCD1234.zip' and not self.download:
            return None

        test_file_content_string = f"{aws_file_name} file content"
        return io.BytesIO(test_file_content_string.encode("utf-8"))
