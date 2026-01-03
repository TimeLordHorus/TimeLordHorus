using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Threading.Tasks;
using TimeLordDashboard.Helpers;
using TimeLordDashboard.Models;
using TimeLordDashboard.Services;

namespace TimeLordDashboard.ViewModels
{
    public partial class SettingsViewModel : ObservableObject
    {
        private readonly SettingsService _settingsService;
        private readonly ExportImportService _exportImportService;

        [ObservableProperty]
        private int selectedThemeIndex;

        [ObservableProperty]
        private bool notificationsEnabled;

        [ObservableProperty]
        private bool wellbeingRemindersEnabled;

        [ObservableProperty]
        private bool soundNotificationsEnabled;

        [ObservableProperty]
        private bool transparencyEffectsEnabled;

        [ObservableProperty]
        private double breakReminderInterval;

        [ObservableProperty]
        private double eyeRestReminderInterval;

        [ObservableProperty]
        private double dailyScreenTimeGoal;

        [ObservableProperty]
        private int dailyWaterGoal;

        [ObservableProperty]
        private bool showFileThumbnails;

        [ObservableProperty]
        private bool autoOrganizeFiles;

        [ObservableProperty]
        private int maxRecentFiles;

        [ObservableProperty]
        private int selectedFileViewIndex;

        [ObservableProperty]
        private bool collectAnalytics;

        [ObservableProperty]
        private string appVersion = "1.0.0";

        public SettingsViewModel()
        {
            _settingsService = SettingsService.Instance;
            _exportImportService = ExportImportService.Instance;

            LoadSettings();
        }

        private void LoadSettings()
        {
            var prefs = _settingsService.CurrentPreferences;

            SelectedThemeIndex = (int)prefs.Theme;
            NotificationsEnabled = prefs.NotificationsEnabled;
            WellbeingRemindersEnabled = prefs.WellbeingRemindersEnabled;
            BreakReminderInterval = prefs.BreakReminderInterval;

            // Load custom settings
            SoundNotificationsEnabled = _settingsService.GetCustomSetting("SoundNotifications", false);
            TransparencyEffectsEnabled = _settingsService.GetCustomSetting("TransparencyEffects", true);
            EyeRestReminderInterval = _settingsService.GetCustomSetting("EyeRestInterval", 20.0);
            DailyScreenTimeGoal = _settingsService.GetCustomSetting("DailyScreenTimeGoal", 8.0);
            DailyWaterGoal = _settingsService.GetCustomSetting("DailyWaterGoal", 8);
            ShowFileThumbnails = _settingsService.GetCustomSetting("ShowFileThumbnails", true);
            AutoOrganizeFiles = _settingsService.GetCustomSetting("AutoOrganizeFiles", true);
            MaxRecentFiles = _settingsService.GetCustomSetting("MaxRecentFiles", 20);
            SelectedFileViewIndex = _settingsService.GetCustomSetting("FileViewIndex", 0);
            CollectAnalytics = _settingsService.GetCustomSetting("CollectAnalytics", true);
        }

        partial void OnSelectedThemeIndexChanged(int value)
        {
            var theme = (ThemePreference)value;
            _settingsService.UpdateTheme(theme);
            ThemeHelper.ApplyTheme(theme);
        }

        partial void OnNotificationsEnabledChanged(bool value)
        {
            _settingsService.UpdateNotificationsEnabled(value);
        }

        partial void OnWellbeingRemindersEnabledChanged(bool value)
        {
            _settingsService.UpdateWellbeingRemindersEnabled(value);
        }

        partial void OnSoundNotificationsEnabledChanged(bool value)
        {
            _settingsService.SetCustomSetting("SoundNotifications", value);
        }

        partial void OnTransparencyEffectsEnabledChanged(bool value)
        {
            _settingsService.SetCustomSetting("TransparencyEffects", value);
        }

        partial void OnBreakReminderIntervalChanged(double value)
        {
            _settingsService.UpdateBreakReminderInterval((int)value);
        }

        partial void OnEyeRestReminderIntervalChanged(double value)
        {
            _settingsService.SetCustomSetting("EyeRestInterval", value);
        }

        partial void OnDailyScreenTimeGoalChanged(double value)
        {
            _settingsService.SetCustomSetting("DailyScreenTimeGoal", value);
        }

        partial void OnDailyWaterGoalChanged(int value)
        {
            _settingsService.SetCustomSetting("DailyWaterGoal", value);
        }

        partial void OnShowFileThumbnailsChanged(bool value)
        {
            _settingsService.SetCustomSetting("ShowFileThumbnails", value);
        }

        partial void OnAutoOrganizeFilesChanged(bool value)
        {
            _settingsService.SetCustomSetting("AutoOrganizeFiles", value);
        }

        partial void OnMaxRecentFilesChanged(int value)
        {
            _settingsService.SetCustomSetting("MaxRecentFiles", value);
        }

        partial void OnSelectedFileViewIndexChanged(int value)
        {
            _settingsService.SetCustomSetting("FileViewIndex", value);
        }

        partial void OnCollectAnalyticsChanged(bool value)
        {
            _settingsService.SetCustomSetting("CollectAnalytics", value);
        }

        [RelayCommand]
        private async Task ExportDataAsync()
        {
            try
            {
                var file = await _exportImportService.PickExportFileAsync(
                    $"TimeLordData_{DateTime.Now:yyyyMMdd}.json",
                    "JSON Files",
                    ".json");

                if (file != null)
                {
                    var success = await _exportImportService.ExportAllDataAsync(file);

                    if (success)
                    {
                        NotificationService.Instance.ShowSimpleNotification(
                            "Export Successful",
                            $"Your data has been exported to {file.Name}");
                    }
                }
            }
            catch (Exception ex)
            {
                NotificationService.Instance.ShowSimpleNotification(
                    "Export Failed",
                    $"Error: {ex.Message}");
            }
        }

        [RelayCommand]
        private async Task ExportMetricsCsvAsync()
        {
            try
            {
                var file = await _exportImportService.PickExportFileAsync(
                    $"WellbeingMetrics_{DateTime.Now:yyyyMMdd}.csv",
                    "CSV Files",
                    ".csv");

                if (file != null)
                {
                    var success = await _exportImportService.ExportMetricsToCsvAsync(file);

                    if (success)
                    {
                        NotificationService.Instance.ShowSimpleNotification(
                            "Export Successful",
                            $"Metrics exported to {file.Name}");
                    }
                }
            }
            catch (Exception ex)
            {
                NotificationService.Instance.ShowSimpleNotification(
                    "Export Failed",
                    $"Error: {ex.Message}");
            }
        }

        [RelayCommand]
        private async Task ClearAllDataAsync()
        {
            // TODO: Show confirmation dialog
            // For now, just log
            System.Diagnostics.Debug.WriteLine("Clear all data requested");

            NotificationService.Instance.ShowSimpleNotification(
                "Clear Data",
                "This feature requires user confirmation dialog");
        }

        [RelayCommand]
        private void ResetToDefaults()
        {
            _settingsService.ResetToDefaults();
            LoadSettings();

            NotificationService.Instance.ShowSimpleNotification(
                "Settings Reset",
                "All settings have been reset to defaults");
        }
    }
}
