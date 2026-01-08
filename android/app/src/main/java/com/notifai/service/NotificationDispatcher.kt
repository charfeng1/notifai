package com.notifai.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import com.notifai.R
import com.notifai.data.local.dao.NotificationDao
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.ui.MainActivity
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotificationDispatcher @Inject constructor(
    @ApplicationContext private val context: Context,
    private val notificationDao: NotificationDao
) {
    companion object {
        private const val TAG = "NotificationDispatcher"

        // Notification channels
        const val CHANNEL_HIGH_PRIORITY = "high_priority"
        const val CHANNEL_BATCH = "batch_notifications"

        // Notification IDs
        private const val BATCH_NOTIFICATION_ID = 1000
        private var highPriorityNotificationId = 2000
    }

    init {
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // High priority channel - for urgent notifications
        val highPriorityChannel = NotificationChannel(
            CHANNEL_HIGH_PRIORITY,
            "Urgent Notifications",
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = "Immediate notifications for high-priority items"
            enableVibration(true)
            setShowBadge(true)
        }

        // Batch channel - for grouped medium priority notifications
        val batchChannel = NotificationChannel(
            CHANNEL_BATCH,
            "Batched Notifications",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "Grouped notifications delivered periodically"
            enableVibration(false)
            setShowBadge(true)
        }

        notificationManager.createNotificationChannel(highPriorityChannel)
        notificationManager.createNotificationChannel(batchChannel)
    }

    /**
     * Dispatch notification based on priority:
     * - P3 (High): Immediate individual notification
     * - P2 (Medium): No immediate notification, will be batched
     * - P1 (Low): No notification at all
     */
    suspend fun dispatch(notification: NotificationEntity) {
        when (notification.priority) {
            3 -> {
                // High priority - send immediately
                sendHighPriorityNotification(notification)
                notificationDao.markAsNotified(notification.id)
                Log.i(TAG, "Sent high priority notification: ${notification.title}")
            }
            2 -> {
                // Medium priority - will be batched, don't notify yet
                Log.d(TAG, "Queued medium priority for batch: ${notification.title}")
            }
            1 -> {
                // Low priority - no notification, just mark as "notified" (handled)
                notificationDao.markAsNotified(notification.id)
                Log.d(TAG, "Low priority, no notification: ${notification.title}")
            }
        }
    }

    private fun sendHighPriorityNotification(notification: NotificationEntity) {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Intent to open the app
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("notificationId", notification.id)
            putExtra("folder", notification.folder)
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            notification.id.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_HIGH_PRIORITY)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("${notification.appName}: ${notification.title}")
            .setContentText(notification.body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(notification.body))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setGroup("high_priority_group")

        notificationManager.notify(highPriorityNotificationId++, builder.build())
    }

    /**
     * Send batched notification for all pending medium priority items
     */
    suspend fun sendBatchNotification() {
        val pending = notificationDao.getPendingMediumPriority()

        if (pending.isEmpty()) {
            Log.d(TAG, "No pending medium priority notifications to batch")
            return
        }

        Log.i(TAG, "Sending batch notification for ${pending.size} items")

        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Intent to open the app
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            BATCH_NOTIFICATION_ID,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // Build summary text
        val summaryText = when {
            pending.size == 1 -> "${pending[0].appName}: ${pending[0].title}"
            pending.size <= 3 -> pending.joinToString(", ") { it.appName }
            else -> "${pending.take(3).joinToString(", ") { it.appName }} and ${pending.size - 3} more"
        }

        // Build inbox style for multiple notifications
        val inboxStyle = NotificationCompat.InboxStyle()
            .setBigContentTitle("${pending.size} notifications")

        pending.take(5).forEach { notif ->
            inboxStyle.addLine("${notif.appName}: ${notif.title}")
        }

        if (pending.size > 5) {
            inboxStyle.setSummaryText("+${pending.size - 5} more")
        }

        val builder = NotificationCompat.Builder(context, CHANNEL_BATCH)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("${pending.size} new notifications")
            .setContentText(summaryText)
            .setStyle(inboxStyle)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setNumber(pending.size)

        notificationManager.notify(BATCH_NOTIFICATION_ID, builder.build())

        // Mark all as notified
        notificationDao.markAsNotified(pending.map { it.id })
    }
}
