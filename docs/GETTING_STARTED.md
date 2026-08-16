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

### Under 16GB RAM (e.g. an old ThinkPad)

The build **will** get OOM-killed mid-link on some steps without enough swap as a safety net — this
isn't a maybe. `pixelos doctor` checks RAM+swap against the 16GB floor and tells you what's missing;
if it fails, set up swap first:

```bash
tools/pixelos-cli/pixelos swap-setup 24   # creates+enables a 24GB swapfile at /swapfile-pixelos
```

Also cap parallelism to keep peak memory down (trades build time for headroom — worth it, a slow
build that finishes beats a fast one that gets killed):

```bash
export PIXELOS_JOBS=2   # both `sync` and `build` read this; add it to ~/.bashrc to make it stick
```

None of this makes an old dual-core machine fast — a full build can realistically take 15-30+ hours
on 2014-era hardware vs. 2-4 hours on something modern. Plan on "one build overnight," not rapid
iteration; that's what `pixelos_x86_64` in VirtualBox is for (see step 4).

Have a second old machine lying around? [docs/DISTCC_SETUP.md](DISTCC_SETUP.md) covers offloading
compile jobs to it via distcc — real setup time (~1-2h) for a real speedup, with honest caveats
about when it's not worth it.

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
version) plus our `manifests/local_manifests/`, then `repo sync -c -j${PIXELOS_JOBS:-$(nproc)}`. First run
downloads ~40-70GB compressed; budget several hours on a normal connection.

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
