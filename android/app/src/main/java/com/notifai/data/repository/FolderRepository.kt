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
        val defaults = listOf(
            FolderEntity(
                id = "work",
                name = "Work",
                description = "Professional messages from work apps like Slack, Jira, Teams, work email, Feishu, DingTalk",
                isDefault = true,
                sortOrder = 0
            ),
            FolderEntity(
                id = "personal",
                name = "Personal",
                description = "Messages from friends and family via WhatsApp, WeChat, Telegram, Douyin, RedNote",
                isDefault = true,
                sortOrder = 1
            ),
            FolderEntity(
                id = "promotions",
                name = "Promotions",
                description = "Marketing, deals, spam, promotional content from shopping and service apps",
                isDefault = true,
                sortOrder = 2
            ),
            FolderEntity(
                id = "alerts",
                name = "Alerts",
                description = "Banking, security, system notifications, delivery updates, transactional messages",
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
