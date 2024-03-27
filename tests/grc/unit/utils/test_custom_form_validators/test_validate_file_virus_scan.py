import pytest
from grc.upload.forms import UploadForm
from grc.utils.form_custom_validators import file_virus_scan
from unittest.mock import patch, MagicMock
from wtforms.validators import ValidationError
from werkzeug.datastructures.file_storage import FileStorage


class TestValidateFileVirusScan:

    def test_validate_file_virus_scan_no_clamav_endpoint(self, app):
        with app.app_context():
            form = UploadForm()
            form.documents.data = None
            app.config.pop('AV_API')
            assert file_virus_scan(form, form.documents) is None

    def test_validate_file_virus_scan_no_files(self, app):
        with app.app_context():
            form = UploadForm()
            form.documents.data = None
            assert file_virus_scan(form, form.documents) is None

    @patch('pyclamd.ClamdNetworkSocket')
    def test_validate_file_virus_scan_unable_to_connect_to_clamav_host(self, mock_clamav_client, app):
        with app.app_context():
            with app.test_request_context():
                mock_clamav_client_instance = mock_clamav_client.return_value
                mock_clamav_client_instance.ping.return_value = False
                form = UploadForm()
                form.documents.data = [FileStorage(filename='test_file1.pdf', stream=MagicMock(),
                                                   content_type='text/plain')]
                with pytest.raises(ValidationError, match='Unable to communicate with virus scanner'):
                    file_virus_scan(form, form.documents)
