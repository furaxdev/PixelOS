# GSI — one image, many phones (with real limits)

This is a different kind of build target from `matissewifi`/`kagura`, and it comes with sharper
edges than either. Read this before syncing or flashing `pixelos_gsi_arm64`.

## What it actually is

A **GSI (Generic System Image)** is possible because of **Project Treble** (Android 8.0+): Google
requires Treble-compliant phones to split their software into a `system` partition (the OS proper)
and a `vendor` partition (the phone-specific kernel modules, HAL implementations, and proprietary
blobs), with a stable interface between them. That split means a single `system.img` — ours — can
boot on phones whose `vendor` partition we never touched and have never seen, as long as the two
sides speak compatible versions of that interface (VNDK).

This is **not** the same thing as "works on every Android phone ever made." It specifically means:

- The phone must actually be **Treble-compliant** — roughly, shipped new with Android 8.0+ and the
  manufacturer's Treble support enabled. Checkable from the phone itself: dial `*#*#TREBLE#*#*` on
  stock firmware, or check `getprop ro.treble.enabled` via adb (`true` required).
- The GSI's Android version and the phone's **vendor partition's** Android version need to be
  compatible (VNDK-wise) — not necessarily identical, but close, and *this project's GSI is built
  against Android 9* (see "Version alignment" below) because that's what the whole repo's manifest
  is pinned to. A phone whose vendor partition shipped for, say, Android 13 may simply refuse to
  boot a Pie-era system image, Treble-compliant or not.
- **`matissewifi` and `kagura` get nothing from this.** Both predate Project Treble entirely (2014
  tablet, 2016 phone with only a community LineageOS 8.1-era port) — there is no vendor-partition
  split to exploit on either, which is exactly why they still need their own full per-device build.
  The GSI is a parallel path for *other, newer* hardware, not a replacement for those two.

## Version alignment — the part most likely to bite

`tools/pixelos-cli/pixelos` pins the **entire synced source tree** to `lineage-16.0` (Android 9) via
`MANIFEST_BRANCH` — every target in this repo, GSI included, builds against that one platform
source. The phh treble device tree that makes the GSI possible
(`manifests/local_manifests/gsi_treble.xml`) needs to track a **matching** Android-version branch for
this to be consistent, and that file has an open `TODO(verify)` on exactly that: public build guides
for phh's tree reference `android-8.0`/`android-10.0`/`android-14.0` branches, not a confirmed
Android 9 one. Don't assume this is solved — confirm the right branch (or accept porting the whole
project's manifest pin to whatever Android version phh's tree actually supports well) before relying
on a synced build here.

## Building it

```bash
pixelos sync                          # pulls device/phh/treble via gsi_treble.xml, same as any target
pixelos gsi-prep                      # one-time: generates treble_arm64_*.mk from that tree
pixelos device pixelos_gsi_arm64
pixelos build pixelos_gsi_arm64 userdebug
```

`gsi-prep` exists because, unlike `matissewifi`/`kagura`, the GSI's base product makefile isn't a
static file in the source tree — phh's `generate.sh` script writes it out for a target ROM fork
(`lineage`, `aosp`, etc.) after sync. `vendor/pixelos/products/pixelos_gsi_arm64.mk` inherits
whatever that script produces, so `gsi-prep` has to run before `pixelos device`, not just before
`pixelos build`.

## What ships vs. doesn't

- **Vanilla, no GApps** (`treble_arm64_bvN` — see the naming note in
  `vendor/pixelos/products/pixelos_gsi_arm64.mk`) — consistent with PixelOS's open-source-first
  positioning everywhere else in this repo. The GApps variant (`-bgN`) is a one-line swap in that
  file if that's ever wanted instead, not an architecture change.
- **arm64 only.** A handful of very low-end 2018+ phones are 32-bit-only (`arm`, not `arm64`) and
  aren't covered — not worth a separate product target for a shrinking and already-marginal slice of
  hardware, but flagging it so "any recent phone" isn't overclaimed.
- **A/B partition scheme only** (the `b` in `bvN`) — effectively universal on Treble-launched phones
  at this point, since Google requires A/B for new Treble-compliant launches, but older
  first-generation Treble devices on A-only partitions aren't covered by this specific target.

## Flashing

Completely different from the per-device zip-sideload flow — see `pixelos flash`'s GSI section for
the actual commands. In short: `fastboot flash system system.img`, then `fastboot -w` to wipe data
(required after any GSI swap), then reboot. No vendor or boot partition is touched, which is the
whole point — and also means a bad boot is recoverable by flashing the phone's stock `system.img`
back, rather than needing a full factory restore.
