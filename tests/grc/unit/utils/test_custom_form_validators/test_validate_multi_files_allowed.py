from io import BytesIO

import pytest
from grc.upload.forms import UploadForm
from grc.utils.form_custom_validators import MultiFileAllowed
from werkzeug.datastructures import FileStorage
from wtforms.validators import StopValidation


def uploaded_file(filename, content):
    return FileStorage(filename=filename, stream=BytesIO(content), content_type='application/octet-stream')


class TestValidateMultiFileAllowed:
    def test_multi_file_allowed_public_file_upload_valid(self, app):
        with app.test_request_context():
            test_files_uploaded = [
                uploaded_file('test_file1.pdf', b'%PDF-1.4'),
                uploaded_file('test_file2.jpg', b'\xff\xd8\xff\xe0'),
                uploaded_file('test_file3.jpeg', b'\xff\xd8\xff\xe0'),
                uploaded_file('test_file4.png', b'\x89PNG\r\n\x1a\n'),
                uploaded_file('test_file5.tif', b'II*\x00'),
                uploaded_file('test_file6.tiff', b'MM\x00*'),
                uploaded_file('test_file7.bmp', b'BM'),
            ]
            form = UploadForm()
            form.documents.data = test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')
            assert validator.__call__(form, form.documents) is None

    def test_multi_file_allowed_public_file_upload_invalid_file_extension_with_message(self, app):
        with app.test_request_context():
            invalid_test_files_uploaded = [
                uploaded_file('test_file1.pdf', b'%PDF-1.4'),
                uploaded_file('test_file2.jpg', b'\xff\xd8\xff\xe0'),
                uploaded_file('test_file3.jpeg', b'\xff\xd8\xff\xe0'),
                uploaded_file('test_file4.pg', b'not allowed'),
                uploaded_file('test_file5.tif', b'II*\x00'),
                uploaded_file('test_file6.tiff', b'MM\x00*'),
                uploaded_file('test_file7.bmp', b'BM'),
                uploaded_file('test_file8.invalid_ext', b'not allowed'),
            ]
            form = UploadForm()
            form.documents.data = invalid_test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')
            with pytest.raises(StopValidation, match='Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB'):
                validator.__call__(form, form.documents)

    def test_multi_file_allowed_public_file_upload_invalid_file_extension_without_message(self, app):
        with app.test_request_context():
            invalid_test_files_uploaded = [
                uploaded_file('test_file1.pdf', b'%PDF-1.4'),
                uploaded_file('test_file2.jpg', b'\xff\xd8\xff\xe0'),
                uploaded_file('test_file3.jpeg', b'\xff\xd8\xff\xe0'),
                uploaded_file('test_file4.pg', b'not allowed'),
                uploaded_file('test_file5.tif', b'II*\x00'),
                uploaded_file('test_file6.tiff', b'MM\x00*'),
                uploaded_file('test_file7.bmp', b'BM'),
                uploaded_file('test_file8.invalid_ext', b'not allowed'),
            ]
            form = UploadForm()
            form.documents.data = invalid_test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, None)
            with pytest.raises(StopValidation, match='File does not have an approved extension: jpg, jpeg, png, tif,'
                                                     ' tiff, bmp, pdf'):
                validator.__call__(form, form.documents)

    def test_multi_file_allowed_public_file_upload_invalid_file_data_not_iterable(self, app):
        with app.test_request_context():
            invalid_test_files_uploaded = uploaded_file('test_file1.pdf', b'%PDF-1.4'),

            form = UploadForm()
            form.documents.data = invalid_test_files_uploaded
            validator = MultiFileAllowed(form.upload_set, None)
            assert validator.__call__(form, form.documents) is None

    def test_multi_file_allowed_rejects_disguised_file_content(self, app):
        with app.test_request_context():
            form = UploadForm()
            form.documents.data = [uploaded_file('test_file.png', b'MZ executable')]
            validator = MultiFileAllowed(form.upload_set, 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')

            with pytest.raises(StopValidation, match='Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB'):
                validator.__call__(form, form.documents)

    def test_multi_file_allowed_rejects_double_extension(self, app):
        with app.test_request_context():
            form = UploadForm()
            form.documents.data = [uploaded_file('test_file.bat.png', b'\x89PNG\r\n\x1a\n')]
            validator = MultiFileAllowed(form.upload_set, 'Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')

            with pytest.raises(StopValidation, match='Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB'):
                validator.__call__(form, form.documents)
