# PixelOS product definition for the Galaxy Tab 4 10.1 (SM-T530, matissewifi).
# This is what `breakfast matissewifi` / `lunch pixelos_matissewifi-<variant>` selects.
#
# TODO(verify): the base product makefile name varies by LineageOS-fork branch/maintainer — it's
# `lineage_<codename>.mk` on most modern branches but plain `lineage.mk` on some older ones (this
# device tree is pinned to lineage-16.0, an older branch — see manifests/local_manifests/matissewifi.xml
# and docs/DEVICE_SUPPORT.md). Confirm the actual filename once the source is synced:
#   ls "$SRC_DIR"/device/samsung/matissewifi/lineage*.mk
# and fix the inherit-product path below if it doesn't match — same class of issue as the
# Trebuchet/TrebuchetQuickStep package name TODO in config/common.mk.
$(call inherit-product, device/samsung/matissewifi/lineage_matissewifi.mk)
$(call inherit-product, vendor/pixelos/config/common.mk)

PRODUCT_NAME := pixelos_matissewifi
PRODUCT_DEVICE := matissewifi
PRODUCT_MODEL := PixelOS matissewifi
# PRODUCT_BRAND stays PixelOS (from config/common.mk) rather than reverting to the OEM's original
# "samsung" — some forks do that for Samsung-specific compatibility checks; we're not chasing that
# here, flag it if a real build turns out to need it.
