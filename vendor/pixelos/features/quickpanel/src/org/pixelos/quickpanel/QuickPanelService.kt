package org.pixelos.quickpanel

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.os.IBinder
import android.provider.MediaStore
import android.provider.Settings
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager

/**
 * One-handed-mode substitute: a pull-tab on the screen edge that expands into a small panel of
 * one-thumb-reachable shortcuts. See docs/FEATURES.md for why this isn't a real "shrink the UI"
 * one-handed mode (that's an Android 10+ framework feature; we're on 9).
 */
class QuickPanelService : Service() {

    private lateinit var windowManager: WindowManager
    private var tabView: View? = null
    private var panelView: View? = null
    private var panelExpanded = false

    private var cameraManager: CameraManager? = null
    private var torchCameraId: String? = null
    private var torchOn = false

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        cameraManager = getSystemService(Context.CAMERA_SERVICE) as? CameraManager
        torchCameraId = findTorchCameraId()
        startForegroundWithNotification()
        addPullTab()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun startForegroundWithNotification() {
        val channelId = "pixelos_quickpanel"
        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        nm.createNotificationChannel(
            NotificationChannel(channelId, getString(R.string.notification_channel_name), NotificationManager.IMPORTANCE_MIN)
        )
        val notification = Notification.Builder(this, channelId)
            .setContentTitle(getString(R.string.app_name))
            .setContentText(getString(R.string.notification_text))
            .setOngoing(true)
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .build()
        startForeground(NOTIFICATION_ID, notification)
    }

    private fun addPullTab() {
        val view = LayoutInflater.from(this).inflate(R.layout.panel_pull_tab, null)
        view.setOnClickListener { togglePanel() }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT,
        ).apply { gravity = Gravity.END or Gravity.CENTER_VERTICAL }

        windowManager.addView(view, params)
        tabView = view
    }

    private fun togglePanel() {
        if (panelExpanded) {
            panelView?.let { windowManager.removeView(it) }
            panelView = null
            panelExpanded = false
            return
        }

        val view = LayoutInflater.from(this).inflate(R.layout.panel_expanded, null)
        view.findViewById<View>(R.id.action_flashlight).setOnClickListener { toggleTorch() }
        view.findViewById<View>(R.id.action_camera).setOnClickListener {
            launchActivity(Intent(MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA))
            togglePanel()
        }
        view.findViewById<View>(R.id.action_home).setOnClickListener {
            launchActivity(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME))
            togglePanel()
        }
        view.findViewById<View>(R.id.action_settings).setOnClickListener {
            launchActivity(Intent(Settings.ACTION_SETTINGS))
            togglePanel()
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT,
        ).apply { gravity = Gravity.END or Gravity.CENTER_VERTICAL; x = 20 }

        windowManager.addView(view, params)
        panelView = view
        panelExpanded = true
    }

    private fun launchActivity(intent: Intent) {
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        try {
            startActivity(intent)
        } catch (_: Exception) {
            // No app resolves this intent on the current build — nothing to fall back to here,
            // silently no-op rather than crash a background overlay service over a missing app.
        }
    }

    private fun findTorchCameraId(): String? {
        val manager = cameraManager ?: return null
        return try {
            manager.cameraIdList.firstOrNull { id ->
                manager.getCameraCharacteristics(id)
                    .get(CameraCharacteristics.FLASH_INFO_AVAILABLE) == true
            }
        } catch (_: Exception) {
            null
        }
    }

    private fun toggleTorch() {
        val manager = cameraManager ?: return
        val id = torchCameraId ?: return
        torchOn = !torchOn
        try {
            manager.setTorchMode(id, torchOn)
        } catch (_: Exception) {
            torchOn = !torchOn // revert our tracked state, the call didn't actually take
        }
    }

    override fun onDestroy() {
        tabView?.let { windowManager.removeView(it) }
        panelView?.let { windowManager.removeView(it) }
        tabView = null
        panelView = null
        if (torchOn) {
            torchCameraId?.let { id -> runCatching { cameraManager?.setTorchMode(id, false) } }
        }
        super.onDestroy()
    }

    companion object {
        private const val NOTIFICATION_ID = 1
    }
}
