import enum

from flask_wtf import Form, FlaskForm
from grc.business_logic.constants.uploads import UploadsConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyMultiFileAllowed
from grc.utils.form_custom_validators import validate_multiple_files_size_limit, file_virus_scan, StrictRequiredIf
from wtforms import MultipleFileField, HiddenField, PasswordField, SubmitField, FormField, FieldList
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):

    class UploadEnum(enum.Enum):
        UPLOAD_FILE = enum.auto()
        SAVE_AND_CONTINUE = enum.auto()

    upload_set = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp', 'pdf']
    file_size_limit_mb = 10

    button_clicked = LazyRadioField(
        lazy_choices=[
            (UploadEnum.UPLOAD_FILE.name, c.UPLOAD_FILE),
            (UploadEnum.SAVE_AND_CONTINUE.name, c.SAVE_AND_CONTINUE)
        ],
        validators=[LazyDataRequired(lazy_message=c.UPLOAD_OR_SAVE_ERROR)]
    )

    documents = MultipleFileField(
        validators=[
            StrictRequiredIf('button_clicked', UploadEnum.UPLOAD_FILE.name,
                             message=c.FILE_TYPE_PUBLIC_ERROR,
                             validators=[
                                 LazyMultiFileAllowed(upload_set, lazy_message=c.FILE_TYPE_PUBLIC_ERROR),
                                 validate_multiple_files_size_limit,
                                 file_virus_scan
                             ]),
        ]
    )

    def get_csrf_token(self):
        return self._csrf.generate_csrf_token('csrf_token')


class DeleteForm(FlaskForm):
    file = HiddenField(
        validators=[DataRequired(message='Field is required')]
    )

    def get_csrf_token(self):
        return self._csrf.generate_csrf_token('csrf_token')


class PasswordForm(Form):
    aws_file_name = HiddenField(
        validators=[DataRequired(message='Field is required')]
    )

    original_file_name = HiddenField(
        validators=[DataRequired(message='Field is required')]
    )

    file_index = HiddenField(
        validators=[DataRequired(message='Field is required')]
    )

    password = PasswordField(
        # We would normally validate DataRequired
        # But we want to generate the error messages dynamically, including the file name in the error message
        # So we do this in the upload/__init__.py file
    )

    button_clicked = SubmitField()


class PasswordsForm(FlaskForm):
    files = FieldList(FormField(PasswordForm), min_entries=1)

    def get_csrf_token(self):
        return self._csrf.generate_csrf_token('csrf_token')


class DeleteAllFilesInSectionForm(FlaskForm):
    def get_csrf_token(self):
        return self._csrf.generate_csrf_token('csrf_token')
