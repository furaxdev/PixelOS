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
                                          resource-name caveat
overlay/PixelOSSettingsIconOverlay/      RRO reskinning a first slice of Settings' top-level icons (Wi-Fi,
                                          Display, Battery, About phone) — partial coverage by design, see
                                          its own manifest comment before assuming it covers "all of Settings"
overlay/PixelOSDreamDefaultsOverlay/     RRO setting PixelOSAmbient as the default Daydream, active while
                                          docked/charging — see features/ambient and docs/FEATURES.md
features/gestures, ambient, quickpanel,
features/qstiles                         Feature layer (roadmap steps 6 and, for qstiles, 3) — real system
                                          apps, not RROs, see docs/FEATURES.md for what/why/limitations of each
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

Three real pieces now, each chosen because it's achievable without patching `frameworks/base` or
forking the Settings app — and one deliberately **not** attempted because it isn't:

- **Accent color** (`overlay/PixelOSAccentOverlay`) — RRO, values overlay.
- **A themed icon set** (`overlay/PixelOSSettingsIconOverlay`) — RRO, drawable overlay. RROs can
  override drawables the same way they override values, so this is genuinely free once you know the
  resource names — the catch is *knowing the resource names*, which drift more across
  Android versions/forks than the accent-color ones do. Only 4 of Settings' many top-level entries
  are covered as a first slice (see the overlay's own manifest comment); it's real but partial.
- **Custom Quick Settings tiles** (`features/qstiles`, `PixelOSQuickTiles`) — not an overlay at all,
  a real system app using the public `TileService` API (stable since Android 7.0, no Android-9-floor
  constraint the way gesture nav/one-handed mode have). An Always-on-display toggle and a Quick Panel
  trigger. See `docs/FEATURES.md` for what each tile does and doesn't track.
- **Layout changes** — still genuinely not started, and still not achievable via RRO. Overriding a
  drawable or a color by resource name is safe; restructuring a `LinearLayout` into a card-based
  grouping the way OneUI/ColorOS do means the overlay's replacement layout has to match the exact
  view ID hierarchy the compiled Settings app code expects, or it crashes at inflate time rather than
  silently no-op'ing like a stale package-name filter would. That's a real source patch or Settings
  app fork, not a resource-overlay project — unchanged from the earlier assessment.
