from flask_wtf import FlaskForm
from wtforms import PasswordField, MultipleFileField
from wtforms.validators import DataRequired
from grc.utils.form_custom_validators import MultiFileAllowed, fileSizeLimit, file_virus_scan


class UnlockFileForm(FlaskForm):
    file = MultipleFileField(
        validators=[
            DataRequired(message='Select a PDF file to upload'),
            MultiFileAllowed(['pdf'], message='Select a PDF file to upload'),
            fileSizeLimit(10),
            file_virus_scan
        ]
    )

    pdf_password = PasswordField()
