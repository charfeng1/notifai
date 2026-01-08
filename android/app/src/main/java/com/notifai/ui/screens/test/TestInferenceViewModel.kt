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
                val startTime = System.currentTimeMillis()
                Log.i("TestInference", "Starting test inference...")

                // Simple test prompt
                val response = llamaClassifier.classify("Hi, which model are you?")

                val duration = System.currentTimeMillis() - startTime
                Log.i("TestInference", "Test completed in ${duration}ms")

                _testResult.value = TestResult(
                    success = response.isNotEmpty(),
                    response = if (response.isEmpty()) "No response from model" else response,
                    durationMs = duration
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
