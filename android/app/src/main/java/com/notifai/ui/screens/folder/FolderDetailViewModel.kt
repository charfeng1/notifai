package com.notifai.ui.screens.folder

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.NotificationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

@HiltViewModel
class FolderDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    notificationRepository: NotificationRepository
) : ViewModel() {

    private val folderName: String = checkNotNull(savedStateHandle["folderName"])

    val notifications: StateFlow<List<NotificationEntity>> =
        notificationRepository.getNotificationsByFolder(folderName)
            .stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(5000),
                initialValue = emptyList()
            )
}
