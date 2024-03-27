from flask_wtf import FlaskForm
from wtforms import PasswordField, FileField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import SingleFileAllowed, fileSizeLimit, fileVirusScan


class UnlockFileForm(FlaskForm):
    upload_set = ['pdf']

    file = FileField(
        validators=[
            DataRequired(message='Select a PDF file to upload'),
            SingleFileAllowed(upload_set, message='Select a PDF file to upload'),
            fileSizeLimit(10),
            fileVirusScan
        ]
    )

    pdf_password = PasswordField()
