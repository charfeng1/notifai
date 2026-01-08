package com.notifai.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "folders")
data class FolderEntity(
    @PrimaryKey val id: String,
    val name: String,
    val description: String,
    val isDefault: Boolean,
    val sortOrder: Int
)
