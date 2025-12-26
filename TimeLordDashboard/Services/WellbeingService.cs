using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using TimeLordDashboard.Models;
using Microsoft.UI.Dispatching;

namespace TimeLordDashboard.Services
{
    /// <summary>
    /// Manages wellbeing metrics, reminders, and health tracking
    /// </summary>
    public class WellbeingService
    {
        private static WellbeingService? _instance;
        private static readonly object _lock = new();
        private readonly DispatcherQueue _dispatcher;

        public ObservableCollection<WellbeingMetric> Metrics { get; } = new();
        public ObservableCollection<WellbeingReminder> Reminders { get; } = new();

        private DateTime _sessionStartTime;
        private DateTime _lastBreakTime;

        public static WellbeingService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new WellbeingService();
                }
            }
        }

        private WellbeingService()
        {
            _dispatcher = DispatcherQueue.GetForCurrentThread();
            _sessionStartTime = DateTime.Now;
            _lastBreakTime = DateTime.Now;

            InitializeDefaultMetrics();
            InitializeDefaultReminders();
            StartTracking();
        }

        private void InitializeDefaultMetrics()
        {
            Metrics.Add(new WellbeingMetric
            {
                Id = Guid.NewGuid(),
                Type = MetricType.ScreenTime,
                Name = "Screen Time",
                Unit = "minutes",
                CurrentValue = 0,
                TargetValue = 480, // 8 hours max recommended
                MinValue = 0,
                MaxValue = 1440,
                IconGlyph = "\uE7F4",
                Color = "#0078D4",
                LastUpdated = DateTime.Now
            });

            Metrics.Add(new WellbeingMetric
            {
                Id = Guid.NewGuid(),
                Type = MetricType.BreakTime,
                Name = "Break Time",
                Unit = "minutes",
                CurrentValue = 0,
                TargetValue = 60, // 1 hour of breaks
                MinValue = 0,
                MaxValue = 480,
                IconGlyph = "\uE823",
                Color = "#107C10",
                LastUpdated = DateTime.Now
            });

            Metrics.Add(new WellbeingMetric
            {
                Id = Guid.NewGuid(),
                Type = MetricType.Hydration,
                Name = "Water Intake",
                Unit = "glasses",
                CurrentValue = 0,
                TargetValue = 8, // 8 glasses per day
                MinValue = 0,
                MaxValue = 15,
                IconGlyph = "\uE7B8",
                Color = "#00B7C3",
                LastUpdated = DateTime.Now
            });

            Metrics.Add(new WellbeingMetric
            {
                Id = Guid.NewGuid(),
                Type = MetricType.Posture,
                Name = "Posture Check",
                Unit = "score",
                CurrentValue = 85,
                TargetValue = 90,
                MinValue = 0,
                MaxValue = 100,
                IconGlyph = "\uE77B",
                Color = "#8E8CD8",
                LastUpdated = DateTime.Now
            });

            Metrics.Add(new WellbeingMetric
            {
                Id = Guid.NewGuid(),
                Type = MetricType.StressLevel,
                Name = "Stress Level",
                Unit = "level",
                CurrentValue = 3,
                TargetValue = 2, // Lower is better
                MinValue = 0,
                MaxValue = 10,
                IconGlyph = "\uE7C5",
                Color = "#E81123",
                LastUpdated = DateTime.Now
            });
        }

        private void InitializeDefaultReminders()
        {
            Reminders.Add(new WellbeingReminder
            {
                Id = Guid.NewGuid(),
                Title = "Take a Break",
                Description = "Stand up, stretch, and rest your eyes for 5 minutes",
                Type = ReminderType.TakeBreak,
                Interval = TimeSpan.FromMinutes(60),
                IsEnabled = true,
                IconGlyph = "\uE823",
                LastTriggered = DateTime.Now
            });

            Reminders.Add(new WellbeingReminder
            {
                Id = Guid.NewGuid(),
                Title = "Drink Water",
                Description = "Stay hydrated! Time for a glass of water",
                Type = ReminderType.DrinkWater,
                Interval = TimeSpan.FromMinutes(45),
                IsEnabled = true,
                IconGlyph = "\uE7B8",
                LastTriggered = DateTime.Now
            });

            Reminders.Add(new WellbeingReminder
            {
                Id = Guid.NewGuid(),
                Title = "Eye Rest",
                Description = "Follow the 20-20-20 rule: Look at something 20 feet away for 20 seconds",
                Type = ReminderType.EyeRest,
                Interval = TimeSpan.FromMinutes(20),
                IsEnabled = true,
                IconGlyph = "\uE7B3",
                LastTriggered = DateTime.Now
            });

            Reminders.Add(new WellbeingReminder
            {
                Id = Guid.NewGuid(),
                Title = "Posture Check",
                Description = "Check your sitting posture and adjust if needed",
                Type = ReminderType.PostureCheck,
                Interval = TimeSpan.FromMinutes(30),
                IsEnabled = true,
                IconGlyph = "\uE77B",
                LastTriggered = DateTime.Now
            });
        }

        private void StartTracking()
        {
            // Start a background task to track screen time
            Task.Run(async () =>
            {
                while (true)
                {
                    await Task.Delay(TimeSpan.FromMinutes(1)); // Update every minute

                    _dispatcher.TryEnqueue(() =>
                    {
                        UpdateScreenTime();
                        CheckReminders();
                    });
                }
            });
        }

        private void UpdateScreenTime()
        {
            var screenTimeMetric = Metrics.FirstOrDefault(m => m.Type == MetricType.ScreenTime);
            if (screenTimeMetric != null)
            {
                var sessionDuration = DateTime.Now - _sessionStartTime;
                screenTimeMetric.CurrentValue = sessionDuration.TotalMinutes;
                screenTimeMetric.LastUpdated = DateTime.Now;

                // Add data point
                screenTimeMetric.History.Add(new MetricDataPoint
                {
                    Timestamp = DateTime.Now,
                    Value = screenTimeMetric.CurrentValue
                });

                // Keep only last 24 hours of data
                var cutoff = DateTime.Now.AddHours(-24);
                screenTimeMetric.History.RemoveAll(dp => dp.Timestamp < cutoff);
            }
        }

        private void CheckReminders()
        {
            foreach (var reminder in Reminders.Where(r => r.IsEnabled))
            {
                var timeSinceLastTrigger = DateTime.Now - reminder.LastTriggered;

                if (timeSinceLastTrigger >= reminder.Interval)
                {
                    // Show Windows notification
                    NotificationService.Instance.ShowReminderNotification(reminder);
                    reminder.LastTriggered = DateTime.Now;
                    System.Diagnostics.Debug.WriteLine($"Reminder triggered: {reminder.Title}");
                }
            }
        }

        public void UpdateMetric(MetricType type, double value)
        {
            var metric = Metrics.FirstOrDefault(m => m.Type == type);
            if (metric != null)
            {
                metric.CurrentValue = value;
                metric.LastUpdated = DateTime.Now;

                metric.History.Add(new MetricDataPoint
                {
                    Timestamp = DateTime.Now,
                    Value = value
                });

                // Keep only last 7 days of data
                var cutoff = DateTime.Now.AddDays(-7);
                metric.History.RemoveAll(dp => dp.Timestamp < cutoff);
            }
        }

        public void LogBreak(int durationMinutes)
        {
            _lastBreakTime = DateTime.Now;

            var breakMetric = Metrics.FirstOrDefault(m => m.Type == MetricType.BreakTime);
            if (breakMetric != null)
            {
                breakMetric.CurrentValue += durationMinutes;
                breakMetric.LastUpdated = DateTime.Now;

                breakMetric.History.Add(new MetricDataPoint
                {
                    Timestamp = DateTime.Now,
                    Value = breakMetric.CurrentValue
                });
            }
        }

        public List<MetricDataPoint> GetMetricHistory(MetricType type, TimeSpan duration)
        {
            var metric = Metrics.FirstOrDefault(m => m.Type == type);
            if (metric == null) return new List<MetricDataPoint>();

            var cutoff = DateTime.Now - duration;
            return metric.History.Where(dp => dp.Timestamp >= cutoff).ToList();
        }

        public double GetAverageMetric(MetricType type, TimeSpan duration)
        {
            var history = GetMetricHistory(type, duration);
            return history.Any() ? history.Average(dp => dp.Value) : 0;
        }
    }
}
