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

Output JSON only: {"folder": "...", "priority": 1-5}
Priority: 1=ignore, 2=low, 3=normal, 4=important, 5=urgent<|im_end|>
<|im_start|>user
App: $appName
Title: $title
Body: $body<|im_end|>
<|im_start|>assistant
""".trimIndent()
    }
}
