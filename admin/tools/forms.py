from flask_wtf import FlaskForm
from wtforms import PasswordField, FileField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import SingleFileAllowed, MultiFileAllowed, validate_file_size_limit, fileVirusScan


class UnlockFileForm(FlaskForm):
    file_size_limit_mb = 10
    upload_set = ['pdf']

    file = FileField(
        validators=[
            DataRequired(message='Select a PDF file to upload'),
            SingleFileAllowed(upload_set, message='Select a PDF file to upload'),
            validate_file_size_limit,
            fileVirusScan
        ]
    )

    pdf_password = PasswordField()
