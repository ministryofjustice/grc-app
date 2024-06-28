import sys
import io
from memory_profiler import profile
from PIL import Image
from urllib.request import urlopen
import base64
import pdfkit


@profile
def create_test_pdf(image_path):

    print(image_path)
    with open(image_path, 'rb') as f:
        image_data = io.BytesIO(f.read())
        image_file = Image.open(image_data)
        width, height = image_file.size
        print(f"Image width {width} height {height}", flush=True)

    byte_base64 = base64.b64encode(image_data.getvalue())
    data = byte_base64.decode('utf-8')

    # Create an HTML template with the image embedded
    html_template = f"""
    <html>
    <body>
        <img src="data:image/jpg;base64,{data}" width="{width}" height="{height}">
    </body>
    </html>
    """

    print(html_template)

    # Create a memory stream to hold the PDF
    pdf_stream: io.BytesIO = io.BytesIO()
    data = pdfkit.from_string(html_template, options={"enable-local-file-access": ""}, verbose=True)
    pdf_stream.write(data)

    # Move the stream position to the beginning
    pdf_stream.seek(0)
    return pdf_stream

if __name__ == '__main__':

    image = sys.argv[1]
    img_to_pdf = create_test_pdf(image)
    with open("output.pdf", "wb") as f:
        f.write(img_to_pdf.read())