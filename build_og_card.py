#!/usr/bin/env python3
"""Build the social-share OG card (1200x630 PNG).

Layout:
  - Hero cart photo backdrop, darkened
  - Top-left: WLM brand mark + name
  - Big centered: "11 → 41 MPH" with the 41 in electric blue
  - Tagline: "FEEL THE SPEED."
  - Subtagline (gold): "+ time-travel to 1946."
  - Bottom strip: tap to drive · domain · 21-sec demo · phone
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
OUT  = SITE / "assets" / "og-speed-demo.jpg"
HERO = SITE / "assets" / "photos" / "hero-cart.jpg"

W, H = 1200, 630
BOLT = (0, 194, 255)
GOLD = (255, 200, 90)
WHITE = (255, 255, 255)
MUTED = (180, 188, 200)

def font(candidates, size):
    base_dirs = ["/System/Library/Fonts/Supplemental","/System/Library/Fonts","/Library/Fonts","/usr/share/fonts"]
    for name in candidates:
        for d in base_dirs:
            p = pathlib.Path(d) / name
            if p.exists():
                try: return ImageFont.truetype(str(p), size=size)
                except Exception: pass
    for name in candidates:
        try: return ImageFont.truetype(name, size=size)
        except Exception: pass
    return ImageFont.load_default()

BIG  = font(["HelveticaNeue.ttc","Helvetica.ttc","Arial Bold.ttf"], 92)
MID  = font(["HelveticaNeue.ttc","Helvetica.ttc","Arial Bold.ttf"], 30)
SUB  = font(["HelveticaNeue.ttc","Helvetica.ttc","Arial.ttf"], 30)
TINY = font(["HelveticaNeue.ttc","Helvetica.ttc","Arial.ttf"], 22)
NUM  = font(["HelveticaNeue.ttc","Helvetica.ttc","Arial Bold.ttf"], 200)
LABEL= font(["HelveticaNeue.ttc","Helvetica.ttc","Arial Bold.ttf"], 18)

def main():
    # ---- Base ----
    if HERO.exists():
        img = Image.open(HERO).convert("RGB").copy()
        src_ratio = img.width / img.height
        tgt_ratio = W / H
        if src_ratio > tgt_ratio:
            new_w = int(img.height * tgt_ratio)
            x = (img.width - new_w) // 2
            img = img.crop((x, 0, x + new_w, img.height))
        else:
            new_h = int(img.width / tgt_ratio)
            y = max(0, (img.height - new_h) // 3)
            img = img.crop((0, y, img.width, y + new_h))
        img = img.resize((W, H), Image.LANCZOS)
        # Darken
        overlay = Image.new("RGB", (W, H), (0, 0, 0))
        img = Image.blend(img, overlay, 0.62)
        # Blue/dark gradient
        grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for y in range(H):
            a = int(140 * (y / H) ** 1.4)
            gd.line([(0, y), (W, y)], fill=(0, 25, 50, a))
        img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")
    else:
        img = Image.new("RGB", (W, H), (8, 10, 16))

    d = ImageDraw.Draw(img, "RGBA")

    # ---- Top-left brand ----
    bx, by = 60, 50
    # Bolt mark
    bolt_pts = [(bx+22, by), (bx+4, by+26), (bx+18, by+26), (bx+14, by+50), (bx+36, by+20), (bx+20, by+20), (bx+26, by)]
    d.polygon(bolt_pts, fill=BOLT)
    d.text((bx + 56, by + 4), "WHITE LIGHTNING", font=MID, fill=WHITE)
    d.text((bx + 56, by + 36), "MOTORS · PERFORMANCE GOLF CARTS", font=LABEL, fill=BOLT)

    # ---- Center numbers row: 11 → 41 (no MPH on top, just label below) ----
    cy = 260
    cx = W // 2
    # 11
    left_cx = cx - 280
    d.text((left_cx, cy), "11", font=NUM, fill=WHITE, anchor="mm")
    d.text((left_cx, cy + 130), "STOCK", font=LABEL, fill=MUTED, anchor="mm")

    # Big arrow / chevron in middle
    ax = cx
    ay = cy
    d.polygon([(ax - 38, ay - 30), (ax - 38, ay + 30), (ax + 22, ay)], fill=BOLT)

    # 41 in blue
    right_cx = cx + 280
    d.text((right_cx, cy), "41", font=NUM, fill=BOLT, anchor="mm")
    d.text((right_cx, cy + 130), "WHITE LIGHTNING", font=LABEL, fill=BOLT, anchor="mm")

    # MPH unit label between bottoms of the two numbers
    d.text((cx, cy + 130), "MPH", font=MID, fill=WHITE, anchor="mm")

    # ---- Tagline ----
    d.text((cx, 470), "FEEL THE SPEED.", font=BIG, fill=WHITE, anchor="mm")
    d.text((cx, 530), "+ time-travel to 1946.", font=SUB, fill=GOLD, anchor="mm")

    # ---- Bottom CTA strip ----
    d.rectangle([(0, H - 64), (W, H)], fill=(0, 0, 0, 220))
    d.text((60, H - 32), "▶  TAP TO DRIVE  ·  whitelightningmotors.com", font=TINY, fill=WHITE, anchor="lm")
    d.text((W - 60, H - 32), "21-sec POV demo  ·  832-832-1993", font=TINY, fill=BOLT, anchor="rm")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "JPEG", quality=88, optimize=True)
    print(f"  wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size//1024} KB, {W}x{H})")

if __name__ == "__main__":
    main()
