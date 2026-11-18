#!/usr/bin/env python3
"""news-image-20261117 -- "Sum up 17 November's world news in one image".

A newspaper front page, THE WORLD, TUESDAY 17 NOVEMBER 2026, with four
illustrated panels, one per story:

  1. US STRIKES IRAN      -- jets hit a missile site on Qeshm Island;
                             Iran drones a US radar base in Bahrain.
  2. KERCH BRIDGE FALLS   -- Ukrainian drones hit the Kerch Bridge for a
                             second day; a road section falls into the strait.
  3. NVIDIA RECORD, NO RETURN -- revenue above $115 billion, but ousted
                             CEO Jensen Huang will not be reinstated.
  4. TRUMP TO SHENZHEN    -- Trump heads to Shenzhen for APEC talks with
                             Xi and Putin (Quad talks in Manila first).

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
ORANGE = (217, 123, 46)
SUN = (244, 196, 96)

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


# -------------------------------------------------------------- scenes ----
def scene_iran(cv, sx, sy, sw, sh):
    """Panel 1: dusk sky, Qeshm Island missile site exploding, US jet,
    Bahrain radar base droned at right."""
    cv.rect(sx, sy, sw, sh, (232, 163, 76))            # dusk sky
    cv.rect(sx, sy + 90, sw, 60, ORANGE)
    cv.rect(sx, sy + 150, sw, 60, (184, 92, 40))
    cv.circle(sx + sw - 70, sy + 55, 30, SUN)          # low sun
    cv.rect(sx, sy + sh - 64, sw, 64, SEA)             # strait
    for wx in range(sx + 10, sx + sw - 10, 46):         # wave ticks
        cv.hline(wx, sy + sh - 44, 26, 3, WHITE)
        cv.hline(wx + 12, sy + sh - 22, 26, 3, WHITE)
    # Qeshm Island (left)
    cv.polygon([(sx + 20, sy + sh - 64), (sx + 60, sy + sh - 118),
                (sx + 190, sy + sh - 118), (sx + 230, sy + sh - 64)],
               (74, 96, 52))
    # missile launcher + missile on the island
    cv.rect(sx + 96, sy + sh - 128, 34, 10, (40, 40, 40))
    cv.line(sx + 113, sy + sh - 128, sx + 132, sy + sh - 168, 7, (60, 60, 60))
    cv.circle(sx + 134, sy + sh - 172, 6, (200, 200, 200))
    # explosion starburst over the site
    ex, ey = sx + 128, sy + sh - 190
    cv.circle(ex, ey, 34, (255, 120, 20))
    cv.circle(ex, ey, 22, (255, 190, 40))
    cv.circle(ex, ey, 11, (255, 240, 160))
    for dx, dy in [(-38, -14), (38, -16), (-30, 22), (34, 20), (0, -42)]:
        cv.polygon([(ex, ey), (ex + dx - 6, ey + dy),
                    (ex + dx + 6, ey + dy)], (255, 120, 20))
    # smoke column
    for cx, cy, r in [(sx + 96, sy + 62, 12), (sx + 84, sy + 44, 15),
                      (sx + 70, sy + 26, 18)]:
        cv.circle(cx, cy, r, (90, 90, 90))
    # US jet, top left, flying right with contrail
    jx, jy = sx + 30, sy + 34
    cv.polygon([(jx, jy), (jx + 74, jy + 10), (jx, jy + 20)], (30, 30, 34))
    cv.polygon([(jx + 26, jy + 8), (jx + 44, jy - 12), (jx + 52, jy + 8)],
               (30, 30, 34))
    cv.polygon([(jx + 26, jy + 12), (jx + 40, jy + 28), (jx + 48, jy + 12)],
               (30, 30, 34))
    cv.line(jx - 58, jy + 4, jx - 2, jy + 8, 3, WHITE)
    # Bahrain radar base (right): small islet, dome + dish
    cv.polygon([(sx + sw - 150, sy + sh - 64), (sx + sw - 130, sy + sh - 96),
                (sx + sw - 40, sy + sh - 96), (sx + sw - 16, sy + sh - 64)],
               (120, 110, 88))
    cv.circle(sx + sw - 66, sy + sh - 96, 20, (220, 220, 220))
    cv.rect(sx + sw - 86, sy + sh - 96, 40, 6, (220, 220, 220))
    cv.line(sx + sw - 108, sy + sh - 100, sx + sw - 128, sy + sh - 132,
            5, (60, 60, 60))
    cv.circle(sx + sw - 130, sy + sh - 134, 7, (200, 200, 200))
    # three drones closing in on the base
    for dx, dy in [(sx + sw - 170, sy + 66), (sx + sw - 120, sy + 44),
                   (sx + sw - 84, sy + 84)]:
        cv.circle(dx, dy, 5, INK)
        cv.line(dx - 10, dy - 6, dx + 10, dy + 6, 2, INK)
        cv.line(dx - 10, dy + 6, dx + 10, dy - 6, 2, INK)


def scene_kerch(cv, sx, sy, sw, sh):
    """Panel 2: Kerch Bridge over the strait, middle section blown out
    and falling, drones overhead."""
    cv.rect(sx, sy, sw, sh, (196, 210, 222))           # pale sky
    cv.ellipse(sx + 70, sy + 34, 46, 12, WHITE)
    cv.ellipse(sx + sw - 90, sy + 52, 54, 13, WHITE)
    cv.rect(sx, sy + 110, sw, sh - 110, SEA)           # strait
    for wx in range(sx + 8, sx + sw - 8, 52):
        cv.hline(wx, sy + 168, 30, 3, WHITE)
        cv.hline(wx + 16, sy + 226, 30, 3, WHITE)
        cv.hline(wx + 4, sy + 268, 30, 3, WHITE)
    deck_y = sy + 108
    # bridge deck, left and right of the gap
    cv.rect(sx + 8, deck_y, 168, 16, (90, 90, 90))
    cv.rect(sx + sw - 176, deck_y, 168, 16, (90, 90, 90))
    for dx in range(sx + 14, sx + 176, 24):             # lane dashes
        cv.rect(dx, deck_y + 7, 12, 2, (255, 210, 60))
    for dx in range(sx + sw - 170, sx + sw - 8, 24):
        cv.rect(dx, deck_y + 7, 12, 2, (255, 210, 60))
    # towers + cables
    for tx in (sx + 60, sx + sw - 76):
        cv.rect(tx, deck_y - 62, 12, 62, (70, 70, 70))
        cv.line(tx + 6, deck_y - 62, tx - 70, deck_y, 2, (140, 140, 140))
        cv.line(tx + 6, deck_y - 62, tx + 82, deck_y, 2, (140, 140, 140))
    # falling road section, tilted, mid-gap
    cv.polygon([(sx + 196, deck_y + 30), (sx + 252, deck_y + 44),
                (sx + 240, deck_y + 62), (sx + 186, deck_y + 48)],
               (90, 90, 90))
    cv.rect(sx + 210, deck_y + 40, 26, 4, (255, 210, 60))
    # splash where the section hits the water
    cv.ellipse(sx + 224, sy + 196, 52, 16, WHITE)
    cv.ellipse(sx + 224, sy + 188, 30, 10, WHITE)
    for dx, dy in [(-40, -16), (-16, -26), (12, -28), (38, -14)]:
        cv.circle(sx + 224 + dx, sy + 190 + dy, 4, WHITE)
    # smoke at the break points
    for cx, cy, r in [(sx + 176, deck_y - 8, 13), (sx + 164, deck_y - 26, 16),
                      (sx + 292, deck_y - 6, 12), (sx + 304, deck_y - 24, 15)]:
        cv.circle(cx, cy, r, (110, 110, 110))
    # blast flash at the gap
    cv.circle(sx + 232, deck_y - 2, 14, (255, 190, 40))
    cv.circle(sx + 232, deck_y - 2, 7, (255, 240, 160))
    # three drones above the bridge
    for dx, dy in [(sx + 120, sy + 30), (sx + 232, sy + 18),
                   (sx + 340, sy + 40)]:
        cv.circle(dx, dy, 5, INK)
        cv.line(dx - 11, dy - 7, dx + 11, dy + 7, 2, INK)
        cv.line(dx - 11, dy + 7, dx + 11, dy - 7, 2, INK)


def scene_nvidia(cv, sx, sy, sw, sh):
    """Panel 3: green chip, record sales bars climbing, red NO RETURN
    banner, empty CEO chair."""
    cv.rect(sx, sy, sw, sh, DARKGREEN)
    # chip, left
    cx, cy = sx + 34, sy + 26
    cv.rect(cx, cy, 150, 104, GREEN)
    cv.frame(cx, cy, 150, 104, 4, (8, 60, 36))
    for i in range(4):                                  # pins
        cv.rect(cx - 12, cy + 16 + i * 26, 12, 8, GOLD)
        cv.rect(cx + 150, cy + 16 + i * 26, 12, 8, GOLD)
    cv.rect(cx + 52, cy + 36, 46, 32, (8, 60, 36))
    cv.text_c(cx + 75, cy + 42, "NV", 3, GOLD)
    # record sales figure, gold, under the chip
    cv.text_c(sx + 109, sy + 148, "$115BN", 4, GOLD)
    cv.text_c(sx + 109, sy + 184, "SALES", 3, WHITE)
    # rising bars, right; trend arrow kept below the RECORD/QUARTER text
    bx, by = sx + 250, sy + 130
    for i, bh in enumerate((34, 56, 82, 112)):
        cv.rect(bx + i * 48, by - bh, 34, bh, (120, 220, 150))
    cv.line(bx - 8, by + 2, bx + 186, by - 80, 5, GOLD)
    cv.polygon([(bx + 186, by - 80), (bx + 160, by - 80),
                (bx + 186, by - 58)], GOLD)
    cv.text_c(sx + 348, sy + 26, "RECORD", 3, WHITE)
    cv.text_c(sx + 348, sy + 52, "QUARTER", 3, WHITE)
    # empty CEO chair, bottom right
    chx, chy = sx + 330, sy + 168
    cv.rect(chx, chy, 8, 74, (10, 10, 10))             # back post
    cv.rect(chx, chy, 58, 8, (10, 10, 10))             # back top
    cv.rect(chx, chy + 66, 78, 10, (10, 10, 10))       # seat
    cv.rect(chx + 6, chy + 76, 7, 46, (10, 10, 10))    # legs
    cv.rect(chx + 64, chy + 76, 7, 46, (10, 10, 10))
    cv.rect(chx + 6, chy + 104, 65, 6, (10, 10, 10))
    # red NO RETURN banner across the bottom
    cv.rect(sx, sy + sh - 46, sw, 46, RED)
    cv.text_c(sx + sw // 2, sy + sh - 38, "NO RETURN", 3, WHITE)


def scene_shenzhen(cv, sx, sy, sw, sh):
    """Panel 4: plane flying in over the Shenzhen skyline, APEC banner,
    US and China flags at the talks."""
    cv.rect(sx, sy, sw, sh, SKY)
    cv.circle(sx + sw - 64, sy + 44, 26, SUN)
    cv.ellipse(sx + 190, sy + 30, 48, 12, WHITE)  # clear of APEC banner
    cv.ellipse(sx + 220, sy + 66, 40, 10, WHITE)
    # APEC banner, top left
    cv.rect(sx + 16, sy + 14, 118, 40, RED)
    cv.text_c(sx + 75, sy + 24, "APEC", 3, WHITE)
    # plane, upper middle, flying right with contrail
    px, py = sx + 150, sy + 96
    cv.line(sx + 16, py + 26, px - 6, py + 10, 3, WHITE)
    cv.ellipse(px + 46, py + 8, 62, 12, WHITE)
    cv.polygon([(px + 30, py + 4), (px + 52, py - 22), (px + 62, py + 4)],
               WHITE)
    cv.polygon([(px + 30, py + 12), (px + 48, py + 32), (px + 58, py + 12)],
               WHITE)
    cv.polygon([(px + 96, py - 2), (px + 112, py - 20), (px + 116, py - 2)],
               WHITE)
    cv.circle(px + 104, py + 6, 3, (40, 90, 160))      # windows
    cv.circle(px + 88, py + 6, 3, (40, 90, 160))
    cv.circle(px + 72, py + 6, 3, (40, 90, 160))
    # Shenzhen skyline, bottom
    base = sy + sh
    towers = [(0, 150, 64), (70, 196, 58), (134, 128, 60),
              (200, 176, 62), (268, 96, 66), (340, 158, 62),
              (408, 132, 60)]
    for tx, th, tw in towers:
        cv.rect(sx + tx, base - th, tw, th, (28, 52, 96))
        for wy in range(base - th + 12, base - 10, 20):
            for wx in range(sx + tx + 10, sx + tx + tw - 8, 16):
                cv.rect(wx, wy, 5, 7, (255, 220, 120))
    # tallest tapered tower with antenna
    cv.polygon([(sx + 268, base - 96), (sx + 282, base - 216),
                (sx + 320, base - 216), (sx + 334, base - 96)],
               (20, 40, 80))
    cv.rect(sx + 298, base - 246, 5, 32, (20, 40, 80))
    cv.circle(sx + 300, base - 248, 4, RED)
    for wy in range(base - 200, base - 10, 22):
        cv.rect(sx + 292, wy, 5, 7, (255, 220, 120))
        cv.rect(sx + 308, wy, 5, 7, (255, 220, 120))
    # flags at the talks: US stripes, China red, on poles by the towers
    for fx, cols in [(sx + 30, [(178, 34, 34), WHITE, (178, 34, 34)]),
                     (sx + 420, [(200, 22, 22), (200, 22, 22),
                                 (200, 22, 22)])]:
        cv.rect(fx, base - 66, 4, 66, (60, 60, 60))
        for i, col in enumerate(cols):
            cv.rect(fx + 4, base - 66 + i * 9, 34, 9, col)
        if fx > sx + 400:
            cv.circle(fx + 12, base - 61, 2, GOLD)
            cv.circle(fx + 22, base - 58, 1, GOLD)
            cv.circle(fx + 22, base - 52, 1, GOLD)


# -------------------------------------------------------------- layout ----
PANELS = [
    ("US STRIKES IRAN", "QESHM HIT, BAHRAIN DRONED", DARKRED, scene_iran),
    ("KERCH BRIDGE FALLS", "SECOND DAY OF DRONE HITS", DARKBLUE, scene_kerch),
    ("NVIDIA RECORD", "$115BN SALES, CEO STAYS OUT", DARKGREEN, scene_nvidia),
    ("TRUMP TO SHENZHEN", "APEC TALKS WITH XI, PUTIN", NAVY, scene_shenzhen),
]


def build():
    cv = Canvas(W, H, PAPER)
    cv.frame(6, 6, W - 12, H - 12, 6, INK)
    # masthead
    cv.text_c(W // 2, 30, "THE WORLD", 12, INK)
    cv.hline(24, 128, W - 48, 3, INK)
    cv.hline(24, 136, W - 48, 2, INK)
    cv.text_c(W // 2, 148, "TUESDAY 17 NOVEMBER 2026", 3, INK)
    cv.text_c(W // 2, 174, "WORLD NEWS IN PICTURES", 2, (90, 60, 30))
    cv.hline(24, 198, W - 48, 3, INK)
    # 2x2 panels
    pw, ph = 488, 386
    for i, (head, cap, strip, draw) in enumerate(PANELS):
        px = 16 + (i % 2) * (pw + 16)
        py = 210 + (i // 2) * (ph + 16)
        cv.rect(px, py, pw, ph, WHITE)
        cv.frame(px, py, pw, ph, 3, INK)
        cv.rect(px + 3, py + 3, pw - 6, 42, strip)
        cv.text_c(px + pw // 2, py + 14, head, 2, WHITE)
        draw(cv, px + 8, py + 53, pw - 16, ph - 53 - 36)
        cv.hline(px + 8, py + ph - 32, pw - 16, 2, INK)
        cv.text_c(px + pw // 2, py + ph - 26, cap, 2, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(build(), path)
    print("wrote", path)


if __name__ == "__main__":
    main()
