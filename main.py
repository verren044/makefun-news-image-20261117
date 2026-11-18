#!/usr/bin/env python3
"""news-image-20261117 v2 -- "Sum up 17 November's world news in one image".

A denser newspaper front page, THE WORLD, TUESDAY 17 NOVEMBER 2026:
28 stories in one image.

  Masthead + a small world map (red numbered dots mark the four anchor
  stories, dark dots mark brief locations).
  Four illustrated anchor panels (compact redraws of v1):
  1. US STRIKES IRAN      -- jets hit a missile site on Qeshm Island;
                             Iran drones a US radar base in Bahrain.
  2. KERCH BRIDGE FALLS   -- Ukrainian drones hit the Kerch Bridge for a
                             second day; a road section falls into the strait.
  3. NVIDIA RECORD, NO RETURN -- revenue $115.8 billion, but ousted
                             CEO Jensen Huang will not be reinstated.
  4. TRUMP TO SHENZHEN    -- Trump heads to Shenzhen for APEC talks with
                             Xi and Putin (Quad talks in Manila first).
  24 briefs (headline + one line), each verified as happening or first
  reported on 17 November 2026: Gaza aid plea; Depardieu admits guilt;
  Japan scrambles jets; Houthis advance in Yemen; Russian plane crashes
  in Kemerovo; tanker sinks off Bulgaria; France strikes over living
  costs; Moldova closes airspace; US loses measles status; settlers kill
  a woman near Jericho; Haiti rallies for Bukele; Mongolia president
  resigns; Houthis hit Saudi pipeline; mines hit more Hormuz ships; oil
  eases as US stocks rise; US curbs China AI chips; US soldier held in
  Britain; Quad seals minerals pacts; India-Japan 2+2 talks; Xi pushes
  open trade; Netanyahu faces vote probe; France role in Ukraine
  revealed; Huang to face Congress; crypto slides in East Europe.

Pure standard library. No network, no randomness, no time, no paid keys.
Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png):
PNG, exactly 1024x1024, under 1 MiB. Two runs are byte-identical.

Run:  python3 main.py
"""

import os
import struct
import zlib
from math import sqrt

W, H = 1024, 1024

PAPER = (247, 241, 222)
INK = (18, 18, 18)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
DARKRED = (122, 20, 20)
NAVY = (24, 48, 96)
DARKBLUE = (18, 60, 110)
DARKGREEN = (14, 59, 46)
GREEN = (31, 160, 85)
GOLD = (212, 175, 55)
SKY = (168, 208, 232)
SEA = (46, 111, 168)
MAPSEA = (150, 190, 215)
LAND = (168, 160, 120)
ORANGE = (217, 123, 46)
SUN = (244, 196, 96)
GREY = (80, 80, 80)

# ---------------------------------------------------------------- font ----
# Hand-checked 5x7 bitmap font. Every glyph below was verified as ASCII art
# before use: rows are 5 chars, '1' = ink. Only glyphs used by this entry
# are defined; draw_text raises on anything else so a missing glyph can
# never silently render as garbage.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ",": ["00000", "00000", "00000", "00000", "00100", "00100", "01000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
}

# ------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        row = bytearray()
        for _ in range(w):
            row += bytes(bg)
        self.px = [bytearray(row) for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            r = self.px[y]
            r[x * 3:x * 3 + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            r = self.px[yy]
            for xx in range(x0, x1):
                r[xx * 3:xx * 3 + 3] = bytes(c)

    def frame(self, x, y, w, h, t, c):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, length, t, c):
        self.rect(x, y, length, t, c)

    def vline(self, x, y, length, t, c):
        self.rect(x, y, t, length, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int(sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / ry
            dx = int(rx * sqrt(max(0.0, 1.0 - dy * dy)))
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def polygon(self, pts, c):
        # Scanline fill; pts = [(x, y), ...] in order.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if y1 == y2:
                    continue
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

    def line(self, x1, y1, x2, y2, t, c):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            x = int(x1 + (x2 - x1) * i / steps)
            y = int(y1 + (y2 - y1) * i / steps)
            self.circle(x, y, max(1, t // 2), c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                raise ValueError("no glyph for %r" % ch)
            for ry, row in enumerate(g):
                for rx, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_c(self, cx, y, s, scale, c):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)


# -------------------------------------------------------------- PNG out ----
def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# -------------------------------------------------------------- map -------
# Equirectangular map, lon -170..190, lat 75..-55, over the map rect.
MAP_X, MAP_Y, MAP_W, MAP_H = 24, 168, 976, 112


def mx(lon):
    return MAP_X + int((lon + 170) / 360.0 * MAP_W)


def my(lat):
    return MAP_Y + int((75 - lat) / 130.0 * MAP_H)


def lonlat_poly(cv, pts, c):
    cv.polygon([(mx(lon), my(lat)) for lon, lat in pts], c)


CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 68), (-95, 73), (-80, 70),
     (-75, 60), (-70, 45), (-80, 32), (-90, 30), (-97, 26), (-105, 20),
     (-115, 28), (-125, 40), (-140, 58), (-160, 60)],
    # Greenland
    [(-45, 60), (-30, 70), (-20, 75), (-40, 80), (-55, 75)],
    # South America
    [(-80, 10), (-75, 5), (-60, -5), (-50, -10), (-40, -20), (-35, -30),
     (-50, -35), (-60, -40), (-70, -50), (-75, -40), (-80, -20)],
    # Europe
    [(-10, 36), (-5, 44), (0, 50), (10, 55), (20, 60), (30, 65), (35, 60),
     (40, 55), (30, 45), (25, 40), (20, 36), (10, 38), (0, 36)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (45, 10), (50, 10), (45, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -25), (12, -15), (10, 0), (5, 5), (-5, 5), (-10, 10)],
    # Asia
    [(40, 70), (60, 72), (80, 73), (100, 76), (120, 72), (140, 72),
     (160, 70), (170, 66), (160, 60), (145, 55), (140, 45), (130, 35),
     (125, 30), (120, 25), (110, 20), (105, 10), (100, 5), (95, 15),
     (90, 20), (80, 10), (75, 8), (70, 20), (60, 25), (50, 30), (45, 40),
     (40, 50)],
    # Australia
    [(113, -22), (120, -15), (130, -12), (140, -15), (150, -25), (150, -37),
     (140, -38), (130, -32), (120, -35), (113, -30)],
    # Japan
    [(130, 31), (132, 33), (138, 36), (141, 39), (142, 44), (140, 45),
     (136, 38), (131, 33)],
    # Britain
    [(-5, 50), (-3, 53), (-1, 55), (-2, 58), (-4, 57), (-5, 53)],
]

# Anchor dots: (lon, lat, number, label, label dx, label dy)
ANCHOR_DOTS = [
    (56.5, 26.8, "1", "QESHM", 12, -4),
    (36.5, 45.3, "2", "KERCH", 12, -4),
    (-122.0, 37.4, "3", "NVIDIA", 12, -4),
    (114.1, 22.5, "4", "SHENZHEN", -62, 10),
]
# Brief-location dots: (lon, lat)
BRIEF_DOTS = [
    (139.7, 35.7),    # Tokyo
    (2.35, 48.85),    # Paris
    (45.0, 12.8),     # Aden
    (28.8, 47.0),     # Chisinau
    (-0.1, 51.5),     # London
    (106.9, 47.9),    # Ulaanbaatar
    (-72.3, 18.5),    # Port-au-Prince
]


def draw_map(cv):
    cv.rect(MAP_X, MAP_Y, MAP_W, MAP_H, MAPSEA)
    for poly in CONTINENTS:
        lonlat_poly(cv, poly, LAND)
    cv.frame(MAP_X, MAP_Y, MAP_W, MAP_H, 2, INK)
    cv.text(MAP_X + 8, MAP_Y + 4, "THE WORLD AT A GLANCE", 1, INK)
    for lon, lat in BRIEF_DOTS:
        cv.circle(mx(lon), my(lat), 4, INK)
    for lon, lat, num, label, dx, dy in ANCHOR_DOTS:
        x, y = mx(lon), my(lat)
        cv.circle(x, y, 9, RED)
        cv.circle(x, y, 7, RED)
        cv.text(x - 2, y - 3, num, 1, WHITE)
        cv.text(x + dx, y + dy, label, 1, INK)


# ---------------------------------------------------- compact scenes -----
# Each scene draws in a 472x128 box (sx, sy).
def scene_iran(cv, sx, sy, sw, sh):
    """Compact panel 1: dusk sky, Qeshm Island explosion, US jet,
    Bahrain radar base droned at right."""
    cv.rect(sx, sy, sw, sh, (232, 163, 76))
    cv.rect(sx, sy + 44, sw, 30, ORANGE)
    cv.rect(sx, sy + 74, sw, 34, (184, 92, 40))
    cv.circle(sx + sw - 52, sy + 26, 18, SUN)
    cv.rect(sx, sy + sh - 20, sw, 20, SEA)
    cv.hline(sx + 12, sy + sh - 12, 24, 2, WHITE)
    cv.hline(sx + 60, sy + sh - 7, 24, 2, WHITE)
    # Qeshm Island (left)
    cv.polygon([(sx + 16, sy + sh - 20), (sx + 44, sy + sh - 56),
                (sx + 150, sy + sh - 56), (sx + 180, sy + sh - 20)],
               (74, 96, 52))
    # missile launcher + missile
    cv.rect(sx + 74, sy + sh - 62, 26, 7, (40, 40, 40))
    cv.line(sx + 87, sy + sh - 62, sx + 100, sy + sh - 84, 5, (60, 60, 60))
    cv.circle(sx + 101, sy + sh - 86, 4, (200, 200, 200))
    # explosion starburst over the site
    ex, ey = sx + 100, sy + 34
    cv.circle(ex, ey, 22, (255, 120, 20))
    cv.circle(ex, ey, 14, (255, 190, 40))
    cv.circle(ex, ey, 7, (255, 240, 160))
    for dx, dy in [(-24, -10), (24, -11), (-19, 14), (22, 13), (0, -27)]:
        cv.polygon([(ex, ey), (ex + dx - 4, ey + dy),
                    (ex + dx + 4, ey + dy)], (255, 120, 20))
    # smoke column
    for cx, cy, r in [(sx + 76, sy + 26, 8), (sx + 66, sy + 14, 10)]:
        cv.circle(cx, cy, r, (90, 90, 90))
    # US jet, top left, flying right with contrail
    jx, jy = sx + 14, sy + 12
    cv.polygon([(jx, jy), (jx + 52, jy + 7), (jx, jy + 14)], (30, 30, 34))
    cv.polygon([(jx + 18, jy + 5), (jx + 30, jy - 8), (jx + 36, jy + 5)],
               (30, 30, 34))
    cv.line(sx + 2, jy + 3, jx - 2, jy + 6, 2, WHITE)
    # Bahrain radar base (right): islet, dome + dish
    cv.polygon([(sx + sw - 118, sy + sh - 20), (sx + sw - 104, sy + sh - 46),
                (sx + sw - 34, sy + sh - 46), (sx + sw - 14, sy + sh - 20)],
               (120, 110, 88))
    cv.circle(sx + sw - 54, sy + sh - 46, 14, (220, 220, 220))
    cv.rect(sx + sw - 68, sy + sh - 46, 30, 4, (220, 220, 220))
    cv.line(sx + sw - 86, sy + sh - 48, sx + sw - 100, sy + sh - 66,
            4, (60, 60, 60))
    cv.circle(sx + sw - 101, sy + sh - 68, 5, (200, 200, 200))
    # two drones closing in on the base
    for dx, dy in [(sx + sw - 140, sy + 30), (sx + sw - 100, sy + 18)]:
        cv.circle(dx, dy, 4, INK)
        cv.line(dx - 8, dy - 5, dx + 8, dy + 5, 2, INK)
        cv.line(dx - 8, dy + 5, dx + 8, dy - 5, 2, INK)


def scene_kerch(cv, sx, sy, sw, sh):
    """Compact panel 2: Kerch Bridge over the strait, middle section
    blown out and falling, drones overhead."""
    cv.rect(sx, sy, sw, sh, (196, 210, 222))
    cv.ellipse(sx + 60, sy + 16, 34, 8, WHITE)
    cv.ellipse(sx + sw - 70, sy + 26, 40, 9, WHITE)
    cv.rect(sx, sy + 56, sw, sh - 56, SEA)
    cv.hline(sx + 10, sy + 84, 26, 2, WHITE)
    cv.hline(sx + 30, sy + 108, 26, 2, WHITE)
    deck_y = sy + 54
    # bridge deck, left and right of the gap
    cv.rect(sx + 8, deck_y, 168, 12, (90, 90, 90))
    cv.rect(sx + sw - 176, deck_y, 168, 12, (90, 90, 90))
    for dx in range(sx + 14, sx + 176, 24):
        cv.rect(dx, deck_y + 5, 12, 2, (255, 210, 60))
    for dx in range(sx + sw - 170, sx + sw - 8, 24):
        cv.rect(dx, deck_y + 5, 12, 2, (255, 210, 60))
    # towers + cables
    for tx in (sx + 60, sx + sw - 76):
        cv.rect(tx, deck_y - 34, 10, 34, (70, 70, 70))
        cv.line(tx + 5, deck_y - 34, tx - 60, deck_y, 2, (140, 140, 140))
        cv.line(tx + 5, deck_y - 34, tx + 70, deck_y, 2, (140, 140, 140))
    # falling road section, tilted, mid-gap
    cv.polygon([(sx + 196, deck_y + 16), (sx + 248, deck_y + 26),
                (sx + 238, deck_y + 40), (sx + 188, deck_y + 30)],
               (90, 90, 90))
    cv.rect(sx + 208, deck_y + 22, 22, 3, (255, 210, 60))
    # splash where the section hits the water
    cv.ellipse(sx + 222, sy + 104, 40, 11, WHITE)
    cv.ellipse(sx + 222, sy + 98, 24, 7, WHITE)
    for dx, dy in [(-30, -11), (-12, -18), (10, -19), (28, -10)]:
        cv.circle(sx + 222 + dx, sy + 100 + dy, 3, WHITE)
    # smoke at the break points
    for cx, cy, r in [(sx + 176, deck_y - 4, 9), (sx + 166, deck_y - 16, 11),
                      (sx + 292, deck_y - 3, 8), (sx + 302, deck_y - 14, 10)]:
        cv.circle(cx, cy, r, (110, 110, 110))
    # blast flash at the gap
    cv.circle(sx + 232, deck_y, 10, (255, 190, 40))
    cv.circle(sx + 232, deck_y, 5, (255, 240, 160))
    # two drones above the bridge
    for dx, dy in [(sx + 120, sy + 14), (sx + 330, sy + 20)]:
        cv.circle(dx, dy, 4, INK)
        cv.line(dx - 8, dy - 5, dx + 8, dy + 5, 2, INK)
        cv.line(dx - 8, dy + 5, dx + 8, dy - 5, 2, INK)


def scene_nvidia(cv, sx, sy, sw, sh):
    """Compact panel 3: green chip, record sales bars climbing, red
    NO RETURN banner, empty CEO chair."""
    cv.rect(sx, sy, sw, sh, DARKGREEN)
    # chip, left
    cx, cy = sx + 22, sy + 10
    cv.rect(cx, cy, 110, 60, GREEN)
    cv.frame(cx, cy, 110, 60, 3, (8, 60, 36))
    for i in range(3):
        cv.rect(cx - 9, cy + 10 + i * 18, 9, 6, GOLD)
        cv.rect(cx + 110, cy + 10 + i * 18, 9, 6, GOLD)
    cv.rect(cx + 38, cy + 19, 34, 22, (8, 60, 36))
    cv.text_c(cx + 55, cy + 24, "NV", 2, GOLD)
    # record sales figure under the chip, clear of the banner
    cv.text_c(sx + 77, sy + 76, "$115BN", 3, GOLD)
    # rising bars, right
    bx, by = sx + 240, sy + 74
    for i, bh in enumerate((20, 32, 46, 60)):
        cv.rect(bx + i * 42, by - bh, 30, bh, (120, 220, 150))
    cv.line(bx - 6, by + 2, bx + 158, by - 44, 4, GOLD)
    cv.polygon([(bx + 158, by - 44), (bx + 136, by - 44),
                (bx + 158, by - 26)], GOLD)
    cv.text_c(sx + 320, sy + 6, "RECORD", 2, WHITE)
    cv.text_c(sx + 320, sy + 24, "QUARTER", 2, WHITE)
    # empty CEO chair, between chip and bars, above the banner
    chx, chy = sx + 150, sy + 78
    cv.rect(chx, chy, 6, 24, (10, 10, 10))             # back post
    cv.rect(chx, chy, 40, 6, (10, 10, 10))             # back top
    cv.rect(chx, chy + 20, 54, 6, (10, 10, 10))        # seat
    # red NO RETURN banner across the bottom
    cv.rect(sx, sy + sh - 24, sw, 24, RED)
    cv.text_c(sx + sw // 2, sy + sh - 19, "NO RETURN", 2, WHITE)


def scene_shenzhen(cv, sx, sy, sw, sh):
    """Compact panel 4: plane flying in over the Shenzhen skyline,
    APEC banner, US and China flags at the talks."""
    cv.rect(sx, sy, sw, sh, SKY)
    cv.circle(sx + sw - 48, sy + 22, 16, SUN)
    cv.ellipse(sx + 170, sy + 16, 34, 8, WHITE)
    cv.ellipse(sx + 190, sy + 40, 28, 7, WHITE)
    # APEC banner, top left
    cv.rect(sx + 12, sy + 8, 96, 30, RED)
    cv.text_c(sx + 60, sy + 15, "APEC", 2, WHITE)
    # plane, upper middle, flying right with contrail
    px, py = sx + 130, sy + 52
    cv.line(sx + 12, py + 18, px - 6, py + 8, 2, WHITE)
    cv.ellipse(px + 36, py + 6, 48, 9, WHITE)
    cv.polygon([(px + 24, py + 3), (px + 40, py - 16), (px + 48, py + 3)],
               WHITE)
    cv.polygon([(px + 24, py + 9), (px + 36, py + 24), (px + 44, py + 9)],
               WHITE)
    cv.polygon([(px + 74, py - 1), (px + 86, py - 14), (px + 90, py - 1)],
               WHITE)
    cv.circle(px + 80, py + 4, 2, (40, 90, 160))
    cv.circle(px + 68, py + 4, 2, (40, 90, 160))
    cv.circle(px + 56, py + 4, 2, (40, 90, 160))
    # Shenzhen skyline, bottom
    base = sy + sh
    towers = [(0, 62, 46), (52, 78, 42), (100, 52, 44),
              (150, 70, 46), (202, 40, 48), (256, 62, 46),
              (308, 54, 44), (358, 66, 46), (410, 58, 46)]
    for tx, th, tw in towers:
        cv.rect(sx + tx, base - th, tw, th, (28, 52, 96))
        for wy in range(base - th + 8, base - 6, 14):
            for wx in range(sx + tx + 7, sx + tx + tw - 6, 12):
                cv.rect(wx, wy, 4, 5, (255, 220, 120))
    # tallest tapered tower with antenna
    cv.polygon([(sx + 202, base - 40), (sx + 212, base - 96),
                (sx + 238, base - 96), (sx + 250, base - 40)],
               (20, 40, 80))
    cv.rect(sx + 223, base - 112, 4, 18, (20, 40, 80))
    cv.circle(sx + 225, base - 114, 3, RED)
    # flags at the talks: US stripes, China red, on poles by the towers
    for fx, cols in [(sx + 24, [(178, 34, 34), WHITE, (178, 34, 34)]),
                     (sx + 420, [(200, 22, 22), (200, 22, 22),
                                 (200, 22, 22)])]:
        cv.rect(fx, base - 48, 3, 48, (60, 60, 60))
        for i, col in enumerate(cols):
            cv.rect(fx + 3, base - 48 + i * 7, 26, 7, col)


# -------------------------------------------------------------- layout ----
PANELS = [
    ("US STRIKES IRAN", "QESHM HIT, BAHRAIN DRONED", DARKRED, scene_iran),
    ("KERCH BRIDGE FALLS", "SECOND DAY OF DRONE HITS", DARKBLUE, scene_kerch),
    ("NVIDIA RECORD", "$115BN SALES, CEO STAYS OUT", DARKGREEN, scene_nvidia),
    ("TRUMP TO SHENZHEN", "APEC TALKS WITH XI, PUTIN", NAVY, scene_shenzhen),
]

# 24 briefs: (headline, caption). Headline <= 39 chars, caption <= 78.
BRIEFS_COL1 = [
    ("GAZA AID PLEA",
     "UK, AUSTRALIA, CANADA AND ITALY URGE ISRAEL TO OPEN CROSSINGS."),
    ("DEPARDIEU ADMITS GUILT",
     "FRENCH STAR DROPS APPEAL IN PARIS SEX ASSAULT CASE."),
    ("JAPAN SCRAMBLES JETS",
     "TWO RUSSIAN PLANES VIOLATE AIRSPACE, TOKYO PROTESTS."),
    ("HOUTHIS ADVANCE IN YEMEN",
     "GOVERNMENT TROOPS RETREAT FROM RED SEA COAST TO ADEN."),
    ("RUSSIAN PLANE CRASHES",
     "AN-12 DOWN IN KEMEROVO, ALL 19 ON BOARD KILLED."),
    ("TANKER SINKS OFF BULGARIA",
     "GAS TANKER GOES DOWN, ALL 19 CREW RESCUED."),
    ("FRANCE STRIKES OVER COSTS",
     "146,000 MARCH, 28,000 IN PARIS, UNIONS DEMAND RELIEF."),
    ("MOLDOVA CLOSES AIRSPACE",
     "RUSSIAN DRONE FLEW OVER CHISINAU, SANDU SAYS."),
    ("US LOSES MEASLES STATUS",
     "5,400 CASES, 10 DEAD, FIRST LOSS IN 26 YEARS."),
    ("SETTLERS KILL WOMAN, 72",
     "PALESTINIAN SHOT DEAD NEAR JERICHO, MINISTRY SAYS."),
    ("HAITI RALLIES FOR BUKELE",
     "THOUSANDS BACK SALVADORAN TROOPS FIGHTING GANGS."),
    ("MONGOLIA LEADER RESIGNS",
     "PRESIDENT KHURELSUKH QUITS AMID GRAFT SCANDAL."),
]
BRIEFS_COL2 = [
    ("HOUTHIS HIT SAUDI PIPELINE",
     "FIVE DRONES FIRED AT EAST-WEST PUMP STATIONS."),
    ("MINES HIT MORE SHIPS",
     "TWO MORE VESSELS STRUCK IN STRAIT OF HORMUZ."),
    ("OIL EASES AS STOCKS RISE",
     "US INVENTORIES UP, HORMUZ RISK LIMITS FALLS."),
    ("US CURBS CHINA AI CHIPS",
     "WASHINGTON BLOCKS REMOTE USE, BEIJING VOWS REPLY."),
    ("US SOLDIER HELD IN BRITAIN",
     "ARRESTED ON SPYING SUSPICION, IN US CUSTODY."),
    ("QUAD SEALS MINERALS PACTS",
     "TRUMP ANNOUNCES DEALS AT MANILA SUMMIT."),
    ("INDIA JAPAN HOLD 2 PLUS 2",
     "FOREIGN AND DEFENCE CHIEFS MEET IN TOKYO."),
    ("XI PUSHES OPEN TRADE",
     "CHINA HOSTS APEC AS SHENZHEN SUMMIT OPENS."),
    ("NETANYAHU FACES VOTE PROBE",
     "PM ACCUSED OF ELECTORAL INTERFERENCE."),
    ("FRANCE ROLE IN UKRAINE",
     "RFI REPORT REVEALS COVERT OPERATION, RUSSIA PROTESTS."),
    ("HUANG TO FACE CONGRESS",
     "EX NVIDIA CHIEF TO TESTIFY ON SECURITY BREACH."),
    ("CRYPTO SLIDES IN EAST EUROPE",
     "ACTIVITY DOWN 7.9 PERCENT IN A YEAR, STUDY FINDS."),
]


def build():
    cv = Canvas(W, H, PAPER)
    cv.frame(6, 6, W - 12, H - 12, 6, INK)
    # masthead
    cv.text_c(W // 2, 20, "THE WORLD", 11, INK)
    cv.hline(24, 104, W - 48, 3, INK)
    cv.hline(24, 112, W - 48, 2, INK)
    cv.text_c(W // 2, 120, "TUESDAY 17 NOVEMBER 2026", 2, INK)
    cv.text_c(W // 2, 140, "WORLD NEWS IN PICTURES - 28 STORIES", 2,
              (90, 60, 30))
    cv.hline(24, 160, W - 48, 3, INK)
    # world map strip
    draw_map(cv)
    # 2x2 anchor panels, compact scenes
    pw, ph = 488, 205
    for i, (head, cap, strip, draw) in enumerate(PANELS):
        px = 16 + (i % 2) * (pw + 16)
        py = 288 + (i // 2) * (ph + 12)
        cv.rect(px, py, pw, ph, WHITE)
        cv.frame(px, py, pw, ph, 3, INK)
        cv.rect(px + 3, py + 3, pw - 6, 36, strip)
        cv.text_c(px + pw // 2, py + 13, head, 2, WHITE)
        draw(cv, px + 8, py + 47, pw - 16, ph - 47 - 30)
        cv.hline(px + 8, py + ph - 30, pw - 16, 2, INK)
        cv.text_c(px + pw // 2, py + ph - 24, cap, 2, INK)
    # briefs
    cv.text(16, 722, "MORE FROM THE WORLD", 2, INK)
    cv.text(1008 - cv.text_w("24 BRIEFS", 2), 722, "24 BRIEFS", 2, INK)
    cv.hline(16, 744, 976, 2, INK)
    for col, bx in enumerate((16, 520)):
        briefs = BRIEFS_COL1 if col == 0 else BRIEFS_COL2
        for j, (head, cap) in enumerate(briefs):
            by = 752 + j * 21
            cv.rect(bx, by + 4, 6, 6, RED)
            cv.text(bx + 12, by, head, 2, INK)
            cv.text(bx + 12, by + 14, cap, 1, GREY)
    cv.vline(508, 752, 252, 2, (150, 140, 120))
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(build(), path)
    print("wrote", path)


if __name__ == "__main__":
    main()
