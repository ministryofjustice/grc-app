import fitz
from io import BytesIO
from typing import List
from flask import make_response
from xhtml2pdf import pisa
from grc.utils.logger import LogLevel, Logger

logger = Logger()


class PDFUtils:

    def create_pdf_from_html(self, html: str, title: str = None) -> BytesIO:
        pdf_stream: BytesIO = BytesIO()
        pisa.CreatePDF(html, dest=pdf_stream)

        pdf_stream.seek(0)

        return pdf_stream

    def merge_pdfs(self, input_pdf_streams: List[BytesIO], update_toc: bool = True) -> BytesIO:
        output_fitz_pdf_document: fitz.Document = fitz.open()

        page_count = 1
        new_toc = []
        current_section = ''

        for input_pdf_stream in input_pdf_streams:
            input_pdf_stream.seek(0)
            input_fitz_pdf_document: fitz.Document = fitz.open(stream=input_pdf_stream, filetype='pdf')

            if update_toc:
                toc = input_fitz_pdf_document.get_toc()
                for t in toc:
                    if t[1][: 2] == '__':
                        this_section = t[1][2: ]
                        this_file = ''
                        if ':' in this_section:
                            this_file = this_section[this_section.index(':') + 1:]
                            this_section = this_section[: this_section.index(':')]

                        if current_section != this_section:
                            new_toc.append([1, this_section, t[2] + page_count - 1])
                        if this_file != '':
                            new_toc.append([2, this_file, t[2] + page_count - 1])

                        current_section = this_section

                page_count += len(input_fitz_pdf_document)

            if input_fitz_pdf_document.is_form_pdf:
                input_fitz_pdf_document = self.flatten_form_pdf(input_fitz_pdf_document)

            output_fitz_pdf_document.insert_pdf(input_fitz_pdf_document)
            input_fitz_pdf_document.close()
            input_pdf_stream.close()
            del input_fitz_pdf_document
            del input_pdf_stream

        if update_toc:
            output_fitz_pdf_document.set_toc(new_toc)

        output_pdf_stream: BytesIO = BytesIO()
        output_fitz_pdf_document.ez_save(output_pdf_stream)
        output_fitz_pdf_document.close()
        del output_fitz_pdf_document

        output_pdf_stream.seek(0)
        return output_pdf_stream

    def is_pdf_password_protected(self, pdf_stream: BytesIO) -> bool:
        pdf_stream.seek(0)

        fitz_pdf_document: fitz.Document = fitz.open(stream=pdf_stream, filetype='pdf')
        needs_password = fitz_pdf_document.needs_pass

        fitz_pdf_document.close()
        del fitz_pdf_document
        return needs_password

    def is_pdf_form(self, pdf_stream: BytesIO) -> bool:
        pdf_stream.seek(0)

        fitz_pdf_document: fitz.Document = fitz.open(stream=pdf_stream, filetype='pdf')
        is_form_pdf = fitz_pdf_document.is_form_pdf

        fitz_pdf_document.close()
        del fitz_pdf_document
        return is_form_pdf

    def is_pdf_password_correct(self, pdf_stream: BytesIO, password: str) -> bool:
        pdf_stream.seek(0)

        fitz_pdf_document: fitz.Document = fitz.open(stream=pdf_stream, filetype='pdf')

        needs_password = fitz_pdf_document.needs_pass
        password_correct = False
        if needs_password:
            password_correct = fitz_pdf_document.authenticate(password)

        fitz_pdf_document.close()
        del fitz_pdf_document
        return needs_password and password_correct

    def remove_pdf_password_protection(self, input_pdf_stream: BytesIO, password: str) -> BytesIO:
        input_pdf_stream.seek(0)

        input_fitz_pdf_document: fitz.Document = fitz.open(stream=input_pdf_stream, filetype='pdf')
        input_fitz_pdf_document.authenticate(password)

        output_fitz_pdf_document: fitz.Document = fitz.open()
        if input_fitz_pdf_document.is_form_pdf:
            input_fitz_pdf_document = self.flatten_form_pdf(input_fitz_pdf_document)
        output_fitz_pdf_document.insert_pdf(input_fitz_pdf_document)
        input_fitz_pdf_document.close()
        input_pdf_stream.close()
        del input_pdf_stream
        del input_fitz_pdf_document

        output_pdf_stream: BytesIO = BytesIO()
        output_fitz_pdf_document.ez_save(output_pdf_stream)
        output_fitz_pdf_document.close()
        del output_fitz_pdf_document

        output_pdf_stream.seek(0)
        return output_pdf_stream

    def remove_pdf_edit_protection(self, input_pdf_stream: BytesIO) -> BytesIO:
        input_pdf_stream.seek(0)

        input_fitz_pdf_document: fitz.Document = fitz.open(stream=input_pdf_stream, filetype='pdf')

        output_fitz_pdf_document: fitz.Document = fitz.open()
        if input_fitz_pdf_document.is_form_pdf:
            input_fitz_pdf_document = self.flatten_form_pdf(input_fitz_pdf_document)
        output_fitz_pdf_document.insert_pdf(input_fitz_pdf_document)
        input_fitz_pdf_document.close()
        input_pdf_stream.close()
        del input_pdf_stream
        del input_fitz_pdf_document

        output_pdf_stream: BytesIO = BytesIO()
        output_fitz_pdf_document.ez_save(output_pdf_stream)
        output_fitz_pdf_document.close()
        del output_fitz_pdf_document

        output_pdf_stream.seek(0)
        return output_pdf_stream

    def flatten_form_pdf(self, input_fitz_pdf_document: fitz.Document) -> fitz.Document:
        output_fitz_pdf_document: fitz.Document = fitz.open()

        for page in input_fitz_pdf_document:
            try:
                pix = page.get_pixmap(dpi=150)
                new_page = output_fitz_pdf_document.new_page(pno=-1)
                new_page.insert_image(rect=new_page.bound(), pixmap=pix)
            except Exception as e:
                logger.log(LogLevel.ERROR, e)
            finally:
                del page

        input_fitz_pdf_document.close()
        del input_fitz_pdf_document
        return output_fitz_pdf_document

    def flatten_form_pdf_stream(self, input_pdf_stream: BytesIO) -> BytesIO:
        input_pdf_stream.seek(0)

        input_fitz_pdf_document: fitz.Document = fitz.open(stream=input_pdf_stream, filetype='pdf')
        flattened_pdf_document = self.flatten_form_pdf(input_fitz_pdf_document)
        input_pdf_stream.close()
        del input_pdf_stream

        output_pdf_stream: BytesIO = BytesIO()
        flattened_pdf_document.ez_save(output_pdf_stream)
        flattened_pdf_document.close()
        del flattened_pdf_document

        output_pdf_stream.seek(0)
        return output_pdf_stream

    def add_pdf_toc(self, input_pdf_document: BytesIO, title: str) -> BytesIO:
        fitz_pdf_document: fitz.Document = fitz.open(stream=input_pdf_document, filetype='pdf')
        fitz_pdf_document.set_toc([[1, f'__{title}', 1]])

        output_pdf_stream: BytesIO = BytesIO()
        fitz_pdf_document.ez_save(output_pdf_stream)
        fitz_pdf_document.close()
        input_pdf_document.close()
        del input_pdf_document
        del fitz_pdf_document

        output_pdf_stream.seek(0)
        return output_pdf_stream

    def get_filename_without_pdf_extension(self, input_file_name: str) -> str:
        if input_file_name.lower().endswith('.pdf'):
            return input_file_name[:-4]
        return input_file_name

    def make_pdf_download_response(self, pdf_bytes, output_file_name):
        response = make_response(pdf_bytes)
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename=output_file_name)
        return response
