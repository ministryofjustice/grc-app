from io import BytesIO
import zipfile
from flask import render_template
from typing import Callable, List, Dict, Tuple
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.uploads_data import UploadsData, EvidenceFile
from grc.external_services.aws_s3_client import AwsS3Client
from grc.utils.logger import LogLevel, Logger
from grc.utils.pdf_utils import PDFUtils
from memory_profiler import profile

logger = Logger()


class ApplicationFiles:
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

    def _get_files_for_section(self, section: str, application_data: ApplicationData) -> list:
        return self.section_files[section](application_data.uploads_data)

    def _get_section_name(self, section: str) -> str:
        return self.section_names[self.sections.index(section)]

    def _create_application_zip(self, application_data: ApplicationData) -> BytesIO:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'x', zipfile.ZIP_DEFLATED, False) as zipper:
            for section in self.sections:
                files = self._get_files_for_section(section, application_data)
                for file_index, evidence_file in enumerate(files):
                    data = AwsS3Client().download_object(evidence_file.aws_file_name)
                    if data is not None:
                        attachment_file_name = (f"{application_data.reference_number}__{section}__{(file_index + 1)}_"
                                                f"{evidence_file.original_file_name}")
                        zipper.writestr(attachment_file_name, data.getvalue())

                    file_name, file_ext = self.get_filename_and_extension(evidence_file.aws_file_name)
                    original_file_name, original_file_ext = self.get_filename_and_extension(evidence_file.original_file_name)
                    if original_file_ext.lower() in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']:
                        data = AwsS3Client().download_object(f'{file_name}_original{original_file_ext}')
                        if data is not None:
                            file_name, file_ext = self.get_filename_and_extension(evidence_file.original_file_name)
                            attachment_file_name = (f"{application_data.reference_number}__{section}__"
                                                    f"{(file_index + 1)}_{file_name}_original{file_ext}")
                            zipper.writestr(attachment_file_name, data.getvalue())

            application_pdf = self.download_pdf_admin(application_data)
            if not application_pdf:
                application_pdf, _ = self.create_pdf_admin_with_filenames(application_data)

            zipper.writestr('application.pdf', application_pdf)
        zip_buffer.seek(0)
        return zip_buffer

    def _create_pdf_attach_files(self, application_data: ApplicationData, pdfs, sections) -> BytesIO:
        self.attach_all_files(pdfs, sections, application_data)
        output_pdf_document = PDFUtils().merge_pdfs(pdfs)
        return output_pdf_document

    def _create_pdf_attach_filenames(self, application_data: ApplicationData, pdfs, sections) -> BytesIO:
        attachments_pdf = self.create_attachment_names_pdf(sections, application_data)
        if attachments_pdf:
            pdfs.append(attachments_pdf)
        output_pdf_document = PDFUtils().merge_pdfs(pdfs)
        return output_pdf_document

    def create_and_upload_attachments(self, reference_number: str, application_data: ApplicationData):
        zip_file_name = f'{reference_number}.zip'
        logger.log(LogLevel.INFO, message=f'creating attachments for {zip_file_name}')
        application_zip = self._create_application_zip(application_data)
        return AwsS3Client().upload_fileobj(application_zip, zip_file_name)

    def download_attachments(self, reference_number: str, application_data: ApplicationData) -> Tuple[bytes, str]:
        zip_file_name = f'{reference_number}.zip'
        data = AwsS3Client().download_object(zip_file_name)
        if data:
            return data.getvalue(), zip_file_name

        logger.log(LogLevel.WARN, message=f'unable to download {zip_file_name}. Attempting to download and attach'
                                          f'files individually')
        application_zip = self._create_application_zip(application_data)
        return application_zip.getvalue(), zip_file_name

    def create_pdf_public(self, application_data: ApplicationData) -> Tuple[bytes, str]:
        file_name = 'grc_' + str(application_data.email_address).replace('@', '_').replace('.', '_') + '.pdf'
        pdfs = [self.create_application_cover_sheet_pdf(application_data, False)]
        output_pdf_document = self._create_pdf_attach_files(application_data, pdfs, self.sections)
        return output_pdf_document.read(), file_name

    @profile
    def create_pdf_admin_with_files_attached(self, application_data) -> Tuple[BytesIO, str]:
        file_name = application_data.reference_number + '.pdf'
        pdfs = [self.create_application_cover_sheet_pdf(application_data, True)]
        all_sections = ['statutoryDeclarations', 'marriageDocuments', 'nameChange', 'medicalReports', 'genderEvidence',
                        'overseasCertificate']
        return self._create_pdf_attach_files(application_data, pdfs, all_sections), file_name

    def create_pdf_admin_with_filenames(self, application_data) -> Tuple[bytes, str]:
        file_name = application_data.reference_number + '.pdf'
        pdfs = [self.create_application_cover_sheet_pdf(application_data, True)]
        all_sections = ['statutoryDeclarations', 'marriageDocuments', 'nameChange', 'medicalReports', 'genderEvidence',
                        'overseasCertificate']
        return self._create_pdf_attach_filenames(application_data, pdfs, all_sections).read(), file_name

    def upload_pdf_admin_with_files_attached(self, application_data: ApplicationData) -> bool:
        file_name = application_data.reference_number + '.pdf'
        return AwsS3Client().upload_fileobj(self.create_pdf_admin_with_files_attached(application_data)[0], file_name)

    @staticmethod
    def download_pdf_admin(application_data: ApplicationData) -> bytes:
        file_name = application_data.reference_number + '.pdf'
        pdf = AwsS3Client().download_object(file_name)
        return pdf.getvalue() if pdf else None

    def delete_application_files(self, reference_number: str, application_data: ApplicationData) -> None:
        AwsS3Client().delete_object(reference_number + '.zip')
        AwsS3Client().delete_object(reference_number + '.pdf')

        for section in self.sections:
            files = self._get_files_for_section(section, application_data)
            for evidence_file in files:
                AwsS3Client().delete_object(evidence_file.aws_file_name)

    def create_application_cover_sheet_pdf(self, application_data: ApplicationData, is_admin: bool) -> BytesIO:
        html_template = ('applications/download.html' if is_admin else 'applications/download_user.html')
        html = render_template(html_template, application_data=application_data)
        return PDFUtils().create_pdf_from_html(html, title='Application')

    def create_attachment_names_pdf(self, all_sections: list, application_data: ApplicationData) -> BytesIO:
        attachments_html = ''
        for section in all_sections:
            files = self._get_files_for_section(section, application_data)
            if len(files) > 0:
                attachments_html += f'<h3 style="font-size: 14px;">{self._get_section_name(section)}</h3>'
                for file_index, evidence_file in enumerate(files):
                    attachments_html += f'<p style="font-size: 12px;">Attachment {file_index + 1} of {len(files)}: {evidence_file.aws_file_name}</p>'

        if attachments_html != '':
            logger.log(LogLevel.INFO, "Adding attachments pdf")
            return PDFUtils().create_pdf_from_html(attachments_html, title='Attachments')

    def attach_all_files(self, pdfs: list, all_sections: list, application_data: ApplicationData) -> None:
        for section in all_sections:
            files = self._get_files_for_section(section, application_data)
            for file_index, evidence_file in enumerate(files):
                self.add_object(pdfs, section, evidence_file.aws_file_name, evidence_file.original_file_name)

    def add_object(self, pdfs, section: str, aws_file_name: str, original_file_name: str) -> None:
        if '.' in aws_file_name:
            file_type = aws_file_name[aws_file_name.rindex('.') + 1:].lower()

            if file_type == 'pdf':
                try:
                    data = AwsS3Client().download_object(aws_file_name)
                    if data is not None:
                        if PDFUtils().is_pdf_password_protected(data):
                            # We can check the type of password (user/owner):
                            # doc.authenticate('') == 2
                            # https://pymupdf.readthedocs.io/en/latest/document.html#Document.authenticate
                            html = f'<h3 style="font-size: 14px; color: red;">Unable to add {original_file_name}. A password is required.</h3>'
                            pdfs.append(PDFUtils().create_pdf_from_html(html, title=f'{self._get_section_name(section)}:{original_file_name}'))
                            logger.log(LogLevel.ERROR, f"file {aws_file_name} needs a password!")
                        else:
                            pdfs.append(PDFUtils().add_pdf_toc(data, f'{self._get_section_name(section)}:{original_file_name}'))
                            logger.log(LogLevel.INFO, f"Attaching {aws_file_name}")
                    else:
                        pdfs.append(self.create_pdf_for_attachment_error(section, original_file_name))
                        logger.log(LogLevel.ERROR, f"Error attaching {aws_file_name}")

                except Exception as e:
                    pdfs.append(self.create_pdf_for_attachment_error(section, original_file_name))
                    logger.log(LogLevel.ERROR, f"Error attaching {aws_file_name} ({e})")
            else:
                try:

                    print(f"will download image {aws_file_name} from S3 bucket", flush=True)
                    data, width, height = AwsS3Client().download_object_data(aws_file_name)
                    if data is not None:
                        print(f"downloaded image {aws_file_name} from S3 bucket with width {width} height {height}", flush=True)
                        #html = f'<body><div style="margin-top:20px;"><img src="{data}" style="max-width: 95%; max-height: 95%; object-fit: contain;"></div></body>'
                        html = f'<body><div class="image-div"><img src="{data}"></div></body>'
                        #html = html_template
                        pdfs.append(PDFUtils().create_pdf_from_html(html, title=f'{self._get_section_name(section)}:{original_file_name}', html_image_type=True))
                        print(f"Adding image {aws_file_name}", flush=True)
                    else:
                        pdfs.append(self.create_pdf_for_attachment_error(section, original_file_name))
                        logger.log(LogLevel.ERROR, f"Error downloading {aws_file_name}")

                except Exception as e:
                    self.create_pdf_for_attachment_error(section, original_file_name)
                    logger.log(LogLevel.ERROR, f"Error attaching {aws_file_name} ({e})")
        else:
            logger.log(LogLevel.ERROR, f"Error attaching {aws_file_name}")
            self.create_pdf_for_attachment_error(section, original_file_name)

    def create_pdf_for_attachment_error(self, section: str, file_name: str) -> BytesIO:
        html = f'<h3 style="font-size: 14px; color: red;">WARNING: Could not attach file ({file_name})</h3>'
        return PDFUtils().create_pdf_from_html(html, title=f'{self._get_section_name(section)}:{file_name}')

    def get_filename_and_extension(self, file_name: str) -> Tuple[str, str]:
        file_ext = ''
        if '.' in file_name:
            file_ext = file_name[file_name.rindex('.'):]
            file_name = file_name[0: file_name.rindex('.')]

        return file_name, file_ext
