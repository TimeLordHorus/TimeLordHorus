using System;
using System.Collections.Generic;

namespace TimeLordDashboard.Models
{
    /// <summary>
    /// Represents a daily task or goal
    /// </summary>
    public class ProductivityTask
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public TaskPriority Priority { get; set; }
        public TaskStatus Status { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? CompletedAt { get; set; }
        public DateTime? DueDate { get; set; }
        public int EstimatedMinutes { get; set; }
        public int ActualMinutes { get; set; }
        public string Category { get; set; } = "General";
        public List<string> Tags { get; set; } = new();
    }

    public enum TaskPriority
    {
        Low,
        Medium,
        High,
        Urgent
    }

    public enum TaskStatus
    {
        NotStarted,
        InProgress,
        Completed,
        Cancelled
    }

    /// <summary>
    /// Represents a focused work session (Pomodoro-style)
    /// </summary>
    public class FocusSession
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = "Focus Session";
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public int PlannedMinutes { get; set; } = 25; // Default Pomodoro
        public int ActualMinutes { get; set; }
        public SessionType Type { get; set; }
        public bool WasInterrupted { get; set; }
        public string Notes { get; set; } = string.Empty;
        public Guid? TaskId { get; set; } // Linked task if any
    }

    public enum SessionType
    {
        Focus,      // 25 min
        ShortBreak, // 5 min
        LongBreak,  // 15 min
        DeepWork    // 90 min
    }

    /// <summary>
    /// Represents a productivity goal
    /// </summary>
    public class ProductivityGoal
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public GoalType Type { get; set; }
        public double TargetValue { get; set; }
        public double CurrentValue { get; set; }
        public string Unit { get; set; } = string.Empty;
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public GoalStatus Status { get; set; }
        public string IconGlyph { get; set; } = "\uE8F4";
    }

    public enum GoalType
    {
        Daily,
        Weekly,
        Monthly,
        Custom
    }

    public enum GoalStatus
    {
        Active,
        Completed,
        Failed,
        Paused
    }

    /// <summary>
    /// Daily productivity summary
    /// </summary>
    public class ProductivitySummary
    {
        public DateTime Date { get; set; }
        public int TotalFocusMinutes { get; set; }
        public int TasksCompleted { get; set; }
        public int TasksCreated { get; set; }
        public double ProductivityScore { get; set; } // 0-100
        public int FocusSessionsCompleted { get; set; }
        public int DistractionsCount { get; set; }
        public TimeSpan DeepWorkTime { get; set; }
        public Dictionary<string, int> CategoryBreakdown { get; set; } = new();
    }

    /// <summary>
    /// Productivity streak tracking
    /// </summary>
    public class ProductivityStreak
    {
        public int CurrentStreak { get; set; }
        public int LongestStreak { get; set; }
        public DateTime? LastProductiveDay { get; set; }
        public int TotalProductiveDays { get; set; }
    }

    /// <summary>
    /// Time block for scheduling
    /// </summary>
    public class TimeBlock
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public string Color { get; set; } = "#0078D4";
        public BlockType Type { get; set; }
        public bool IsRecurring { get; set; }
        public Guid? TaskId { get; set; }
    }

    public enum BlockType
    {
        Focus,
        Meeting,
        Break,
        Learning,
        Email,
        Other
    }
}
