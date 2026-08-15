# PixelOS

> Custom Android distribution based on LineageOS — a ColorOS/OneUI-style skin on top of an AOSP fork.

⚠️ **Naming note:** this repository is currently named `PixOS` on GitHub (typo for `PixelOS`). Rename it in
`Settings → General → Repository name` — GitHub auto-redirects the old URL, so no links break. Everything
below assumes the final name `PixelOS`.

## What this is

PixelOS is a custom Android ROM: a themed, feature-layered fork of **LineageOS**, not a from-scratch AOSP
build. Building AOSP from zero (kernel, HAL, drivers per device) is a multi-year, multi-person effort — forking
an already-maintained base and building the "skin" (launcher, settings, system apps, theming, OTA) on top of
it is the realistic path for a small team. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the reasoning.

## Targets

| Target | Codename | Base | Status |
|---|---|---|---|
| Samsung Galaxy Tab 4 10.1 (SM-T530) | `matissewifi` | LineageOS 16.0 (Android 9) — last version with a maintained device tree for this SoC (msm8226, 1.5GB RAM) | Planned |
| Generic x86_64 (VirtualBox / QEMU) | `pixelos_x86_64` | LineageOS's own `lineage_x86_64` target | Planned — primary dev/test loop |

The tablet is 2014-era hardware (Snapdragon 400, 1.5GB RAM) — treat modern-Android-skin ambitions (fluid
animations, heavy theming engine) as a stretch goal there. The x86_64 VirtualBox target is where you'll do
almost all day-to-day development and UI iteration, because build-test-flash cycles on real hardware are slow
and risky (bricking).

## Repository layout

```
manifests/           LineageOS repo manifest + local_manifests (device/vendor trees to pull in)
vendor/pixelos/       Rebrand layer: product identity, boot animation, wallpaper RRO, brand mark,
                       and the Lawnchair-based launcher (see vendor/pixelos/launcher/README.md)
tools/pixelos-cli/    `pixelos` CLI — wraps repo sync / breakfast / brunch / flashing workflows
site/                 Static landing page (GitHub Pages)
docs/                 Architecture, getting started, device support notes
.github/workflows/    CI: lint/validate on every push, manual/self-hosted build workflow
```

## Quick start

```bash
tools/pixelos-cli/pixelos doctor      # checks your build host has what AOSP/LineageOS builds need
tools/pixelos-cli/pixelos init        # installs repo tool, sets up git identity, ccache
tools/pixelos-cli/pixelos sync        # repo sync (needs ~250GB free disk, several hours first time)
tools/pixelos-cli/pixelos device matissewifi
tools/pixelos-cli/pixelos build matissewifi userdebug
```

Full walkthrough: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

## What needs you (accounts/logins I can't act on for you)

- **Rename the repo** — Settings → General (see note above).
- **Enable GitHub Pages** — Settings → Pages → Source: "GitHub Actions" (the `pages.yml` workflow will then
  deploy `site/` automatically on push to your default branch).
- **A real build machine** — AOSP/LineageOS builds need ~250GB disk, 16GB+ RAM, several build-hours. GitHub's
  hosted Actions runners (14GB disk) cannot do this. Options: your own Linux box, a rented bare-metal/VPS with
  enough disk, or a self-hosted GitHub Actions runner you register yourself (Settings → Actions → Runners →
  "New self-hosted runner") — `build.yml` targets `runs-on: [self-hosted, pixelos-builder]` for this reason.
- **Signing keys** — generate your own release keystore locally (`tools/pixelos-cli/pixelos keys`); never
  commit it. Store it as a GitHub Actions secret if you want CI to sign builds.
- **Samsung/Odin USB drivers + bootloader unlock** on the physical tablet — device-side, can't be scripted.
- **A JDK + Android SDK/Gradle toolchain** to build the launcher — Lawnchair is a Gradle project, separate
  from the AOSP build's own prebuilt toolchain (`tools/pixelos-cli/pixelos launcher-build` assumes this is
  already set up; see `vendor/pixelos/launcher/README.md`).

## License

Apache 2.0 (matches AOSP/LineageOS licensing) — see [LICENSE](LICENSE).
