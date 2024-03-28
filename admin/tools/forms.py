from flask_wtf import FlaskForm
from wtforms import PasswordField, MultipleFileField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import MultiFileAllowed, validate_file_size_limit, fileVirusScan


class UnlockFileForm(FlaskForm):
    file_size_limit_mb = 10
    file = MultipleFileField(
        validators=[
            DataRequired(message='Select a PDF file to upload'),
            MultiFileAllowed(['pdf'], message='Select a PDF file to upload'),
            validate_file_size_limit,
            fileVirusScan
        ]
    )

    pdf_password = PasswordField()
