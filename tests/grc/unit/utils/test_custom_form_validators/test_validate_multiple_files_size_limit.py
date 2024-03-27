import pytest
from grc.upload.forms import UploadForm
from grc.utils.form_custom_validators import validate_multiple_files_size_limit
from unittest.mock import MagicMock
from werkzeug.datastructures.file_storage import FileStorage
from wtforms.validators import ValidationError


class TestValidateMultipleFileSizeLimit:

    def test_validate_multiple_files_size_limit_valid_file_size_one_file(self, app):
        with app.app_context():
            file_size_limit_bytes = 10 * 1024 * 1024
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = file_size_limit_bytes
            test_files = [FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')]
            form = UploadForm()
            form.file_size_limit_mb = 10
            form.documents.data = test_files
            assert validate_multiple_files_size_limit(form, form.documents) is None

    def test_validate_multiple_files_size_limit_valid_file_size_multiple_files(self, app):
        with app.app_context():
            file_size_limit_bytes = 10 * 1024 * 1024
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = file_size_limit_bytes
            test_files = [
                FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain'),
                FileStorage(filename='test_file2.jpeg', stream=mock_stream, content_type='text/plain'),
                FileStorage(filename='test_file3.tiff', stream=mock_stream, content_type='text/plain')
            ]
            form = UploadForm()
            form.file_size_limit_mb = 10
            form.documents.data = test_files
            assert validate_multiple_files_size_limit(form, form.documents) is None

    def test_validate_multiple_files_size_limit_invalid_file_size_one_file(self, app):
        with app.app_context():
            over_file_size_limit_bytes = 11 * 1024 * 1024
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = over_file_size_limit_bytes
            test_files = [FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')]
            form = UploadForm()
            form.file_size_limit_mb = 10
            form.documents.data = test_files
            with pytest.raises(ValidationError, match='The selected file must be smaller than 10MB'):
                validate_multiple_files_size_limit(form, form.documents)

    def test_validate_multiple_files_size_limit_invalid_file_size_multiple_files(self, app):
        with app.app_context():
            under_file_size_limit_bytes = 7 * 1024 * 1024
            over_file_size_limit_bytes = 11 * 1024 * 1024
            mock_stream_valid = MagicMock()
            mock_stream_invalid = MagicMock()
            mock_stream_valid.read.return_value.__len__.return_value = under_file_size_limit_bytes
            mock_stream_invalid.read.return_value.__len__.return_value = over_file_size_limit_bytes
            test_files = [
                FileStorage(filename='test_file1.pdf', stream=mock_stream_valid, content_type='text/plain'),
                FileStorage(filename='test_file2.pdf', stream=mock_stream_invalid, content_type='text/plain'),
                FileStorage(filename='test_file3.pdf', stream=mock_stream_valid, content_type='text/plain')
            ]
            form = UploadForm()
            form.file_size_limit_mb = 10
            form.documents.data = test_files
            with pytest.raises(ValidationError, match='The selected file must be smaller than 10MB'):
                validate_multiple_files_size_limit(form, form.documents)

    def test_validate_multiple_files_size_limit_invalid_empty_file(self, app):
        with app.app_context():
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = 0
            test_files = [FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')]
            form = UploadForm()
            form.file_size_limit_mb = 10
            form.documents.data = test_files
            with pytest.raises(ValidationError, match='The selected file is empty. Check that the file you are '
                                                      'uploading has the content you expect'):
                validate_multiple_files_size_limit(form, form.documents)

    def test_validate_multiple_files_size_limit_invalid_multiple_files_one_empty_file(self, app):
        with app.app_context():
            mock_stream_valid = MagicMock()
            mock_stream_invalid = MagicMock()
            mock_stream_valid.read.return_value.__len__.return_value = 10 * 1024 * 1024
            mock_stream_invalid.read.return_value.__len__.return_value = 0
            test_files = [
                FileStorage(filename='test_file1.pdf', stream=mock_stream_valid, content_type='text/plain'),
                FileStorage(filename='test_file2.pdf', stream=mock_stream_invalid, content_type='text/plain')
            ]
            form = UploadForm()
            form.file_size_limit_mb = 10
            form.documents.data = test_files
            with pytest.raises(ValidationError, match='The selected file is empty. Check that the file you are '
                                                      'uploading has the content you expect'):
                validate_multiple_files_size_limit(form, form.documents)
