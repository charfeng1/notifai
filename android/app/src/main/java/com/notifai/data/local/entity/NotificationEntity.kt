package com.notifai.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "notifications")
data class NotificationEntity(
    @PrimaryKey val id: String,
    val packageName: String,
    val appName: String,
    val title: String,
    val body: String,
    val timestamp: Long,
    val folder: String,
    val priority: Int,
    val isRead: Boolean = false
)
