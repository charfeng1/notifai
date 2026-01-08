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
        val result = monitoredAppDao.isAppMonitored(packageName) ?: false
        android.util.Log.d("MonitoredAppRepository", "isAppMonitored($packageName) = $result")
        return result
    }

    suspend fun loadInstalledApps() {
        val pm = context.packageManager

        android.util.Log.w("MonitoredAppRepository", "=== STARTING APP SCAN ===")

        val existingApps = monitoredAppDao.getAllAppsOnce()
        val existingByPackage = existingApps.associateBy { it.packageName }

        // Get all installed packages with launch intent (user-launchable apps)
        val launchIntent = android.content.Intent(android.content.Intent.ACTION_MAIN, null)
        launchIntent.addCategory(android.content.Intent.CATEGORY_LAUNCHER)

        // Use MATCH_ALL flag to get all apps including disabled/hidden ones
        val flags = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
            PackageManager.MATCH_ALL
        } else {
            PackageManager.GET_META_DATA
        }

        val allResolveInfos = pm.queryIntentActivities(launchIntent, flags)
        android.util.Log.w("MonitoredAppRepository", "Total launcher activities found (with MATCH_ALL): ${allResolveInfos.size}")

        val apps = allResolveInfos
            .mapNotNull { resolveInfo ->
                try {
                    val appInfo = resolveInfo.activityInfo.applicationInfo
                    val appName = pm.getApplicationLabel(appInfo).toString()
                    val isSystem = (appInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0
                    val isUpdatedSystem = (appInfo.flags and ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0

                    val shouldInclude = !isSystem || isUpdatedSystem

                    android.util.Log.w("MonitoredAppRepository",
                        "App: $appName | Package: ${appInfo.packageName} | System: $isSystem | UpdatedSystem: $isUpdatedSystem | Include: $shouldInclude")

                    if (!shouldInclude) {
                        return@mapNotNull null
                    }

                    val existing = existingByPackage[appInfo.packageName]
                    MonitoredAppEntity(
                        packageName = appInfo.packageName,
                        appName = appName,
                        isEnabled = existing?.isEnabled ?: false // Preserve user selection
                    )
                } catch (e: Exception) {
                    android.util.Log.e("MonitoredAppRepository", "Error loading app: ${e.message}", e)
                    null
                }
            }
            .distinctBy { it.packageName } // Remove duplicates
            .sortedBy { it.appName }

        android.util.Log.w("MonitoredAppRepository", "=== FILTERED TO ${apps.size} USER APPS ===")

        // Batch insert for atomicity
        apps.forEachIndexed { index, app ->
            android.util.Log.d("MonitoredAppRepository", "${index + 1}. Inserting: ${app.appName} (${app.packageName})")
            monitoredAppDao.insert(app)
        }

        android.util.Log.w("MonitoredAppRepository", "=== INSERTION COMPLETE ===")
    }

    suspend fun toggleApp(packageName: String, enabled: Boolean) {
        android.util.Log.w("MonitoredAppRepository", "toggleApp($packageName, $enabled)")
        val app = monitoredAppDao.getApp(packageName)
        if (app == null) {
            android.util.Log.e("MonitoredAppRepository", "toggleApp: App $packageName not found in database!")
            return
        }
        android.util.Log.d("MonitoredAppRepository", "toggleApp: Updating ${app.appName} from isEnabled=${app.isEnabled} to $enabled")
        monitoredAppDao.update(app.copy(isEnabled = enabled))
        android.util.Log.d("MonitoredAppRepository", "toggleApp: Update complete")
    }

    suspend fun clearAll() {
        android.util.Log.w("MonitoredAppRepository", "=== CLEARING ALL APPS FROM DATABASE ===")
        monitoredAppDao.deleteAll()
        android.util.Log.w("MonitoredAppRepository", "=== DATABASE CLEARED ===")
    }
}
