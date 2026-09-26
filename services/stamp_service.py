from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont

ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
STAMP_PATH = ASSET_DIR / "tai_stamp.png"

Position = Literal["top_left", "top_right", "bottom_left", "bottom_right"]


def _date_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def add_visit_stamp(
    photo_bytes: bytes,
    visited_date: str,
    position: Position = "bottom_right",
) -> bytes:
    """Return JPEG bytes with the red 'たい' stamp and visit date overlaid.

    The original input bytes are never modified. The caller stores the original and
    returned versions separately.
    """
    base = Image.open(BytesIO(photo_bytes)).convert("RGB")
    stamp = Image.open(STAMP_PATH).convert("RGBA")

    width, height = base.size
    short_side = min(width, height)
    stamp_size = max(120, int(short_side * 0.26))
    stamp.thumbnail((stamp_size, stamp_size), Image.Resampling.LANCZOS)

    pad = max(16, int(short_side * 0.035))
    date_font = _date_font(max(18, int(stamp_size * 0.11)))
    date_text = visited_date.replace("-", ".")

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text_box = draw.textbbox((0, 0), date_text, font=date_font)
    text_w = text_box[2] - text_box[0]
    text_h = text_box[3] - text_box[1]
    block_w = max(stamp.width, text_w)
    block_h = stamp.height + text_h + max(5, int(stamp_size * 0.025))

    if position == "top_left":
        x, y = pad, pad
    elif position == "top_right":
        x, y = width - block_w - pad, pad
    elif position == "bottom_left":
        x, y = pad, height - block_h - pad
    else:
        x, y = width - block_w - pad, height - block_h - pad

    stamp_x = x + (block_w - stamp.width) // 2
    overlay.alpha_composite(stamp, dest=(stamp_x, y))

    text_x = x + (block_w - text_w) // 2
    text_y = y + stamp.height + max(5, int(stamp_size * 0.025))
    # Small cream keyline keeps the date readable on dark/light photos.
    draw.text(
        (text_x, text_y),
        date_text,
        font=date_font,
        fill=(198, 41, 35, 255),
        stroke_width=max(1, int(stamp_size * 0.01)),
        stroke_fill=(255, 249, 235, 235),
    )

    result = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    out = BytesIO()
    result.save(out, format="JPEG", quality=92, optimize=True)
    return out.getvalue()
