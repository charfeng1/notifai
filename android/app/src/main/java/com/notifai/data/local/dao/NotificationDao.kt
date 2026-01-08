package com.notifai.data.local.dao

import androidx.room.*
import com.notifai.data.local.entity.NotificationEntity
import kotlinx.coroutines.flow.Flow

data class FolderCount(
    val folder: String,
    val count: Int
)

@Dao
interface NotificationDao {
    @Query("SELECT * FROM notifications ORDER BY timestamp DESC")
    fun getAllNotifications(): Flow<List<NotificationEntity>>

    @Query("SELECT * FROM notifications WHERE folder = :folder ORDER BY timestamp DESC")
    fun getNotificationsByFolder(folder: String): Flow<List<NotificationEntity>>

    @Query("SELECT folder, COUNT(*) as count FROM notifications GROUP BY folder")
    fun getFolderCounts(): Flow<List<FolderCount>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(notification: NotificationEntity)

    @Query("UPDATE notifications SET isRead = 1 WHERE id = :id")
    suspend fun markAsRead(id: String)

    @Query("DELETE FROM notifications WHERE timestamp < :timestamp")
    suspend fun deleteOlderThan(timestamp: Long)

    @Query("DELETE FROM notifications")
    suspend fun deleteAll()

    // Get pending medium priority notifications that haven't been notified yet
    @Query("SELECT * FROM notifications WHERE priority = 2 AND notified = 0 ORDER BY timestamp ASC")
    suspend fun getPendingMediumPriority(): List<NotificationEntity>

    // Mark notifications as notified
    @Query("UPDATE notifications SET notified = 1 WHERE id IN (:ids)")
    suspend fun markAsNotified(ids: List<String>)

    // Mark single notification as notified
    @Query("UPDATE notifications SET notified = 1 WHERE id = :id")
    suspend fun markAsNotified(id: String)

    // Delete all notifications in a specific folder
    @Query("DELETE FROM notifications WHERE folder = :folderName")
    suspend fun deleteByFolder(folderName: String)

    // Update folder name for all notifications when folder is renamed
    @Query("UPDATE notifications SET folder = :newName WHERE folder = :oldName")
    suspend fun updateFolderName(oldName: String, newName: String)
}
