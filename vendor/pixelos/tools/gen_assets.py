#!/usr/bin/env python3
"""Regenerate PixelOS's wallpaper pack and boot animation from scratch.

Deterministic, no external assets — run this instead of hand-editing the PNGs/zip directly.
Requires Pillow: pip install pillow
"""
import math
import os
import zipfile
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR_ROOT = os.path.dirname(HERE)

# Same palette as site/index.html's --accent / --accent2 / --accent3, plus a dark base matching
# its --bg, used for the wallpaper pack's blob-mesh background.
ACCENT = (0x6c, 0x4b, 0xff)
ACCENT2 = (0xa0, 0x3b, 0xdb)
ACCENT3 = (0x12, 0xb8, 0x94)
DARK_BASE = (0x0a, 0x0b, 0x12)

# Each wallpaper variant is a named list of layers, composited back-to-front, all from one family —
# geometric ("poly"/"stripe", flat diagonal-cut shards à la Android 5.0's stock wallpaper) or fluid
# ("wave"/"glow"), never mixed within a single image. All parameters are hand-placed floats, never
# randomized, so regenerating the pack is always byte-identical (see the gen-assets-check job in
# .github/workflows/lint.yml).
WALLPAPER_VARIANTS = {
    # --- geometric family: flat, opaque, diagonally-cut polygon shards + thin stripe accents ---
    "shards": {
        "base": ACCENT,
        "layers": [
            {"kind": "poly", "color": ACCENT2,
             "points": [(0.0, 0.0), (1.0, 0.0), (1.0, 0.42), (0.0, 0.68)]},
            {"kind": "poly", "color": (0x1a, 0x0f, 0x33),
             "points": [(0.0, 0.68), (1.0, 0.42), (1.0, 0.58), (0.0, 0.88)]},
            {"kind": "poly", "color": ACCENT3,
             "points": [(0.0, 0.88), (1.0, 0.58), (1.0, 1.0), (0.0, 1.0)]},
            {"kind": "stripe", "color": (0xff, 0xff, 0xff), "width": 10,
             "a": (0.0, 0.68), "b": (1.0, 0.42)},
            {"kind": "stripe", "color": (0xff, 0xff, 0xff), "width": 6,
             "a": (0.0, 0.88), "b": (1.0, 0.58)},
        ],
    },
    "facets": {
        "base": (0x1a, 0x0f, 0x33),
        "layers": [
            {"kind": "poly", "color": ACCENT,
             "points": [(0.0, 0.0), (0.62, 0.0), (0.30, 0.45), (0.0, 0.30)]},
            {"kind": "poly", "color": ACCENT2,
             "points": [(0.62, 0.0), (1.0, 0.0), (1.0, 0.55), (0.30, 0.45)]},
            {"kind": "poly", "color": ACCENT3,
             "points": [(0.0, 0.30), (0.30, 0.45), (0.20, 1.0), (0.0, 1.0)]},
            {"kind": "poly", "color": (0xf2, 0xf0, 0xff),
             "points": [(0.30, 0.45), (1.0, 0.55), (1.0, 1.0), (0.20, 1.0)]},
            {"kind": "stripe", "color": (0xff, 0xff, 0xff), "width": 8,
             "a": (0.62, 0.0), "b": (0.30, 0.45)},
            {"kind": "stripe", "color": ACCENT, "width": 8,
             "a": (0.30, 0.45), "b": (0.20, 1.0)},
        ],
    },
    # --- fluid family: flowing translucent wave bands + soft glows, no rings/lines ---
    "waves": {
        "base": DARK_BASE,
        "layers": [
            {"kind": "wave", "y": 0.30, "amp": 70, "wavelength": 700, "phase": 0.0,
             "thickness": 200, "slope": 0.08, "color": ACCENT, "alpha": 120},
            {"kind": "wave", "y": 0.48, "amp": 100, "wavelength": 850, "phase": 1.4,
             "thickness": 240, "slope": -0.06, "color": ACCENT2, "alpha": 120},
            {"kind": "wave", "y": 0.68, "amp": 80, "wavelength": 620, "phase": 2.8,
             "thickness": 220, "slope": 0.05, "color": ACCENT3, "alpha": 130},
        ],
    },
    "dusk": {
        "base": (0x14, 0x0d, 0x22),
        "layers": [
            {"kind": "glow", "x": 0.30, "y": 0.78, "r": 0.42, "color": ACCENT, "alpha": 130},
            {"kind": "glow", "x": 0.80, "y": 0.15, "r": 0.30, "color": ACCENT3, "alpha": 110},
            {"kind": "wave", "y": 0.78, "amp": 60, "wavelength": 1100, "phase": 0.6,
             "thickness": 320, "slope": -0.04, "color": ACCENT2, "alpha": 100},
        ],
    },
}

# Which variant ships as the system default (see overlay/PixelOSWallpaperOverlay).
DEFAULT_VARIANT = "shards"


def _new_layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def _radial_alpha_mask(size, center, radius, max_alpha):
    """Concentric circles drawn outer-to-inner, each overwriting with higher alpha — a soft
    center-to-edge falloff rather than a hard-edged disc."""
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    cx, cy = center
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        alpha = int(max_alpha * (1 - t) ** 1.6)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    return mask.filter(ImageFilter.GaussianBlur(radius=max(2, radius * 0.06)))


def _render_glow(size, spec):
    max_dim = max(size)
    center = (size[0] * spec["x"], size[1] * spec["y"])
    radius = spec["r"] * max_dim
    mask = _radial_alpha_mask(size, center, radius, spec["alpha"])
    layer = Image.new("RGBA", size, spec["color"] + (0,))
    layer.putalpha(mask)
    return layer


def _render_poly(size, spec):
    """A flat, fully-opaque polygon shard — fraction coordinates, sharp edges (no blur), the way
    the classic Android stock wallpaper's diagonal paper-cut shapes work."""
    layer = _new_layer(size)
    d = ImageDraw.Draw(layer)
    w, h = size
    points = [(x * w, y * h) for x, y in spec["points"]]
    d.polygon(points, fill=spec["color"] + (255,))
    return layer


def _render_stripe(size, spec):
    """A thin, crisp diagonal accent line along a shard boundary — the highlight edge in the
    reference image, not a soft glow line."""
    layer = _new_layer(size)
    d = ImageDraw.Draw(layer)
    w, h = size
    ax, ay = spec["a"][0] * w, spec["a"][1] * h
    bx, by = spec["b"][0] * w, spec["b"][1] * h
    d.line([(ax, ay), (bx, by)], fill=spec["color"] + (255,), width=spec["width"])
    return layer


def _render_wave(size, spec):
    """A flowing translucent band: a sine-curved top edge, a parallel bottom edge offset by
    `thickness`, filled — the fluid/organic element."""
    layer = _new_layer(size)
    d = ImageDraw.Draw(layer)
    w, h = size
    y0, amp, wl, phase, thick, slope = (
        spec["y"] * h, spec["amp"], spec["wavelength"], spec["phase"], spec["thickness"], spec["slope"],
    )
    step = 6
    top = []
    for x in range(0, w + step, step):
        y = y0 + slope * x + amp * math.sin(2 * math.pi * x / wl + phase)
        top.append((x, y))
    bottom = []
    for x in range(w, -step, -step):
        y = y0 + thick + slope * x + amp * math.sin(2 * math.pi * x / wl + phase)
        bottom.append((x, y))
    d.polygon(top + bottom, fill=spec["color"] + (spec["alpha"],))
    return layer.filter(ImageFilter.GaussianBlur(radius=18))


_RENDERERS = {"glow": _render_glow, "poly": _render_poly, "wave": _render_wave, "stripe": _render_stripe}


def render_wallpaper(size, variant):
    img = Image.new("RGBA", size, variant["base"] + (255,))
    for spec in variant["layers"]:
        layer = _RENDERERS[spec["kind"]](size, spec)
        img = Image.alpha_composite(img, layer)
    return img.convert("RGB")


def make_wallpaper_pack(out_dir, size=(1440, 2560)):
    paths = {}
    for name, variant in WALLPAPER_VARIANTS.items():
        img = render_wallpaper(size, variant)
        path = os.path.join(out_dir, f"{name}.png")
        img.save(path, "PNG", optimize=True)
        paths[name] = path
        print(f"wrote {path} ({size[0]}x{size[1]})")
    return paths


def rounded_square_mark(size, fill="white"):
    """The little rounded-square brand dot from the site nav — used only in the boot animation,
    deliberately not on the wallpapers (kept those clean/abstract, no centered logo)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.28
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=fill)
    return img


def diagonal_gradient(size, angle_offset=0.0):
    """Cheap gradient used only for the low-res boot animation frames (blob-mesh rendering is
    too slow per-frame at 30fps-worth of images; the wallpapers above use render_wallpaper)."""
    stops = [ACCENT, ACCENT2, ACCENT3]

    def lerp(a, b, t):
        return a + (b - a) * t

    def gradient_color(t):
        n = len(stops) - 1
        seg = min(int(t * n), n - 1)
        local_t = (t * n) - seg
        a, b = stops[seg], stops[seg + 1]
        return tuple(int(lerp(a[i], b[i], local_t)) for i in range(3))

    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    diag = w + h
    for y in range(h):
        for x in range(w):
            t = ((x + y) / diag + angle_offset) % 1.0
            px[x, y] = gradient_color(t)
    return img


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
    import shutil

    pack_dir = os.path.join(VENDOR_ROOT, "assets", "wallpapers")
    os.makedirs(pack_dir, exist_ok=True)
    pack_paths = make_wallpaper_pack(pack_dir)

    default_wallpaper_out = os.path.join(
        VENDOR_ROOT, "overlay", "PixelOSWallpaperOverlay", "res", "drawable-nodpi", "default_wallpaper.png"
    )
    shutil.copyfile(pack_paths[DEFAULT_VARIANT], default_wallpaper_out)
    print(f"wrote {default_wallpaper_out} (copy of '{DEFAULT_VARIANT}', the system default)")

    bootanim_out = os.path.join(VENDOR_ROOT, "prebuilt", "common", "media", "bootanimation.zip")
    make_bootanimation(bootanim_out)
