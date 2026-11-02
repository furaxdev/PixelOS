# PixelOS product definition for the Sony Xperia XZ (F8331 single-SIM / F8332 dual-SIM, kagura).
# This is what `breakfast kagura` / `lunch pixelos_kagura-<variant>` selects.
#
# Second device target, proving the product-makefile pattern generalizes beyond matissewifi: every
# device-specific concern (base tree, codename, model string) lives here; everything shared
# (identity, overlays, launcher, feature layer) stays in config/common.mk untouched.
#
# TODO(verify): same class of issue as pixelos_matissewifi.mk's base-makefile TODO — confirm the
# actual filename once device/sony/kagura is synced:
#   ls "$SRC_DIR"/device/sony/kagura/lineage*.mk
# This device tree (see manifests/local_manifests/kagura.xml) is less actively maintained than
# matissewifi's — expect to patch more than just this filename.
$(call inherit-product, device/sony/kagura/lineage_kagura.mk)
$(call inherit-product, vendor/pixelos/config/common.mk)

PRODUCT_NAME := pixelos_kagura
PRODUCT_DEVICE := kagura
PRODUCT_MODEL := PixelOS kagura
# Covers both F8331 (single-SIM) and F8332 (dual-SIM) — same codename/tree, SIM count is a
# runtime firmware property, not a build-time split. See docs/DEVICE_SUPPORT.md.
