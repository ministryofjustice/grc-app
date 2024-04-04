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

    @patch('pyclamd.ClamdNetworkSocket')
    def test_validate_file_virus_scan_file_contains_virus(self, mock_clamav_client, app):
        with app.app_context():
            with app.test_request_context():
                mock_clamav_client_instance = mock_clamav_client.return_value
                mock_clamav_client_instance.ping.return_value = True
                mock_clamav_client_instance.scan_stream.return_value = {'stream': ('FOUND', 'Test message')}
                form = UploadForm()
                form.documents.data = [FileStorage(filename='test_file1.pdf', stream=MagicMock(),
                                                   content_type='text/plain')]
                with pytest.raises(ValidationError, match='The selected file contains a virus'):
                    file_virus_scan(form, form.documents)

    @patch('pyclamd.ClamdNetworkSocket')
    def test_validate_file_virus_scan_multiple_files_one_contains_virus(self, mock_clamav_client, app):
        with app.app_context():
            with app.test_request_context():
                mock_clamav_client_instance = mock_clamav_client.return_value
                mock_clamav_client_instance.ping.return_value = True
                mock_stream_valid_file_1 = MagicMock()
                mock_stream_valid_file_1.read.return_value = 'test_file1.pdf'
                mock_stream_valid_file_3 = MagicMock()
                mock_stream_valid_file_3.read.return_value = 'test_file3.pdf'
                mock_stream_invalid_file_with_virus = MagicMock()
                mock_stream_invalid_file_with_virus.read.return_value = 'test_file2.pdf'
                mock_result = {'stream': ('FOUND', 'Test message')}
                mock_clamav_client_instance.scan_stream.side_effect = lambda \
                    arg: mock_result if arg == 'test_file2.pdf' else None

                form = UploadForm()
                form.documents.data = [
                    FileStorage(filename='test_file1.pdf', stream=mock_stream_valid_file_1, content_type='text/plain'),
                    FileStorage(filename='test_file2.pdf', stream=mock_stream_invalid_file_with_virus,
                                content_type='text/plain'),
                    FileStorage(filename='test_file3.pdf', stream=mock_stream_valid_file_3, content_type='text/plain')
                ]
                with pytest.raises(ValidationError, match='The selected file contains a virus'):
                    file_virus_scan(form, form.documents)

    @patch('pyclamd.ClamdNetworkSocket')
    def test_validate_file_virus_scan_file_valid_no_virus(self, mock_clamav_client, app):
        with app.app_context():
            with app.test_request_context():
                mock_clamav_client_instance = mock_clamav_client.return_value
                mock_clamav_client_instance.ping.return_value = True
                mock_clamav_client_instance.scan_stream.return_value = None
                form = UploadForm()
                form.documents.data = [FileStorage(filename='test_file1.pdf', stream=MagicMock(),
                                                   content_type='text/plain')]
                assert file_virus_scan(form, form.documents) is None

    @patch('pyclamd.ClamdNetworkSocket')
    def test_validate_file_virus_scan_file_multiple_valid_no_virus(self, mock_clamav_client, app):
        with app.app_context():
            with app.test_request_context():
                mock_clamav_client_instance = mock_clamav_client.return_value
                mock_clamav_client_instance.ping.return_value = True
                mock_clamav_client_instance.scan_stream.return_value = None
                form = UploadForm()
                form.documents.data = [
                    FileStorage(filename='test_file1.pdf', stream=MagicMock(), content_type='text/plain'),
                    FileStorage(filename='test_file2.pdf', stream=MagicMock(), content_type='text/plain'),
                    FileStorage(filename='test_file3.pdf', stream=MagicMock(), content_type='text/plain')
                ]
                assert file_virus_scan(form, form.documents) is None

    @patch('pyclamd.ClamdNetworkSocket')
    def test_validate_file_virus_scan_file_error_scanning_file(self, mock_clamav_client, app):
        with app.app_context():
            with app.test_request_context():
                mock_clamav_client_instance = mock_clamav_client.return_value
                mock_clamav_client_instance.ping.return_value = True
                mock_clamav_client_instance.scan_stream.return_value = {'stream': ('ERROR', 'Test message')}
                form = UploadForm()
                form.documents.data = [
                    FileStorage(filename='test_file1.pdf', stream=MagicMock(), content_type='text/plain')
                ]
                with pytest.raises(ValidationError, match='Error scanning uploaded file'):
                    file_virus_scan(form, form.documents)
