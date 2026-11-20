"""Fail an image build if pip replaced the repaired wheel or dropped a codec."""

import ctypes
from importlib.metadata import distribution
import json

from PIL import features

pillow = distribution("pillow")
assert pillow.version == "13.0.0"
origin = json.loads(pillow.read_text("direct_url.json") or "{}")
assert origin.get("url", "").startswith("file:///opt/pillow/"), origin
required = (
    "freetype2", "littlecms2", "webp", "avif", "raqm", "harfbuzz", "fribidi",
    "jpg", "jpg_2000", "zlib", "libtiff", "libjpeg_turbo", "zlib_ng", "xcb",
)
missing = [name for name in required if not features.check(name)]
assert not missing, f"Missing required Pillow capabilities: {missing}"
decoders = [path for path in pillow.files or () if "brotlidec" in path.name and ".so" in path.name]
assert decoders, "Expected the repaired wheel's independently inventoried decoder"
for path in decoders:
    decoder = ctypes.CDLL(str(pillow.locate_file(path))).BrotliDecoderVersion
    decoder.restype = ctypes.c_uint32
    version = decoder()
    assert (version >> 24, (version >> 12) & 0xFFF, version & 0xFFF) >= (1, 2, 1)
print("Pillow 13.0.0 repaired wheel, required codecs and Brotli >=1.2.1 verified")
