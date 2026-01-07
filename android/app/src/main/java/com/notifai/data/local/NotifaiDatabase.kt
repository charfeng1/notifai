package com.notifai.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.notifai.data.local.dao.*
import com.notifai.data.local.entity.*

@Database(
    entities = [
        NotificationEntity::class,
        FolderEntity::class,
        MonitoredAppEntity::class,
        SettingsEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class NotifaiDatabase : RoomDatabase() {
    abstract fun notificationDao(): NotificationDao
    abstract fun folderDao(): FolderDao
    abstract fun monitoredAppDao(): MonitoredAppDao
    abstract fun settingsDao(): SettingsDao
}
