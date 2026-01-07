package com.notifai.domain.classifier

import android.content.Context
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class LlamaClassifier @Inject constructor(
    @ApplicationContext private val context: Context
) {

    companion object {
        private const val TAG = "LlamaClassifier"
        private const val MODEL_FILENAME = "Qwen3-0.6B-Q5_K_M.gguf"

        init {
            System.loadLibrary("llama_jni")
        }
    }

    private var isInitialized = false

    // Native methods
    private external fun nativeInit(modelPath: String): Boolean
    private external fun nativeInference(prompt: String): String
    private external fun nativeCleanup()

    suspend fun initialize(): Boolean = withContext(Dispatchers.IO) {
        try {
            // Check if model exists in assets
            val modelFile = File(context.filesDir, MODEL_FILENAME)

            if (!modelFile.exists()) {
                Log.i(TAG, "Copying model from assets to internal storage...")
                val startTime = System.currentTimeMillis()

                context.assets.open("models/$MODEL_FILENAME").use { input ->
                    modelFile.outputStream().use { output ->
                        input.copyTo(output)
                    }
                }

                val copyTime = System.currentTimeMillis() - startTime
                Log.i(TAG, "Model copied in ${copyTime}ms")
            }

            // Initialize native model
            Log.i(TAG, "Initializing model at: ${modelFile.absolutePath}")
            val initStartTime = System.currentTimeMillis()

            isInitialized = nativeInit(modelFile.absolutePath)

            val initTime = System.currentTimeMillis() - initStartTime
            Log.i(TAG, "Model initialization took ${initTime}ms, result: $isInitialized")

            isInitialized
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize model", e)
            false
        }
    }

    suspend fun classify(prompt: String): String = withContext(Dispatchers.Default) {
        if (!isInitialized) {
            Log.e(TAG, "Classifier not initialized")
            return@withContext ""
        }

        try {
            val startTime = System.currentTimeMillis()
            val result = nativeInference(prompt)
            val duration = System.currentTimeMillis() - startTime

            Log.i(TAG, "Classification took ${duration}ms")
            Log.d(TAG, "Result: $result")

            result
        } catch (e: Exception) {
            Log.e(TAG, "Inference failed", e)
            ""
        }
    }

    fun cleanup() {
        if (isInitialized) {
            nativeCleanup()
            isInitialized = false
            Log.i(TAG, "Model cleaned up")
        }
    }
}
