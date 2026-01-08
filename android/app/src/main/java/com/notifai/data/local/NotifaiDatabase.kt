package com.notifai.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import com.notifai.data.local.dao.*
import com.notifai.data.local.entity.*

@Database(
    entities = [
        NotificationEntity::class,
        FolderEntity::class,
        MonitoredAppEntity::class,
        SettingsEntity::class
    ],
    version = 3,
    exportSchema = false
)
abstract class NotifaiDatabase : RoomDatabase() {
    abstract fun notificationDao(): NotificationDao
    abstract fun folderDao(): FolderDao
    abstract fun monitoredAppDao(): MonitoredAppDao
    abstract fun settingsDao(): SettingsDao

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE notifications ADD COLUMN processingTimeMs INTEGER NOT NULL DEFAULT 0")
            }
        }

        val MIGRATION_2_3 = object : Migration(2, 3) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE notifications ADD COLUMN notified INTEGER NOT NULL DEFAULT 0")
            }
        }
    }
}
