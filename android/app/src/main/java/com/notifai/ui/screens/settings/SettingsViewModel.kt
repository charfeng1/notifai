package com.notifai.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.data.local.entity.MonitoredAppEntity
import com.notifai.data.repository.MonitoredAppRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val monitoredAppRepository: MonitoredAppRepository
) : ViewModel() {

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    val monitoredApps: StateFlow<List<MonitoredAppEntity>> =
        monitoredAppRepository.allApps
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun loadInstalledApps() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                monitoredAppRepository.loadInstalledApps()
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun reloadApps() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // Clear existing apps and reload
                monitoredAppRepository.clearAll()
                monitoredAppRepository.loadInstalledApps()
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun toggleApp(packageName: String, enabled: Boolean) {
        viewModelScope.launch {
            monitoredAppRepository.toggleApp(packageName, enabled)
        }
    }
}
