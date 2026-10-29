#!/usr/bin/env python3
"""Renders assets/hero.gif: an animated pipeline banner for the workflow's hero sticky note."""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

W, H, FRAMES = 760, 212, 16
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "hero.gif"
BG, INK, MUTED = (255, 255, 255), (28, 28, 36), (120, 124, 140)
ORANGE, ORANGE2 = (255, 102, 0), (255, 170, 110)
GREEN, SLACK = (52, 168, 83), (74, 21, 75)

def font(size, bold=True):
    p = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    return ImageFont.truetype(p, size)

def card(d, box, title, sub, color, r=14):
    d.rounded_rectangle(box, radius=r, fill=(248, 248, 250), outline=color, width=3)
    x0, y0, x1, y1 = box
    d.text(((x0 + x1) / 2, y0 + 30), title, fill=INK, font=font(17), anchor="mm")
    d.text(((x0 + x1) / 2, y0 + 54), sub, fill=MUTED, font=font(12, False), anchor="mm")

frames = []
for t in range(FRAMES):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # stage 1 – live waveform (voice note)
    card(d, (20, 36, 180, 166), "Meeting audio", "any Indian language", ORANGE)
    for i in range(16):
        x = 48 + i * 7
        a = (math.sin(i * 0.9 + t * 0.55) * 0.5 + 0.5) * (0.35 + 0.65 * math.sin(i * 0.4) ** 2)
        h = 4 + a * 34
        d.rounded_rectangle((x, 130 - h / 2, x + 4, 130 + h / 2), radius=2, fill=ORANGE if i % 5 else ORANGE2)
    # stage 2 – Sarvam brain
    card(d, (220, 36, 400, 166), "Sarvam AI", "Saaras v4 → Sarvam-105B", ORANGE)
    pulse = 0.5 + 0.5 * math.sin(t * 0.45)
    cx, cy = 310, 132
    for k in range(3):
        rr = 10 + k * 9 + pulse * 5
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, int(130 + 60 * k), int(80 + 50 * k)), width=2)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=ORANGE)
    # stage 3 – ticket
    card(d, (440, 36, 580, 166), "Action items", "bug · feature · task", INK)
    d.rounded_rectangle((462, 118, 558, 130), radius=4, fill=(230, 230, 236))
    d.rounded_rectangle((462, 138, 530, 150), radius=4, fill=(230, 230, 236))
    # stage 4 – destinations
    d.rounded_rectangle((620, 36, 740, 96), radius=12, fill=INK)
    d.text((680, 66), "GitHub", fill=BG, font=font(16), anchor="mm")
    d.rounded_rectangle((620, 106, 740, 166), radius=12, fill=GREEN)
    d.text((680, 136), "Sheets", fill=BG, font=font(16), anchor="mm")
    # arrows + travelling dot
    for x0, x1 in ((180, 220), (400, 440), (580, 620)):
        d.line((x0 + 6, 101, x1 - 6, 101), fill=(200, 202, 210), width=3)
        d.polygon(((x1 - 10, 95), (x1 - 2, 101), (x1 - 10, 107)), fill=(200, 202, 210))
    prog = (t / FRAMES)
    px = 26 + prog * (734 - 26)
    d.line((20, 184, 740, 184), fill=(235, 236, 240), width=2)
    d.ellipse((px - 5, 179, px + 5, 189), fill=ORANGE)
    d.text((W / 2, 201), "hear  →  understand  →  act", fill=MUTED, font=font(12, False), anchor="mm")
    frames.append(im.quantize(colors=24, method=Image.Quantize.MEDIANCUT))

OUT.parent.mkdir(exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=2)
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


# ───────────── static PNG icons for the warm-up panels ─────────────
def icon(name, draw_fn):
    im = Image.new("RGBA", (300, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_fn(d)
    p = OUT.parent / f"{name}.png"
    im.save(p, optimize=True)
    print(f"wrote {p} ({p.stat().st_size // 1024} KB)")

def hear(d):
    for i in range(30):
        x = 20 + i * 9
        h = 8 + 60 * (0.3 + 0.7 * abs(math.sin(i * 0.5)) * abs(math.sin(i * 0.17 + 1)))
        d.rounded_rectangle((x, 45 - h / 2, x + 5, 45 + h / 2), radius=3, fill=ORANGE if i % 4 else ORANGE2)

def think(d):
    pts = [(40, 45), (110, 20), (110, 70), (180, 45), (250, 20), (250, 70)]
    for a, b in [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5)]:
        d.line((pts[a], pts[b]), fill=(255, 190, 150), width=3)
    for i, (x, y) in enumerate(pts):
        r = 11 if i in (0, 3) else 8
        d.ellipse((x - r, y - r, x + r, y + r), fill=ORANGE if i in (0, 3) else ORANGE2)

def speak(d):
    d.polygon(((40, 35), (62, 35), (90, 15), (90, 75), (62, 55), (40, 55)), fill=ORANGE)
    for k in range(3):
        r = 25 + k * 20
        d.arc((90 - r, 45 - r, 90 + r, 45 + r), start=-40, end=40, fill=ORANGE2, width=4)
    d.text((200, 45), "नमस्ते", fill=INK, font=ImageFont.truetype("/System/Library/Fonts/Supplemental/Kohinoor.ttc", 30), anchor="mm")

icon("hear", hear); icon("think", think); icon("speak", speak)
