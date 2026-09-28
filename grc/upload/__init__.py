import datetime
import io
from typing import List, Callable
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, request, url_for, abort, make_response, g
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
from grc.business_logic.data_store import DataStore
from grc.business_logic.data_structures.application_data import any_duplicate_aws_file_names
from grc.business_logic.data_structures.uploads_data import (
    UploadsData,
    EvidenceFile,
    MEDICAL_REPORT_SLOT_FIRST,
    MEDICAL_REPORT_SLOT_SECOND,
)
from grc.business_logic.constants.uploads import UploadsConstants as c
from grc.upload.forms import (
    UploadForm,
    MedicalReportsUploadForm,
    DeleteForm,
    PasswordsForm,
    DeleteAllFilesInSectionForm,
)
from grc.utils.decorators import LoginRequired
from grc.external_services.aws_s3_client import AwsS3Client
from grc.utils.flask_child_form_add_custom_errors import add_error_for_child_form
from grc.utils.pdf_utils import PDFUtils
from grc.utils.redirect import local_redirect
from grc.utils.logger import LogLevel, Logger

logger = Logger()
upload = Blueprint('upload', __name__)


class UploadSection:
    def __init__(self, url: str, data_section: str, html_file: str, file_list: Callable[[UploadsData], List[EvidenceFile]]):
        self.url = url
        self.data_section = data_section
        self.html_file = html_file
        self.file_list = file_list


sections = [
    UploadSection(url='medical-reports', data_section='medicalReports', html_file='medical-reports.html', file_list=(lambda u: u.medical_reports)),
    UploadSection(url='gender-evidence', data_section='genderEvidence', html_file='evidence.html', file_list=(lambda u: u.evidence_of_living_in_gender)),
    UploadSection(url='name-change', data_section='nameChange', html_file='name-change.html', file_list=(lambda u: u.name_change_documents)),
    UploadSection(url='marriage-documents', data_section='marriageDocuments', html_file='marriage-documents.html', file_list=(lambda u: u.partnership_documents)),
    UploadSection(url='overseas-certificate', data_section='overseasCertificate', html_file='overseas-certificate.html', file_list=(lambda u: u.overseas_documents)),
    UploadSection(url='statutory-declarations', data_section='statutoryDeclarations', html_file='statutory-declarations.html', file_list=(lambda u: u.statutory_declarations)),
    UploadSection(url='birth-or-adoption-certificate', data_section='birthOrAdoptionCertificate',html_file='birth-or-adoption-certificate.html', file_list=(lambda u: u.birth_or_adoption_certificates))
]


def delete_file(application_data, file_name, section):
    try:
        AwsS3Client().delete_object(file_name)
    except Exception as e:
        logger.log(LogLevel.ERROR, f"Could not delete file ({file_name}). Error was {e}")
        # We could not delete the file. Perhaps it doesn't exist.
        pass

    files = section.file_list(application_data.uploads_data)
    file_to_remove = next(filter(lambda file: file.aws_file_name == file_name, files), None)
    try:
        files.remove(file_to_remove)
    except:
        pass

    return application_data


def create_aws_file_name(reference_number, section_name, original_file_name):
    filename = secure_filename(original_file_name)
    last_dot_position = filename.rfind('.')
    file_prefix = (filename[:last_dot_position]) if last_dot_position > -1 else filename
    file_extension = (filename[(last_dot_position + 1):]) if last_dot_position > -1 else ''
    aws_file_name = f"{reference_number}__{section_name}__{file_prefix}_{uuid.uuid4().hex}.{file_extension}"
    return aws_file_name


def check_pdf_password(section, application_data, passwordForm):
    files = section.file_list(application_data.uploads_data)
    file_to_check = next(filter(lambda file: file.aws_file_name == passwordForm.aws_file_name.data, files), None)
    if file_to_check is not None:
        data = AwsS3Client().download_object(file_to_check.aws_file_name)
        if data is not None:
            input_pdf_stream = io.BytesIO(data.getvalue())
            if not PDFUtils().is_pdf_password_protected(input_pdf_stream):
                return True

            if PDFUtils().is_pdf_password_correct(input_pdf_stream, passwordForm.password.data):

                # Generate a new PDF
                output_pdf_stream = PDFUtils().remove_pdf_password_protection(input_pdf_stream, passwordForm.password.data)

                AwsS3Client().delete_object(file_to_check.aws_file_name)
                AwsS3Client().upload_fileobj(output_pdf_stream, file_to_check.aws_file_name)

                file_to_check.password_required = False
                DataStore.save_application(application_data)
                return True
    return False


def clear_form_errors(form):
    for _form_field, form_error in form.errors.items():
        form_error.clear()


def delete_password_protected_files(section, application_data):
    password_protected_files = [file for file in section.file_list(application_data.uploads_data) if file.password_required]
    for file in password_protected_files:
        application_data = delete_file(application_data, file.aws_file_name, section)
    return application_data


def resize_image(document):
    try:
        img = Image.open(document)

        #To use JPEG, image must be RBG
        if img.mode in ("RGBA", "P"):
            logger.log(LogLevel.INFO, "Image changed from RBGA to RBG")
            img = img.convert("RGB")

        img = rotate_image_to_match_exif_orientation_flag(img)

        width, height = img.size
        ratio = 1.
        if height >= width:
            if width > 1400:
                ratio = 1400 / width
            elif height > 2100:
                ratio = 2100 / height
        else:
            if width > 2100:
                ratio = 2100 / width
            elif height > 1400:
                ratio = 1400 / height
        if ratio != 1.:
            img = img.resize((int(width * ratio), int(height * ratio)), Image.Resampling.LANCZOS)

        bytes_buffer = io.BytesIO()
        img.save(bytes_buffer, format='JPEG', quality=50)
        bytes_buffer.seek(0)

        return True, bytes_buffer

    except Exception as e:
        file_name = document.filename
        logger.log(LogLevel.ERROR, f"Could not resize image ({file_name}). Error was {e}")

    return False, document


def upload_file_or_raise(s3_client, document, object_name, created_object_names):
    if not s3_client.upload_fileobj(document, object_name):
        raise RuntimeError(f'Could not upload {object_name}')
    created_object_names.append(object_name)


def store_evidence_file(s3_client, document, application_data, section, created_object_names,
                        medical_report_slot=None):
    original_file_name = document.filename
    object_name = create_aws_file_name(application_data.reference_number, section.data_section, original_file_name)
    password_required = False
    file_type = original_file_name.rsplit('.', 1)[-1].lower() if '.' in original_file_name else ''

    if file_type == 'pdf':
        data = io.BytesIO(document.read())
        document.seek(0)
        try:
            if PDFUtils().is_pdf_form(data):
                document = PDFUtils().flatten_form_pdf_stream(data)
            if PDFUtils().is_pdf_password_protected(data):
                password_required = True
            upload_file_or_raise(s3_client, document, object_name, created_object_names)
        except Exception as error:
            logger.log(LogLevel.ERROR, f'User uploaded PDF attachment ({object_name}) which could not be stored: {error}')
            raise
    elif file_type in ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp']:
        resized, resized_document = resize_image(document)
        if resized:
            original_object_name, file_extension = object_name.rsplit('.', 1)
            upload_file_or_raise(
                s3_client,
                document,
                f'{original_object_name}_original.{file_extension}',
                created_object_names,
            )
            object_name = f'{original_object_name}.jpg'
        upload_file_or_raise(s3_client, resized_document, object_name, created_object_names)
    else:
        upload_file_or_raise(s3_client, document, object_name, created_object_names)

    evidence_file = EvidenceFile()
    evidence_file.original_file_name = original_file_name
    evidence_file.aws_file_name = object_name
    evidence_file.password_required = password_required
    evidence_file.medical_report_slot = medical_report_slot
    return evidence_file


def rollback_uploaded_files(s3_client, object_names):
    for object_name in reversed(object_names):
        if not s3_client.delete_object(object_name):
            logger.log(LogLevel.ERROR, f'Could not roll back uploaded object {object_name}')


def add_upload_failure_errors(field):
    field.errors.extend([c.UPLOAD_FAILED_ERROR, c.UPLOAD_FAILED_RETRY])


def medical_report_files(files, slot):
    return [file for file in files if getattr(file, 'medical_report_slot', None) == slot]


def legacy_medical_report_files(files):
    return [
        file for file in files
        if getattr(file, 'medical_report_slot', None) not in {
            MEDICAL_REPORT_SLOT_FIRST,
            MEDICAL_REPORT_SLOT_SECOND,
        }
    ]


def medical_reports_complete(files):
    if legacy_medical_report_files(files):
        return True
    return bool(
        medical_report_files(files, MEDICAL_REPORT_SLOT_FIRST)
        and medical_report_files(files, MEDICAL_REPORT_SLOT_SECOND)
    )


def rotate_image_to_match_exif_orientation_flag(image: Image):
    try:
        exif_data = image.getexif()
        orientation_flag = exif_data.get(274)  # 274 (0x0112) is the Orientation flag: https://exiftool.org/TagNames/EXIF.html

        # Rotate as needed: https://jdhao.github.io/2019/07/31/image_rotation_exif_info/
        if orientation_flag == 8:
            image = image.transpose(Image.ROTATE_90)
        if orientation_flag == 3:
            image = image.transpose(Image.ROTATE_180)
        if orientation_flag == 6:
            image = image.transpose(Image.ROTATE_270)

        return image

    except Exception as e:
        return image


@upload.route('/upload/<section_url>', methods=['GET', 'POST'])
@LoginRequired
def uploadInfoPage(section_url: str):
    section = next(filter(lambda section: section.url == section_url, sections), None)
    if section is None:
        return abort(404)

    is_medical_reports = section.url == 'medical-reports'
    form = MedicalReportsUploadForm() if is_medical_reports else UploadForm()
    deleteform = DeleteForm()
    deleteAllFilesInSectionForm = DeleteAllFilesInSectionForm()
    application_data = DataStore.load_application_by_session_reference_number()
    files = section.file_list(application_data.uploads_data)
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.button_clicked.data == form.UploadEnum.UPLOAD_FILE.name:
                uploads = []
                if is_medical_reports:
                    uploads.extend((document, MEDICAL_REPORT_SLOT_FIRST)
                                   for document in form.first_medical_report.data if document.filename)
                    uploads.extend((document, MEDICAL_REPORT_SLOT_SECOND)
                                   for document in form.second_medical_report.data if document.filename)
                else:
                    uploads.extend((document, None) for document in form.documents.data if document.filename)

                s3_client = AwsS3Client()
                created_object_names = []
                new_evidence_files = []
                try:
                    for document, medical_report_slot in uploads:
                        new_evidence_files.append(store_evidence_file(
                            s3_client,
                            document,
                            application_data,
                            section,
                            created_object_names,
                            medical_report_slot,
                        ))
                    files.extend(new_evidence_files)
                    DataStore.save_application(application_data)
                except Exception as error:
                    logger.log(LogLevel.ERROR, message=f'Error uploading file: {error}')
                    for evidence_file in new_evidence_files:
                        if evidence_file in files:
                            files.remove(evidence_file)
                    rollback_uploaded_files(s3_client, created_object_names)
                    if is_medical_reports:
                        if form.first_medical_report.data and any(file.filename for file in form.first_medical_report.data):
                            add_upload_failure_errors(form.first_medical_report)
                        if form.second_medical_report.data and any(file.filename for file in form.second_medical_report.data):
                            add_upload_failure_errors(form.second_medical_report)
                    else:
                        add_upload_failure_errors(form.documents)
                else:
                    if any(file.password_required for file in new_evidence_files):
                        return local_redirect(url_for('upload.documentPassword', section_url=section.url))
                    return local_redirect(url_for('upload.uploadInfoPage', section_url=section.url) + '#file-upload-section')

            elif form.button_clicked.data == form.UploadEnum.SAVE_AND_CONTINUE.name:
                if is_medical_reports and not medical_reports_complete(files):
                    if not medical_report_files(files, MEDICAL_REPORT_SLOT_FIRST):
                        form.first_medical_report.errors.append(c.FILE_TYPE_PUBLIC_ERROR)
                    if not medical_report_files(files, MEDICAL_REPORT_SLOT_SECOND):
                        form.second_medical_report.errors.append(c.FILE_TYPE_PUBLIC_ERROR)
                elif len(files) > 0:
                    return local_redirect(url_for('taskList.index'))
                else:
                    form.documents.errors.append(c.FILE_TYPE_PUBLIC_ERROR)

    return render_template(
        f"upload/{section.html_file}",
        form=form,
        deleteform=deleteform,
        deleteAllFilesInSectionForm=deleteAllFilesInSectionForm,
        section_url=section.url,
        currently_uploaded_files=files,
        duplicate_aws_file_names=any_duplicate_aws_file_names(files),
        first_medical_report_files=medical_report_files(files, MEDICAL_REPORT_SLOT_FIRST),
        second_medical_report_files=medical_report_files(files, MEDICAL_REPORT_SLOT_SECOND),
        legacy_medical_report_files=legacy_medical_report_files(files),
        date_now=datetime.datetime.now(),
        date_two_years_ago=(datetime.datetime.now() - relativedelta(years=2)),
        lang_code=g.lang_code
    )


@upload.route('/upload/<section_url>/document-password', methods=['GET', 'POST'])
@LoginRequired
def documentPassword(section_url: str):
    section = next(filter(lambda section: section.url == section_url, sections), None)
    if section is None:
        return abort(404)

    passwordsForm = PasswordsForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if request.method == 'POST':
        remove_file_button_was_clicked = False
        for password_form in passwordsForm.files:
            if password_form.button_clicked.data:
                remove_file_button_was_clicked = True

        if remove_file_button_was_clicked:
            for password_form in passwordsForm.files:
                if password_form.button_clicked.data:
                    delete_file(application_data, password_form.aws_file_name.data, section)
                    DataStore.save_application(application_data)
        else:
            passwordsForm.validate()

            for passwordForm in passwordsForm.files:
                if passwordForm.password.data:
                    password_ok = check_pdf_password(section, application_data, passwordForm)
                    if not password_ok:
                        wrong_password_error_message = f"{passwordForm.original_file_name.data}: The password is incorrect"
                        add_error_for_child_form(passwordsForm.files, passwordForm, 'password', wrong_password_error_message)
                else:
                    no_password_error_message = f"{passwordForm.original_file_name.data}: Enter the password for this document"
                    add_error_for_child_form(passwordsForm.files, passwordForm, 'password', no_password_error_message)

    files = [file for file in section.file_list(application_data.uploads_data) if file.password_required]
    if len(files) == 0:
        return local_redirect(url_for('upload.uploadInfoPage', section_url=section.url) + '#file-upload-section')

    files_before = len(passwordsForm.files)
    passwordsForm.process(data={ 'files': files })
    files_after = len(passwordsForm.files)

    if files_before != files_after:
        clear_form_errors(passwordsForm)

    return render_template(
        "upload/document-password.html",
        passwordsForm=passwordsForm,
        section_url=section.url,
        currently_uploaded_files=files
    )


@upload.route('/upload/<section_url>/remove-file', methods=['POST'])
@LoginRequired
def removeFile(section_url: str):
    section = next(filter(lambda section: section.url == section_url, sections), None)
    if section is None:
        return abort(404)

    form = DeleteForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data = delete_file(application_data, form.file.data, section)
        DataStore.save_application(application_data)

    files = section.file_list(application_data.uploads_data)
    #if 'referrer' in request and request.referrer.endswith('/document-password') and len(files) > 0:
    #    return local_redirect(url_for('upload.documentPassword', section_url=section.url))
    #else:
    return local_redirect(url_for('upload.uploadInfoPage', section_url=section.url) + '#file-upload-section')


@upload.route('/upload/<section_url>/remove-all-files-in-section', methods=['POST'])
@LoginRequired
def removeAllFilesInSection(section_url: str):
    # The following line looks pointless, but it validates the CSRF token
    #   Without this, we get an HTTP 405 Method Not Allowed error on the following page
    form = DeleteAllFilesInSectionForm()

    section = next(filter(lambda section: section.url == section_url, sections), None)
    if section is None:
        return abort(404)

    application_data = DataStore.load_application_by_session_reference_number()

    files = section.file_list(application_data.uploads_data)
    aws_file_names = list(map(lambda file: file.aws_file_name, files))
    for aws_file_name in aws_file_names:
        application_data = delete_file(application_data, aws_file_name, section)

    DataStore.save_application(application_data)

    return local_redirect(url_for('upload.uploadInfoPage', section_url=section.url))


@upload.route('/upload/<section_url>/download', methods=['GET'])
@LoginRequired
def download(section_url):
    section = next(filter(lambda section: section.url == section_url, sections), None)
    if section is None:
        return abort(404)

    file_name = request.args.get('file', default=None)
    if file_name is not None:
        application_data = DataStore.load_application_by_session_reference_number()
        files = [file for file in section.file_list(application_data.uploads_data) if file.aws_file_name == file_name]
        if '_original.' in file_name:
            pass
        elif len(files) == 0:
            return abort(403)

        data = AwsS3Client().download_object(file_name)
        if data:
            file_type = 'application/octet-stream'
            if '.' in file_name:
                file_type = file_name[file_name.rindex('.') + 1:].lower()
                if file_type == 'pdf':
                    file_type = 'application/pdf'
                elif file_type == 'jpg':
                    file_type = 'image/jpeg'
                else:
                    file_type = 'image/' + file_type

            bytes = data.getvalue()
            if bytes is None:
                return abort(406)

            response = make_response(bytes)
            response.headers.set('Content-Type', file_type)
            response.headers.set('Content-Disposition', 'attachment', filename=file_name)
            return response

    abort(404)
