package org.pixelos.gestures

import android.content.Context
import android.view.MotionEvent
import android.view.View

/**
 * A thin transparent strip pinned to one screen edge. Tracks a single-finger drag away from that
 * edge and reports it as one of two gesture kinds via [onSwipe] on release:
 *  - a short drag  -> [SwipeKind.SHORT]  (home / back, depending on which edge owns this view)
 *  - a long drag   -> [SwipeKind.LONG]   (recents — bottom edge only; left/right ignore this kind)
 *
 * Deliberately not built on GestureDetector's fling velocity heuristics — tracking raw start/end
 * distance is simpler to reason about correctly without a device to test timing thresholds on.
 */
class EdgeSwipeView(
    context: Context,
    private val axis: Axis,
    private val onSwipe: (SwipeKind) -> Unit,
) : View(context) {

    enum class Axis { VERTICAL, HORIZONTAL }
    enum class SwipeKind { SHORT, LONG }

    private var startX = 0f
    private var startY = 0f

    companion object {
        // In pixels at a nominal ~2x density; good enough for a first pass — revisit with real
        // device testing rather than trying to hand-tune dp math no one has verified on hardware.
        private const val SHORT_THRESHOLD_PX = 60f
        private const val LONG_THRESHOLD_PX = 220f
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.rawX
                startY = event.rawY
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                if (event.actionMasked == MotionEvent.ACTION_CANCEL) return true
                val distance = when (axis) {
                    Axis.VERTICAL -> startY - event.rawY   // positive = dragged upward
                    Axis.HORIZONTAL -> kotlin.math.abs(event.rawX - startX)
                }
                if (distance >= LONG_THRESHOLD_PX && axis == Axis.VERTICAL) {
                    onSwipe(SwipeKind.LONG)
                } else if (distance >= SHORT_THRESHOLD_PX) {
                    onSwipe(SwipeKind.SHORT)
                }
                return true
            }
        }
        return false
    }
}
