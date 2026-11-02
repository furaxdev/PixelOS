package org.pixelos.qstiles

import android.provider.Settings
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService

/**
 * Toggles the system Daydream/screensaver feature on or off — the same mechanism
 * vendor/pixelos/overlay/PixelOSDreamDefaultsOverlay configures the *default* for (active while
 * docked/charging, PixelOSAmbient as the dream). This tile just flips the master on/off switch,
 * it doesn't change which dream is configured.
 *
 * "screensaver_enabled" is used as a raw Settings.Secure key rather than a named SDK constant —
 * it's a long-stable AOSP key (Daydream has used it since Honeycomb) but isn't part of the public
 * android.provider.Settings.Secure constant set, the way some ROM-side code accesses it. Same class
 * of "confirmed by convention, not yet verified against this specific synced tree" caveat as other
 * TODOs in this repo — check Settings.Secure in the synced frameworks/base source if this doesn't
 * actually toggle anything on a real build.
 */
class AodTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        refreshTileState()
    }

    override fun onClick() {
        super.onClick()
        val enabled = isScreensaverEnabled()
        Settings.Secure.putInt(contentResolver, SCREENSAVER_ENABLED_KEY, if (enabled) 0 else 1)
        refreshTileState()
    }

    private fun refreshTileState() {
        qsTile?.let { tile ->
            tile.state = if (isScreensaverEnabled()) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
            tile.updateTile()
        }
    }

    private fun isScreensaverEnabled(): Boolean =
        Settings.Secure.getInt(contentResolver, SCREENSAVER_ENABLED_KEY, 0) == 1

    companion object {
        private const val SCREENSAVER_ENABLED_KEY = "screensaver_enabled"
    }
}
