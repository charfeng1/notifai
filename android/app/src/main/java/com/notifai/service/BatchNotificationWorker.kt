package com.notifai.service

import android.content.Context
import android.util.Log
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit

@HiltWorker
class BatchNotificationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val notificationDispatcher: NotificationDispatcher
) : CoroutineWorker(context, workerParams) {

    companion object {
        private const val TAG = "BatchNotificationWorker"
        private const val WORK_NAME = "batch_notifications"
        private const val BATCH_INTERVAL_MINUTES = 30L

        /**
         * Schedule the periodic batch notification worker
         */
        fun schedule(context: Context) {
            val workRequest = PeriodicWorkRequestBuilder<BatchNotificationWorker>(
                BATCH_INTERVAL_MINUTES, TimeUnit.MINUTES
            ).build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                workRequest
            )

            Log.i(TAG, "Scheduled batch notification worker every $BATCH_INTERVAL_MINUTES minutes")
        }

        /**
         * Cancel the periodic batch notification worker
         */
        fun cancel(context: Context) {
            WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
            Log.i(TAG, "Cancelled batch notification worker")
        }

        /**
         * Trigger an immediate batch (for testing or manual trigger)
         */
        fun triggerNow(context: Context) {
            val workRequest = androidx.work.OneTimeWorkRequestBuilder<BatchNotificationWorker>()
                .build()
            WorkManager.getInstance(context).enqueue(workRequest)
            Log.i(TAG, "Triggered immediate batch notification")
        }
    }

    override suspend fun doWork(): Result {
        return try {
            Log.i(TAG, "Running batch notification worker")
            notificationDispatcher.sendBatchNotification()
            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "Batch notification worker failed", e)
            Result.retry()
        }
    }
}
