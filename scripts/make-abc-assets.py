#!/usr/bin/env python3
"""Renders assets/abc/: 7 animated section banners (GIF) + pictogram cards (PNG) for the ABCs of n8n canvas."""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "abc"; OUT.mkdir(parents=True, exist_ok=True)
INK, MUTED, BG = (28, 28, 36), (140, 144, 160), (255, 255, 255)
ORANGE, ORANGE2, BLUE, GREEN, PURPLE, RED, TEAL = (255, 102, 0), (255, 176, 120), (66, 133, 244), (52, 168, 83), (142, 68, 173), (229, 57, 53), (0, 150, 136)
def font(sz): return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", sz)

# ───────── section banners (GIF, 640x110) ─────────
W, H, N = 640, 110, 14
def banner(name, color, title, draw):
    frames = []
    for t in range(N):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        draw(d, t / N)
        d.text((330, 55), title, fill=INK, font=font(26), anchor="lm")
        frames.append(im.quantize(colors=24, method=Image.Quantize.MEDIANCUT))
    p = OUT / f"{name}.gif"
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True, disposal=2)
    print("wrote", p.name, p.stat().st_size // 1024, "KB")

def tri(d, p):  # bolt that pulses + dot that leaves
    glow = 0.5 + 0.5 * math.sin(p * 2 * math.pi)
    d.polygon([(120, 15), (95, 60), (118, 60), (105, 95), (150, 45), (126, 45), (140, 15)], fill=ORANGE if glow > .5 else ORANGE2)
    x = 170 + p * 120; d.line((170, 55, 300, 55), fill=(230, 232, 238), width=3); d.ellipse((x - 6, 49, x + 6, 61), fill=ORANGE)
def dat(d, p):  # bars morph
    for i in range(9):
        h = 20 + 60 * (0.5 + 0.5 * math.sin(i * 0.9 + p * 2 * math.pi))
        d.rounded_rectangle((70 + i * 24, 90 - h, 86 + i * 24, 90), radius=4, fill=BLUE if i % 3 else (150, 190, 255))
def app(d, p):  # tiles light up in sequence
    k = int(p * 6)
    for i in range(6):
        x, y = 70 + (i % 3) * 70, 18 + (i // 3) * 45
        d.rounded_rectangle((x, y, x + 56, y + 34), radius=8, fill=GREEN if i <= k else (225, 240, 228))
    d.line((200, 55, 300, 55), fill=(230, 232, 238), width=3)
def ai(d, p):  # pulse rings
    cx, cy = 150, 55
    for k in range(4):
        r = 8 + ((p + k / 4) % 1) * 45
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 120 + 30 * k, 90 + 30 * k), width=3)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=RED)
def flow(d, p):  # dot takes alternating branches
    d.line((60, 55, 140, 55), fill=(230, 232, 238), width=3)
    for yy in (25, 85): d.line((140, 55, 200, yy, 280, 55), fill=(230, 232, 238), width=3, joint="curve")
    q = p * 2 % 1; up = p < .5
    if q < .35: x, y = 60 + q / .35 * 80, 55
    elif q < .7: s = (q - .35) / .35; x, y = 140 + s * 60, 55 + (-30 if up else 30) * s
    else: s = (q - .7) / .3; x, y = 200 + s * 80, (25 if up else 85) + (30 if up else -30) * s
    d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=PURPLE)
def human(d, p):  # approve toggle
    on = (p * 2) % 1 < .5
    d.rounded_rectangle((70, 35, 150, 75), radius=20, fill=GREEN if on else (210, 212, 220))
    x = 130 if on else 90; d.ellipse((x - 16, 39, x + 16, 71), fill=BG)
    d.text((175, 55), "approve?", fill=MUTED, font=font(18), anchor="lm")
def adv(d, p):  # typing code
    txt = "{ data: items.map(fn) }"; n = int(p * (len(txt) + 4))
    d.rounded_rectangle((60, 25, 300, 85), radius=10, fill=(32, 34, 44))
    d.text((75, 55), txt[:n] + ("▌" if n < len(txt) else ""), fill=(120, 230, 160), font=ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16), anchor="lm")

for args in [("triggers", ORANGE, "Triggers", tri), ("data", BLUE, "Data manipulation", dat), ("apps", GREEN, "App integrations", app),
             ("ai", RED, "AI Agent", ai), ("flow", PURPLE, "Flow control", flow), ("human", TEAL, "Human in the loop", human), ("advanced", INK, "Advanced", adv)]:
    banner(*args)

# ───────── node pictograms (PNG, 200x70, transparent) ─────────
def card(name, color, draw):
    im = Image.new("RGBA", (200, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im); draw(d, color); p = OUT / f"{name}.png"; im.save(p, optimize=True)
def pic_bolt(d, c): d.polygon([(100, 5), (80, 38), (97, 38), (88, 65), (122, 28), (104, 28), (114, 5)], fill=c)
def pic_clock(d, c): d.ellipse((70, 5, 130, 65), outline=c, width=5); d.line((100, 35, 100, 15), fill=c, width=4); d.line((100, 35, 116, 45), fill=c, width=4)
def pic_hook(d, c): d.arc((70, 10, 130, 70), 200, 340, fill=c, width=6); d.polygon([(60, 36), (80, 24), (80, 48)], fill=c); d.polygon([(140, 36), (120, 24), (120, 48)], fill=c)
def pic_form(d, c): d.rounded_rectangle((65, 5, 135, 65), radius=6, outline=c, width=4); [d.line((78, y, 122, y), fill=c, width=4) for y in (22, 35, 48)]
def pic_mail(d, c): d.rounded_rectangle((60, 12, 140, 60), radius=6, outline=c, width=4); d.line((60, 14, 100, 42, 140, 14), fill=c, width=4)
def pic_loop(d, c): d.arc((70, 8, 130, 62), 20, 330, fill=c, width=6); d.polygon([(128, 22), (142, 8), (144, 30)], fill=c)
def pic_pencil(d, c): d.line((70, 60, 120, 10), fill=c, width=10); d.polygon([(66, 66), (72, 52), (80, 60)], fill=c)
def pic_cal(d, c): d.rounded_rectangle((65, 10, 135, 65), radius=6, outline=c, width=4); d.rectangle((65, 10, 135, 24), fill=c); [d.rectangle((x, y, x + 8, y + 8), fill=c) for x in (78, 96, 114) for y in (32, 48)]
def pic_funnel(d, c): d.polygon([(60, 8), (140, 8), (108, 40), (108, 64), (92, 58), (92, 40)], fill=c)
def pic_scissors(d, c): d.ellipse((62, 40, 84, 62), outline=c, width=4); d.ellipse((62, 8, 84, 30), outline=c, width=4); d.line((82, 26, 140, 60), fill=c, width=5); d.line((82, 44, 140, 10), fill=c, width=5)
def pic_box(d, c): d.polygon([(100, 6), (140, 24), (100, 42), (60, 24)], outline=c, width=4); d.polygon([(60, 24), (100, 42), (100, 66), (60, 48)], fill=c); d.polygon([(140, 24), (100, 42), (100, 66), (140, 48)], outline=c, width=4)
def pic_grid(d, c): [d.rectangle((x, y, x + 20, y + 14), outline=c, width=3) for x in (62, 90, 118) for y in (12, 30, 48)]
def pic_page(d, c): d.rounded_rectangle((70, 5, 130, 65), radius=5, outline=c, width=4); [d.line((82, y, 118, y), fill=c, width=3) for y in (24, 36, 48)]
def pic_plane(d, c): d.polygon([(60, 36), (140, 8), (110, 66), (98, 42)], fill=c)
def pic_hash(d, c): [d.line((x, 10, x - 6, 62), fill=c, width=5) for x in (92, 116)]; [d.line((66, y, 134, y), fill=c, width=5) for y in (26, 48)]
def pic_brain(d, c): d.ellipse((66, 8, 134, 62), outline=c, width=5); d.line((100, 8, 100, 62), fill=c, width=4); d.arc((76, 18, 100, 42), 0, 360, fill=c, width=3); d.arc((100, 28, 124, 52), 0, 360, fill=c, width=3)
def pic_wrench(d, c): d.line((70, 60, 115, 15), fill=c, width=10); d.ellipse((108, 4, 138, 34), outline=c, width=8); d.rectangle((118, 6, 136, 20), fill=(0, 0, 0, 0))
def pic_chip(d, c): d.rounded_rectangle((75, 15, 125, 55), radius=4, outline=c, width=4); [d.line((x, 5, x, 15), fill=c, width=3) for x in (85, 100, 115)]; [d.line((x, 55, x, 65), fill=c, width=3) for x in (85, 100, 115)]
def pic_fork(d, c): d.line((60, 35, 100, 35), fill=c, width=5); d.line((100, 35, 140, 12), fill=c, width=5); d.line((100, 35, 140, 58), fill=c, width=5); [d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=c) for x, y in ((60, 35), (140, 12), (140, 58))]
def pic_merge(d, c): d.line((140, 35, 100, 35), fill=c, width=5); d.line((100, 35, 60, 12), fill=c, width=5); d.line((100, 35, 60, 58), fill=c, width=5); [d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=c) for x, y in ((140, 35), (60, 12), (60, 58))]
def pic_cycle(d, c): d.arc((70, 8, 130, 62), 30, 300, fill=c, width=6); d.polygon([(120, 10), (138, 14), (126, 30)], fill=c); d.text((100, 36), "5", fill=c, font=font(18), anchor="mm")
def pic_reply(d, c): d.polygon([(60, 30), (90, 8), (90, 22), (140, 22), (140, 52), (90, 52), (90, 66)], fill=c) if False else (d.arc((80, 20, 140, 70), 180, 360, fill=c, width=6), d.polygon([(58, 36), (82, 20), (82, 52)], fill=c))
def pic_chat(d, c): d.rounded_rectangle((60, 8, 140, 52), radius=12, fill=c); d.polygon([(76, 50), (76, 66), (94, 50)], fill=c); [d.ellipse((x - 4, 26, x + 4, 34), fill=(255, 255, 255, 255)) for x in (84, 100, 116)]
def pic_hand(d, c): d.rounded_rectangle((80, 30, 120, 66), radius=10, fill=c); [d.rounded_rectangle((x, 8, x + 9, 40), radius=4, fill=c) for x in (82, 94, 106)]; d.rounded_rectangle((116, 20, 125, 44), radius=4, fill=c)
def pic_globe(d, c): d.ellipse((68, 5, 132, 65), outline=c, width=4); d.ellipse((86, 5, 114, 65), outline=c, width=3); d.line((68, 35, 132, 35), fill=c, width=3)
def pic_code(d, c): d.text((100, 36), "</>", fill=c, font=font(34), anchor="mm")
def pic_mic(d, c): d.rounded_rectangle((88, 5, 112, 42), radius=12, fill=c); d.arc((76, 20, 124, 56), 0, 180, fill=c, width=4); d.line((100, 56, 100, 66), fill=c, width=4)
def pic_plug(d, c): d.rounded_rectangle((80, 24, 120, 50), radius=6, fill=c); [d.line((x, 8, x, 24), fill=c, width=5) for x in (90, 110)]; d.line((100, 50, 100, 66), fill=c, width=4)
PICS = {"bolt": (pic_bolt, ORANGE), "clock": (pic_clock, ORANGE), "hook": (pic_hook, ORANGE), "form": (pic_form, ORANGE), "mail": (pic_mail, ORANGE), "loop": (pic_loop, ORANGE), "chat-trigger": (pic_chat, ORANGE),
        "pencil": (pic_pencil, BLUE), "cal": (pic_cal, BLUE), "funnel": (pic_funnel, BLUE), "scissors": (pic_scissors, BLUE), "box": (pic_box, BLUE),
        "gmail": (pic_mail, GREEN), "sheet": (pic_grid, GREEN), "page": (pic_page, GREEN), "plane": (pic_plane, GREEN), "hash": (pic_hash, GREEN), "subflow": (pic_loop, GREEN), "mic": (pic_mic, GREEN),
        "brain": (pic_brain, RED), "wrench": (pic_wrench, RED), "chip": (pic_chip, RED), "chat": (pic_chat, RED),
        "fork": (pic_fork, PURPLE), "merge": (pic_merge, PURPLE), "cycle": (pic_cycle, PURPLE),
        "reply": (pic_reply, TEAL), "hand": (pic_hand, TEAL), "mail-wait": (pic_mail, TEAL), "hash-wait": (pic_hash, TEAL),
        "globe": (pic_globe, INK), "code": (pic_code, INK), "plug": (pic_plug, INK)}
for name, (fn, color) in PICS.items(): card(name, color, fn)
print("wrote", len(PICS), "pictograms")
