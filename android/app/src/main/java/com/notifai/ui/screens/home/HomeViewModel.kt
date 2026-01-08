package com.notifai.ui.screens.home

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.notifai.data.local.entity.FolderEntity
import com.notifai.data.local.entity.NotificationEntity
import com.notifai.data.repository.FolderRepository
import com.notifai.data.repository.NotificationRepository
import com.notifai.domain.classifier.LlamaClassifier
import com.notifai.service.NotificationIntentCache
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val folderRepository: FolderRepository,
    private val notificationRepository: NotificationRepository,
    private val notificationIntentCache: NotificationIntentCache,
    private val llamaClassifier: LlamaClassifier,
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
            // Use first() to wait for actual DB state, not the initial empty value
            if (folderRepository.allFolders.first().isEmpty()) {
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

    /**
     * Add a new custom folder.
     * Returns false if a folder with the same name already exists.
     */
    fun addFolder(name: String, description: String): Boolean {
        val currentFolders = folders.value
        // Check for duplicate name (case-insensitive)
        if (currentFolders.any { it.name.equals(name, ignoreCase = true) }) {
            return false
        }

        viewModelScope.launch {
            val nextSortOrder = (currentFolders.maxOfOrNull { it.sortOrder } ?: 3) + 1

            val folder = FolderEntity(
                id = UUID.randomUUID().toString(),
                name = name,
                description = description,
                isDefault = false,
                sortOrder = nextSortOrder
            )

            folderRepository.insert(folder)
            llamaClassifier.invalidateCache()
        }
        return true
    }

    /**
     * Update an existing custom folder.
     * Returns false if the new name conflicts with an existing folder.
     */
    fun updateFolder(folder: FolderEntity, newName: String, newDescription: String): Boolean {
        if (folder.isDefault) return false

        val currentFolders = folders.value
        // Check for duplicate name (excluding the folder being edited)
        if (currentFolders.any { it.id != folder.id && it.name.equals(newName, ignoreCase = true) }) {
            return false
        }

        viewModelScope.launch {
            // If name changed, update all notifications first
            if (folder.name != newName) {
                notificationRepository.updateFolderName(folder.name, newName)
            }

            val updatedFolder = folder.copy(name = newName, description = newDescription)
            folderRepository.update(updatedFolder)
            llamaClassifier.invalidateCache()
        }
        return true
    }

    /**
     * Delete a custom folder and all its notifications
     */
    fun deleteFolder(folder: FolderEntity) {
        if (folder.isDefault) return

        viewModelScope.launch {
            notificationRepository.deleteByFolder(folder.name)
            folderRepository.delete(folder)
            llamaClassifier.invalidateCache()
        }
    }
}
