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
    PixelOSWallpaperOverlay \
    PixelOSAccentOverlay

PRODUCT_COPY_FILES += \
    vendor/pixelos/prebuilt/common/media/bootanimation.zip:system/media/bootanimation.zip

# Launcher: our Lawnchair fork (see vendor/pixelos/launcher/README.md for why this is an
# android_app_import rather than a plain module) replaces the inherited default launcher.
PRODUCT_PACKAGES += \
    Lawnchair

# Drop the base product's launcher so Lawnchair is the only app with a HOME intent-filter —
# that's what makes it the default with no chooser/explicit "set as default" step.
# TODO(verify): confirm this is the actual module name once the source is synced — it has been
# `Trebuchet` on older lineage branches and `TrebuchetQuickStep` on newer ones. Check
# packages/apps/Trebuchet/Android.mk (or .bp) in the synced tree; fix this line if it's wrong,
# a stale name here is a silent no-op, not a build error.
PRODUCT_PACKAGES := $(filter-out Trebuchet TrebuchetQuickStep,$(PRODUCT_PACKAGES))
