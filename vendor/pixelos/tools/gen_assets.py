#!/usr/bin/env python3
"""Regenerate PixelOS's default wallpaper and boot animation from scratch.

Deterministic, no external assets — run this instead of hand-editing the PNGs/zip directly.
Requires Pillow: pip install pillow
"""
import math
import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR_ROOT = os.path.dirname(HERE)

# Same palette as site/index.html's --accent / --accent2 / --accent3
BRAND_STOPS = [(0x6c, 0x4b, 0xff), (0xa0, 0x3b, 0xdb), (0x12, 0xb8, 0x94)]


def lerp(a, b, t):
    return a + (b - a) * t


def gradient_color(t, stops=BRAND_STOPS):
    """t in [0,1] across the stop list."""
    n = len(stops) - 1
    seg = min(int(t * n), n - 1)
    local_t = (t * n) - seg
    a, b = stops[seg], stops[seg + 1]
    return tuple(int(lerp(a[i], b[i], local_t)) for i in range(3))


def diagonal_gradient(size, angle_offset=0.0):
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    diag = w + h
    for y in range(h):
        for x in range(w):
            t = ((x + y) / diag + angle_offset) % 1.0
            px[x, y] = gradient_color(t)
    return img


def rounded_square_mark(size, fill="white"):
    """The little rounded-square brand dot from the site nav, as a standalone mark."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.28
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=fill)
    return img


def make_wallpaper(path, size=(1440, 2560)):
    img = diagonal_gradient(size)

    # soft radial highlight for depth, matching the site hero's glow treatment
    highlight_mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(highlight_mask)
    cx, cy = size[0] * 0.28, size[1] * 0.22
    max_r = math.hypot(size[0], size[1]) * 0.75
    steps = 80
    for i in range(steps, 0, -1):
        t = i / steps
        r = max_r * t
        alpha = int(70 * (1 - t))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    white = Image.new("RGB", size, (255, 255, 255))
    img = Image.composite(white, img, highlight_mask)

    mark = rounded_square_mark(size[0] // 6)
    img = img.convert("RGBA")
    img.alpha_composite(mark, (size[0] // 2 - mark.width // 2, int(size[1] * 0.42)))
    img.convert("RGB").save(path, "PNG", optimize=True)
    print(f"wrote {path} ({size[0]}x{size[1]})")


def _frame(size, t, pulse=0.0):
    """One boot animation frame: gradient background + fading/pulsing brand mark."""
    img = diagonal_gradient(size, angle_offset=t * 0.15)
    mark_size = int(size[1] * (0.16 + 0.02 * pulse))
    mark = rounded_square_mark(mark_size, fill=(255, 255, 255, int(255 * min(1.0, t * 2 + 0.3))))
    img = img.convert("RGBA")
    img.alpha_composite(mark, (size[0] // 2 - mark.width // 2, size[1] // 2 - mark.height // 2))
    return img.convert("RGB")


def make_bootanimation(path, size=(240, 320), intro_frames=14, loop_frames=24):
    part0_dir = os.path.join(HERE, "_build", "part0")
    part1_dir = os.path.join(HERE, "_build", "part1")
    os.makedirs(part0_dir, exist_ok=True)
    os.makedirs(part1_dir, exist_ok=True)

    # part0: fade/scale the mark in, plays once
    for i in range(intro_frames):
        t = i / (intro_frames - 1)
        frame = _frame(size, t)
        frame.save(os.path.join(part0_dir, f"{i:05d}.png"))

    # part1: gentle pulse + slow background drift, loops forever
    for i in range(loop_frames):
        t = i / loop_frames
        pulse = math.sin(t * 2 * math.pi)
        frame = _frame(size, 1.0, pulse=pulse)
        frame.save(os.path.join(part1_dir, f"{i:05d}.png"))

    desc = f"{size[0]} {size[1]} 30\np 1 0 part0\np 0 0 part1\n"
    with open(os.path.join(HERE, "_build", "desc.txt"), "w") as f:
        f.write(desc)

    # Fixed timestamp on every entry: zf.write() would otherwise embed each source file's mtime,
    # making the zip non-reproducible byte-for-byte between runs (breaks CI's regenerate-and-diff check).
    fixed_time = (2026, 1, 1, 0, 0, 0)

    def _write_deterministic(zf, src_path, arcname):
        with open(src_path, "rb") as f:
            data = f.read()
        info = zipfile.ZipInfo(arcname, date_time=fixed_time)
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = 0o644 << 16
        zf.writestr(info, data)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as zf:
        _write_deterministic(zf, os.path.join(HERE, "_build", "desc.txt"), "desc.txt")
        for name in sorted(os.listdir(part0_dir)):
            _write_deterministic(zf, os.path.join(part0_dir, name), f"part0/{name}")
        for name in sorted(os.listdir(part1_dir)):
            _write_deterministic(zf, os.path.join(part1_dir, name), f"part1/{name}")

    print(f"wrote {path} ({intro_frames} intro + {loop_frames} loop frames @ {size[0]}x{size[1]})")


if __name__ == "__main__":
    wallpaper_out = os.path.join(
        VENDOR_ROOT, "overlay", "PixelOSWallpaperOverlay", "res", "drawable-nodpi", "default_wallpaper.png"
    )
    bootanim_out = os.path.join(VENDOR_ROOT, "prebuilt", "common", "media", "bootanimation.zip")
    make_wallpaper(wallpaper_out)
    make_bootanimation(bootanim_out)
