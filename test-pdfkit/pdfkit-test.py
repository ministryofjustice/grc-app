from flask import Flask, render_template, Blueprint, url_for
import jinja2
import sys
import io
import os
import base64
import pdfkit
import ApplicationData
from datetime import datetime
from dateutil import tz
from memory_profiler import profile
from io import BytesIO
from PIL import Image
from urllib.request import urlopen

app = Flask(__name__)

@app.template_filter('format_date')
def format_date_filter(context, dt):
    if dt:
        dt = dt.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('Europe/London'))
        return datetime.strftime(dt, '%d/%m/%Y %H:%M')
    return ''

def create_cover_sheet():
    TEMPLATE_FILE = 'templates/applications/download.html'
    with open(TEMPLATE_FILE) as file_:
        template = Template(file_.read())
        template.globals['static_file'] = static_file

    html = template.render(title="My Example Page", name='John Doe')
    print(f"Rendered html {html}")
    return html

def create_cover_sheet_flask():
    TEMPLATE_FILE = 'applications/download.html'
    #html = render_template(html_template, application_data=application_data)
    applicationData = ApplicationData.ApplicationData()
    html = render_template(TEMPLATE_FILE, application_data=applicationData.get_data())
    print(f"Rendered html {html}")
    return html

@profile
def open_image(image_path):

    print(image_path)
    with open(image_path, 'rb') as f:
        image_data = io.BytesIO(f.read())
        image_file = Image.open(image_data)
        width, height = image_file.size
        print(f"Image width {width} height {height}", flush=True)

    byte_base64 = base64.b64encode(image_data.getvalue())
    data = byte_base64.decode('utf-8')

    # Create an HTML template with the image embedded
    html = f"""<div class="image-div"><img src="data:image/jpg;base64,{data}" id="pdf-img"/></div>"""

    return html

def create_pdf_from_html(html: str, isImage) -> BytesIO:

    print(f"Size of html buffer received in create_pdf_from_html {len(html)}", flush=True)
    print(f"Current working directory in create_pdf_from_html is {os.getcwd()}", flush=True)

    if isImage:
        css = 'static/image.css'
        #css = url_for('static', filename='image.css', _external=True)
    else:
        #css = url_for('static', filename='app.css', _external=True)
        css = 'static/app.css'

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
    #image = "./mgb_sig_scan.jpg"

    cover_html_str = create_cover_sheet_flask()
    cover_stream_data = create_pdf_from_html(cover_html_str, False)
    with open("output-cover.pdf", "wb") as f:
            f.write(cover_stream_data.read())
            f.close()

    #image_html_str = open_image(image)
    #image_stream_data = create_pdf_from_html(image_html_str, True)
    #with open("output-image.pdf", "wb") as f:
    #f.write(image_stream_data.read())
    #f.close()

    return "<p>Wrapper finished!</p>"

if __name__ == '__main__':
    app.run()