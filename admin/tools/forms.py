from flask_wtf import FlaskForm
from wtforms import PasswordField, MultipleFileField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import MultiFileAllowed, fileSizeLimit, fileVirusScan


class UnlockFileForm(FlaskForm):
    upload_set = ['pdf']

    file = MultipleFileField(
        validators=[
            DataRequired(message='Select a PDF file to upload'),
            MultiFileAllowed(upload_set, message='Select a PDF file to upload'),
            fileSizeLimit(10),
            fileVirusScan
        ]
    )

    pdf_password = PasswordField()
