from flask import Flask
from jinja2 import Template
import sys
import io
import os
from memory_profiler import profile
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
import base64
import pdfkit

app = Flask(__name__)

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
    #html = f'<img src="data:image/jpg;base64,{data}" style="max-width: 90%; max-height: 90%; object-fit: contain;">'

    html = f"""
    <html>
    <body>
        <img src="data:image/jpg;base64,{data}" style="max-width: 90%; max-height: 90%; object-fit: contain;">
    </body>
    </html>
    """

    return html

global static_file
def static_file(filename, pdf=False):

    print(f"static_file method root path is {os.getcwd()}", flush=True)

    # wkhtmltopdf only read absolute path
    if pdf:
        basedir = os.path.abspath(os.getcwd())
        print(f"static_file method basedir is {basedir}", flush=True)
        return "".join([basedir, "/static/assets/", filename])
    else:
        return filename

def create_cover_sheet():

    TEMPLATE_FILE = 'templates/applications/download.html'
    with open(TEMPLATE_FILE) as file_:
        template = Template(file_.read())
        template.globals['static_file'] = static_file

    html = template.render(title="My Example Page", name="John Doe")
    print(f"Rendered html {html}")
    return html

def create_pdf_from_html(html: str) -> BytesIO:

    print(f"Size of html buffer received in create_pdf_from_html {len(html)}", flush=True)
    print(f"Current working directory in create_pdf_from_html is {os.getcwd()}", flush=True)

    #css = 'example.css'
    css = 'static/assets/app.css'
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

@app.route('/')
def wrapper():
    #image = sys.argv[1]
    image = "./jpg.jpeg"
    cover_html_str = create_cover_sheet()
    cover_stream_data = create_pdf_from_html(cover_html_str)
    with open("output-cover.pdf", "wb") as f:
            f.write(cover_stream_data.read())
            f.close()

    image_html_str = open_image(image)
    image_stream_data = create_pdf_from_html(image_html_str)
    with open("output-image.pdf", "wb") as f:
        f.write(image_stream_data.read())
        f.close()

    return "<p>Wrapper finished!</p>"

if __name__ == '__main__':
    app.run()