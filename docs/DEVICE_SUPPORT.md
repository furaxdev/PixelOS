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

## `pixelos_x86_64` (VirtualBox / QEMU)

No physical-device risk — this is a build target, not a device port. Use it as the primary target while
iterating on UI/theming; only touch the tablet for periodic validation builds.
