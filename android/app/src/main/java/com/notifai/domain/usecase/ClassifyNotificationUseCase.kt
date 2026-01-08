package com.notifai.domain.usecase

import android.util.Log
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.NotificationRepository
import com.notifai.domain.classifier.ClassificationParser
import com.notifai.domain.classifier.LlamaClassifier
import com.notifai.domain.classifier.PromptBuilder
import com.notifai.service.NotificationDispatcher
import javax.inject.Inject

class ClassifyNotificationUseCase @Inject constructor(
    private val llamaClassifier: LlamaClassifier,
    private val promptBuilder: PromptBuilder,
    private val classificationParser: ClassificationParser,
    private val notificationRepository: NotificationRepository,
    private val notificationDispatcher: NotificationDispatcher
) {

    companion object {
        private const val TAG = "ClassifyNotificationUseCase"
        private const val DEFAULT_FOLDER = "Personal"
        private const val DEFAULT_PRIORITY = 2 // 3-tier: 1=low, 2=medium, 3=high
    }

    suspend operator fun invoke(
        notificationId: String,
        packageName: String,
        appName: String,
        title: String,
        body: String,
        timestamp: Long
    ): Result<Unit> {
        return try {
            // Build prompt
            val prompt = promptBuilder.buildPrompt(appName, title, body)
            Log.d(TAG, "Classifying notification from $appName: $title")

            // Run AI inference (will auto-initialize on first use)
            val result = llamaClassifier.classify(prompt)
            val response = result.response
            val processingTimeMs = result.inferenceTimeMs

            if (response.isEmpty()) {
                Log.w(TAG, "Empty response from classifier, using defaults")
                // Save with defaults if classification fails
                val notification = NotificationEntity(
                    id = notificationId,
                    packageName = packageName,
                    appName = appName,
                    title = title,
                    body = body,
                    timestamp = timestamp,
                    folder = DEFAULT_FOLDER,
                    priority = DEFAULT_PRIORITY,
                    isRead = false,
                    processingTimeMs = processingTimeMs,
                    notified = false
                )
                notificationRepository.insert(notification)
                notificationDispatcher.dispatch(notification)
                return Result.success(Unit)
            }

            // Parse result
            val classification = classificationParser.parse(response)

            val (folder, priority) = if (classification != null) {
                Pair(classification.folder, classification.priority)
            } else {
                Log.w(TAG, "Failed to parse classification, using defaults")
                Pair(DEFAULT_FOLDER, DEFAULT_PRIORITY)
            }

            // Store in database - use the same ID as the intent cache
            val notification = NotificationEntity(
                id = notificationId,
                packageName = packageName,
                appName = appName,
                title = title,
                body = body,
                timestamp = timestamp,
                folder = folder,
                priority = priority,
                isRead = false,
                processingTimeMs = processingTimeMs,
                notified = false
            )

            notificationRepository.insert(notification)
            Log.i(TAG, "Notification classified: folder=$folder, priority=$priority, time=${processingTimeMs}ms")

            // Dispatch notification based on priority
            // P3: Immediate notification
            // P2: Queued for batch (every 30 min)
            // P1: No notification
            notificationDispatcher.dispatch(notification)

            Result.success(Unit)

        } catch (e: Exception) {
            Log.e(TAG, "Classification failed", e)
            Result.failure(e)
        }
    }
}
