# banner.py
# -----------------------------------
# Run this file once to generate a default banner.jpg
# -----------------------------------

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# make sure folder exists
os.makedirs("assets", exist_ok=True)

def load_font(size):
    """Try to load a font from system; fallback to default"""
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",    # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", # Linux
        "C:/Windows/Fonts/arial.ttf",                      # Windows
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

# create banner image
W, H = 1200, 400
banner = Image.new("RGB", (W, H), "#0ea5e9")

# gradient background
grad = Image.new("RGB", (W, H))
for y in range(H):
    for x in range(W):
        r = 15
        g = 90 + int(100 * x / W)
        b = 160 + int(60 * y / H)
        grad.putpixel((x, y), (r, g, b))
banner = Image.blend(banner, grad, 0.5)

# vignette (soft shadow edges)
vignette = Image.new("L", (W, H), 0)
drawv = ImageDraw.Draw(vignette)
drawv.ellipse((-200, -100, W + 200, H + 100), fill=255)
vignette = vignette.filter(ImageFilter.GaussianBlur(120))
banner = Image.composite(banner, Image.new("RGB", (W, H), (15, 23, 42)), vignette)

# overlay text panel
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(overlay)
glass_rect = [30, H // 3, W - 30, H - 30]
d.rounded_rectangle(glass_rect, radius=24, fill=(255, 255, 255, 60), outline=(255, 255, 255, 90), width=2)

# fonts
font_title = load_font(72)
font_sub = load_font(28)

title = "ElectroX"
subtitle = "Certified Pre-Owned Electronics • Warranty • Easy Returns"
tw = d.textlength(title, font=font_title)
sw = d.textlength(subtitle, font=font_sub)

cx = W // 2
ty = glass_rect[1] + 35
sy = ty + 80

d.text((cx - tw / 2, ty), title, font=font_title, fill=(255, 255, 255, 240))
d.text((cx - sw / 2, sy), subtitle, font=font_sub, fill=(255, 255, 255, 220))

banner = Image.alpha_composite(banner.convert("RGBA"), overlay).convert("RGB")
banner.save("assets/banner.jpg", quality=95)
print("✅ Created assets/banner.jpg successfully!")
