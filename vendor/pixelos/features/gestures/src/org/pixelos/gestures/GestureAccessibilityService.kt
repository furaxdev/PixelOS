package org.pixelos.gestures

import android.accessibilityservice.AccessibilityService
import android.graphics.PixelFormat
import android.util.DisplayMetrics
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent

/**
 * Holds BIND_ACCESSIBILITY_SERVICE (needed for performGlobalAction) and owns three small edge
 * overlay windows that translate swipes into navigation actions. See docs/FEATURES.md for the
 * "why a service+overlay instead of real Q-style gesture nav" background — this is a substitute
 * for that, not a reimplementation of it.
 */
class GestureAccessibilityService : AccessibilityService() {

    private var windowManager: WindowManager? = null
    private val overlays = mutableListOf<View>()

    override fun onServiceConnected() {
        super.onServiceConnected()
        windowManager = getSystemService(WindowManager::class.java)
        addEdgeOverlay(EdgeSwipeView.Axis.VERTICAL, edge = Edge.BOTTOM) { kind ->
            when (kind) {
                EdgeSwipeView.SwipeKind.SHORT -> performGlobalAction(GLOBAL_ACTION_HOME)
                EdgeSwipeView.SwipeKind.LONG -> performGlobalAction(GLOBAL_ACTION_RECENTS)
            }
        }
        addEdgeOverlay(EdgeSwipeView.Axis.HORIZONTAL, edge = Edge.LEFT) {
            performGlobalAction(GLOBAL_ACTION_BACK)
        }
        addEdgeOverlay(EdgeSwipeView.Axis.HORIZONTAL, edge = Edge.RIGHT) {
            performGlobalAction(GLOBAL_ACTION_BACK)
        }
    }

    private enum class Edge { BOTTOM, LEFT, RIGHT }

    private fun addEdgeOverlay(
        axis: EdgeSwipeView.Axis,
        edge: Edge,
        onSwipe: (EdgeSwipeView.SwipeKind) -> Unit,
    ) {
        val wm = windowManager ?: return
        val metrics = DisplayMetrics().also { wm.defaultDisplay.getRealMetrics(it) }
        val thicknessPx = (EDGE_THICKNESS_DP * metrics.density).toInt()

        val (width, height, gravity) = when (edge) {
            Edge.BOTTOM -> Triple(WindowManager.LayoutParams.MATCH_PARENT, thicknessPx, Gravity.BOTTOM)
            Edge.LEFT -> Triple(thicknessPx, WindowManager.LayoutParams.MATCH_PARENT, Gravity.START or Gravity.CENTER_VERTICAL)
            Edge.RIGHT -> Triple(thicknessPx, WindowManager.LayoutParams.MATCH_PARENT, Gravity.END or Gravity.CENTER_VERTICAL)
        }

        val params = WindowManager.LayoutParams(
            width,
            height,
            WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT,
        ).apply { this.gravity = gravity }

        val view = EdgeSwipeView(this, axis, onSwipe)
        wm.addView(view, params)
        overlays.add(view)
    }

    override fun onDestroy() {
        val wm = windowManager
        if (wm != null) {
            for (view in overlays) wm.removeView(view)
        }
        overlays.clear()
        super.onDestroy()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Intentionally empty — this service doesn't act on accessibility events, only gestures.
    }

    override fun onInterrupt() {
        // Nothing to interrupt: no ongoing feedback (speech, etc.) for this service to stop.
    }

    companion object {
        private const val EDGE_THICKNESS_DP = 24
    }
}
