package com.notifai.service

import android.app.*
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.notifai.R
import com.notifai.domain.classifier.LlamaClassifier
import com.notifai.domain.usecase.ClassifyNotificationUseCase
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class ClassificationService : Service() {

    @Inject
    lateinit var classifyNotificationUseCase: ClassifyNotificationUseCase

    @Inject
    lateinit var llamaClassifier: LlamaClassifier

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    companion object {
        private const val TAG = "ClassificationService"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "classification_service"
        private const val CHANNEL_NAME = "Classification Service"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        Log.d(TAG, "ClassificationService created")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Start as foreground service
        startForeground(NOTIFICATION_ID, createNotification())

        intent?.let {
            val notificationId = it.getStringExtra("notificationId") ?: return@let
            val packageName = it.getStringExtra("packageName") ?: return@let
            val appName = it.getStringExtra("appName") ?: ""
            val title = it.getStringExtra("title") ?: ""
            val body = it.getStringExtra("body") ?: ""
            val timestamp = it.getLongExtra("timestamp", System.currentTimeMillis())

            serviceScope.launch {
                try {
                    Log.d(TAG, "Processing notification from $appName")

                    // Classify notification (model initialized in Application class)
                    val result = classifyNotificationUseCase(
                        notificationId, packageName, appName, title, body, timestamp
                    )

                    if (result.isFailure) {
                        Log.e(TAG, "Classification failed: ${result.exceptionOrNull()}")
                    } else {
                        Log.i(TAG, "Classification successful for $appName")
                    }

                } catch (e: Exception) {
                    Log.e(TAG, "Error during classification", e)
                } finally {
                    stopSelf(startId)
                }
            }
        }

        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Processes notifications in background using AI"
                setShowBadge(false)
            }

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.classification_service_title))
            .setContentText(getString(R.string.classification_service_description))
            .setSmallIcon(android.R.drawable.ic_dialog_info) // Temporary icon
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }
}
