package com.notifai.data.local.dao

import androidx.room.*
import com.notifai.data.local.entity.SettingsEntity

@Dao
interface SettingsDao {
    @Query("SELECT value FROM settings WHERE key = :key")
    suspend fun getValue(key: String): String?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(setting: SettingsEntity)

    @Query("DELETE FROM settings WHERE key = :key")
    suspend fun delete(key: String)
}
