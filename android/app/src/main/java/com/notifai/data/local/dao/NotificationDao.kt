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
}
