# Registers PixelOS product makefiles with the build system, so `lunch`/`breakfast` can find them.
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/pixelos_x86_64.mk \
    $(LOCAL_DIR)/pixelos_matissewifi.mk \
    $(LOCAL_DIR)/pixelos_kagura.mk \
    $(LOCAL_DIR)/pixelos_gsi_arm64.mk

COMMON_LUNCH_CHOICES := \
    pixelos_x86_64-eng \
    pixelos_x86_64-userdebug \
    pixelos_x86_64-user \
    pixelos_matissewifi-userdebug \
    pixelos_matissewifi-user \
    pixelos_kagura-userdebug \
    pixelos_kagura-user \
    pixelos_gsi_arm64-userdebug \
    pixelos_gsi_arm64-user
