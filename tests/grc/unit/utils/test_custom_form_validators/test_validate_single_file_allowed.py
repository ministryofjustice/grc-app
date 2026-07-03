from io import BytesIO

import pytest
from admin.tools.forms import UnlockFileForm
from grc.utils.form_custom_validators import SingleFileAllowed, sanitise_uploaded_filename
from werkzeug.datastructures import FileStorage
from wtforms.validators import StopValidation


def uploaded_file(filename, content=b'%PDF-1.4'):
    return FileStorage(filename=filename, stream=BytesIO(content), content_type='application/octet-stream')


class TestValidateSingleFileAllowed:

    def test_single_file_allowed_admin_unlock_file_tool_valid(self, admin_app):
        with admin_app.app_context():
            test_file_uploaded = uploaded_file('test_file1.pdf')
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
            invalid_test_file_uploaded = uploaded_file('test_file1.jpeg', b'\xff\xd8\xff\xe0')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed(form.upload_set, 'Select a PDF file to upload')
            with pytest.raises(StopValidation, match='Select a PDF file to upload'):
                validator.__call__(form, form.file)

    def test_single_file_allowed_admin_unlock_file_tool_invalid_file_extension_no_message(self, admin_app):
        with admin_app.app_context():
            invalid_test_file_uploaded = uploaded_file('test_file1.jpeg', b'\xff\xd8\xff\xe0')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed(form.upload_set, None)
            with pytest.raises(StopValidation, match='File does not have an approved extension: pdf'):
                validator.__call__(form, form.file)

    def test_single_file_allowed_admin_unlock_file_tool_valid_file_upload_set_not_iterable(self, admin_app):
        with admin_app.app_context():
            invalid_test_file_uploaded = uploaded_file('test_file1.pdf')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed('pdf', 'Select a PDF file to upload')
            assert validator.__call__(form, form.file) is None

    def test_single_file_allowed_admin_unlock_file_tool_invalid_disguised_pdf(self, admin_app):
        with admin_app.app_context():
            invalid_test_file_uploaded = uploaded_file('test_file1.pdf', b'not a pdf')
            form = UnlockFileForm()
            form.file.data = invalid_test_file_uploaded
            validator = SingleFileAllowed(form.upload_set, 'Select a PDF file to upload')

            with pytest.raises(StopValidation, match='Select a PDF file to upload'):
                validator.__call__(form, form.file)

    def test_sanitise_uploaded_filename_removes_unsafe_characters(self):
        assert sanitise_uploaded_filename('../unsafe<script>.PDF') == 'unsafe_script.pdf'
