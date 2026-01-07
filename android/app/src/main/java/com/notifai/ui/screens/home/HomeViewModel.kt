package com.notifai.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.data.local.entity.FolderEntity
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.FolderRepository
import com.notifai.data.repository.NotificationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val folderRepository: FolderRepository,
    private val notificationRepository: NotificationRepository
) : ViewModel() {

    val folders: StateFlow<List<FolderEntity>> = folderRepository.allFolders
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val folderCounts: StateFlow<Map<String, Int>> = notificationRepository.folderCounts
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyMap())

    val recentNotifications: StateFlow<List<NotificationEntity>> = notificationRepository.allNotifications
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    init {
        // Insert default folders on first launch
        viewModelScope.launch {
            if (folders.value.isEmpty()) {
                folderRepository.insertDefaultFolders()
            }
        }
    }
}
