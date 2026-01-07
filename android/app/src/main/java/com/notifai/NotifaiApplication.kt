package com.notifai

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class NotifaiApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        // Application initialization
        // Model will be lazy-initialized on first classification
    }
}
