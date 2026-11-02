package org.pixelos.qstiles

import android.content.Intent
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService

/**
 * Momentary trigger, not a true on/off toggle: tapping sends a broadcast that
 * org.pixelos.quickpanel.QuickPanelService listens for (dynamically registered, not in its
 * manifest) and open/closes its pull-out panel in response. We have no reliable way to know the
 * panel's actual expanded state from here (it's private state in another process, not exposed via
 * any binder/content provider) — so this tile doesn't track active/inactive like AodTileService
 * does, it's always shown inactive and just fires the toggle on tap. Flagging this rather than
 * faking a state that could drift out of sync with reality.
 */
class QuickPanelTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        qsTile?.let { tile ->
            tile.state = Tile.STATE_INACTIVE
            tile.updateTile()
        }
    }

    override fun onClick() {
        super.onClick()
        val intent = Intent(ACTION_TOGGLE_PANEL).setPackage(QUICKPANEL_PACKAGE)
        sendBroadcast(intent)
    }

    companion object {
        private const val QUICKPANEL_PACKAGE = "org.pixelos.quickpanel"
        // Mirrors org.pixelos.quickpanel.QuickPanelService.ACTION_TOGGLE_PANEL — duplicated as a
        // string literal rather than a cross-module import since these build as separate
        // android_app modules with no shared library between them (see Android.bp in each).
        private const val ACTION_TOGGLE_PANEL = "org.pixelos.quickpanel.ACTION_TOGGLE"
    }
}
