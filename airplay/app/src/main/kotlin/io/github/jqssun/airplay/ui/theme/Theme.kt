package io.github.jqssun.airplay.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Personal night palette; affects this app only.
@Composable
fun AirPlayTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Color(0xFF7ED7FF),
            onPrimary = Color(0xFF00283B),
            primaryContainer = Color(0xFF164764),
            onPrimaryContainer = Color(0xFFD4F1FF),
            secondary = Color(0xFFB6C9E6),
            background = Color(0xFF080F20),
            onBackground = Color(0xFFEDF4FF),
            surface = Color(0xFF0B1730),
            onSurface = Color(0xFFEDF4FF),
            surfaceVariant = Color(0xFF24334B),
            onSurfaceVariant = Color(0xFFBDCCE3)
        ),
        content = content
    )
}
