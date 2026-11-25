#!/usr/bin/env python3
"""News image entry: front page of THE WORLD for Wednesday 25 November 2026.

Draws a 1024x1024 newspaper front page with pure stdlib Python: a hand-built
5x7 bitmap font, pixel-art illustrations, and a hand-rolled PNG encoder
(zlib + struct). No third-party packages, no network, deterministic output.
"""
import os
import struct
import sys
import zlib

# The grader runs with `python3 -P -s`: never rely on cwd being on sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 244, 230)
INK = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
SEA = (46, 110, 158)
SKY = (176, 214, 235)
GREY = (120, 116, 108)
LIGHT = (238, 232, 218)
GOLD = (201, 162, 39)
GREEN = (46, 125, 70)

# ---------------------------------------------------------------- PNG encoder
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode_png(rgb, w, h):
    """rgb: bytes-like, w*h*3. Returns complete PNG bytes (filter 0 rows)."""
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=2):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for yy in range(cy - rr, cy + rr + 1):
                dx = int((rr * rr - (yy - cy) ** 2) ** 0.5)
                self.set(cx - dx, yy, c)
                self.set(cx + dx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        """Filled triangle, scanline fill."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            def edge(px, py, qx, qy):
                if py == qy:
                    return px
                return px + (qx - px) * (y - py) / (qy - py)
            xs = []
            if ay <= y <= by:
                xs.append(edge(ax, ay, bx, by))
            if by <= y <= cy:
                xs.append(edge(bx, by, cx, cy))
            if ay <= y <= cy:
                xs.append(edge(ax, ay, cx, cy))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, y, xb - xa + 1, 1, c)


# ---------------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 cells, '#' = ink. Text is drawn upper-cased.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", "     ", " ##  ", "  #  "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "  #  "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "(": ("   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"),
    ")": ("##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ### ", "#   #", "#   #", " # # ", "# #  ", "#  # ", " ## #"),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    "|": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "*": ("     ", " # # ", "  #  ", "#####", "  #  ", " # # ", "     "),
}


def text_width(text, scale):
    return sum((6 if ch != " " else 6) for ch in text.upper()) * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw upper-cased text; returns width drawn."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT["?"])
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    cv.rect(cx + gx * scale, y + gy * scale, scale, scale, color)
        cx += 6 * scale
    return cx - x - scale


def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, text, scale, color, max_chars, leading=None):
    """Wrapped text block; returns y just below the last line."""
    lead = leading if leading is not None else 9 * scale
    for line in wrap(text, max_chars):
        draw_text(cv, x, y, line, scale, color)
        y += lead
    return y


# ---------------------------------------------------------------- illustrations
def draw_ship_scene(cv, x, y, w, h):
    """Gulf of Finland: cargo ship on the sea, drone overhead, smoke."""
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + w - 110, y + 58, 34, (255, 214, 90))
    cv.disc(x + w - 110, y + 58, 26, (255, 226, 130))
    # distant clouds
    for cx, cy, cw in ((x + 60, y + 40, 120), (x + 300, y + 26, 150), (x + 620, y + 48, 110)):
        cv.rect(cx, cy, cw, 14, (240, 246, 250))
        cv.rect(cx + 18, cy - 10, cw - 50, 12, (240, 246, 250))
    sea_y = y + h - 70
    cv.rect(x, sea_y, w, 70, SEA)
    cv.rect(x, sea_y, w, 6, (120, 180, 210))
    # cargo ship
    sx, sy = x + 190, sea_y - 6
    cv.rect(sx, sy - 66, 420, 14, (60, 60, 64))          # deck
    for i, cc in enumerate((RED, BLUE, GOLD, GREEN)):
        cv.rect(sx + 30 + i * 96, sy - 118, 84, 52, cc)   # containers
        cv.frame(sx + 30 + i * 96, sy - 118, 84, 52, INK, 2)
    cv.rect(sx + 420, sy - 96, 46, 30, (240, 240, 235))   # bridge
    cv.rect(sx + 430, sy - 88, 26, 14, BLUE)
    cv.rect(sx + 470, sy - 96, 18, 30, INK)              # funnel
    cv.rect(sx + 470, sy - 96, 18, 10, RED)
    # hull: trapezoid via rows
    for r in range(64):
        ww = 560 - int(r * 1.6)
        cv.rect(sx - 30 + (560 - ww) // 2, sy + r, ww, 1, (24, 24, 28))
    cv.rect(sx - 30, sy + 8, 560, 8, RED)                # waterline stripe
    # smoke puffs trailing right from the funnel, inside the frame
    for px, py, pr in ((sx + 500, sy - 100, 11), (sx + 532, sy - 108, 14),
                       (sx + 566, sy - 102, 16), (sx + 598, sy - 94, 12)):
        cv.disc(px, py, pr, (200, 200, 196))
        cv.disc(px, py, pr - 5, (225, 225, 220))
    # drone above the ship
    dx, dy = x + 700, y + 92
    cv.rect(dx - 26, dy - 8, 52, 14, INK)
    cv.rect(dx - 8, dy + 6, 16, 10, (90, 90, 90))
    for ox in (-34, 34):
        cv.rect(dx + ox - 12, dy - 14, 24, 4, INK)
    cv.disc(dx - 34, dy - 12, 4, (90, 90, 90))
    cv.disc(dx + 34, dy - 12, 4, (90, 90, 90))
    # dashed flight path from drone down to the ship
    for i in range(6):
        cv.rect(dx - 40 + i * 26, dy + 34 + i * 12, 14, 4, RED)
    # waves
    for wy in (sea_y + 18, sea_y + 36, sea_y + 54):
        for wx in range(x + 20, x + w - 40, 90):
            cv.rect(wx, wy, 54, 5, (200, 228, 240))
            cv.rect(wx + 12, wy + 7, 30, 4, (200, 228, 240))
    cv.frame(x, y, w, h, INK, 3)


def draw_tower(cv, x, y, s):
    """Riyadh's tallest tower, struck at the crown."""
    cv.rect(x + 34 * s, y + 30 * s, 12 * s, 60 * s, BLUE)
    cv.rect(x + 30 * s, y + 26 * s, 20 * s, 8 * s, BLUE)
    cv.rect(x + 24 * s, y + 34 * s, 32 * s, 8 * s, (90, 130, 180))
    cv.rect(x + 20 * s, y + 42 * s, 40 * s, 48 * s, (120, 160, 200))
    for r in range(6):
        cv.rect(x + (22 + r) * s, y + (46 + r * 7) * s, (36 - 2 * r) * s, 3 * s, INK)
    cv.vline(x + 40 * s, y + 6 * s, 24 * s, INK, 2 * s)
    cv.disc(x + 40 * s, y + 5 * s, 3 * s, RED)
    # impact burst at the crown
    for dx, dy in ((-16, -8), (16, -10), (-20, 4), (20, 2), (0, -16), (-8, 10), (10, 12)):
        cv.rect(x + (40 + dx) * s - 2 * s, y + (14 + dy) * s, 4 * s, 2 * s, RED)
    cv.disc(x + 40 * s, y + 14 * s, 5 * s, (255, 200, 60))


def draw_medal(cv, x, y, s):
    """Medal of Freedom: ribbon and gold disc with a star."""
    cv.triangle(x + 18 * s, y + 6 * s, x + 34 * s, y + 6 * s, x + 26 * s, y + 44 * s, RED)
    cv.triangle(x + 46 * s, y + 6 * s, x + 62 * s, y + 6 * s, x + 54 * s, y + 44 * s, BLUE)
    cv.disc(x + 40 * s, y + 62 * s, 26 * s, GOLD)
    cv.ring(x + 40 * s, y + 62 * s, 26 * s, (150, 115, 20), 2 * s)
    cv.ring(x + 40 * s, y + 62 * s, 19 * s, (150, 115, 20), 1 * s)
    # five-point star, drawn as small rects
    cv.rect(x + 38 * s, y + 44 * s, 4 * s, 36 * s, (120, 88, 10))
    cv.rect(x + 24 * s, y + 56 * s, 32 * s, 4 * s, (120, 88, 10))
    cv.rect(x + 27 * s, y + 68 * s, 26 * s, 4 * s, (120, 88, 10))
    cv.rect(x + 28 * s, y + 50 * s, 24 * s, 4 * s, (120, 88, 10))


def draw_court(cv, x, y, s):
    """Courthouse: pediment, columns, steps."""
    cv.triangle(x + 6 * s, y + 26 * s, x + 74 * s, y + 26 * s, x + 40 * s, y + 6 * s, (200, 190, 170))
    cv.frame(x + 6 * s, y + 6 * s, 68 * s, 20 * s, INK, 1)
    cv.rect(x + 8 * s, y + 26 * s, 64 * s, 4 * s, INK)
    for i in range(4):
        cv.rect(x + (12 + i * 17) * s, y + 30 * s, 8 * s, 40 * s, (220, 212, 196))
        cv.frame(x + (12 + i * 17) * s, y + 30 * s, 8 * s, 40 * s, INK, 1)
    cv.rect(x + 4 * s, y + 70 * s, 72 * s, 5 * s, (200, 190, 170))
    cv.rect(x, y + 76 * s, 80 * s, 5 * s, (180, 170, 150))
    cv.disc(x + 40 * s, y + 16 * s, 4 * s, INK)


def draw_quake(cv, x, y, s):
    """Himalayan peaks with a shaking crack."""
    cv.triangle(x + 2 * s, y + 78 * s, x + 34 * s, y + 78 * s, x + 20 * s, y + 22 * s, (110, 120, 140))
    cv.triangle(x + 30 * s, y + 78 * s, x + 78 * s, y + 78 * s, x + 56 * s, y + 10 * s, (70, 84, 110))
    cv.triangle(x + 50 * s, y + 26 * s, x + 62 * s, y + 26 * s, x + 56 * s, y + 10 * s, (245, 245, 240))
    cv.triangle(x + 15 * s, y + 34 * s, x + 25 * s, y + 34 * s, x + 20 * s, y + 22 * s, (245, 245, 240))
    cv.rect(x + 2 * s, y + 78 * s, 76 * s, 4 * s, INK)
    # crack zigzag across the ground
    pts = [(x + 4 * s, y + 84 * s), (x + 16 * s, y + 80 * s), (x + 28 * s, y + 86 * s),
           (x + 42 * s, y + 80 * s), (x + 56 * s, y + 86 * s), (x + 70 * s, y + 80 * s)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        steps = max(abs(bx - ax), abs(by - ay))
        for i in range(steps + 1):
            cv.set(ax + (bx - ax) * i // steps, ay + (by - ay) * i // steps, RED)
            cv.set(ax + (bx - ax) * i // steps, ay + (by - ay) * i // steps + 1, RED)
    # shock waves
    for r in (10, 16, 22):
        cv.ring(x + 40 * s, y + 40 * s, r * s // 2, RED, 1)


# ---------------------------------------------------------------- layout
def center_text(cv, y, text, scale, color):
    w = text_width(text, scale)
    draw_text(cv, (W - w) // 2, y, text, scale, color)


def sub_story(cv, x, y, w, h, icon, headline, body):
    cv.frame(x, y, w, h, INK, 2)
    cv.rect(x + 2, y + 2, w - 4, 26, LIGHT)
    draw_text(cv, x + 10, y + 8, headline, 2, RED)
    icon(cv, x + 14, y + 40, 1)
    tx = x + 118
    tw = w - 132
    draw_block(cv, tx, y + 44, body, 1, INK, max(8, tw // 6), leading=11)


def build():
    cv = Canvas(W, H, PAPER)
    cv.frame(6, 6, W - 12, H - 12, INK, 4)
    cv.frame(16, 16, W - 32, H - 32, INK, 2)

    # masthead
    center_text(cv, 34, "THE WORLD", 9, INK)
    cv.hline(60, 118, W - 120, INK, 3)
    center_text(cv, 130, "WEDNESDAY 25 NOVEMBER 2026", 3, RED)
    center_text(cv, 158, "ONE DAY IN PICTURES  *  THE WORLD IN BRIEF", 1, GREY)
    cv.hline(60, 182, W - 120, INK, 2)

    # main headline
    center_text(cv, 198, "UKRAINE CONFIRMS", 5, INK)
    center_text(cv, 243, "DRONE HIT ON", 5, INK)
    center_text(cv, 288, "RUSSIAN SHIP", 5, INK)
    cv.hline(60, 340, W - 120, RED, 3)

    # deck
    y = 356
    y = draw_block(cv, 90, y,
                   "ZELENSKIY SAYS KYIV STRUCK A RUSSIAN CARGO SHIP IN THE "
                   "GULF OF FINLAND. NORWAY, A FIRM ALLY, URGES CAUTION.",
                   2, INK, 70, leading=20)

    # main picture: the ship in the Gulf of Finland
    draw_ship_scene(cv, 60, 420, W - 120, 210)
    center_text(cv, 640, "A DRONE STRIKE AT SEA: THE GULF OF FINLAND, 25 NOVEMBER 2026", 1, GREY)

    # four more stories of the day
    gy, gh, gw = 668, 138, 452
    sub_story(cv, 40, gy, gw, gh, draw_tower,
              "RIYADH TOWER HIT",
              "Houthi strike hits Riyadh's tallest tower. 11 wounded, Saudi "
              "civil defence says. Coalition calls it a terrorist attack.")
    sub_story(cv, 532, gy, gw, gh, draw_medal,
              "MEDAL FOR GIULIANI",
              "Trump awards the Medal of Freedom to Rudy Giuliani at the "
              "White House, honouring the former New York mayor.")
    sub_story(cv, 40, gy + 158, gw, gh, draw_court,
              "HUAWEI CONVICTED",
              "US jury convicts Huawei of trade-secret theft and bank fraud "
              "over its Iran business. It escapes a racketeering charge.")
    sub_story(cv, 532, gy + 158, gw, gh, draw_quake,
              "QUAKE SHAKES NEPAL",
              "Magnitude 5.6 earthquake hits Nepal near the Chinese border. "
              "Tremors felt across eastern India. No major damage reported.")

    # footer
    cv.hline(60, 962, W - 120, INK, 2)
    center_text(cv, 976,
                "SOURCES: REUTERS - AP - THE TIMES OF INDIA  |  ALL STORIES LEADING THE NEWS ON 25 NOVEMBER 2026",
                1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get("ENTRY_OUT") or "/output"
    entry_out = os.environ.get("ENTRY_OUT")
    if entry_out and os.path.isdir(entry_out):
        out_dir = entry_out
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build().px, W, H)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
