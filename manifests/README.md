# Manifests

This repo does not vendor AOSP/LineageOS source (~250GB). `pixelos-cli sync` runs:

```bash
repo init -u https://github.com/LineageOS/android.git -b lineage-16.0
mkdir -p .repo/local_manifests
cp manifests/local_manifests/*.xml .repo/local_manifests/
repo sync -c -j"$(nproc)"
```

`local_manifests/*.xml` files declare extra `<project>` entries the upstream LineageOS manifest doesn't
include — device trees, vendor blobs, and (later) our own overlay/patch repos.

Branch `lineage-16.0` is pinned because it's the newest LineageOS major with a maintained tree for our first
target (`matissewifi`). The `pixelos_x86_64` target builds fine from the same branch. If you add a device with
a newer maintained tree, you'll need a second manifest branch/config — don't just bump this one and assume
`matissewifi` still builds.
