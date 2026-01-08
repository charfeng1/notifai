package com.notifai.ui.screens.test

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.domain.classifier.LlamaClassifier
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TestResult(
    val success: Boolean,
    val response: String,
    val durationMs: Long
)

@HiltViewModel
class TestInferenceViewModel @Inject constructor(
    private val llamaClassifier: LlamaClassifier
) : ViewModel() {

    private val _testResult = MutableStateFlow<TestResult?>(null)
    val testResult: StateFlow<TestResult?> = _testResult.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun testInference() {
        viewModelScope.launch {
            _isLoading.value = true
            _testResult.value = null

            try {
                Log.i("TestInference", "Starting test inference...")

                // Test with a sample notification in proper Qwen chat format
                val testPrompt = """
<|im_start|>system
You classify notifications into folders.

Folders:
[Work]: Job-related notifications
[Personal]: Friends and family
[Promotions]: Marketing and sales
[Alerts]: System alerts and security

Output JSON only: {"folder": "...", "priority": 1-3}
Priority: 1=low, 2=medium, 3=high
/no_think<|im_end|>
<|im_start|>user
App: Slack
Title: New message from John
Body: Hey, can you review the PR when you get a chance?<|im_end|>
<|im_start|>assistant
""".trimIndent()
                val result = llamaClassifier.classify(testPrompt)

                Log.i("TestInference", "Test completed in ${result.inferenceTimeMs}ms")

                _testResult.value = TestResult(
                    success = result.response.isNotEmpty(),
                    response = if (result.response.isEmpty()) "No response from model" else result.response,
                    durationMs = result.inferenceTimeMs
                )
            } catch (e: Exception) {
                Log.e("TestInference", "Test failed", e)
                _testResult.value = TestResult(
                    success = false,
                    response = "Error: ${e.message}",
                    durationMs = 0
                )
            } finally {
                _isLoading.value = false
            }
        }
    }
}
