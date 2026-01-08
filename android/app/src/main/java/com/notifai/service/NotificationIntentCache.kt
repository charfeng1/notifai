package com.notifai.service

import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.util.Log
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Cache for storing PendingIntents from captured notifications.
 * Allows users to tap on notifications in our app and open the original app/conversation.
 *
 * Note: PendingIntents may expire, so we also store package name for fallback.
 */
@Singleton
class NotificationIntentCache @Inject constructor() {

    companion object {
        private const val TAG = "NotificationIntentCache"
        private const val MAX_CACHE_SIZE = 500
    }

    data class CachedIntent(
        val pendingIntent: PendingIntent?,
        val packageName: String,
        val timestamp: Long = System.currentTimeMillis()
    )

    private val cache = ConcurrentHashMap<String, CachedIntent>()

    /**
     * Store a notification's intent for later use
     */
    fun put(notificationId: String, pendingIntent: PendingIntent?, packageName: String) {
        // Evict old entries if cache is too large
        if (cache.size >= MAX_CACHE_SIZE) {
            evictOldest()
        }

        cache[notificationId] = CachedIntent(pendingIntent, packageName)
        Log.d(TAG, "Cached intent for notification: $notificationId (cache size: ${cache.size})")
    }

    /**
     * Get the cached intent for a notification
     */
    fun get(notificationId: String): CachedIntent? {
        return cache[notificationId]
    }

    /**
     * Try to open the notification's original destination
     * Returns true if successful, false if fallback needed
     */
    fun openNotification(context: Context, notificationId: String): Boolean {
        val cached = cache[notificationId]

        if (cached == null) {
            Log.w(TAG, "No cached intent for notification: $notificationId")
            return false
        }

        // Try the original PendingIntent first
        cached.pendingIntent?.let { intent ->
            try {
                intent.send()
                Log.i(TAG, "Opened notification via PendingIntent: $notificationId")
                return true
            } catch (e: PendingIntent.CanceledException) {
                Log.w(TAG, "PendingIntent was cancelled, falling back to app launch")
            }
        }

        // Fallback: launch the app directly
        return launchApp(context, cached.packageName)
    }

    /**
     * Launch an app by package name (fallback when PendingIntent expires)
     */
    fun launchApp(context: Context, packageName: String): Boolean {
        return try {
            val launchIntent = context.packageManager.getLaunchIntentForPackage(packageName)
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(launchIntent)
                Log.i(TAG, "Launched app: $packageName")
                true
            } else {
                Log.e(TAG, "No launch intent for package: $packageName")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to launch app: $packageName", e)
            false
        }
    }

    /**
     * Remove oldest entries when cache is full
     */
    private fun evictOldest() {
        val entriesToRemove = cache.entries
            .sortedBy { it.value.timestamp }
            .take(MAX_CACHE_SIZE / 4)

        entriesToRemove.forEach { cache.remove(it.key) }
        Log.d(TAG, "Evicted ${entriesToRemove.size} old entries from cache")
    }

    /**
     * Clear all cached intents
     */
    fun clear() {
        cache.clear()
    }
}
