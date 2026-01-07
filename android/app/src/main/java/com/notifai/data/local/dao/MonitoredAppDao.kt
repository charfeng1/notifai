package com.notifai.data.local.dao

import androidx.room.*
import com.notifai.data.local.entity.MonitoredAppEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface MonitoredAppDao {
    @Query("SELECT * FROM monitored_apps ORDER BY appName ASC")
    fun getAllApps(): Flow<List<MonitoredAppEntity>>

    @Query("SELECT * FROM monitored_apps")
    suspend fun getAllAppsOnce(): List<MonitoredAppEntity>

    @Query("SELECT * FROM monitored_apps WHERE packageName = :packageName")
    suspend fun getApp(packageName: String): MonitoredAppEntity?

    @Query("SELECT isEnabled FROM monitored_apps WHERE packageName = :packageName")
    suspend fun isAppMonitored(packageName: String): Boolean?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(app: MonitoredAppEntity)

    @Update
    suspend fun update(app: MonitoredAppEntity)

    @Query("DELETE FROM monitored_apps")
    suspend fun deleteAll()
}
