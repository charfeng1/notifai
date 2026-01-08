package com.notifai.data.local.dao

import androidx.room.*
import com.notifai.data.local.entity.FolderEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface FolderDao {
    @Query("SELECT * FROM folders ORDER BY sortOrder ASC")
    fun getAllFolders(): Flow<List<FolderEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(folder: FolderEntity)

    @Update
    suspend fun update(folder: FolderEntity)

    @Delete
    suspend fun delete(folder: FolderEntity)

    @Query("SELECT * FROM folders WHERE isDefault = 1 ORDER BY sortOrder ASC")
    suspend fun getDefaultFolders(): List<FolderEntity>

    @Query("DELETE FROM folders WHERE isDefault = 0")
    suspend fun deleteCustomFolders()
}
