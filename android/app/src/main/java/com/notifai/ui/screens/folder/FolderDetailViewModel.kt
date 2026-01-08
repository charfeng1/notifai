package com.notifai.ui.screens.folder

import android.content.Context
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.NotificationRepository
import com.notifai.service.NotificationIntentCache
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FolderDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val notificationRepository: NotificationRepository,
    private val notificationIntentCache: NotificationIntentCache,
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val folderName: String = checkNotNull(savedStateHandle["folderName"])

    val notifications: StateFlow<List<NotificationEntity>> =
        notificationRepository.getNotificationsByFolder(folderName)
            .stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(5000),
                initialValue = emptyList()
            )

    /**
     * Open the original app/conversation for a notification
     */
    fun openNotification(notification: NotificationEntity) {
        val opened = notificationIntentCache.openNotification(context, notification.id)

        if (!opened) {
            notificationIntentCache.launchApp(context, notification.packageName)
        }

        viewModelScope.launch {
            notificationRepository.markAsRead(notification.id)
        }
    }
}
