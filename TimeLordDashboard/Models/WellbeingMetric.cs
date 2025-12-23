using System;
using System.Collections.Generic;

namespace TimeLordDashboard.Models
{
    /// <summary>
    /// Represents a wellbeing or health metric
    /// </summary>
    public class WellbeingMetric
    {
        public Guid Id { get; set; }
        public MetricType Type { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Unit { get; set; } = string.Empty;
        public double CurrentValue { get; set; }
        public double TargetValue { get; set; }
        public double MinValue { get; set; }
        public double MaxValue { get; set; }
        public DateTime LastUpdated { get; set; }
        public string IconGlyph { get; set; } = "\uE95E";
        public string Color { get; set; } = "#00B7C3";
        public List<MetricDataPoint> History { get; set; } = new();
    }

    public enum MetricType
    {
        ScreenTime,
        BreakTime,
        Steps,
        HeartRate,
        Sleep,
        Hydration,
        Posture,
        EyeStrain,
        StressLevel,
        Activity,
        Custom
    }

    /// <summary>
    /// Represents a single data point for a metric over time
    /// </summary>
    public class MetricDataPoint
    {
        public DateTime Timestamp { get; set; }
        public double Value { get; set; }
        public string? Note { get; set; }
    }

    /// <summary>
    /// Represents a reminder for wellbeing activities
    /// </summary>
    public class WellbeingReminder
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public ReminderType Type { get; set; }
        public TimeSpan Interval { get; set; }
        public DateTime LastTriggered { get; set; }
        public bool IsEnabled { get; set; }
        public string IconGlyph { get; set; } = "\uE7E7"; // Clock icon
    }

    public enum ReminderType
    {
        TakeBreak,
        DrinkWater,
        Stretch,
        EyeRest,
        PostureCheck,
        Meditation,
        Custom
    }

    /// <summary>
    /// Represents a breathing exercise session
    /// </summary>
    public class BreathingExercise
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public int InhaleSeconds { get; set; } = 4;
        public int HoldSeconds { get; set; } = 4;
        public int ExhaleSeconds { get; set; } = 4;
        public int Cycles { get; set; } = 5;
        public string Description { get; set; } = string.Empty;
    }
}
