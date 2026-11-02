# Architecture & decisions

## Why fork LineageOS instead of building AOSP from 0

A "custom Android OS" in the ColorOS/OneUI sense is **not a new operating system kernel-up** — it's a themed,
feature-layered distribution built on top of AOSP. Every major vendor skin (ColorOS, OneUI, MIUI, HyperOS)
works this way: same Linux kernel + AOSP frameworks, different launcher/settings/system-UI/theming/services.

Building straight from raw AOSP means porting every driver/HAL yourself per device — display, GPU, modem,
camera, sensors, Wi-Fi/BT firmware glue. That's what SoC vendors and LineageOS maintainers already do, and
re-doing it alone is not a realistic scope. Forking LineageOS gets you:

- A maintained device tree + vendor blobs for a huge range of devices (including our target, `matissewifi`).
- A kernel already patched for that SoC.
- CVE/security patches merged upstream regularly.
- A working OTA/build system (`repo` + `lunch`/`breakfast`/`brunch`) instead of building one.

What we actually build on top: launcher, system UI theming, settings app customizations, bundled system
apps, an update/OTA branding layer, and CI/tooling around it.

## Two build targets, two purposes

1. **`pixelos_x86_64`** (VirtualBox/QEMU) — this is the *inner dev loop*. UI/theming/app changes are iterated
   here because boot time is seconds, snapshots let you roll back instantly, and there's no bricking risk.
2. **`matissewifi`** (Galaxy Tab 4 SM-T530) — the real target, but slow to iterate on (old, weak hardware,
   physical flashing). Treat it as an integration/validation target you flash periodically, not where you
   debug UI layout.

## Source layout

```
manifests/local_manifests/*.xml   Extra <project> entries repo needs beyond upstream LineageOS manifest
tools/pixelos-cli/                 Thin bash wrapper around repo/breakfast/brunch/fastboot — see its own README
site/                               Static marketing site, deployed via GitHub Pages
.github/workflows/lint.yml          Fast checks on every push/PR (shellcheck, xmllint, html validation)
.github/workflows/build.yml         Manual-dispatch build job, `runs-on: self-hosted` (see README "what needs you")
```

We deliberately do **not** vendor the LineageOS source tree into this repo — it's ~250GB. This repo holds the
manifest, local_manifest overlays, our own patches/overlays, tooling, docs, and site. `repo sync` on your build
machine pulls the actual AOSP/LineageOS source into a separate, gitignored working tree.

## Roadmap (rough)

Status tags: **prepared** = source/tooling exists in this repo, not yet built or booted anywhere (we
have no real build machine attached to this session — see README "what needs you"). **verified** =
someone has actually run it on a real build host and confirmed the result. Nothing is "verified" yet;
don't read "prepared" as "done".

1. ⏳ `pixelos_x86_64` boots stock LineageOS unmodified — proves the manifest/tooling works. Blocks
   every later step's real-world verification; still needs a first real `pixelos sync` + `build`.
2. ✅ **prepared** — **Rebrand pass** (`vendor/pixelos/`, see its own README): `ro.product.*` identity,
   boot animation, and a wallpaper pack (2 geometric — `shards`, `facets` — + 2 fluid — `waves`,
   `dusk`) with `shards` wired as the system default via RRO. Bundling all four into an in-picker
   chooser (rather than just shipping one as the fixed default) needs a wallpaper-picker app —
   tracked as follow-up, not this step.
3. 🟡 **partially prepared** — **Settings / Quick Settings restyle**: only the system accent color
   is overlaid so far (`overlay/PixelOSAccentOverlay`, see `vendor/pixelos/README.md`). Layout changes,
   custom QS tiles, and a themed Settings icon set are unstarted — those need real source patches or
   a Settings app fork, a plain RRO can't do them.
4. ✅ **prepared** — **Launcher** (`vendor/pixelos/launcher/`, see its own README): Lawnchair fork
   pinned via `manifests/local_manifests/lawnchair.xml`, imported as a prebuilt (`android_app_import`,
   since Lawnchair is Gradle-built, not Soong) and set as the sole default Home app. Deeper brand
   theming (accent color, default wallpaper inside the launcher itself) is flagged as follow-up —
   needs the real synced source to confirm which resources are safely overlayable.
5. 🟡 **partially prepared** — **physical device targets**, plural now rather than a single tablet:
   `matissewifi` and `kagura` (Sony Xperia XZ, see `docs/DEVICE_SUPPORT.md`) each have a device tree
   pulled in via local_manifest and a product def (`vendor/pixelos/products/pixelos_<name>.mk`,
   mirroring the x86_64 one) — both flag a `TODO(verify)` on their base makefile filename, and
   `kagura`'s tree is community-maintained and less trustworthy than `matissewifi`'s to begin with
   (see its doc section). Confirms the pattern in `config/common.mk` generalizes: device-specific
   concerns live only in `products/<name>.mk` + the matching local_manifest, nothing in the shared
   rebrand/theming/feature layer changes per device. First successful boot on either still needs a
   real sync+build. Adding another per-device target should mean writing those two files again, not
   touching anything under step 2/3/4/6.
7. 🟡 **partially prepared** — **GSI target** (`pixelos_gsi_arm64`, see `docs/GSI.md`): a different
   answer to "need a build per phone" than step 5 — a system-only image installable on any Project
   Treble-compliant phone (≈2017+) instead of one more per-device tree, via the phh treble project
   (`manifests/local_manifests/gsi_treble.xml`). Deliberately **not** a replacement for step 5:
   `matissewifi`/`kagura` both predate Treble and get nothing from this. Has an open version-
   alignment question more fundamental than the usual per-device `TODO(verify)`s — this repo's whole
   manifest is pinned to Android 9 (`lineage-16.0`), and the right phh-tree branch to match that
   hasn't been confirmed. Read `docs/GSI.md` in full before syncing or flashing this target; it's the
   least proven step on this list, not just unbuilt.
6. ✅ **prepared** — **Feature layer** (`vendor/pixelos/features/`, see `docs/FEATURES.md`): gesture
   navigation, always-on display, and a one-handed quick-actions panel — the three you picked. All
   three are real system apps (not RROs) since our Android 9 base predates the native framework
   support for gesture nav and one-handed mode; `docs/FEATURES.md` explains that constraint and each
   feature's approach/limitations in detail, including the AOD-on-LCD battery caveat for `matissewifi`.
