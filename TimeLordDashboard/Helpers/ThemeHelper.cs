using Microsoft.UI.Xaml;
using System;
using TimeLordDashboard.Models;
using Windows.UI.ViewManagement;

namespace TimeLordDashboard.Helpers
{
    /// <summary>
    /// Helper class for managing application theme
    /// </summary>
    public static class ThemeHelper
    {
        private static Window? _mainWindow;

        public static void Initialize(Window mainWindow)
        {
            _mainWindow = mainWindow;
        }

        /// <summary>
        /// Apply theme based on user preference
        /// </summary>
        public static void ApplyTheme(ThemePreference preference)
        {
            if (_mainWindow?.Content is FrameworkElement rootElement)
            {
                switch (preference)
                {
                    case ThemePreference.Light:
                        rootElement.RequestedTheme = ElementTheme.Light;
                        break;

                    case ThemePreference.Dark:
                        rootElement.RequestedTheme = ElementTheme.Dark;
                        break;

                    case ThemePreference.System:
                    default:
                        rootElement.RequestedTheme = GetSystemTheme();
                        break;
                }

                System.Diagnostics.Debug.WriteLine($"Theme applied: {preference}");
            }
        }

        /// <summary>
        /// Get the current system theme
        /// </summary>
        public static ElementTheme GetSystemTheme()
        {
            var uiSettings = new UISettings();
            var color = uiSettings.GetColorValue(UIColorType.Background);

            // If background is dark, use dark theme
            return (color.R + color.G + color.B) / 3 < 128
                ? ElementTheme.Dark
                : ElementTheme.Light;
        }

        /// <summary>
        /// Get current theme as string
        /// </summary>
        public static string GetCurrentThemeString()
        {
            if (_mainWindow?.Content is FrameworkElement rootElement)
            {
                return rootElement.ActualTheme switch
                {
                    ElementTheme.Light => "Light",
                    ElementTheme.Dark => "Dark",
                    _ => "Default"
                };
            }

            return "Default";
        }

        /// <summary>
        /// Check if current theme is dark
        /// </summary>
        public static bool IsDarkTheme()
        {
            if (_mainWindow?.Content is FrameworkElement rootElement)
            {
                return rootElement.ActualTheme == ElementTheme.Dark;
            }

            return false;
        }

        /// <summary>
        /// Toggle between light and dark theme
        /// </summary>
        public static void ToggleTheme()
        {
            if (_mainWindow?.Content is FrameworkElement rootElement)
            {
                var newTheme = rootElement.ActualTheme == ElementTheme.Light
                    ? ElementTheme.Dark
                    : ElementTheme.Light;

                rootElement.RequestedTheme = newTheme;
                System.Diagnostics.Debug.WriteLine($"Theme toggled to: {newTheme}");
            }
        }

        /// <summary>
        /// Apply Mica background material (Windows 11)
        /// </summary>
        public static void ApplyMicaBackground(Window window)
        {
            try
            {
                // Get window handle
                var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(window);

                // Apply Mica backdrop
                if (Microsoft.UI.Composition.SystemBackdrops.MicaController.IsSupported())
                {
                    var micaController = new Microsoft.UI.Composition.SystemBackdrops.MicaController();
                    micaController.SetSystemBackdropConfiguration(
                        new Microsoft.UI.Composition.SystemBackdrops.SystemBackdropConfiguration
                        {
                            IsInputActive = true
                        });

                    System.Diagnostics.Debug.WriteLine("Mica background applied");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying Mica: {ex.Message}");
            }
        }
    }
}
