package com.notifai.data.repository

import com.notifai.data.local.dao.SettingsDao
import com.notifai.data.local.entity.SettingsEntity
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SettingsRepository @Inject constructor(
    private val settingsDao: SettingsDao
) {
    companion object {
        const val KEY_PERSONAL_INSTRUCTIONS = "personal_instructions"
    }

    suspend fun getPersonalInstructions(): String? =
        settingsDao.getValue(KEY_PERSONAL_INSTRUCTIONS)

    suspend fun setPersonalInstructions(instructions: String) =
        settingsDao.insert(SettingsEntity(KEY_PERSONAL_INSTRUCTIONS, instructions))
}
