from io import BytesIO
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.stamp_service import add_visit_stamp


def test_add_visit_stamp_returns_valid_jpeg():
    im = Image.new("RGB", (1200, 900), "white")
    buf = BytesIO()
    im.save(buf, "JPEG")
    out = add_visit_stamp(buf.getvalue(), "2026-09-25")
    stamped = Image.open(BytesIO(out))
    assert stamped.format == "JPEG"
    assert stamped.size == (1200, 900)
