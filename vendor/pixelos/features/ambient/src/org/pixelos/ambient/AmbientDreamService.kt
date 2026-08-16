package org.pixelos.ambient

import android.service.dreams.DreamService

/**
 * Brand-styled ambient clock, shown via the standard AOSP Daydream framework (present since
 * Android 4.2 — nothing backported). See docs/FEATURES.md for the important caveat: matissewifi's
 * LCD panel gets no power benefit from this, unlike true AMOLED always-on-display. Product config
 * (vendor/pixelos/config/common.mk) defaults this to activate only while charging/docked, not as a
 * general "screen never sleeps" mode.
 */
class AmbientDreamService : DreamService() {

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        isInteractive = false
        isFullscreen = true
        isScreenBright = false
        setContentView(R.layout.dream_ambient)
    }
}
