# Shared PixelOS identity, included by every PixelOS product makefile.
# Keep this device-agnostic — device-specific bits belong in products/<name>.mk.

PIXELOS_VERSION := 0.1.0-dev

PRODUCT_BRAND := PixelOS
PRODUCT_MANUFACTURER := PixelOS

PRODUCT_GMS_CLIENTID_BASE := android-pixelos

PRODUCT_PROPERTY_OVERRIDES += \
    ro.product.brand=PixelOS \
    ro.product.manufacturer=PixelOS \
    ro.build.display.id=PixelOS-$(PIXELOS_VERSION) \
    ro.pixelos.version=$(PIXELOS_VERSION)

# Runtime Resource Overlays (RRO) — see vendor/pixelos/overlay/*, each a standalone package rather
# than a legacy PRODUCT_PACKAGE_OVERLAYS static overlay. Keeps rebasing on upstream LineageOS cheap:
# we never touch frameworks/base source, only overlay resources at runtime.
PRODUCT_PACKAGES += \
    PixelOSWallpaperOverlay

PRODUCT_COPY_FILES += \
    vendor/pixelos/prebuilt/common/media/bootanimation.zip:system/media/bootanimation.zip
