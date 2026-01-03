using System;
using System.Collections.Generic;

namespace TimeLordDashboard.Models
{
    /// <summary>
    /// User preferences and settings
    /// </summary>
    public class UserPreferences
    {
        public Guid UserId { get; set; }
        public string UserName { get; set; } = string.Empty;
        public ThemePreference Theme { get; set; } = ThemePreference.System;
        public bool NotificationsEnabled { get; set; } = true;
        public bool WellbeingRemindersEnabled { get; set; } = true;
        public int BreakReminderInterval { get; set; } = 60; // minutes
        public DashboardLayout Layout { get; set; } = new();
        public Dictionary<string, object> CustomSettings { get; set; } = new();
    }

    public enum ThemePreference
    {
        Light,
        Dark,
        System
    }

    /// <summary>
    /// Dashboard layout configuration
    /// </summary>
    public class DashboardLayout
    {
        public List<WidgetPosition> Widgets { get; set; } = new();
        public int Columns { get; set; } = 3;
        public bool AutoArrange { get; set; } = false;
    }

    /// <summary>
    /// Position and size of a widget on the dashboard
    /// </summary>
    public class WidgetPosition
    {
        public Guid WidgetId { get; set; }
        public string WidgetType { get; set; } = string.Empty;
        public int Column { get; set; }
        public int Row { get; set; }
        public int ColumnSpan { get; set; } = 1;
        public int RowSpan { get; set; } = 1;
        public bool IsVisible { get; set; } = true;
    }
}
