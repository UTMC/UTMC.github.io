#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import cairosvg
import os.path

DIR = "../files/"

# =========================================
# Input
# =========================================

INPUT_SVG = os.path.normpath(os.path.join(DIR, "utmclogo.svg"))

# =========================================
# Output definitions
# =========================================

OUTPUTS = [
    ("favicon-16.png", 16),
    ("favicon-32.png", 32),
    ("favicon-48.png", 48),
    ("apple-touch-icon.png", 180),
    ("icon-192.png", 192),
    ("icon-512.png", 512),
]

ICO_SIZES = [16, 32, 48]

# =========================================
# Helpers
# =========================================

def output_path(filename: str) -> str:
    return os.path.normpath(os.path.join(DIR, filename))

def render_svg_to_png(svg_path: str, size: int) -> Image.Image:
    """
    Render SVG to RGBA Pillow Image.
    """
    png_bytes = cairosvg.svg2png(
        url=svg_path,
        output_width=size,
        output_height=size,
    )

    from io import BytesIO
    img = Image.open(BytesIO(png_bytes)).convert("RGBA")
    return img


def add_white_background(img: Image.Image) -> Image.Image:
    """
    Composite transparent image onto white background.
    """
    background = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(background, img)
    return composited.convert("RGB")


# =========================================
# Generate PNGs
# =========================================

for filename, size in OUTPUTS:
    img = render_svg_to_png(INPUT_SVG, size)
    img = add_white_background(img)

    img.save(output_path(filename), format="PNG")
    print(f"Generated: {filename}")

# =========================================
# Generate favicon.ico
# =========================================

ico_images = []

for size in ICO_SIZES:
    img = render_svg_to_png(INPUT_SVG, size)
    img = add_white_background(img)
    ico_images.append(img)

ico_images[0].save(
    output_path("favicon.ico"),
    format="ICO",
    sizes=[(s, s) for s in ICO_SIZES],
    append_images=ico_images[1:],
)

print("Generated: favicon.ico")

# =========================================
# Generate safari-pinned-tab.svg
# =========================================

# Safari pinned tab is monochrome SVG.
# We simply copy the original here.
# You may want to optimize it manually later.

Path(output_path("safari-pinned-tab.svg")).write_text(
    Path(INPUT_SVG).read_text(encoding="utf-8"),
    encoding="utf-8",
)

print("Generated: safari-pinned-tab.svg")

print("Done.")