"""TPET-948 native-wheel contracts, not a vulnerability scan or complete SBOM.

Run only in isolated frozen images with CGR_NATIVE_IMAGE_TESTS=1. Capture
_font_raster_sha256() in the retained Pillow 13 wheel image, then supply that
CGR_NATIVE_FONT_SHA256 to both baseline and candidate runs on the same platform.
The baseline's bundled Brotli 1.2.0 must fail the decoder test. No OS library
version cutoff is applied: Debian fixes include vendor-backported revisions.
Also set CGR_WKHTMLTOPDF_TESTS=1 only in Public/Admin images to exercise the
production HTML renderer with its real binary, Qt fonts and CSS from /app.
"""

import base64
import ctypes
import hashlib
import os
import shutil
from importlib.metadata import distribution
from io import BytesIO

import pytest

if os.environ.get("CGR_NATIVE_IMAGE_TESTS") != "1":
    pytest.skip("Requires explicit isolated native-image opt-in", allow_module_level=True)

import fitz
from flask import Flask
from PIL import Image, ImageChops, ImageDraw, ImageFont, features
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from werkzeug.datastructures import FileStorage
from xhtml2pdf import pisa

from grc.upload import resize_image
from grc.utils.pdf_utils import PDFUtils


SAVE_OPTIONS = {
    "JPEG": {"quality": 100, "subsampling": 0},
    "TIFF": {"compression": "tiff_lzw"},
    "WEBP": {"lossless": True, "exact": True},
    "AVIF": {"quality": 100, "subsampling": "4:4:4", "max_threads": 1},
    "JPEG2000": {"irreversible": False},
}


def _sample(mode="RGB"):
    image = Image.new("RGB", (32, 24))
    image.putdata([(20 + x * 5, 15 + y * 7, 30 + (x + y) * 3)
                   for y in range(24) for x in range(32)])
    if mode == "RGBA":
        image.putalpha(Image.frombytes("L", image.size, bytes(32 + i % 192 for i in range(768))))
        return image
    return image.convert(mode)


def _encoded(image, format):
    output = BytesIO()
    image.save(output, format=format, **SAVE_OPTIONS.get(format, {}))
    output.seek(0)
    return output


def test_pillow_pin_and_baseline_native_capabilities():
    assert distribution("pillow").version == "13.0.0"
    required = (
        "freetype2", "littlecms2", "webp", "avif", "raqm", "harfbuzz", "fribidi",
        "jpg", "jpg_2000", "zlib", "libtiff", "libjpeg_turbo", "zlib_ng", "xcb",
    )
    assert not [name for name in required if not features.check(name)]
    # Record versions for paired-image evidence, not portable exact-version assertions.
    print({name: features.version(name) for name in required})


@pytest.mark.parametrize("format,mode", [
    ("JPEG", "RGB"), ("JPEG", "CMYK"),
    ("PNG", "RGB"), ("PNG", "RGBA"),
    ("TIFF", "RGB"), ("TIFF", "RGBA"), ("TIFF", "CMYK"),
    ("BMP", "RGB"),
    ("WEBP", "RGB"), ("WEBP", "RGBA"),
    ("AVIF", "RGB"), ("AVIF", "RGBA"),
    ("JPEG2000", "RGB"), ("JPEG2000", "RGBA"), ("JPEG2000", "CMYK"),
])
def test_real_codecs_preserve_known_pixels(format, mode):
    expected = _sample(mode)
    with Image.open(_encoded(expected, format)) as actual:
        actual.load()  # Opening alone does not exercise lazy native decoders.
        assert (actual.format, actual.mode, actual.size) == (format, mode, expected.size)
        maximum_error = max(high for low, high in ImageChops.difference(expected, actual).getextrema())
        # JPEG and AVIF still incur quantisation / RGB-YUV rounding at quality 100.
        assert maximum_error <= (4 if format in ("JPEG", "AVIF") else 0)


@pytest.mark.parametrize("format,mode,size,expected_size,expected_mode,expected_sha256", [
    ("PNG", "RGBA", (1600, 2400), (1400, 2100), "RGB",
     "8b279de1dda3b28ea8d8e175495ec52afd5baad9f702b9d06e8b0d66c13c0232"),
    ("TIFF", "CMYK", (2400, 1600), (2100, 1400), "CMYK",
     "9005070100a066af468f7ffbf68737bffeb41cd8394f9d4291a73003892078ea"),
    ("PNG", "P", (32, 24), (32, 24), "RGB",
     "6c28ce61a38485d4761a903da5030283e6abc1fc2c39668de69a7c2380b36d3e"),
])
def test_app_resize_preserves_colour_and_document_bounds(format, mode, size, expected_size, expected_mode, expected_sha256):
    source = Image.new("RGB", size, (40, 100, 160)).convert(mode)
    if mode == "RGBA":
        source.putalpha(96)
    document = FileStorage(stream=_encoded(source, format), filename="synthetic-image")
    # A minimal request context supports the real logger without create_app/services.
    with Flask(__name__, static_folder=None).test_request_context():
        success, result = resize_image(document)
    assert success is True
    # Measured before the native fix, including palette dithering and JPEG quality=50.
    assert hashlib.sha256(result.getvalue()).hexdigest() == expected_sha256
    with Image.open(result) as decoded:
        assert (decoded.format, decoded.mode, decoded.size) == ("JPEG", expected_mode, expected_size)


def test_app_resize_rejects_invalid_image_without_replacing_input():
    document = FileStorage(stream=BytesIO(b"not an image"), filename="synthetic.png")
    with Flask(__name__, static_folder=None).test_request_context():
        success, result = resize_image(document)
    assert success is False
    assert result is document


@pytest.mark.parametrize("renderer", ["xhtml2pdf", "reportlab"])
def test_pdf_generation_and_app_merge_preserve_text_and_rgb_image(renderer):
    source = _sample()
    image = _encoded(source, "PNG")
    output = BytesIO()
    text = "Tystysgrif geni neu fabwysiadu. Synthetic evidence."
    if renderer == "xhtml2pdf":
        uri = "data:image/png;base64," + base64.b64encode(image.getvalue()).decode("ascii")

        def data_only(resource, basepath=None):
            assert resource == uri, "Unexpected PDF resource: no network/local uploads allowed"
            return resource

        status = pisa.CreatePDF(
            f'<html><body><p>{text}</p><img src="{uri}" /></body></html>',
            dest=output, encoding="utf-8", link_callback=data_only, capacity=1024 * 1024,
        )
        assert status.err == 0
    else:
        canvas = Canvas(output, pagesize=(595, 842), invariant=1)
        canvas.drawString(40, 780, text)
        canvas.drawImage(ImageReader(image), 40, 700, width=32, height=24)
        canvas.save()

    # Production HTML generation uses wkhtmltopdf, not xhtml2pdf; only these pure
    # in-memory application helpers are reused here (no subprocess, DB or S3).
    utils = PDFUtils()
    titles = ["Synthetic evidence", "Additional image"]
    parts = [utils.add_pdf_toc(BytesIO(output.getvalue()), title) for title in titles]
    merged = utils.merge_pdfs(parts)
    with fitz.open(stream=merged, filetype="pdf") as pdf:
        assert len(pdf) == 2
        assert pdf.get_toc() == [[1, title, i + 1] for i, title in enumerate(titles)]
        for page in pdf:
            assert text in " ".join(page.get_text().split())
            images = page.get_images(full=True)
            assert len(images) == 1
            pixmap = fitz.Pixmap(pdf, images[0][0])
            assert (pixmap.width, pixmap.height, pixmap.n) == (32, 24, 3)
            assert pixmap.samples == source.tobytes()  # Independent PDF decoder oracle.
            assert page.get_image_rects(images[0][0])
            assert min(page.get_pixmap(dpi=72, alpha=False).samples) < 128


def _font_raster_sha256():
    font_bytes = distribution("reportlab").locate_file("reportlab/fonts/Vera.ttf").read_bytes()
    font = ImageFont.truetype(BytesIO(font_bytes), 24, layout_engine=ImageFont.Layout.RAQM)
    assert font.layout_engine == ImageFont.Layout.RAQM
    image = Image.new("L", (640, 72), 255)
    ImageDraw.Draw(image).text((8, 8), "Tystysgrif geni: Cymru, â ê î ô û.",
                               font=font, fill=0, language="cy", direction="ltr")
    bounds = ImageChops.invert(image).getbbox()
    assert bounds and 0 < bounds[0] < bounds[2] < 640 and 0 < bounds[1] < bounds[3] < 72
    return hashlib.sha256(font_bytes + image.tobytes()).hexdigest()


def test_freetype_raqm_raster_matches_retained_wheel():
    expected = os.environ.get("CGR_NATIVE_FONT_SHA256")
    assert expected, "Supply _font_raster_sha256() from the retained baseline image, not this candidate"
    assert _font_raster_sha256() == expected


def test_wheel_vendored_brotli_decoder_is_fixed():
    pillow = distribution("pillow")
    decoders = [path for path in pillow.files or ()
                if "brotlidec" in path.name.lower() and ".so" in path.name]
    assert decoders, (
        "No wheel-vendored decoder found: absence is NOT remediation proof. "
        "A source-linked strategy needs explicit fixed vendor-package/linkage evidence "
        "and an agreed test contract; do not apply upstream 1.2.1 to Debian's raw OS API."
    )
    for path in decoders:
        version = ctypes.CDLL(str(pillow.locate_file(path))).BrotliDecoderVersion
        version.argtypes = []
        version.restype = ctypes.c_uint32
        value = version()
        actual = (value >> 24, (value >> 12) & 0xFFF, value & 0xFFF)
        assert actual >= (1, 2, 1), f"{path}: BrotliDecoderVersion={actual}"


@pytest.mark.skipif(
    os.environ.get("CGR_WKHTMLTOPDF_TESTS") != "1",
    reason="Requires explicit Public/Admin wkhtmltopdf opt-in (not Dashboard/JWKS)",
)
@pytest.mark.parametrize("html_image_type", [
    pytest.param(False, id="document-en-cy"),
    pytest.param(True, id="image-attachment"),
])
def test_app_wkhtmltopdf_preserves_production_content(html_image_type, tmp_path, monkeypatch):
    assert shutil.which("wkhtmltopdf"), (
        "CGR_WKHTMLTOPDF_TESTS=1 requires the real wkhtmltopdf binary on PATH; "
        "run in a Public/Admin image, never skip a missing opted-in dependency"
    )
    # Use the image's existing headless Qt plugin/fonts, with private runtime/cache.
    runtime = tmp_path / "qt-runtime"
    runtime.mkdir(mode=0o700)
    cache = tmp_path / "qt-cache"
    cache.mkdir()
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    monkeypatch.setenv("XDG_CACHE_HOME", str(cache))

    colours = ((208, 32, 48), (32, 176, 64), (48, 80, 208), (208, 176, 32))
    source = Image.new("RGB", (96, 64))
    for index, colour in enumerate(colours):
        x, y = index % 2 * 48, index // 2 * 32
        source.paste(colour, (x, y, x + 48, y + 32))
    uri = "data:image/png;base64," + base64.b64encode(_encoded(source, "PNG").getvalue()).decode("ascii")
    # No external resources: the generated PNG and production CSS fonts are data URIs.
    heading = "Gender Recognition Certificate"
    text = "Synthetic evidence / Tystiolaeth synthetig: Cymru, â ê î ô û."
    if html_image_type:
        # Match ApplicationFiles.attach_all_files exactly: image-only quirks mode.
        # A standards-mode page with preceding text collapses this 100%-height layout.
        html = f'<body><div class="image-div"><img src="{uri}"></div></body>'
    else:
        # Use the actual application macro's heading/list classes and inline size.
        # Its print styles select sans-serif; GDS-only webfont text may be outlines,
        # not extractable PDF text. The public cover also puts its data-URI in a table.
        html = (
            '<!doctype html><html lang="en" class="govuk-template"><head>'
            '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '</head><body class="govuk-template__body">'
            f'<h4 class="govuk-heading-m">{heading}</h4>'
            f'<ul class="govuk-list govuk-list--bullet" style="font-size: 12px;"><li>{text}</li></ul>'
            f'<table style="width: 100%;"><tr><td style="width: 110px;"><img src="{uri}"></td></tr></table>'
            '</body></html>'
        )
    title = "Synthetic evidence / Tystiolaeth synthetig: â ê î ô û."
    # Do not replace pdfkit, the subprocess, CSS, production options or TOC helper.
    # The helper uses /tmp for its cache, so run only in an isolated test container.
    with PDFUtils().create_pdf_from_html(html, title=title, html_image_type=html_image_type) as stream:
        assert isinstance(stream, BytesIO) and stream.tell() == 0
        assert stream.getvalue().startswith(b"%PDF-")
        with fitz.open(stream=stream, filetype="pdf") as pdf:
            assert not pdf.is_encrypted and len(pdf) == 1
            assert pdf.get_toc() == [[1, f"__{title}", 1]]
            page = pdf[0]
            extracted = " ".join(page.get_text().split())
            if html_image_type:
                assert extracted == ""  # Attachment text exists in its TOC, not the image page.
            else:
                assert heading in extracted and text in extracted, (
                    f"text={extracted!r}; fonts={len(page.get_fonts())}; "
                    f"vector_paths={len(page.get_drawings())}"
                )
            images = page.get_images(full=True)
            assert len(images) == 1
            embedded = fitz.Pixmap(pdf, images[0][0])
            assert (embedded.width, embedded.height, embedded.n) == (96, 64, 3)
            rects = page.get_image_rects(images[0][0])
            assert len(rects) == 1
            rect = rects[0]
            assert 0 <= rect.x0 < rect.x1 <= page.rect.width
            assert 1 < rect.y0 < rect.y1 <= page.rect.height
            assert rect.width / rect.height == pytest.approx(1.5, rel=0.01)
            if not html_image_type:
                text_area = fitz.Rect(0, 0, page.rect.width, rect.y0 - 1)
                assert min(page.get_pixmap(clip=text_area, dpi=144, alpha=False).samples) < 128
            rendered = page.get_pixmap(clip=rect, dpi=144, colorspace=fitz.csRGB, alpha=False)
            for index, colour in enumerate(colours):
                # Qt can recompress PNG as JPEG. Check solid centres, not edge ringing,
                # in both the embedded image and its actual visible page placement.
                for pixmap in (embedded, rendered):
                    x = int(pixmap.width * (index % 2 + 0.5) / 2)
                    y = int(pixmap.height * (index // 2 + 0.5) / 2)
                    pixel = pixmap.pixel(x, y)
                    assert max(abs(actual - expected) for actual, expected in zip(pixel, colour)) <= 8
