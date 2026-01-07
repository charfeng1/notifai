package com.notifai.domain.classifier

import android.util.Log
import java.io.File

/**
 * Runtime CPU feature detection and optimal library loader.
 *
 * Detects ARM CPU features (dotprod, i8mm) and loads the best
 * optimized native library for maximum inference performance.
 *
 * Based on llama.rn's RNLlama.java CPU detection strategy.
 */
object LlamaLibraryLoader {
    private const val TAG = "LlamaLibraryLoader"

    @Volatile
    private var loadedLibrary: String? = null

    @Volatile
    private var isLoaded = false

    /**
     * Load the optimal native library based on CPU features.
     * Returns the name of the loaded library for logging.
     */
    @Synchronized
    fun loadOptimalLibrary(): String {
        if (isLoaded) {
            return loadedLibrary ?: "llama_jni"
        }

        val cpuFeatures = getCpuFeatures()
        Log.d(TAG, "Detected CPU features: $cpuFeatures")

        // Detect specific CPU features
        val hasFp16 = cpuFeatures.contains("fphp") || cpuFeatures.contains("asimdhp")
        val hasDotProd = cpuFeatures.contains("asimddp") || cpuFeatures.contains("dotprod")
        val hasI8mm = cpuFeatures.contains("i8mm")

        Log.i(TAG, "CPU capabilities: fp16=$hasFp16, dotprod=$hasDotProd, i8mm=$hasI8mm")

        // Try to load best available library in order of preference
        val librariesToTry = mutableListOf<String>()

        if (hasDotProd && hasI8mm) {
            librariesToTry.add("llama_jni_v8_2_dotprod_i8mm")
        }
        if (hasI8mm) {
            librariesToTry.add("llama_jni_v8_2_i8mm")
        }
        if (hasDotProd) {
            librariesToTry.add("llama_jni_v8_2_dotprod")
        }
        if (hasFp16) {
            librariesToTry.add("llama_jni_v8_2")
        }
        librariesToTry.add("llama_jni_v8")
        librariesToTry.add("llama_jni") // Generic fallback

        for (libName in librariesToTry) {
            try {
                System.loadLibrary(libName)
                loadedLibrary = libName
                isLoaded = true
                Log.i(TAG, "✓ Successfully loaded optimized library: $libName")
                return libName
            } catch (e: UnsatisfiedLinkError) {
                Log.d(TAG, "Library $libName not available, trying next...")
            }
        }

        // This shouldn't happen if at least llama_jni is built
        throw RuntimeException("Failed to load any native library! Tried: $librariesToTry")
    }

    /**
     * Check if the native library is already loaded.
     */
    fun isLibraryLoaded(): Boolean = isLoaded

    /**
     * Get the name of the loaded library.
     */
    fun getLoadedLibraryName(): String? = loadedLibrary

    /**
     * Read CPU features from /proc/cpuinfo.
     * Returns lowercase string of features for easy matching.
     */
    private fun getCpuFeatures(): String {
        return try {
            val cpuInfo = File("/proc/cpuinfo").readText()
            val features = StringBuilder()

            cpuInfo.lines().forEach { line ->
                val lower = line.lowercase()
                if (lower.startsWith("features") || lower.startsWith("flags")) {
                    val idx = lower.indexOf(':')
                    if (idx != -1 && idx + 1 < lower.length) {
                        features.append(lower.substring(idx + 1).trim())
                        features.append(" ")
                    }
                }
            }

            features.toString()
        } catch (e: Exception) {
            Log.w(TAG, "Failed to read /proc/cpuinfo", e)
            ""
        }
    }

    /**
     * Get a human-readable description of loaded library capabilities.
     */
    fun getCapabilitiesDescription(): String {
        return when (loadedLibrary) {
            "llama_jni_v8_2_dotprod_i8mm" -> "ARMv8.2 + DotProd + I8MM (Best)"
            "llama_jni_v8_2_i8mm" -> "ARMv8.2 + I8MM"
            "llama_jni_v8_2_dotprod" -> "ARMv8.2 + DotProd"
            "llama_jni_v8_2" -> "ARMv8.2 + FP16"
            "llama_jni_v8" -> "ARMv8 + NEON"
            "llama_jni_x86_64" -> "x86_64 + SSE4.2"
            "llama_jni" -> "Generic (Fallback)"
            else -> "Unknown"
        }
    }
}
