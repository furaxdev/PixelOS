# vendor/pixelos

The branding/rebrand layer, built on top of the LineageOS source tree pulled in by `pixelos sync`.
This directory lives in *this* repo (not a separate `repo`-managed project) and gets symlinked into
the synced source tree as `vendor/pixelos` by `tools/pixelos-cli/pixelos device` — see that script.

```
config/common.mk                        Shared PixelOS identity (ro.product.*, version, included packages)
products/AndroidProducts.mk              Registers our product makefiles with the build system
products/pixelos_x86_64.mk               Product def: inherits lineage_x86_64 + config/common.mk
products/pixelos_matissewifi.mk          Product def: inherits the matissewifi device tree + config/common.mk
overlay/PixelOSWallpaperOverlay/         RRO replacing the system default wallpaper with assets/wallpapers/shards.png
overlay/PixelOSAccentOverlay/            RRO retinting Settings/Quick Settings' accent color — see its own
                                          resource-name caveat, the rest of Settings/QS restyling is unstarted
overlay/PixelOSDreamDefaultsOverlay/     RRO setting PixelOSAmbient as the default Daydream, active while
                                          docked/charging — see features/ambient and docs/FEATURES.md
features/gestures, ambient, quickpanel   Feature layer (roadmap step 6) — real system apps, not RROs,
                                          see docs/FEATURES.md for what/why/limitations of each
permissions/                             privapp-permissions allowlist required for the feature apps' special
                                          permissions (SYSTEM_ALERT_WINDOW, CAMERA) since Android O
prebuilt/common/media/bootanimation.zip  Boot animation (generated, see tools/gen_assets.py)
assets/wallpapers/                       Wallpaper pack — 2 geometric (shards, facets) + 2 fluid (waves, dusk)
                                          variants, source-only beyond the one wired as system default; bundling
                                          the rest into an in-picker chooser needs a wallpaper-picker app, future work
assets/brand/                            Brand mark (adaptive icon source) for the launcher — not wired into
                                          Lawnchair yet, see vendor/pixelos/launcher/README.md's follow-up note
tools/gen_assets.py                      Regenerates the wallpaper pack + bootanimation.zip from scratch
```

## Regenerating assets

```bash
python3 vendor/pixelos/tools/gen_assets.py
```

Requires Pillow (`pip install pillow`). Deterministic given the same script — re-run and commit the
output whenever the brand palette changes (keep it in sync with `site/index.html`'s CSS variables).

## What "rebrand" means at this stage

This is step 2 of the roadmap in `docs/ARCHITECTURE.md`: product identity strings, boot animation,
default wallpaper, and a brand mark ready for later use.

## Settings / Quick Settings (roadmap step 3)

Only the system accent color is touched so far (`overlay/PixelOSAccentOverlay`) — that's the smallest
real slice of "restyle Settings/QS" that a plain RRO can do without patching `frameworks/base` or the
Settings app itself. Layout changes, custom Quick Settings tiles, or a themed Settings icon set are
not started; they'd need actual source patches or a Settings app fork, not just a resource overlay.
