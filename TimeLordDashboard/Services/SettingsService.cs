using Microsoft.Data.Sqlite;
using System;
using System.Text.Json;
using TimeLordDashboard.Models;

namespace TimeLordDashboard.Services
{
    /// <summary>
    /// Manages user settings and preferences with database persistence
    /// </summary>
    public class SettingsService
    {
        private static SettingsService? _instance;
        private static readonly object _lock = new();
        private readonly DatabaseService _database;
        private UserPreferences? _currentPreferences;

        public static SettingsService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new SettingsService();
                }
            }
        }

        private SettingsService()
        {
            _database = DatabaseService.Instance;
            LoadPreferences();
        }

        public UserPreferences CurrentPreferences
        {
            get => _currentPreferences ??= GetDefaultPreferences();
            private set => _currentPreferences = value;
        }

        private void LoadPreferences()
        {
            try
            {
                var reader = _database.ExecuteReader("SELECT * FROM UserPreferences LIMIT 1");

                if (reader != null && reader.Read())
                {
                    CurrentPreferences = new UserPreferences
                    {
                        UserId = Guid.Parse(reader["UserId"].ToString() ?? Guid.NewGuid().ToString()),
                        UserName = reader["UserName"].ToString() ?? string.Empty,
                        Theme = (ThemePreference)(int)(long)reader["Theme"],
                        NotificationsEnabled = (long)reader["NotificationsEnabled"] == 1,
                        WellbeingRemindersEnabled = (long)reader["WellbeingRemindersEnabled"] == 1,
                        BreakReminderInterval = (int)(long)reader["BreakReminderInterval"],
                        CustomSettings = DeserializeCustomSettings(reader["CustomSettings"].ToString() ?? "{}")
                    };

                    reader.Close();
                }
                else
                {
                    // No preferences found, create default
                    CurrentPreferences = GetDefaultPreferences();
                    SavePreferences();
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading preferences: {ex.Message}");
                CurrentPreferences = GetDefaultPreferences();
            }
        }

        public void SavePreferences()
        {
            try
            {
                var customSettingsJson = SerializeCustomSettings(CurrentPreferences.CustomSettings);

                _database.ExecuteNonQuery(@"
                    INSERT OR REPLACE INTO UserPreferences
                    (UserId, UserName, Theme, NotificationsEnabled, WellbeingRemindersEnabled,
                     BreakReminderInterval, CustomSettings)
                    VALUES (@UserId, @UserName, @Theme, @NotificationsEnabled,
                            @WellbeingRemindersEnabled, @BreakReminderInterval, @CustomSettings)",
                    new SqliteParameter("@UserId", CurrentPreferences.UserId.ToString()),
                    new SqliteParameter("@UserName", CurrentPreferences.UserName),
                    new SqliteParameter("@Theme", (int)CurrentPreferences.Theme),
                    new SqliteParameter("@NotificationsEnabled", CurrentPreferences.NotificationsEnabled ? 1 : 0),
                    new SqliteParameter("@WellbeingRemindersEnabled", CurrentPreferences.WellbeingRemindersEnabled ? 1 : 0),
                    new SqliteParameter("@BreakReminderInterval", CurrentPreferences.BreakReminderInterval),
                    new SqliteParameter("@CustomSettings", customSettingsJson)
                );

                System.Diagnostics.Debug.WriteLine("Preferences saved successfully");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving preferences: {ex.Message}");
            }
        }

        public void UpdateTheme(ThemePreference theme)
        {
            CurrentPreferences.Theme = theme;
            SavePreferences();
        }

        public void UpdateNotificationsEnabled(bool enabled)
        {
            CurrentPreferences.NotificationsEnabled = enabled;
            SavePreferences();
        }

        public void UpdateWellbeingRemindersEnabled(bool enabled)
        {
            CurrentPreferences.WellbeingRemindersEnabled = enabled;
            SavePreferences();
        }

        public void UpdateBreakReminderInterval(int minutes)
        {
            if (minutes >= 15 && minutes <= 120)
            {
                CurrentPreferences.BreakReminderInterval = minutes;
                SavePreferences();
            }
        }

        public void SetCustomSetting(string key, object value)
        {
            CurrentPreferences.CustomSettings[key] = value;
            SavePreferences();
        }

        public T? GetCustomSetting<T>(string key, T? defaultValue = default)
        {
            if (CurrentPreferences.CustomSettings.TryGetValue(key, out var value))
            {
                try
                {
                    if (value is JsonElement jsonElement)
                    {
                        return JsonSerializer.Deserialize<T>(jsonElement.GetRawText());
                    }
                    return (T)Convert.ChangeType(value, typeof(T));
                }
                catch
                {
                    return defaultValue;
                }
            }
            return defaultValue;
        }

        private UserPreferences GetDefaultPreferences()
        {
            return new UserPreferences
            {
                UserId = Guid.NewGuid(),
                UserName = Environment.UserName,
                Theme = ThemePreference.System,
                NotificationsEnabled = true,
                WellbeingRemindersEnabled = true,
                BreakReminderInterval = 60,
                Layout = new DashboardLayout
                {
                    Columns = 3,
                    AutoArrange = false
                }
            };
        }

        private string SerializeCustomSettings(System.Collections.Generic.Dictionary<string, object> settings)
        {
            try
            {
                return JsonSerializer.Serialize(settings);
            }
            catch
            {
                return "{}";
            }
        }

        private System.Collections.Generic.Dictionary<string, object> DeserializeCustomSettings(string json)
        {
            try
            {
                return JsonSerializer.Deserialize<System.Collections.Generic.Dictionary<string, object>>(json)
                    ?? new System.Collections.Generic.Dictionary<string, object>();
            }
            catch
            {
                return new System.Collections.Generic.Dictionary<string, object>();
            }
        }

        public void ExportSettings(string filePath)
        {
            try
            {
                var json = JsonSerializer.Serialize(CurrentPreferences, new JsonSerializerOptions
                {
                    WriteIndented = true
                });

                System.IO.File.WriteAllText(filePath, json);
                System.Diagnostics.Debug.WriteLine($"Settings exported to {filePath}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error exporting settings: {ex.Message}");
                throw;
            }
        }

        public void ImportSettings(string filePath)
        {
            try
            {
                var json = System.IO.File.ReadAllText(filePath);
                var preferences = JsonSerializer.Deserialize<UserPreferences>(json);

                if (preferences != null)
                {
                    CurrentPreferences = preferences;
                    SavePreferences();
                    System.Diagnostics.Debug.WriteLine($"Settings imported from {filePath}");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error importing settings: {ex.Message}");
                throw;
            }
        }

        public void ResetToDefaults()
        {
            CurrentPreferences = GetDefaultPreferences();
            SavePreferences();
        }
    }
}
