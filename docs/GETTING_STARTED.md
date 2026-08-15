# Getting started

## 1. Build host

You need a real Linux machine (or VM with plenty of resources) — this **cannot** run inside this sandboxed
session or on GitHub-hosted Actions runners. Minimum, per LineageOS docs:

- Ubuntu 22.04/24.04 (or similar) x86_64
- 250GB+ free disk (SSD strongly recommended)
- 16GB+ RAM (32GB recommended, builds use `-j<cores>`)
- A few hours for the first `repo sync` + build

Check your machine:

```bash
tools/pixelos-cli/pixelos doctor
```

## 2. Install prerequisites + repo tool

```bash
tools/pixelos-cli/pixelos init
```

This installs the `repo` tool, checks/installs OpenJDK, git, and the LineageOS build-dependency package list,
and sets a git identity if you don't have one configured (needed by `repo`).

## 3. Sync source

```bash
tools/pixelos-cli/pixelos sync
```

Runs `repo init` against the LineageOS manifest (branch `lineage-16.0`, matching our oldest target's supported
version) plus our `manifests/local_manifests/`, then `repo sync -c -j$(nproc)`. First run downloads ~40-70GB
compressed; budget several hours on a normal connection.

## 4. Pick a target

**Emulator/VirtualBox (fast inner loop, do this first):**

```bash
tools/pixelos-cli/pixelos device pixelos_x86_64
tools/pixelos-cli/pixelos build pixelos_x86_64 eng
```

Produces a bootable `.iso`/disk image under `out/target/product/pixelos_x86_64/` — import it into VirtualBox
as an EFI-enabled VM (2 vCPU / 4GB RAM minimum) or run with QEMU directly.

**Galaxy Tab 4 SM-T530 (`matissewifi`):**

```bash
tools/pixelos-cli/pixelos device matissewifi
tools/pixelos-cli/pixelos build matissewifi userdebug
```

Pulls in the community device/vendor trees declared in
`manifests/local_manifests/matissewifi.xml`. Flashing a physical device is destructive if done wrong —
read `docs/DEVICE_SUPPORT.md` fully before touching a real tablet, back up first, and expect to need Odin
(Windows/Wine) for the initial bootloader/recovery step since Samsung locks that down outside `fastboot`.

## 5. Sign your builds (optional but recommended before flashing anything real)

```bash
tools/pixelos-cli/pixelos keys
```

Generates a release keystore under `~/.pixelos-keys/` (never committed — it's in `.gitignore`). Point
`build/target/product/security` at it per the LineageOS signing docs before building `user`/`userdebug`
release candidates.
