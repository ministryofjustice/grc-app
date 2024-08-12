import pytest
from admin.tools.forms import UnlockFileForm
from grc.upload.forms import UploadForm
from grc.utils.form_custom_validators import MultiFileAllowed
from werkzeug.datastructures import FileStorage
from unittest.mock import MagicMock
from wtforms.validators import StopValidation


class TestValidateMultiFileAllowed:
    def test_multi_file_allowed_public_file_upload_valid(self, app):
        with app.test_request_context():
            test_files_uploaded = [
                FileStorage(filename='test_file1.pdf', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file2.jpg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file3.jpeg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file4.png', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file5.tif', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file6.tiff', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file7.bmp', stream=MagicMock(), content_type='text/plain'),
            ]
            form = UploadForm()
            form.documents.data = test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')
            assert validator.__call__(form, form.documents) is None

    def test_multi_file_allowed_public_file_upload_invalid_file_extension_with_message(self, app):
        with app.test_request_context():
            invalid_test_files_uploaded = [
                FileStorage(filename='test_file1.pdf', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file2.jpg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file3.jpeg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file4.pg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file5.tif', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file6.tiff', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file7.bmp', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file8.invalid_ext', stream=MagicMock(), content_type='text/plain'),
            ]
            form = UploadForm()
            form.documents.data = invalid_test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')
            with pytest.raises(StopValidation, match='Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB'):
                validator.__call__(form, form.documents)

    def test_multi_file_allowed_public_file_upload_invalid_file_extension_without_message(self, app):
        with app.test_request_context():
            invalid_test_files_uploaded = [
                FileStorage(filename='test_file1.pdf', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file2.jpg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file3.jpeg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file4.pg', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file5.tif', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file6.tiff', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file7.bmp', stream=MagicMock(), content_type='text/plain'),
                FileStorage(filename='test_file8.invalid_ext', stream=MagicMock(), content_type='text/plain'),
            ]
            form = UploadForm()
            form.documents.data = invalid_test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, None)
            with pytest.raises(StopValidation, match='File does not have an approved extension: jpg, jpeg, png, tif,'
                                                     ' tiff, bmp, pdf'):
                validator.__call__(form, form.documents)

    def test_multi_file_allowed_public_file_upload_invalid_file_data_not_iterable(self, app):
        with app.test_request_context():
            invalid_test_files_uploaded = FileStorage(filename='test_file1.pdf', stream=MagicMock(),
                                                      content_type='text/plain'),

            form = UploadForm()
            form.documents.data = invalid_test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, None)
            assert validator.__call__(form, form.documents) is None
