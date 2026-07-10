#!/usr/bin/env python3
# ============================================================
#  Velora GRUB Theme - Asset Generator
#  Generates background + selection highlight PNGs
#  Run this on a machine with Pillow installed:
#  pip install Pillow
# ============================================================

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print("Install Pillow: pip install Pillow")
    exit(1)

import os
OUT = os.path.dirname(os.path.abspath(__file__))

# ── Background 1920x1080 ─────────────────────────────────────
def make_background():
    img = Image.new("RGB", (1920, 1080), color=(10, 21, 16))
    draw = ImageDraw.Draw(img)

    # Subtle radial gradient feel - dark green center glow
    for r in range(600, 0, -2):
        alpha = int(18 * (1 - r / 600))
        c = (
            max(0, 10 + alpha),
            max(0, 21 + alpha * 2),
            max(0, 16 + alpha),
        )
        draw.ellipse(
            [960 - r, 540 - r, 960 + r, 540 + r],
            outline=c
        )

    # Very subtle grid lines
    for x in range(0, 1920, 80):
        draw.line([(x, 0), (x, 1080)], fill=(15, 30, 22), width=1)
    for y in range(0, 1080, 80):
        draw.line([(0, y), (1920, y)], fill=(15, 30, 22), width=1)

    img.save(os.path.join(OUT, "background.png"))
    print("✅ background.png generated")


# ── Selection highlight ──────────────────────────────────────
def make_select():
    # GRUB themes use 3-slice: select_c.png (center), select_w.png (left), select_e.png (right)
    # We just make a simple full-width one
    for name in ["select_c.png"]:
        img = Image.new("RGBA", (400, 40), color=(47, 107, 82, 60))
        draw = ImageDraw.Draw(img)
        # Left accent bar
        draw.rectangle([0, 0, 3, 40], fill=(137, 193, 125, 220))
        # Top/bottom border
        draw.rectangle([0, 0, 400, 1], fill=(95, 158, 110, 80))
        draw.rectangle([0, 39, 400, 40], fill=(95, 158, 110, 40))
        img.save(os.path.join(OUT, name))
    print("✅ select_c.png generated")


# ── Progress bar ─────────────────────────────────────────────
def make_progress():
    # progress_bar_c.png - background
    img = Image.new("RGBA", (300, 6), color=(255, 255, 255, 20))
    img.save(os.path.join(OUT, "progress_bar_c.png"))

    # progress_bar_hl_c.png - fill
    img2 = Image.new("RGBA", (300, 6), color=(47, 107, 82, 255))
    img2.save(os.path.join(OUT, "progress_bar_hl_c.png"))
    print("✅ progress bar assets generated")


if __name__ == "__main__":
    make_background()
    make_select()
    make_progress()
    print("\nAll GRUB assets generated in:", OUT)
