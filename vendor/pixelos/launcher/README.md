# PixelOS launcher (Lawnchair fork)

Per `docs/ARCHITECTURE.md`'s roadmap: forking [Lawnchair](https://github.com/LawnchairLauncher/lawnchair)
rather than writing a launcher from scratch, same reasoning as forking LineageOS itself — it's already
maintained, Quickstep-compatible, and themeable. Pinned via `manifests/local_manifests/lawnchair.xml`
to `packages/apps/Lawnchair` at tag `v15.0.0-beta3.0` (bump deliberately, not by tracking a moving branch).

## Why this isn't a plain `PRODUCT_PACKAGES += Lawnchair`

Lawnchair is a **Gradle** Android project, not a Soong (`Android.bp`) one — AOSP's build system can't
compile it directly the way it compiles in-tree apps. The standard way vendor trees pull in a
Gradle-built app is: build the APK out-of-band with Gradle, then import the prebuilt via Soong's
`android_app_import`. That's what `Android.bp` in this directory does — it expects a signed APK at
`prebuilt/Lawnchair.apk`, which is **not checked into git** (build artifact, not source — see
`.gitignore`).

## Build steps (on your real build machine, after `pixelos sync`)

```bash
cd "$SRC_DIR/packages/apps/Lawnchair"
./gradlew tasks --group lawnchair   # list the actual assemble task for this Lawnchair version —
                                     # the exact task name (e.g. assembleLawnWithQuickstepRelease)
                                     # has changed across Lawnchair releases, don't assume last year's name
./gradlew <the assemble task you found>
cp app/build/outputs/apk/**/release/*.apk \
   "$REPO_ROOT/vendor/pixelos/launcher/prebuilt/Lawnchair.apk"
```

Requires a JDK + Android SDK/Gradle toolchain — separate from the AOSP source tree's own prebuilt
toolchain, so this is another "what needs you" item: make sure `ANDROID_HOME`/`ANDROID_SDK_ROOT` is
set and the SDK platform/build-tools versions Lawnchair's `build.gradle` asks for are installed.

Once `prebuilt/Lawnchair.apk` exists, `pixelos build pixelos_x86_64 <variant>` picks it up normally
via `PRODUCT_PACKAGES += Lawnchair` in `vendor/pixelos/config/common.mk`.

## Becoming the default home app

`config/common.mk` drops `Trebuchet` from `PRODUCT_PACKAGES` after inheriting the base product, so
Lawnchair ships as the only app with a `HOME` intent-filter — no explicit "set as default" step or
launcher chooser needed. **Verify the actual package name once the source is synced** — LineageOS's
launcher module has been named differently across branches (`Trebuchet` vs `TrebuchetQuickStep`); check
`packages/apps/Trebuchet/Android.mk` (or `.bp`) in the synced tree and update the `filter-out` below if
it doesn't match.

## Branding hooks not yet wired

Lawnchair supports resource-level theming, but which resources are safely overlayable depends on the
exact release — needs checking against the real `res/` once synced before writing an RRO for it. Until
then, PixelOS's brand mark (`vendor/pixelos/assets/brand/`) and wallpaper are ready to use as Lawnchair's
default icon pack / wallpaper once that's confirmed; tracked as follow-up, not guessed at here.
