package com.notifai.data.repository

import com.notifai.data.local.dao.FolderDao
import com.notifai.data.local.entity.FolderEntity
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class FolderRepository @Inject constructor(
    private val folderDao: FolderDao
) {
    val allFolders: Flow<List<FolderEntity>> = folderDao.getAllFolders()

    suspend fun insertDefaultFolders() {
        // Descriptions match training data format exactly
        val defaults = listOf(
            FolderEntity(
                id = "work",
                name = "Work",
                description = "Job-related notifications (emails from colleagues, calendar invites, project updates, work apps like Slack, Jira)",
                isDefault = true,
                sortOrder = 0
            ),
            FolderEntity(
                id = "personal",
                name = "Personal",
                description = "Family, friends, personal accounts, social media, messaging from personal contacts",
                isDefault = true,
                sortOrder = 1
            ),
            FolderEntity(
                id = "promotions",
                name = "Promotions",
                description = "Marketing, sales, deals, newsletters, advertisements, discount offers",
                isDefault = true,
                sortOrder = 2
            ),
            FolderEntity(
                id = "alerts",
                name = "Alerts",
                description = "System alerts, security, deliveries, bills, account notifications, reminders",
                isDefault = true,
                sortOrder = 3
            )
        )

        defaults.forEach { folderDao.insert(it) }
    }

    suspend fun insert(folder: FolderEntity) = folderDao.insert(folder)

    suspend fun update(folder: FolderEntity) = folderDao.update(folder)

    suspend fun delete(folder: FolderEntity) = folderDao.delete(folder)
}
