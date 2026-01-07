package com.notifai.data.repository

import com.notifai.data.local.dao.NotificationDao
import com.notifai.data.local.entity.NotificationEntity
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotificationRepository @Inject constructor(
    private val notificationDao: NotificationDao
) {
    val allNotifications: Flow<List<NotificationEntity>> = notificationDao.getAllNotifications()

    fun getNotificationsByFolder(folder: String): Flow<List<NotificationEntity>> =
        notificationDao.getNotificationsByFolder(folder)

    val folderCounts: Flow<Map<String, Int>> = notificationDao.getFolderCounts()

    suspend fun insert(notification: NotificationEntity) =
        notificationDao.insert(notification)

    suspend fun markAsRead(id: String) =
        notificationDao.markAsRead(id)

    suspend fun deleteOlderThan(timestamp: Long) =
        notificationDao.deleteOlderThan(timestamp)
}
