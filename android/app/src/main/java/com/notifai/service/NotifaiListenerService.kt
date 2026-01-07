package com.notifai.service

import android.app.Notification
import android.content.Intent
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import com.notifai.data.repository.MonitoredAppRepository
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class NotifaiListenerService : NotificationListenerService() {

    @Inject
    lateinit var monitoredAppRepository: MonitoredAppRepository

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    companion object {
        private const val TAG = "NotifaiListenerService"
    }

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        super.onNotificationPosted(sbn)

        val packageName = sbn.packageName
        val notification = sbn.notification

        // Ignore our own notifications
        if (packageName == applicationContext.packageName) {
            return
        }

        serviceScope.launch {
            try {
                // Check if app is monitored
                if (!monitoredAppRepository.isAppMonitored(packageName)) {
                    Log.d(TAG, "Ignoring notification from unmonitored app: $packageName")
                    return@launch
                }

                // Extract notification data
                val extras = notification.extras
                val title = extras.getString(Notification.EXTRA_TITLE) ?: ""
                val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""

                if (title.isEmpty() && text.isEmpty()) {
                    Log.d(TAG, "Skipping empty notification from $packageName")
                    return@launch
                }

                // Get app name
                val pm = packageManager
                val appInfo = pm.getApplicationInfo(packageName, 0)
                val appName = pm.getApplicationLabel(appInfo).toString()

                Log.i(TAG, "Received notification from $appName: $title")

                // Start classification service
                val intent = Intent(this@NotifaiListenerService, ClassificationService::class.java).apply {
                    putExtra("packageName", packageName)
                    putExtra("appName", appName)
                    putExtra("title", title)
                    putExtra("body", text)
                    putExtra("timestamp", System.currentTimeMillis())
                }

                startForegroundService(intent)

            } catch (e: Exception) {
                Log.e(TAG, "Error processing notification from $packageName", e)
            }
        }
    }

    override fun onListenerConnected() {
        super.onListenerConnected()
        Log.i(TAG, "NotificationListenerService connected")
    }

    override fun onListenerDisconnected() {
        super.onListenerDisconnected()
        Log.w(TAG, "NotificationListenerService disconnected")
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
}
