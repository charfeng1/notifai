package com.notifai.domain.classifier

import com.notifai.data.repository.FolderRepository
import com.notifai.data.repository.SettingsRepository
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PromptBuilder @Inject constructor(
    private val folderRepository: FolderRepository,
    private val settingsRepository: SettingsRepository
) {

    // Cache the system prompt to detect changes
    @Volatile
    private var cachedSystemPrompt: String? = null

    /**
     * Builds the system prompt portion (cacheable in KV cache).
     * This only changes when folders or personal instructions change.
     */
    suspend fun buildSystemPrompt(): String {
        val folders = folderRepository.allFolders.first()
        val personalInstructions = settingsRepository.getPersonalInstructions() ?: ""

        // Match training format: "- FolderName: description"
        val folderDescriptions = folders.joinToString("\n") { folder ->
            "- ${folder.name}: ${folder.description}"
        }

        val userSection = if (personalInstructions.isNotEmpty()) {
            "\n\nUser preferences:\n$personalInstructions"
        } else ""

        return """
<|im_start|>system
You are a notification classifier. Classify the notification into a folder and priority level.

Folders:
$folderDescriptions$userSection

Priority levels:
- 1 (Low): Can ignore or check later (promotions, social media, newsletters)
- 2 (Medium): Worth checking today (regular emails, app updates, deliveries)
- 3 (High): Requires immediate attention (urgent messages, security alerts, time-sensitive)

Respond with ONLY a JSON object: {"folder": "<folder>", "priority": <1-3>}
/no_think<|im_end|>
""".trimIndent()
    }

    /**
     * Builds the user message portion (changes for each notification).
     */
    fun buildUserMessage(appName: String, title: String, body: String): String {
        return """
<|im_start|>user
App: $appName
Title: $title
Body: $body<|im_end|>
<|im_start|>assistant
""".trimIndent()
    }

    /**
     * Checks if system prompt has changed since last cache.
     * Returns true if prompt changed (cache needs refresh).
     */
    suspend fun hasSystemPromptChanged(): Boolean {
        val newPrompt = buildSystemPrompt()
        val changed = cachedSystemPrompt != newPrompt
        cachedSystemPrompt = newPrompt
        return changed
    }

    /**
     * Legacy method - builds full prompt for compatibility.
     */
    suspend fun buildPrompt(
        appName: String,
        title: String,
        body: String
    ): String {
        return buildSystemPrompt() + "\n" + buildUserMessage(appName, title, body)
    }
}
