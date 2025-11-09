# logo.py
# -----------------------------------
# Run this file once to generate logo.png
# -----------------------------------

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs("assets", exist_ok=True)

def load_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

# Create base
L = 256
logo = Image.new("RGBA", (L, L), (0, 0, 0, 0))
draw = ImageDraw.Draw(logo)

# circular base
draw.ellipse((8, 8, L - 8, L - 8), fill=(15, 23, 42, 255))  # navy

# lightning bolt
bolt = [
    (L * 0.55, L * 0.18),
    (L * 0.42, L * 0.50),
    (L * 0.62, L * 0.50),
    (L * 0.45, L * 0.85),
    (L * 0.58, L * 0.55),
    (L * 0.38, L * 0.55),
]
draw.polygon(bolt, fill=(250, 204, 21, 255))  # amber

# glow ring
ring = Image.new("L", (L, L), 0)
dr = ImageDraw.Draw(ring)
dr.ellipse((10, 10, L - 10, L - 10), fill=180)
ring = ring.filter(ImageFilter.GaussianBlur(8))
shadow = Image.new("RGBA", (L, L), (0, 0, 0, 0))
shadow.putalpha(ring)
logo = Image.alpha_composite(logo, shadow)

# brand text “EX”
dtext = ImageDraw.Draw(logo)
font_small = load_font(28)
txt = "EX"
tw = dtext.textlength(txt, font=font_small)
dtext.text(((L - tw) / 2, L * 0.72), txt, font=font_small, fill=(255, 255, 255, 200))

logo.convert("RGB").save("assets/logo.png", quality=95)
print("✅ Created assets/logo.png successfully!")
