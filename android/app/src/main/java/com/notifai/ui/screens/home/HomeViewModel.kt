package com.notifai.ui.screens.home

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.data.local.entity.FolderEntity
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.FolderRepository
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
class HomeViewModel @Inject constructor(
    private val folderRepository: FolderRepository,
    private val notificationRepository: NotificationRepository,
    private val notificationIntentCache: NotificationIntentCache,
    @ApplicationContext private val context: Context
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

    /**
     * Open the original app/conversation for a notification
     */
    fun openNotification(notification: NotificationEntity) {
        // Try cached PendingIntent first, fallback to app launch
        val opened = notificationIntentCache.openNotification(context, notification.id)

        if (!opened) {
            // Fallback: launch the app directly
            notificationIntentCache.launchApp(context, notification.packageName)
        }

        // Mark as read
        viewModelScope.launch {
            notificationRepository.markAsRead(notification.id)
        }
    }
}
