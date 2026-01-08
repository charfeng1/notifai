package com.notifai.ui.theme

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector

data class FolderStyle(
    val color: Color,
    val colorLight: Color,
    val colorDark: Color,
    val icon: ImageVector
)

object FolderStyleProvider {

    private val defaultStyles = mapOf(
        "Work" to FolderStyle(WorkColor, WorkColorLight, WorkColorDark, Icons.Rounded.Work),
        "Personal" to FolderStyle(PersonalColor, PersonalColorLight, PersonalColorDark, Icons.Rounded.Person),
        "Promotions" to FolderStyle(PromotionsColor, PromotionsColorLight, PromotionsColorDark, Icons.Rounded.LocalOffer),
        "Alerts" to FolderStyle(AlertsColor, AlertsColorLight, AlertsColorDark, Icons.Rounded.Warning)
    )

    private val customPalette = listOf(
        FolderStyle(CustomPurple, CustomPurpleLight, CustomPurpleDark, Icons.Rounded.Folder),
        FolderStyle(CustomPink, CustomPinkLight, CustomPinkDark, Icons.Rounded.Favorite),
        FolderStyle(CustomCyan, CustomCyanLight, CustomCyanDark, Icons.Rounded.Cloud),
        FolderStyle(CustomOrange, CustomOrangeLight, CustomOrangeDark, Icons.Rounded.Star),
        FolderStyle(CustomTeal, CustomTealLight, CustomTealDark, Icons.Rounded.Eco),
        FolderStyle(CustomIndigo, CustomIndigoLight, CustomIndigoDark, Icons.Rounded.Bookmark),
        FolderStyle(CustomRose, CustomRoseLight, CustomRoseDark, Icons.Rounded.FavoriteBorder),
        FolderStyle(CustomLime, CustomLimeLight, CustomLimeDark, Icons.Rounded.Lightbulb)
    )

    /**
     * Get style for a folder. Uses hash-based approach for custom folders
     * to ensure consistent colors across the app.
     */
    fun getStyle(folderName: String, sortOrder: Int): FolderStyle {
        return defaultStyles[folderName] ?: getStyleByName(folderName)
    }

    fun getColorForFolder(folderName: String): Color {
        return defaultStyles[folderName]?.color
            ?: customPalette[(folderName.hashCode() and Int.MAX_VALUE) % customPalette.size].color
    }

    /**
     * Get style for a folder by name only (uses hash for custom folders).
     * Use this when sortOrder is not available.
     */
    fun getStyleByName(folderName: String): FolderStyle {
        return defaultStyles[folderName]
            ?: customPalette[(folderName.hashCode() and Int.MAX_VALUE) % customPalette.size]
    }
}
