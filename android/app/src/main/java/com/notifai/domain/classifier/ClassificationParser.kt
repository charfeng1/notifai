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
            // Extract JSON from response
            val jsonStart = response.indexOf("{")
            val jsonEnd = response.lastIndexOf("}") + 1

            if (jsonStart >= 0 && jsonEnd > jsonStart) {
                val jsonStr = response.substring(jsonStart, jsonEnd)
                Log.d(TAG, "Extracted JSON: $jsonStr")

                val result = json.decodeFromString<ClassificationResult>(jsonStr)

                // Validate result
                if (result.priority !in 1..5) {
                    Log.w(TAG, "Invalid priority: ${result.priority}, defaulting to 3")
                    return result.copy(priority = 3)
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
