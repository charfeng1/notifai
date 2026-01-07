package com.notifai.data.repository

import android.content.Context
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import com.notifai.data.local.dao.MonitoredAppDao
import com.notifai.data.local.entity.MonitoredAppEntity
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class MonitoredAppRepository @Inject constructor(
    private val monitoredAppDao: MonitoredAppDao,
    @ApplicationContext private val context: Context
) {
    val allApps: Flow<List<MonitoredAppEntity>> = monitoredAppDao.getAllApps()

    suspend fun isAppMonitored(packageName: String): Boolean {
        return monitoredAppDao.isAppMonitored(packageName) ?: false
    }

    suspend fun loadInstalledApps() {
        val pm = context.packageManager
        val apps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            .filter { it.flags and ApplicationInfo.FLAG_SYSTEM == 0 } // User apps only
            .map { appInfo ->
                MonitoredAppEntity(
                    packageName = appInfo.packageName,
                    appName = pm.getApplicationLabel(appInfo).toString(),
                    isEnabled = false // Default: opt-in
                )
            }

        apps.forEach { monitoredAppDao.insert(it) }
    }

    suspend fun toggleApp(packageName: String, enabled: Boolean) {
        val app = allApps.value?.find { it.packageName == packageName }
        app?.let {
            monitoredAppDao.update(it.copy(isEnabled = enabled))
        }
    }
}
