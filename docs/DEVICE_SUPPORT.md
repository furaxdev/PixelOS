# Device support notes

## Samsung Galaxy Tab 4 10.1 — SM-T530 (`matissewifi`)

- SoC: Qualcomm Snapdragon 400 (MSM8226), quad-core 1.2GHz
- RAM: 1.5GB
- Released 2014 — this hardware is the hard ceiling on how modern the software layer can feel. Don't expect
  smooth heavy blur/animation-driven theming; keep the feature layer light on this target.
- Community device trees exist for LineageOS up to **16.0** (Android 9). Later LineageOS majors have no
  maintained tree for this codename — going past 16.0 means porting yourself, which is out of scope for a
  first release.
- Sources (pulled automatically via `manifests/local_manifests/matissewifi.xml`):
  - Device tree: `github.com/matissewifi/android_device_samsung_matissewifi` (branch `lineage-16.0`)
  - Common device tree: `github.com/matissewifi/android_device_samsung_matisse-common`
  - Vendor blobs: `github.com/matissewifi/android_vendor_samsung_matissewifi`

### Variants sharing the same board (not our target, just context)

`matisselte` (LTE model) and `matisse3g` (3G model) exist as siblings under the same maintainer org if you
ever want to support those variants — different modem, otherwise same tree family.

### Before flashing a physical unit

1. Full backup (TWRP/Odin) — this is destructive if you mess up partitions.
2. Unlock bootloader via Samsung's official OEM unlock toggle (Developer Options) — note Samsung Knox trips
   permanently (`0x1`) on unlock, which is irreversible and can affect Knox-dependent features/warranty.
3. Flash a matching **TWRP recovery** for `matissewifi` first (via Odin, since the stock bootloader doesn't
   speak `fastboot` on this device family) before attempting to flash PixelOS itself.
4. First boot after flashing a new major Android version on old eMMC hardware can take 10+ minutes — don't
   pull the battery thinking it's bricked.

## Sony Xperia XZ — F8331 single-SIM / F8332 dual-SIM (`kagura`)

- SoC: Qualcomm Snapdragon 820 (MSM8996), quad-core (2x2.15GHz Kryo + 2x1.6GHz Kryo)
- RAM: 3GB, 32GB storage. **F8331 (single-SIM) has no microSD slot** — the card tray only exists on
  the F8332 dual-SIM model, where it's shared with the second SIM (hybrid tray). Don't assume
  expandable storage when writing anything single-SIM-specific.
- Released 2016 — notably more capable hardware than `matissewifi` (modern-for-its-era flagship SoC),
  so this is a better target for validating heavier theming/animation work once it boots.
- **Weaker footing than `matissewifi`:** Sony's own open-source releases
  (`github.com/sonyxperiadev`) stop at AOSP, not LineageOS, and there's no single actively-maintained
  LineageOS fork for this codename — community ports are scattered across different maintainers over
  the years rather than living under one stable org. `manifests/local_manifests/kagura.xml` pins the
  most-cited port as of this writing (lineage-15.1 / Android 8.1, not 16.0 like matissewifi) — treat
  it as a starting point to verify/patch, not a known-working tree. Check the file's own TODO(verify)
  note before syncing.
- F8331 and F8332 share the **same codename and device tree** (`kagura`) — the SIM count is a
  runtime/firmware property, not a build-time split, so `pixelos_kagura` covers both SKUs.

### Before flashing a physical unit

1. Full backup — Sony devices of this era use `fastboot` (unlike the Samsung Odin flow above), so
   back up via adb/fastboot tooling or a TWRP backup before unlocking.
2. Unlock the bootloader via Sony's official unlock tool (requires an unlock code requested from
   Sony's developer site tied to the device's IMEI) — **this permanently voids some DRM-dependent
   features** (camera quality presets tied to Sony's blobs, some streaming app DRM) even after
   relocking; it is not silently reversible the way some OEMs' toggles are.
3. Flash a matching TWRP (or use `fastboot boot` a TWRP image without permanently flashing it, safer
   for first verification) before attempting to flash PixelOS.

## `pixelos_x86_64` (VirtualBox / QEMU)

No physical-device risk — this is a build target, not a device port. Use it as the primary target while
iterating on UI/theming; only touch the tablet for periodic validation builds.
