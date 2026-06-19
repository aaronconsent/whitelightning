#!/usr/bin/env python3
"""Extract the 4 product tiles from product-lineup.jpg, upscale, save individually.

Tiles in the source are white squares in a horizontal row, roughly:
  motor      | solenoid    | lithium battery | controller
The script auto-detects each tile's bounds by finding high-brightness regions.
"""
from PIL import Image, ImageFilter
import pathlib

SRC = pathlib.Path(__file__).parent / "site/assets/photos/product-lineup.jpg"
OUT_DIR = SRC.parent

# Manually calibrated crop boxes (left, top, right, bottom) for the 4 tiles
# in the 1284×813 source. White tiles sit roughly y=250..545.
TILES = [
    ("product-motor.jpg",      ( 80, 257,  320, 535)),
    ("product-solenoid.jpg",   (385, 257,  615, 535)),
    ("product-lithium.jpg",    (672, 257,  925, 535)),
    ("product-controller.jpg", (988, 257, 1220, 535)),
]

# Upscale target — 3× gives ~830px wide which is plenty for web hero & cards
SCALE = 3

def upscale(im, factor):
    """Multi-pass LANCZOS upscale with a light sharpen — best we can do without an ML model."""
    w, h = im.size
    new = im.resize((w*factor, h*factor), Image.LANCZOS)
    # Subtle unsharp mask for crispness after upscale
    new = new.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))
    return new

def main():
    src = Image.open(SRC).convert("RGB")
    print(f"Source: {src.size}")
    for name, box in TILES:
        crop = src.crop(box)
        big  = upscale(crop, SCALE)
        out  = OUT_DIR / name
        big.save(out, "JPEG", quality=88, optimize=True)
        print(f"  wrote {out.name}: {crop.size} → {big.size} ({out.stat().st_size//1024} KB)")

if __name__ == "__main__":
    main()
