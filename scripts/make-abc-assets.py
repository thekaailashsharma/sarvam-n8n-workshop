#!/usr/bin/env python3
"""assets/abc/: hero + 7 section banners (GIF) and node pictograms (PNG) for the ABCs of n8n canvas.
Design: white, generous space, SF Pro, one soft accent per section, thin-stroke pictograms."""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "abc"; OUT.mkdir(parents=True, exist_ok=True)
INK, GREY, LINE, BG = (29, 29, 31), (134, 134, 139), (229, 229, 234), (255, 255, 255)
def sf(size, weight="Semibold"):
    f = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size); f.set_variation_by_name(weight); return f
def mono(size): return ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", size)

SECTIONS = [  # key, letter, title, subtitle, accent
    ("triggers", "A", "Triggers", "How a workflow starts", (255, 149, 0)),
    ("data", "B", "Data", "Shape items as they flow", (0, 122, 255)),
    ("flow", "C", "Flow control", "Branch, merge, loop", (175, 82, 222)),
    ("ai", "D", "AI Agent", "A model that reasons and acts", (255, 59, 48)),
    ("apps", "E", "Apps", "Hundreds of integrations", (52, 199, 89)),
    ("human", "F", "Human in the loop", "Pause for a person", (90, 200, 250)),
    ("advanced", "G", "Advanced", "Code, HTTP, MCP", (29, 29, 31)),
]
def tint(c, a=0.14): return tuple(int(255 - (255 - v) * a) for v in c)

# ───────── illustrations (x in 200..480, y in 20..150) ─────────
def il_triggers(d, p, c):
    cx, cy = 300, 85; r = 10 + ((p * 2) % 1) * 40
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=tint(c, 0.5), width=3)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=c)
    d.line((320, 85, 470, 85), fill=LINE, width=3); x = 330 + ((p + .3) % 1) * 130; d.ellipse((x - 5, 80, x + 5, 90), fill=c)
def il_data(d, p, c):
    for i in range(7):
        h = 20 + 70 * (0.5 + 0.5 * math.sin(i * 0.8 + p * 2 * math.pi)); x = 220 + i * 36
        d.rounded_rectangle((x, 130 - h, x + 18, 130), radius=6, fill=c if i % 2 == 0 else tint(c, 0.45))
def il_flow(d, p, c):
    d.line((210, 85, 290, 85), fill=LINE, width=3)
    for yy in (40, 130): d.line((290, 85, 360, yy, 440, 85), fill=LINE, width=3, joint="curve")
    q = (p * 2) % 1; up = p < .5
    if q < .35: x, y = 210 + q / .35 * 80, 85
    elif q < .7: s = (q - .35) / .35; x, y = 290 + s * 70, 85 + (-45 if up else 45) * s
    else: s = (q - .7) / .3; x, y = 360 + s * 80, (40 if up else 130) + (45 if up else -45) * s
    for px, py in ((210, 85), (440, 85)): d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=LINE)
    d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=c)
def il_ai(d, p, c):
    cx, cy = 330, 85
    for k in range(3):
        r = 12 + ((p + k / 3) % 1) * 55; a = 1 - ((p + k / 3) % 1)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=tint(c, 0.15 + 0.6 * a), width=3)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=c)
def il_apps(d, p, c):
    k = int(p * 6)
    for i in range(6):
        x, y = 215 + (i % 3) * 90, 32 + (i // 3) * 60
        d.rounded_rectangle((x, y, x + 72, y + 44), radius=12, fill=c if i <= k else tint(c, 0.18))
def il_human(d, p, c):
    on = (p * 2) % 1 < .5
    d.rounded_rectangle((250, 60, 370, 110), radius=25, fill=c if on else LINE)
    x = 343 if on else 277; d.ellipse((x - 20, 65, x + 20, 105), fill=BG)
def il_advanced(d, p, c):
    txt = "items.map(fn)"; n = int(p * (len(txt) + 3))
    d.rounded_rectangle((210, 45, 470, 125), radius=16, fill=(29, 29, 31))
    d.text((232, 85), txt[:n] + ("▍" if n < len(txt) else ""), fill=(120, 230, 160), font=mono(22), anchor="lm")
ILS = {"triggers": il_triggers, "data": il_data, "flow": il_flow, "ai": il_ai, "apps": il_apps, "human": il_human, "advanced": il_advanced}

W, H, N = 960, 170, 16
for key, letter, title, sub, c in SECTIONS:
    frames = []
    for t in range(N):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        d.rounded_rectangle((30, 25, 150, 145), radius=30, fill=c)
        d.text((90, 85), letter, fill=BG, font=sf(64, "Bold"), anchor="mm")
        ILS[key](d, t / N, c)
        d.text((530, 70), title, fill=INK, font=sf(34, "Semibold"), anchor="lm")
        d.text((530, 112), sub, fill=GREY, font=sf(20, "Regular"), anchor="lm")
        frames.append(im.quantize(colors=32, method=Image.Quantize.MEDIANCUT))
    p = OUT / f"{key}.gif"; frames[0].save(p, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=2)
    print("wrote", p.name, p.stat().st_size // 1024, "KB")

# ───────── hero: letters drop in ─────────
HW, HH, HN = 1200, 240, 20
frames = []
for t in range(HN):
    im = Image.new("RGB", (HW, HH), BG); d = ImageDraw.Draw(im)
    for i, (key, letter, title, sub, c) in enumerate(SECTIONS):
        s = min(1, max(0, (t / HN - i * 0.08) / 0.3)); ease = 1 - (1 - s) ** 3
        x = 40 + i * 120; y = 20 + (1 - ease) * 60
        d.rounded_rectangle((x, y, x + 96, y + 96), radius=24, fill=c if s > 0 else BG)
        if s > 0: d.text((x + 48, y + 48), letter, fill=BG, font=sf(48, "Bold"), anchor="mm")
    d.text((40, 170), "ABCs of n8n", fill=INK, font=sf(40, "Bold"), anchor="lm")
    d.text((320, 172), "Every node type, one canvas. Open a card, press Execute, learn by watching data move.", fill=GREY, font=sf(20, "Regular"), anchor="lm")
    frames.append(im.quantize(colors=32, method=Image.Quantize.MEDIANCUT))
p = OUT / "hero.gif"; frames[0].save(p, save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=True, disposal=2)
print("wrote hero.gif", p.stat().st_size // 1024, "KB")

# ───────── pictograms: 2.5px strokes, 220x90, transparent ─────────
S = 4  # stroke
def card(name, c, draw):
    im = Image.new("RGBA", (220, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im); draw(d, c); im.save(OUT / f"{name}.png", optimize=True)
def o(d, box, c, w=S): d.ellipse(box, outline=c, width=w)
def pic_bolt(d, c): d.polygon([(112, 10), (90, 50), (108, 50), (100, 80), (130, 38), (112, 38), (122, 10)], outline=c, width=S)
def pic_clock(d, c): o(d, (80, 15, 140, 75), c); d.line((110, 45, 110, 28), fill=c, width=S); d.line((110, 45, 124, 54), fill=c, width=S)
def pic_hook(d, c): d.line((70, 45, 150, 45), fill=c, width=S); d.polygon([(150, 45), (136, 35), (136, 55)], fill=c); o(d, (56, 31, 84, 59), c)
def pic_form(d, c): d.rounded_rectangle((78, 15, 142, 75), radius=8, outline=c, width=S); [d.line((92, y, 128, y), fill=c, width=S) for y in (33, 45, 57)]
def pic_mail(d, c): d.rounded_rectangle((70, 22, 150, 68), radius=8, outline=c, width=S); d.line((72, 26, 110, 50, 148, 26), fill=c, width=S)
def pic_loop(d, c): d.arc((80, 18, 140, 72), 25, 325, fill=c, width=S); d.polygon([(136, 30), (150, 16), (152, 38)], fill=c)
def pic_chat(d, c): d.rounded_rectangle((70, 16, 150, 62), radius=16, outline=c, width=S); d.polygon([(88, 60), (88, 76), (104, 60)], fill=c)
def pic_pencil(d, c): d.line((82, 70, 130, 22), fill=c, width=S); d.line((94, 70, 142, 22), fill=c, width=S); d.line((130, 22, 142, 22), fill=c, width=S); d.polygon([(78, 76), (82, 64), (94, 70)], fill=c)
def pic_cal(d, c): d.rounded_rectangle((76, 18, 144, 76), radius=8, outline=c, width=S); d.line((76, 36, 144, 36), fill=c, width=S); [o(d, (x, y, x + 8, y + 8), c, 2) for x in (90, 106, 122) for y in (46, 60)]
def pic_funnel(d, c): d.polygon([(72, 16), (148, 16), (118, 50), (118, 74), (102, 66), (102, 50)], outline=c, width=S)
def pic_scissors(d, c): o(d, (74, 50, 96, 72), c); o(d, (74, 18, 96, 40), c); d.line((94, 36, 148, 70), fill=c, width=S); d.line((94, 54, 148, 20), fill=c, width=S)
def pic_box(d, c): d.polygon([(110, 14), (150, 32), (110, 50), (70, 32)], outline=c, width=S); d.line((70, 32, 70, 60, 110, 78, 150, 60, 150, 32), fill=c, width=S); d.line((110, 50, 110, 78), fill=c, width=S)
def pic_grid(d, c): [d.rounded_rectangle((x, y, x + 20, y + 16), radius=3, outline=c, width=3) for x in (72, 100, 128) for y in (18, 40, 62)]
def pic_page(d, c): d.rounded_rectangle((80, 14, 140, 76), radius=8, outline=c, width=S); [d.line((94, y, 126, y), fill=c, width=3) for y in (34, 46, 58)]
def pic_plane(d, c): d.polygon([(70, 46), (150, 16), (122, 76), (108, 52)], outline=c, width=S)
def pic_hash(d, c): [d.line((x, 18, x - 6, 72), fill=c, width=S) for x in (102, 126)]; [d.line((78, y, 144, y), fill=c, width=S) for y in (36, 56)]
def pic_brain(d, c): o(d, (76, 18, 144, 72), c); d.line((110, 18, 110, 72), fill=c, width=3); d.arc((86, 28, 110, 52), 0, 360, fill=c, width=3); d.arc((110, 38, 134, 62), 0, 360, fill=c, width=3)
def pic_wrench(d, c): d.line((80, 70, 122, 28), fill=c, width=S + 2); o(d, (116, 12, 148, 44), c, S); d.rectangle((128, 14, 146, 28), fill=(0, 0, 0, 0))
def pic_chip(d, c): d.rounded_rectangle((86, 26, 134, 66), radius=6, outline=c, width=S); [d.line((x, 14, x, 26), fill=c, width=3) for x in (96, 110, 124)]; [d.line((x, 66, x, 78), fill=c, width=3) for x in (96, 110, 124)]
def pic_fork(d, c): d.line((72, 45, 110, 45), fill=c, width=S); d.line((110, 45, 148, 20), fill=c, width=S); d.line((110, 45, 148, 70), fill=c, width=S); [o(d, (x - 7, y - 7, x + 7, y + 7), c, 3) for x, y in ((72, 45), (148, 20), (148, 70))]
def pic_merge(d, c): d.line((148, 45, 110, 45), fill=c, width=S); d.line((110, 45, 72, 20), fill=c, width=S); d.line((110, 45, 72, 70), fill=c, width=S); [o(d, (x - 7, y - 7, x + 7, y + 7), c, 3) for x, y in ((148, 45), (72, 20), (72, 70))]
def pic_cycle(d, c): d.arc((80, 18, 140, 72), 30, 300, fill=c, width=S); d.polygon([(130, 20), (148, 24), (136, 40)], fill=c)
def pic_reply(d, c): d.arc((90, 30, 150, 86), 180, 360, fill=c, width=S); d.polygon([(68, 46), (92, 30), (92, 62)], fill=c)
def pic_hand(d, c): d.rounded_rectangle((90, 40, 130, 76), radius=12, outline=c, width=S); [d.line((x, 16, x, 42), fill=c, width=S) for x in (96, 110, 124)]; d.line((130, 30, 130, 54), fill=c, width=S)
def pic_globe(d, c): o(d, (78, 14, 142, 78), c); o(d, (96, 14, 124, 78), c, 3); d.line((78, 46, 142, 46), fill=c, width=3)
def pic_code(d, c): d.text((110, 46), "</>", fill=c, font=sf(36, "Semibold"), anchor="mm")
def pic_mic(d, c): d.rounded_rectangle((98, 14, 122, 52), radius=12, outline=c, width=S); d.arc((86, 30, 134, 66), 0, 180, fill=c, width=S); d.line((110, 66, 110, 78), fill=c, width=S)
def pic_plug(d, c): d.rounded_rectangle((90, 34, 130, 60), radius=8, outline=c, width=S); [d.line((x, 16, x, 34), fill=c, width=S) for x in (100, 120)]; d.line((110, 60, 110, 78), fill=c, width=S)
ACC = dict((k, c) for k, _, _, _, c in SECTIONS)
PICS = {"bolt": ("triggers", pic_bolt), "clock": ("triggers", pic_clock), "hook": ("triggers", pic_hook), "form": ("triggers", pic_form), "mail": ("triggers", pic_mail), "loop": ("triggers", pic_loop), "chat-trigger": ("triggers", pic_chat),
        "pencil": ("data", pic_pencil), "cal": ("data", pic_cal), "funnel": ("data", pic_funnel), "scissors": ("data", pic_scissors), "box": ("data", pic_box), "code-data": ("data", pic_code),
        "fork": ("flow", pic_fork), "merge": ("flow", pic_merge), "cycle": ("flow", pic_cycle), "pencil-flow": ("flow", pic_pencil), "box-flow": ("flow", pic_box), "code-flow": ("flow", pic_code),
        "brain": ("ai", pic_brain), "wrench": ("ai", pic_wrench), "chip": ("ai", pic_chip), "chat": ("ai", pic_chat),
        "gmail": ("apps", pic_mail), "sheet": ("apps", pic_grid), "page": ("apps", pic_page), "plane": ("apps", pic_plane), "hash": ("apps", pic_hash), "subflow": ("apps", pic_loop), "mic": ("apps", pic_mic),
        "reply": ("human", pic_reply), "hand": ("human", pic_hand), "mail-wait": ("human", pic_mail), "hash-wait": ("human", pic_hash),
        "globe": ("advanced", pic_globe), "code": ("advanced", pic_code), "code-advanced": ("advanced", pic_code), "plug": ("advanced", pic_plug)}
for name, (sec, fn) in PICS.items(): card(name, ACC[sec], fn)
print("wrote", len(PICS), "pictograms")
