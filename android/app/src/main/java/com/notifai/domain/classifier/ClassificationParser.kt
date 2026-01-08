package com.notifai.domain.classifier

import android.util.Log
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

@Serializable
data class ClassificationResult(
    val folder: String,
    val priority: Int
)

@Singleton
class ClassificationParser @Inject constructor() {

    private val json = Json { ignoreUnknownKeys = true }

    companion object {
        private const val TAG = "ClassificationParser"
    }

    fun parse(response: String): ClassificationResult? {
        return try {
            // Strip <think>...</think> tags (Qwen3 thinking mode output)
            val cleanedResponse = response
                .replace(Regex("<think>.*?</think>", RegexOption.DOT_MATCHES_ALL), "")
                .trim()

            Log.d(TAG, "Cleaned response: $cleanedResponse")

            // Extract JSON from response
            val jsonStart = cleanedResponse.indexOf("{")
            val jsonEnd = cleanedResponse.lastIndexOf("}") + 1

            if (jsonStart >= 0 && jsonEnd > jsonStart) {
                val jsonStr = cleanedResponse.substring(jsonStart, jsonEnd)
                Log.d(TAG, "Extracted JSON: $jsonStr")

                val result = json.decodeFromString<ClassificationResult>(jsonStr)

                // Validate result (3-tier: 1=low, 2=medium, 3=high)
                if (result.priority !in 1..3) {
                    Log.w(TAG, "Invalid priority: ${result.priority}, defaulting to 2")
                    return result.copy(priority = 2)
                }

                result
            } else {
                Log.e(TAG, "No valid JSON found in response: $response")
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse response: $response", e)
            null
        }
    }
}
