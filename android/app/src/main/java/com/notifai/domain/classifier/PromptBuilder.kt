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

    suspend fun buildPrompt(
        appName: String,
        title: String,
        body: String
    ): String {
        val folders = folderRepository.allFolders.first()
        val personalInstructions = settingsRepository.getPersonalInstructions() ?: ""

        val folderDescriptions = folders.joinToString("\n") { folder ->
            "[${folder.name}]: ${folder.description}"
        }

        val userSection = if (personalInstructions.isNotEmpty()) {
            "\n\nUser preferences:\n$personalInstructions"
        } else ""

        return """
<|im_start|>system
You classify notifications into folders.

Folders:
$folderDescriptions$userSection

Output JSON only: {"folder": "...", "priority": 1-3}
Priority: 1=low, 2=medium, 3=high
/no_think<|im_end|>
<|im_start|>user
App: $appName
Title: $title
Body: $body<|im_end|>
<|im_start|>assistant
""".trimIndent()
    }
}
