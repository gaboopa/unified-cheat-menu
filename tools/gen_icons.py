"""Redraw every DDS under gfx/ as a badge: a coloured shape with glyphs taken from the file name.

    python tools/gen_icons.py [--self-check]

Each file keeps its own pixel size, read from its header. Output is uncompressed 32-bit BGRA. To add an icon, drop any
DDS of the wanted size at the path and run this. No game data is read; other generators' --game-dir is accepted and ignored.
"""
import colorsys
import math
import os
import re
import struct
import sys
import zlib

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Classic 5x7 font: five columns, bit 0 at the top.
FONT = {c: bytes.fromhex(h) for c, h in zip("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", """
3E5149453E 00427F4000 4261514946 2141454B31 1814127F10 2745454539 3C4A494930 0171090503 3649494936 064949291E
7E1111117E 7F49494936 3E41414122 7F4141221C 7F49494941 7F09090901 3E4149497A 7F0808087F 00417F4100 2040413F01
7F08142241 7F40404040 7F020C027F 7F0408107F 3E4141413E 7F09090906 3E4151215E 7F09192946 4649494931 01017F0101
3F4040403F 1F2040201F 3F4038403F 6314081463 0708700807 6151494543""".split())}
GLYPHS = {"on": "ON", "off": "NO"}
# Folder name -> shape. Everything else is a rounded square.
SHAPES = {"traits": "circle", "casus_bellis": "diamond", "men_at_arms_big": "rect"}


def glyphs(stem):
    """`blood_ancester_10` -> B10, `house_guard` -> HG, `lady` -> L."""
    if stem in GLYPHS:
        return GLYPHS[stem]
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", stem.upper()) if p]
    if parts[-1].isdigit() and len(parts) > 1:
        return parts[0][0] + parts[-1]
    return "".join(p[0] for p in parts[:2])


def distance(shape, x, y, hw, hh):
    """Signed distance from the shape's edge at (x, y) relative to the centre; negative is inside."""
    ax, ay = abs(x), abs(y)
    if shape == "circle":
        return math.hypot(x, y) - min(hw, hh)
    if shape == "diamond":
        return (ax + ay - min(hw, hh)) / math.sqrt(2)
    radius = 0 if shape == "rect" else min(hw, hh) / 5
    qx, qy = ax - hw + radius, ay - hh + radius
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - radius


def text_cells(text, w, h):
    """Set of (x, y) pixels covered by the text, centred on a w by h image."""
    cols = len(text) * 6 - 1
    scale = max(1, min(int(w * 0.62 / cols), int(h * 0.5 / 7)))
    left, top = (w - cols * scale) // 2, (h - 7 * scale) // 2
    cells = set()
    for i, ch in enumerate(text):
        for col, bits in enumerate(FONT[ch]):
            for row in range(7):
                if bits >> row & 1:
                    x, y = left + (i * 6 + col) * scale, top + row * scale
                    cells.update((x + a, y + b) for a in range(scale) for b in range(scale))
    return cells


def draw(stem, shape, w, h):
    """BGRA pixels, top row first."""
    hue = zlib.crc32(stem.encode()) % 360 / 360
    fill = [round(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.55, 0.45)]
    border = [round(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.35, 0.9)]
    hw, hh = w / 2 - 1, h / 2 - 1
    thickness = max(1.5, min(w, h) / 24)
    cells = text_cells(glyphs(stem), w, h)
    out = bytearray()
    for y in range(h):
        for x in range(w):
            d = distance(shape, x + 0.5 - w / 2, y + 0.5 - h / 2, hw, hh)
            alpha = max(0, min(1, 0.5 - d))
            r, g, b = (245, 240, 225) if (x, y) in cells else border if d > -thickness else fill
            out += bytes((b, g, r, round(alpha * 255)))
    return bytes(out)


def dds_header(w, h):
    pixel_format = struct.pack("<8I", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    return b"DDS " + struct.pack("<7I", 124, 0x100F, h, w, w * 4, 0, 0) + bytes(44) + pixel_format + struct.pack("<5I", 0x1000, 0, 0, 0, 0)


def regenerate(path):
    with open(path, "rb") as f:
        head = f.read(20)
    if head[:4] != b"DDS ":
        sys.exit(f"{path}: not a DDS file")
    h, w = struct.unpack("<II", head[12:20])
    stem = os.path.splitext(os.path.basename(path))[0]
    shape = SHAPES.get(os.path.basename(os.path.dirname(path)), "square")
    with open(path, "wb") as f:
        f.write(dds_header(w, h) + draw(stem, shape, w, h))


def self_check():
    assert glyphs("blood_ancester_10") == "B10" and glyphs("house_guard") == "HG" and glyphs("on") == "ON"
    assert glyphs("100_stat_man") == "1S" and glyphs("magic_positive.1") == "M1"
    head = dds_header(30, 20)
    assert len(head) == 128 and struct.unpack("<II", head[12:20]) == (20, 30)
    assert struct.unpack("<I", head[76:80])[0] == 32 and struct.unpack("<I", head[88:92])[0] == 32
    for shape in ("circle", "diamond", "square", "rect"):
        px = draw("house_guard", shape, 30, 20)
        assert len(px) == 30 * 20 * 4 and px[10 * 30 * 4 + 15 * 4 + 3] == 255  # centre is opaque
    assert draw("x", "circle", 30, 30)[3] == 0  # corner outside a circle is clear
    print("gen_icons self-check OK")


def main():
    if "--self-check" in sys.argv:
        return self_check()
    n = 0
    for root, _, files in os.walk(os.path.join(MOD_DIR, "gfx")):
        for name in files:
            if name.lower().endswith(".dds"):
                regenerate(os.path.join(root, name))
                n += 1
    print(f"Redrew {n} icons")


if __name__ == "__main__":
    main()
