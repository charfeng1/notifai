package com.notifai.domain.usecase

import android.util.Log
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.NotificationRepository
import com.notifai.domain.classifier.ClassificationParser
import com.notifai.domain.classifier.LlamaClassifier
import com.notifai.domain.classifier.PromptBuilder
import java.util.UUID
import javax.inject.Inject

class ClassifyNotificationUseCase @Inject constructor(
    private val llamaClassifier: LlamaClassifier,
    private val promptBuilder: PromptBuilder,
    private val classificationParser: ClassificationParser,
    private val notificationRepository: NotificationRepository
) {

    companion object {
        private const val TAG = "ClassifyNotificationUseCase"
        private const val DEFAULT_FOLDER = "Personal"
        private const val DEFAULT_PRIORITY = 3
    }

    suspend operator fun invoke(
        packageName: String,
        appName: String,
        title: String,
        body: String,
        timestamp: Long
    ): Result<Unit> {
        return try {
            // Build prompt
            val prompt = promptBuilder.buildPrompt(appName, title, body)
            Log.d(TAG, "Built prompt for $appName: $title")

            // Run inference
            val response = llamaClassifier.classify(prompt)

            if (response.isEmpty()) {
                Log.e(TAG, "Empty response from classifier")
                return Result.failure(Exception("Empty classifier response"))
            }

            // Parse result
            val classification = classificationParser.parse(response)

            val (folder, priority) = if (classification != null) {
                Pair(classification.folder, classification.priority)
            } else {
                Log.w(TAG, "Failed to parse classification, using defaults")
                Pair(DEFAULT_FOLDER, DEFAULT_PRIORITY)
            }

            // Store in database
            val notification = NotificationEntity(
                id = UUID.randomUUID().toString(),
                packageName = packageName,
                appName = appName,
                title = title,
                body = body,
                timestamp = timestamp,
                folder = folder,
                priority = priority,
                isRead = false
            )

            notificationRepository.insert(notification)
            Log.i(TAG, "Notification classified: folder=$folder, priority=$priority")

            Result.success(Unit)

        } catch (e: Exception) {
            Log.e(TAG, "Classification failed", e)
            Result.failure(e)
        }
    }
}
