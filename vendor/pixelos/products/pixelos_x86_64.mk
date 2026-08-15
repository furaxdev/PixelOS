# PixelOS product definition for the x86_64 (VirtualBox/QEMU) dev/test target.
# This is what `breakfast pixelos_x86_64` / `lunch pixelos_x86_64-<variant>` selects.

$(call inherit-product, vendor/lineage/target/product/lineage_x86_64.mk)
$(call inherit-product, vendor/pixelos/config/common.mk)

PRODUCT_NAME := pixelos_x86_64
PRODUCT_DEVICE := x86_64
PRODUCT_MODEL := PixelOS x86_64
