import pytest
from admin.tools.forms import UnlockFileForm
from grc.utils.form_custom_validators import SingleFileAllowed
from werkzeug.datastructures import FileStorage
from unittest.mock import MagicMock
from wtforms.validators import StopValidation


class TestValidateSingleFileAllowed:

    def test_single_file_allowed_admin_unlock_file_tool_valid(self, admin_app):
        with admin_app.app_context():
            test_file_uploaded = FileStorage(filename='test_file1.pdf', stream=MagicMock(), content_type='text/plain')
            form = UnlockFileForm()
            form.file.data = test_file_uploaded
            validator = SingleFileAllowed(form.upload_set, 'Select a PDF file to upload')
            assert validator.__call__(form, form.file) is None

    def test_single_file_allowed_admin_unlock_file_tool_invalid_no_file_data(self, admin_app):
        with admin_app.app_context():
            form = UnlockFileForm()
            form.file.data = None
            validator = SingleFileAllowed(form.upload_set, 'Select a PDF file to upload')
            assert validator.__call__(form, form.file) is None

    def test_single_file_allowed_admin_unlock_file_tool_invalid_file_extension(self, admin_app):
        with admin_app.app_context():
            invalid_test_file_uploaded = FileStorage(filename='test_file1.jpeg', stream=MagicMock(),
                                                     content_type='text/plain')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed(form.upload_set, 'Select a PDF file to upload')
            with pytest.raises(StopValidation, match='Select a PDF file to upload'):
                validator.__call__(form, form.file)

    def test_single_file_allowed_admin_unlock_file_tool_invalid_file_extension_no_message(self, admin_app):
        with admin_app.app_context():
            invalid_test_file_uploaded = FileStorage(filename='test_file1.jpeg', stream=MagicMock(),
                                                     content_type='text/plain')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed(form.upload_set, None)
            with pytest.raises(StopValidation, match='File does not have an approved extension: pdf'):
                validator.__call__(form, form.file)

    def test_single_file_allowed_admin_unlock_file_tool_valid_file_upload_set_not_iterable(self, admin_app):
        with admin_app.app_context():
            invalid_test_file_uploaded = FileStorage(filename='test_file1.pdf', stream=MagicMock(),
                                                     content_type='text/plain')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed('pdf', 'Select a PDF file to upload')
            assert validator.__call__(form, form.file) is None
