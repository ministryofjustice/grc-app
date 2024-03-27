import pytest
from admin.tools.forms import UnlockFileForm
from grc.utils.form_custom_validators import validate_file_size_limit
from unittest.mock import MagicMock
from werkzeug.datastructures.file_storage import FileStorage
from wtforms.validators import ValidationError


class TestValidateFileSizeLimit:

    def test_validate_file_size_limit_valid_file_size(self, app):
        with app.app_context():
            file_size_limit_bytes = 10 * 1024 * 1024
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = file_size_limit_bytes
            test_files = FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')
            form = UnlockFileForm()
            form.file_size_limit_mb = 10
            form.file.data = test_files
            assert validate_file_size_limit(form, form.file) is None

    def test_validate_files_size_limit_invalid_file_size_one_file(self, app):
        with app.app_context():
            over_file_size_limit_bytes = 11 * 1024 * 1024
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = over_file_size_limit_bytes
            test_files = FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')
            form = UnlockFileForm()
            form.file_size_limit_mb = 10
            form.file.data = test_files
            with pytest.raises(ValidationError, match='The selected file must be smaller than 10MB'):
                validate_file_size_limit(form, form.file)

    def test_validate_files_size_limit_invalid_empty_file(self, app):
        with app.app_context():
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = 0
            test_files = FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')
            form = UnlockFileForm()
            form.file_size_limit_mb = 10
            form.file.data = test_files
            with pytest.raises(ValidationError, match='The selected file is empty. Check that the file you are '
                                                      'uploading has the content you expect'):
                validate_file_size_limit(form, form.file)

    def test_validate_files_size_limit_valid_max_limit_not_set(self, app):
        with app.app_context():
            file_size_limit_bytes = 10 * 1024 * 1024
            mock_stream = MagicMock()
            mock_stream.read.return_value.__len__.return_value = file_size_limit_bytes
            test_files = FileStorage(filename='test_file1.pdf', stream=mock_stream, content_type='text/plain')
            form = UnlockFileForm()
            form.file_size_limit_mb = None
            form.file.data = test_files
            assert validate_file_size_limit(form, form.file) is None
