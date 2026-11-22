#!/usr/bin/env python3
"""Render v19: GTA 6 parking ticket 3D meme, 1024x1024, deterministic.
Rebuilds the approved design from scratch with PIL: Vice City dusk street
(sky gradient, sun glow, neon buildings, palms, wet reflections) with a
slightly tilted, curved-looking paper ticket floating above it.
Fixed seed, no timestamps, no external assets -> byte-identical output.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
rng = random.Random(20261119)

FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- background
img = Image.new("RGB", (W, H))
px = img.load()
# dusk sky: deep indigo top -> magenta -> orange horizon band -> dark street
stops = [(0.00, (30, 22, 66)), (0.26, (96, 48, 108)), (0.42, (196, 88, 118)),
         (0.52, (250, 140, 92)), (0.60, (255, 182, 116)), (0.66, (64, 38, 66)),
         (1.00, (12, 10, 22))]
for y in range(H):
    t = y / H
    for i in range(len(stops) - 1):
        if stops[i][0] <= t <= stops[i + 1][0]:
            f = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
            px[0, y]  # touch
            c = lerp(stops[i][1], stops[i + 1][1], f)
            break
    else:
        c = stops[-1][1]
    for x in range(W):
        px[x, y] = c

d = ImageDraw.Draw(img, "RGBA")
# sun glow low on horizon, top-right corner so it peeks above the ticket
for r, alpha in [(190, 26), (130, 48), (80, 90), (48, 160)]:
    d.ellipse([860 - r, 190 - r, 860 + r, 190 + r], fill=(255, 190, 120, alpha))
d.ellipse([860 - 46, 190 - 46, 860 + 46, 190 + 46], fill=(255, 224, 170, 255))
# faint clouds
for _ in range(14):
    cx, cy = rng.randint(40, 984), rng.randint(60, 560)
    cw, ch = rng.randint(120, 300), rng.randint(10, 26)
    d.ellipse([cx, cy, cx + cw, cy + ch], fill=(255, 150, 130, 26))

# buildings: dark silhouettes left + right with lit windows and neon signs
def building(x0, y0, bw, bh, hue):
    d.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(16, 13, 30, 255))
    for wy in range(y0 + 18, y0 + bh - 14, 34):
        for wx in range(x0 + 12, x0 + bw - 16, 30):
            if rng.random() < 0.42:
                col = rng.choice([(255, 200, 90), (120, 230, 255),
                                  (255, 110, 180), (255, 240, 190)])
                d.rectangle([wx, wy, wx + 14, wy + 18], fill=col + (200,))
    # roof neon edge
    d.line([x0, y0, x0 + bw, y0], fill=hue + (220,), width=4)

building(-20, 60, 210, 620, (255, 60, 180))
building(150, 150, 150, 530, (0, 220, 255))
building(740, 90, 170, 590, (255, 90, 60))
building(880, 30, 170, 650, (180, 80, 255))
building(330, 270, 120, 410, (255, 200, 80))

# neon signs (glow via layered text)
def neon_text(xy, s, size, col):
    f = font(FB, size)
    for off, a in [(6, 60), (3, 120)]:
        d.text((xy[0] + off, xy[1] + off), s, font=f, fill=col + (a,))
    d.text(xy, s, font=f, fill=(255, 255, 255, 255))
    d.text(xy, s, font=f, fill=col + (255,))

neon_text((18, 300), "OCEAN VIEW", 44, (255, 50, 170))
neon_text((18, 352), "MOTEL", 44, (255, 50, 170))
neon_text((800, 250), "80s", 58, (190, 110, 255))
neon_text((776, 316), "ARCADE", 44, (190, 110, 255))
neon_text((770, 470), "VICE CITY", 30, (0, 220, 255))

# palm silhouettes
def palm(bx, by, s, lean):
    d.line([bx, by, bx + lean, by - 150 * s], fill=(8, 8, 16, 255), width=int(9 * s))
    tx, ty = bx + lean, by - 150 * s
    for k in range(7):
        ang = -160 + k * 32
        r = 95 * s
        ex = tx + r * math.cos(math.radians(ang))
        ey = ty + r * math.sin(math.radians(ang)) * 0.55 - 18
        d.line([tx, ty, ex, ey], fill=(8, 8, 16, 255), width=int(6 * s))
        d.line([tx, ty, (tx + ex) / 2, (ty + ey) / 2 + 26 * s],
               fill=(8, 8, 16, 255), width=int(4 * s))

palm(120, 700, 1.15, -28)
palm(940, 700, 1.05, 30)
palm(300, 690, 0.7, -14)
palm(700, 690, 0.65, 18)

# wet street: dark base + neon reflection streaks, then blur them
street = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(street)
sd.rectangle([0, 660, W, H], fill=(14, 11, 24, 255))
for _ in range(46):
    x = rng.randint(0, W - 8)
    wdt = rng.randint(3, 12)
    hgt = rng.randint(60, 320)
    col = rng.choice([(255, 60, 170), (255, 140, 70), (0, 220, 255),
                      (190, 110, 255), (255, 220, 150)])
    sd.rectangle([x, 680, x + wdt, 680 + hgt], fill=col + (rng.randint(50, 130),))
street = street.filter(ImageFilter.GaussianBlur(7))
img = Image.alpha_composite(img.convert("RGBA"), street)
d = ImageDraw.Draw(img, "RGBA")
# road centre line + puddle glints
d.line([0, 700, W, 700], fill=(255, 210, 140, 60), width=3)
for _ in range(26):
    x, y = rng.randint(30, 990), rng.randint(720, 990)
    d.ellipse([x, y, x + rng.randint(20, 90), y + 5], fill=(255, 255, 255, 26))

# ---------------------------------------------------------------- ticket
TW, TH = 920, 660
ticket = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
td = ImageDraw.Draw(ticket)
# paper body with slightly torn corners (notched polygon)
paper = [(26, 6), (TW - 34, 0), (TW - 6, 26), (TW - 2, TH - 40),
         (TW - 30, TH - 4), (30, TH - 2), (4, TH - 34), (0, 30)]
td.polygon(paper, fill=(243, 240, 230, 255))
# paper shading: soft vertical gradient + creases
shade = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
shd = ImageDraw.Draw(shade)
for i in range(TH):
    a = int(10 * (i / TH))
    shd.line([0, i, TW, i], fill=(120, 100, 70, a))
for _ in range(9):  # crease lines
    x0, y0 = rng.randint(40, TW - 40), rng.randint(40, TH - 40)
    shd.line([x0, y0, x0 + rng.randint(-160, 160), y0 + rng.randint(-40, 40)],
             fill=(150, 130, 95, 46), width=2)
for _ in range(260):  # paper grain
    x, y = rng.randint(8, TW - 8), rng.randint(8, TH - 8)
    shd.point([x, y], fill=(120, 105, 80, rng.randint(18, 55)))
ticket = Image.alpha_composite(ticket, shade)
td = ImageDraw.Draw(ticket)
# inner border
td.rectangle([22, 20, TW - 22, TH - 20], outline=(30, 28, 26, 255), width=3)

# top micro-line: third make.fun, functional filing line
td.text((40, 34), "FILED VIA make.fun  ·  TICKET NO. VC-2026-1119",
        font=font(FB, 21), fill=(90, 80, 66, 255))

# header
td.text((40, 64), "LEONIDA PARKING AUTHORITY", font=font(FB, 36),
        fill=(24, 22, 20, 255))
td.text((40, 112), "OVERSTAY NOTICE", font=font(FB, 36), fill=(24, 22, 20, 255))

# red METER EXPIRED stamp, diagonal, top right
# (shrunk + moved up vs original 300x150 @ (615,28): the old stamp's
# bottom edge overlapped the lifted $4,748 / $1,300 prices. New size
# 210x105 @ (680,8): rotated bbox ~228x150, bottom edge clears the
# $4,748 row top (ticket y~151) by ~15px at the prices' x-range and the
# whole stamp stays inside the paper, clear of the right edge.)
stamp = Image.new("RGBA", (210, 105), (0, 0, 0, 0))
sdd = ImageDraw.Draw(stamp)
sdd.rectangle([6, 6, 204, 99], outline=(198, 24, 32, 235), width=5)
sdd.rectangle([14, 14, 196, 91], outline=(198, 24, 32, 200), width=2)
sdd.text((20, 15), "METER", font=font(FB, 36), fill=(198, 24, 32, 240))
sdd.text((20, 54), "EXPIRED", font=font(FB, 36), fill=(198, 24, 32, 240))
for _ in range(120):  # distressed stamp speckle
    x, y = rng.randint(6, 204), rng.randint(6, 99)
    sdd.point([x, y], fill=(243, 240, 230, rng.randint(90, 200)))
stamp = stamp.rotate(-13, expand=True, resample=Image.BICUBIC)
ticket.alpha_composite(stamp, (680, 8))

# dates
td.text((40, 160), "PARKED LOS SANTOS - SEP 17, 2013", font=font(FB, 27),
        fill=(24, 22, 20, 255))
td.text((40, 192), "TICKETED VICE CITY - NOV 19, 2026", font=font(FB, 27),
        fill=(24, 22, 20, 255))
td.line([40, 232, TW - 40, 232], fill=(24, 22, 20, 255), width=3)

# itemised charges: label left, price right
items = [
    ("Parking: 4,748 days @ $1/day", "$4,748"),
    ("Late fee: 13 years overdue", "$1,300"),
    ("Tow: Los Santos to Vice City", "$313"),
    ("Trailer rewatched 47 times", "$47"),
    ("Copium, extra large", "$26"),
]
y = 248
for label, price in items:
    td.text((40, y), label, font=font(FR, 30), fill=(24, 22, 20, 255))
    pw = td.textlength(price, font=font(FB, 30))
    # Ticket is tilted -7deg when composed: a price at the right edge sits
    # ~tan(7deg)*(price centre x - label x) lower on screen than its label.
    # Lift each price by that amount so it is level with its label.
    lift = math.tan(math.radians(7)) * ((TW - 40 - pw / 2) - 40)
    td.text((TW - 40 - pw, y - lift), price, font=font(FB, 30),
            fill=(24, 22, 20, 255))
    y += 44
td.line([40, y + 4, TW - 40, y + 4], fill=(24, 22, 20, 255), width=4)
total = "TOTAL DUE $6,434"
tw = td.textlength(total, font=font(FB, 44))
td.text((TW - 40 - tw, y + 16), total, font=font(FB, 44), fill=(24, 22, 20, 255))

# magenta paid bar
bar_y = TH - 118
td.rectangle([22, bar_y, TW - 22, TH - 20], fill=(214, 28, 110, 255))
td.text((44, bar_y + 10), "PAID BY MY AI AGENT", font=font(FB, 40),
        fill=(255, 255, 255, 255))
td.text((44, bar_y + 58), "funded by bounties it earned on make.fun",
        font=font(FR, 25), fill=(255, 235, 245, 255))
# make.fun pill (second make.fun)
pill = "make.fun"
pf = font(FB, 30)
pw = td.textlength(pill, font=pf)
px0, py0 = TW - 44 - pw - 36, bar_y + 22
td.rounded_rectangle([px0, py0, px0 + pw + 36, py0 + 52], radius=26,
                     fill=(255, 255, 255, 255))
td.text((px0 + 18, py0 + 8), pill, font=pf, fill=(214, 28, 110, 255))

# ---------------------------------------------------------------- compose
# soft drop shadow of the ticket, offset down-right
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shd2 = ImageDraw.Draw(shadow)
tilted = ticket.rotate(-7, expand=True, resample=Image.BICUBIC)
sx, sy = (W - tilted.width) // 2 + 26, (H - tilted.height) // 2 + 52
mask = tilted.split()[3]
black = Image.new("RGBA", tilted.size, (0, 0, 0, 170))
shadow.paste(black, (sx, sy), mask)
shadow = shadow.filter(ImageFilter.GaussianBlur(16))
img = Image.alpha_composite(img, shadow)
img.alpha_composite(tilted, ((W - tilted.width) // 2, (H - tilted.height) // 2 + 8))

# subtle vignette
vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, 46], fill=(0, 0, 0, 70))
vd.rectangle([0, H - 46, W, H], fill=(0, 0, 0, 70))
img = Image.alpha_composite(img, vig)

img.convert("RGB").save("/home/hatch/workspace/makefun/gta6-meme-x-01/entry-v19-build/meme-v19.png")
print("saved meme-v19.png")
