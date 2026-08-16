# PixelOS brand reference

Source of truth for anything the `/video` skill (or any future PixelOS visual work) needs. Keep
this in sync with `site/index.html` and `vendor/pixelos/tools/gen_assets.py` if the palette moves —
don't let three copies of "the brand colors" drift apart.

## Palette

| Token | Hex | Role |
|---|---|---|
| `--accent` | `#6c4bff` | Primary violet |
| `--accent2` | `#a03bdb` | Magenta |
| `--accent3` | `#12b894` | Teal |
| `--bg` | `#0a0b12` | Near-black ground — PixelOS's brand is dark-first, don't default to a light hero |
| `--fg` | `#f4f5f7` | Light text on dark ground |
| `--muted` | `#9198a6` | Secondary text |

The three-color violet→magenta→teal gradient (in that order, that direction) is the single most
recognizable brand element — it's on the wallpapers, the boot animation, the site hero, the brand
mark. Reuse the *gradient*, not just the three flat colors in isolation, wherever the design calls
for something that reads as "PixelOS" rather than generic tech-purple.

## Brand mark

`vendor/pixelos/assets/brand/mark.svg` — a rounded square (border-radius ~30% of its size) filled
with the violet→magenta→teal gradient at a diagonal angle. This is the "dot" from the site nav and
the shape used for the adaptive icon foreground/background. Treat it as the logo; don't redesign it
per-video, reuse the actual file/gradient definition.

## Assets already on disk (reuse, don't regenerate)

- `vendor/pixelos/assets/wallpapers/shards.png` + `facets.png` — geometric family, flat diagonal-cut
  polygon shards (Android-stock-wallpaper lineage)
- `vendor/pixelos/assets/wallpapers/waves.png` + `dusk.png` — fluid family, translucent wave bands
  and soft glows
- `vendor/pixelos/prebuilt/common/media/bootanimation.zip` — the actual boot animation frames (PNG
  sequence inside the zip), if a video ever wants to show/reference boot
- `site/index.html` — has a hand-built inline SVG phone/tablet mockup (status bar, app icon grid,
  dock) worth referencing for proportions/style if a video needs a device frame, rather than
  reinventing one from scratch

## Voice

Tagline: "A custom Android experience, built as PixelOS." Copy elsewhere on the site is direct,
slightly technical, comfortable saying "not started yet" or "prepared, not verified" rather than
oversell — PixelOS's whole positioning is honesty about what's real vs. planned. A teaser video can
be more purely aspirational/exciting than the docs are (that's normal for a teaser), but shouldn't
claim the OS does something it doesn't yet.
