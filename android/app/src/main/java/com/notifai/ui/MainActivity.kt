package com.notifai.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.notifai.ui.screens.folder.FolderDetailScreen
import com.notifai.ui.screens.home.HomeScreen
import com.notifai.ui.screens.settings.SettingsScreen
import com.notifai.ui.screens.test.TestInferenceScreen
import com.notifai.ui.theme.NotifaiTheme
import dagger.hilt.android.AndroidEntryPoint

sealed class Screen(val route: String) {
    data object Home : Screen("home")
    data object Settings : Screen("settings")
    data object TestInference : Screen("test")
    data object FolderDetail : Screen("folder/{folderName}") {
        fun createRoute(folderName: String) = "folder/$folderName"
    }
}

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            NotifaiTheme {
                NotifaiApp()
            }
        }
    }
}

@Composable
fun NotifaiApp() {
    val navController = rememberNavController()

    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier
        ) {
            composable(Screen.Home.route) {
                HomeScreen(
                    onNavigateToSettings = {
                        navController.navigate(Screen.Settings.route)
                    },
                    onNavigateToFolder = { folderName ->
                        navController.navigate(Screen.FolderDetail.createRoute(folderName))
                    },
                    onNavigateToTest = {
                        navController.navigate(Screen.TestInference.route)
                    }
                )
            }

            composable(Screen.Settings.route) {
                SettingsScreen(
                    onBackClick = {
                        navController.popBackStack()
                    }
                )
            }

            composable(Screen.TestInference.route) {
                TestInferenceScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }

            composable(
                route = Screen.FolderDetail.route,
                arguments = listOf(navArgument("folderName") { type = NavType.StringType })
            ) { backStackEntry ->
                val folderName = backStackEntry.arguments?.getString("folderName") ?: ""
                FolderDetailScreen(
                    folderName = folderName,
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
        }
    }
}
