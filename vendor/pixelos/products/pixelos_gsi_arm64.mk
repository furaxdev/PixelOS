# PixelOS product definition for a generic Treble GSI (arm64, A/B partitions, vanilla/no GApps).
# This is what `breakfast pixelos_gsi_arm64` / `lunch pixelos_gsi_arm64-<variant>` selects.
#
# Different in kind from pixelos_matissewifi.mk / pixelos_kagura.mk: those build a complete image
# tied to one phone's kernel+blobs; this builds a system-only image that installs on ANY Project
# Treble-compliant device (roughly 2017+ phones) because the vendor partition — the hardware-specific
# half — comes from the device itself, not from us. See docs/GSI.md for what this does and doesn't
# cover, especially: it does NOT help matissewifi or kagura, both of which predate Treble.
#
# Prerequisite build step (NOT a repo sync step — this generates real product makefiles from the
# phh treble device tree pulled in by manifests/local_manifests/gsi_treble.xml):
#   cd "$SRC_DIR" && device/phh/treble/generate.sh lineage
# `pixelos gsi-prep` runs this for you. Without it, the inherit-product path below won't exist yet.
#
# TODO(verify): confirm this exact generated filename once generate.sh has actually run — naming
# follows phh's {arch}_{a|b}{v|g}{N|S} convention (arm64, A/B, vanilla, no su) as of this writing,
# but confirm against the real generated output:
#   ls "$SRC_DIR"/device/phh/treble/treble_arm64_*.mk
$(call inherit-product, device/phh/treble/treble_arm64_bvN.mk)
$(call inherit-product, vendor/pixelos/config/common.mk)

PRODUCT_NAME := pixelos_gsi_arm64
PRODUCT_DEVICE := treble_arm64_bvN
PRODUCT_MODEL := PixelOS GSI (arm64)

# Vanilla (no GApps) — consistent with PixelOS's open-source-first rebrand positioning elsewhere in
# this repo, and simpler to redistribute. Switching to the -bgN (GApps) treble variant instead is a
# one-line change here, not an architecture change, if that's ever wanted.
