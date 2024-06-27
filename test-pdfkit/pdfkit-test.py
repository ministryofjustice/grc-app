import sys
import io
import os
from memory_profiler import profile
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
import base64
import pdfkit


@profile
def open_image(image_path):

    print(image_path)

    # Open the Image from the command line
    with open(image_path, 'rb') as f:
        image_data = io.BytesIO(f.read())
        image_file = Image.open(image_data)
        width, height = image_file.size
        print(f"Image width {width} height {height}", flush=True)

    byte_base64 = base64.b64encode(image_data.getvalue())
    data = byte_base64.decode('utf-8')

    html = f"""
    <html>
    <body>
        <img src="data:image/jpg;base64,{data}" style="max-width: 90%; max-height: 90%; object-fit: contain;">
    </body>
    </html>
    """

    return html

    # Create a memory stream to hold the PDF
    #css = 'example.css'
    #pdf_stream: io.BytesIO = io.BytesIO()
    #html = f'<img src="{data}" style="max-width: 90%; max-height: 90%; object-fit: contain;">'
    #data = pdfkit.from_string(html, options={"enable-local-file-access": ""}, css=css, verbose=True)
    #pdf_stream.write(data)

    # Move the stream position to the beginning
    #pdf_stream.seek(0)
    #return pdf_stream

def create_cover_sheet():
    html_template = 'templates/applications/download.html'
    return PDFUtils().create_pdf_from_html(html, title='Application')

def create_pdf_from_html(html: str) -> BytesIO:

    print(f"Size of html buffer received in create_pdf_from_html {len(html)}", flush=True)
    print(f"Current working directory in create_pdf_from_html is {os.getcwd()}", flush=True)

    css = 'example.css'
    #css = 'grc/static/app.css'
    pdf_stream: BytesIO = BytesIO()
    data = pdfkit.from_string(
        html,
        options={"enable-local-file-access": ""},
        css=css,
        verbose=True
    )
    pdf_stream.write(data)
    pdf_stream.seek(0)
    print(f"Size of pdf_stream returned by create_pdf_from_html {pdf_stream.getbuffer().nbytes}", flush=True)
    return pdf_stream


if __name__ == '__main__':

    image = sys.argv[1]
    img_html_str = open_image(image)
    pdf_stream_data = create_pdf_from_html(img_html_str)
    with open("output.pdf", "wb") as f:
        f.write(pdf_stream_data.read())