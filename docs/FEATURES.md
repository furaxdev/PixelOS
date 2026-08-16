# Feature layer (roadmap step 6)

Chosen features: gesture navigation, always-on display, and a one-handed/quick-actions panel.

## The constraint that shapes all three: we're on Android 9

`manifests/README.md` pins the whole build to `lineage-16.0` (Android 9 Pie) — that's what our
oldest target, `matissewifi`, has a maintained device tree for. Gesture navigation and one-handed
mode both shipped as **native AOSP framework features starting in Android 10 (Q)**. On Pie, neither
exists to toggle on via a resource overlay — there's no `NavigationBarModeGesturalOverlay` or
`OneHandedModeController` to enable, because SystemUI on this branch was never built with them.

Two ways to actually get these features on Android 9:
1. Backport the Q-era SystemUI code — real, invasive frameworks patches, a much bigger and riskier
   undertaking than anything else in this repo so far.
2. Build them as **standalone system apps** using stable public Android APIs, sitting on top of
   SystemUI rather than inside it.

We went with (2) for all three features. It's less integrated (you won't get pixel-perfect AOSP-Q
gesture nav), but it's real, buildable, self-contained, and doesn't require patching upstream
sources — consistent with the RRO-first approach used for rebranding.

## `vendor/pixelos/features/gestures` — PixelOSGestures

An `AccessibilityService` + thin edge-overlay windows (`WindowManager`, `TYPE_ACCESSIBILITY_OVERLAY`)
that capture swipes starting within ~24dp of the bottom/left/right edges and translate them to
`performGlobalAction()` calls — `GLOBAL_ACTION_HOME`, `GLOBAL_ACTION_BACK`, `GLOBAL_ACTION_RECENTS`.
This is the same underlying mechanism third-party "gesture control" apps have used for years; the
difference here is it ships as a privileged system app, pre-enabled, rather than something the user
has to find and grant accessibility access to manually.

**Known limitation:** `performGlobalAction()` triggers the action but doesn't animate/interact with
the nav bar the way native Q gesture nav does (no live nav-bar-hiding transition, no
drag-to-preview-recents). It's real navigation, not real *animation*. Fine as a first pass; flagged
so nobody's surprised it doesn't look like Android 13.

## `vendor/pixelos/features/ambient` — PixelOSAmbient

A `DreamService` (the standard AOSP "Daydream" / screensaver framework — present since Android 4.2,
nothing backported here) showing a brand-styled clock, activated while charging/docked by default via
overlaid `config_dreamsActivatedOnDockByDefault` / `config_dreamsActivatedOnChargeByDefault` values.

**Read this before enabling it on `matissewifi`:** "always-on display" implies an AMOLED panel that
can light individual pixels at near-zero power. `matissewifi` (Galaxy Tab 4, 2014) has a **TFT LCD**
— there's no low-power always-on mode possible on this hardware. What PixelOSAmbient actually does
on `matissewifi` is show a full-brightness clock screen instead of turning the display off, which
**costs more battery than sleeping normally**, not less. It's included because you asked for the
feature, but the honest recommendation is: only activate it while charging/docked (which is the
default we set), never as a battery-powered "screen never sleeps" mode. It'll make real sense on
whatever OLED device eventually joins the target list.

## `vendor/pixelos/features/quickpanel` — PixelOSQuickPanel

A one-handed-mode *substitute*, not a reimplementation — Android 9 has no framework hook to shrink
the whole UI into a corner. Instead: a small pull-tab overlay on one screen edge that expands into a
floating panel with a few one-thumb-reachable shortcuts (flashlight toggle, camera, home, settings).
Scoped deliberately small for a first pass — screenshot capture was considered and dropped, it needs
the same `performGlobalAction`/accessibility-service path as the gestures feature and didn't seem
worth duplicating that machinery for v1.

## Status

**Prepared, not verified** — same status as everything else in `vendor/pixelos/` per
`docs/ARCHITECTURE.md`'s roadmap tags. This is real Kotlin against stable public APIs, written
carefully, but it has never been compiled — there's no Android SDK/build machine in the session that
wrote it. Treat first build + first real device/emulator test as where actual bugs surface, and
report back here (or just fix and PR) once that happens.

## Wiring

All three are added to `PRODUCT_PACKAGES` in `vendor/pixelos/config/common.mk`, each
`product_specific: true` and privileged (`certificate: "platform"`), with a
`privapp-permissions-pixelos.xml` allowlisting the special permissions (`SYSTEM_ALERT_WINDOW`, the
accessibility-bound `performGlobalAction`, etc.) that privileged apps must have explicitly allowlisted
since Android O — declaring a permission in the manifest alone isn't enough for a system app.
