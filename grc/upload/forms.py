import enum

from flask_wtf import Form, FlaskForm
from grc.business_logic.constants.uploads import UploadsConstants as c
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyMultiFileAllowed
from grc.utils.form_custom_validators import validate_multiple_files_size_limit, file_virus_scan, StrictRequiredIf
from wtforms import MultipleFileField, HiddenField, PasswordField, SubmitField, FormField, FieldList
from wtforms.validators import DataRequired, StopValidation


class BaseUploadForm(FlaskForm):

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

    def get_csrf_token(self):
        return self._csrf.generate_csrf_token('csrf_token')


class UploadForm(BaseUploadForm):
    documents = MultipleFileField(
        validators=[
            StrictRequiredIf('button_clicked', BaseUploadForm.UploadEnum.UPLOAD_FILE.name,
                             message=c.FILE_TYPE_PUBLIC_ERROR,
                             validators=[
                                 LazyMultiFileAllowed(BaseUploadForm.upload_set, lazy_message=c.FILE_TYPE_PUBLIC_ERROR),
                                 validate_multiple_files_size_limit,
                                 file_virus_scan
                             ]),
        ]
    )


def optional_multiple_files(_form, field):
    if not any(getattr(file, 'filename', '') for file in (field.data or [])):
        field.errors[:] = []
        raise StopValidation()


def medical_report_validators():
    return [
        optional_multiple_files,
        LazyMultiFileAllowed(BaseUploadForm.upload_set, lazy_message=c.FILE_TYPE_PUBLIC_ERROR),
        validate_multiple_files_size_limit,
        file_virus_scan,
    ]


class MedicalReportsUploadForm(BaseUploadForm):
    first_medical_report = MultipleFileField(validators=medical_report_validators())
    second_medical_report = MultipleFileField(validators=medical_report_validators())

    @staticmethod
    def _has_files(field):
        return any(getattr(file, 'filename', '') for file in (field.data or []))

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators)
        if self.button_clicked.data == self.UploadEnum.UPLOAD_FILE.name and not (
            self._has_files(self.first_medical_report) or self._has_files(self.second_medical_report)
        ):
            if not self.first_medical_report.errors:
                self.first_medical_report.errors.append(c.FILE_TYPE_PUBLIC_ERROR)
            return False
        return is_valid


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
