import io
import os
import zipfile
from flask import render_template
from typing import Callable, List, Dict
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.uploads_data import UploadsData, EvidenceFile
from grc.external_services.aws_s3_client import AwsS3Client
from grc.utils.logger import LogLevel, Logger
from grc.utils.pdf_utils import create_pdf_from_html, merge_pdfs, is_pdf_password_protected

logger = Logger()

sections = ['medicalReports', 'genderEvidence', 'nameChange', 'marriageDocuments', 'overseasCertificate', 'statutoryDeclarations']
section_names = ['Medical Reports', 'Gender Evidence', 'Name Change', 'Marriage Documents', 'Overseas Certificate', 'Statutory Declarations']
section_files:  Dict[str, Callable[[UploadsData], List[EvidenceFile]]] = {
    'medicalReports': (lambda u: u.medical_reports),
    'genderEvidence': (lambda u: u.evidence_of_living_in_gender),
    'nameChange': (lambda u: u.name_change_documents),
    'marriageDocuments': (lambda u: u.partnership_documents),
    'overseasCertificate': (lambda u: u.overseas_documents),
    'statutoryDeclarations': (lambda u: u.statutory_declarations),
}

def get_files_for_section(section, application_data):
    return section_files[section](application_data.uploads_data)

def get_section_name(section):
    return section_names[sections.index(section)]


class ApplicationFiles():
    def create_or_download_attachments(self, reference_number, application_data: ApplicationData, download=False):
        bytes = None
        zip_file_file_name = ''

        try:
            zip_file_file_name = reference_number + '.zip'

            data = None if os.getenv('FLASK_ENV', '') == 'development' else AwsS3Client().download_object(zip_file_file_name)
            if data:
                if download:
                    bytes = data.getvalue()
            else:
                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, 'x', zipfile.ZIP_DEFLATED, False) as zipper:
                    for section in sections:
                        files = get_files_for_section(section, application_data)
                        for file_index, evidence_file in enumerate(files):
                            data = AwsS3Client().download_object(evidence_file.aws_file_name)
                            if data is not None:
                                attachment_file_name = f"{reference_number}__{section}__{(file_index + 1)}_{evidence_file.original_file_name}"
                                zipper.writestr(attachment_file_name, data.getvalue())

                    data, _ = self.create_or_download_pdf(reference_number, application_data, attach_files=False, download=True)
                    zipper.writestr('application.pdf', data)

                bytes = zip_buffer.getvalue()
                AwsS3Client().upload_fileobj(zip_buffer, attachment_file_name)
                if not download:
                    bytes = None

        except Exception as e:
            logger.log(LogLevel.ERROR, e)

        return bytes, zip_file_file_name


    def create_or_download_pdf(self, reference_number, application_data: ApplicationData, is_admin=True, attach_files=True, download=False):
        bytes = None
        file_name = ''

        try:
            file_name = reference_number + '.pdf' if is_admin else 'grc_' + str(application_data.email_address).replace('@', '_').replace('.', '_') + '.pdf'

            data = None
            if is_admin and not attach_files:
                data = None if os.getenv('FLASK_ENV', '') == 'development' else AwsS3Client().download_object(file_name)
            if data:
                if download:
                    bytes = data.getvalue()
            else:
                all_sections = sections
                if is_admin:
                    all_sections = ['statutoryDeclarations', 'marriageDocuments', 'nameChange', 'medicalReports', 'genderEvidence', 'overseasCertificate']

                pdfs = []
                pdfs.append(create_application_cover_sheet_pdf(application_data, is_admin))

                if attach_files:
                    attach_all_files(pdfs, all_sections, application_data)

                else:
                    attachments_pdf = create_attachment_names_pdf(all_sections, application_data)
                    if attachments_pdf:
                        pdfs.append(attachments_pdf)

                data = merge_pdfs(pdfs)
                
                bytes = data.read()
                if is_admin and not attach_files:
                    AwsS3Client().upload_fileobj(data, file_name)
                if not download:
                    bytes = None

        except Exception as e:
            logger.log(LogLevel.ERROR, e)

        return bytes, file_name


    def delete_application_files(self, reference_number, application_data: ApplicationData):
        AwsS3Client().delete_object(reference_number + '.zip')
        AwsS3Client().delete_object(reference_number + '.pdf')

        for section in sections:
            files = get_files_for_section(section, application_data)
            for evidence_file in files:
                AwsS3Client().delete_object(evidence_file.aws_file_name)


def create_application_cover_sheet_pdf(application_data, is_admin):
    html_template = ('applications/download.html' if is_admin else 'applications/download_user.html')
    html = render_template(html_template, application_data=application_data)
    return create_pdf_from_html(html)


def create_attachment_names_pdf(all_sections, application_data):
    attachments_html = ''
    for section in all_sections:
        files = get_files_for_section(section, application_data)
        if len(files) > 0:
            attachments_html += f'<h3 style="font-size: 14px;">{get_section_name(section)}</h3>'
            for file_index, evidence_file in enumerate(files):
                attachments_html += f'<p style="font-size: 12px;">Attachment {file_index + 1} of {len(files)}: {evidence_file.aws_file_name}</p>'

    if attachments_html != '':
        logger.log(LogLevel.INFO, "Adding attachments pdf")
        return create_pdf_from_html(attachments_html)


def attach_all_files(pdfs, all_sections, application_data):
    for section in all_sections:
        files = get_files_for_section(section, application_data)
        for file_index, evidence_file in enumerate(files):
            add_object(pdfs, section, evidence_file.aws_file_name, evidence_file.original_file_name, file_index + 1, len(files))


def add_object(pdfs, section, object_name, original_file_name, idx, num):
    if '.' in object_name:
        file_type = object_name[object_name.rindex('.') + 1:]

        if file_type.lower() == 'pdf':
            try:
                data = AwsS3Client().download_object(object_name)
                if data is not None:
                    if is_pdf_password_protected(data):
                        # We can check the type of password (user/owner):
                        # doc.authenticate('') == 2
                        # https://pymupdf.readthedocs.io/en/latest/document.html#Document.authenticate
                        html = f'<h3 style="font-size: 14px; color: red;">Unable to add {original_file_name}. A password is required.</h3>'
                        pdfs.append(create_pdf_from_html(html))
                        logger.log(LogLevel.ERROR, f"file {object_name} needs a password!")
                    else:
                        pdfs.append(data)
                        logger.log(LogLevel.INFO, f"Attaching {object_name}")
                else:
                    logger.log(LogLevel.ERROR, f"Error attaching {object_name}")
                    pdfs.append(create_pdf_for_attachment_error(original_file_name))
            except:
                logger.log(LogLevel.ERROR, f"Error attaching {object_name}")
                pdfs.append(create_pdf_for_attachment_error(original_file_name))
        else:
            try:
                data, width, height = AwsS3Client().download_object_data(object_name)
                if data is not None:
                    html = f'<img src="{data}" width="{width}" height="{height}" style="max-width: 90%;">'
                    pdfs.append(create_pdf_from_html(html))
                    logger.log(LogLevel.INFO, f"Adding image {object_name}")
                else:
                    logger.log(LogLevel.ERROR, f"Error downloading {object_name}")
                    pdfs.append(create_pdf_for_attachment_error(original_file_name))

            except:
                logger.log(LogLevel.ERROR, f"Error attaching {object_name}")
                create_pdf_for_attachment_error(original_file_name)
    else:
        logger.log(LogLevel.ERROR, f"Error attaching {object_name}")
        create_pdf_for_attachment_error(original_file_name)


def create_pdf_for_attachment_error(file_name):
    html = f'<h3 style="font-size: 14px; color: red;">WARNING: Could not attach file ({file_name})</h3>'
    return create_pdf_from_html(html)
