# vendor/pixelos

The branding/rebrand layer, built on top of the LineageOS source tree pulled in by `pixelos sync`.
This directory lives in *this* repo (not a separate `repo`-managed project) and gets symlinked into
the synced source tree as `vendor/pixelos` by `tools/pixelos-cli/pixelos device` — see that script.

```
config/common.mk                        Shared PixelOS identity (ro.product.*, version, included packages)
products/AndroidProducts.mk              Registers our product makefiles with the build system
products/pixelos_x86_64.mk               Product def: inherits lineage_x86_64 + config/common.mk
overlay/PixelOSWallpaperOverlay/         Runtime Resource Overlay replacing the system default wallpaper
prebuilt/common/media/bootanimation.zip  Boot animation (generated, see tools/gen_assets.py)
assets/brand/                            Brand mark (adaptive icon source) for the future launcher — not
                                          wired into any package yet, that lands with the launcher itself
tools/gen_assets.py                      Regenerates the wallpaper PNG + bootanimation.zip from scratch
```

## Regenerating assets

```bash
python3 vendor/pixelos/tools/gen_assets.py
```

Requires Pillow (`pip install pillow`). Deterministic given the same script — re-run and commit the
output whenever the brand palette changes (keep it in sync with `site/index.html`'s CSS variables).

## What "rebrand" means at this stage

This is step 2 of the roadmap in `docs/ARCHITECTURE.md`: product identity strings, boot animation,
default wallpaper, and a brand mark ready for later use. It does **not** yet touch Settings, Quick
Settings, or ship a launcher — those are separate roadmap steps, deliberately not bundled in here.
