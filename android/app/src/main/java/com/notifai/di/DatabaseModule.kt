package com.notifai.di

import android.content.Context
import androidx.room.Room
import com.notifai.data.local.NotifaiDatabase
import com.notifai.data.local.dao.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): NotifaiDatabase {
        return Room.databaseBuilder(
            context,
            NotifaiDatabase::class.java,
            "notifai_db"
        )
            .addMigrations(NotifaiDatabase.MIGRATION_1_2)
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideNotificationDao(db: NotifaiDatabase): NotificationDao = db.notificationDao()

    @Provides
    fun provideFolderDao(db: NotifaiDatabase): FolderDao = db.folderDao()

    @Provides
    fun provideMonitoredAppDao(db: NotifaiDatabase): MonitoredAppDao = db.monitoredAppDao()

    @Provides
    fun provideSettingsDao(db: NotifaiDatabase): SettingsDao = db.settingsDao()
}
