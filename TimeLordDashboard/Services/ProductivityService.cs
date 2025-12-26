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
    /// Manages productivity tracking including tasks, focus sessions, and goals
    /// </summary>
    public class ProductivityService
    {
        private static ProductivityService? _instance;
        private static readonly object _lock = new();
        private readonly DispatcherQueue? _dispatcher;

        public ObservableCollection<ProductivityTask> TodayTasks { get; } = new();
        public ObservableCollection<FocusSession> FocusSessions { get; } = new();
        public ObservableCollection<ProductivityGoal> ActiveGoals { get; } = new();
        public ObservableCollection<TimeBlock> TodaySchedule { get; } = new();

        private FocusSession? _currentSession;
        private DateTime _sessionStartTime;
        private System.Threading.Timer? _sessionTimer;

        public static ProductivityService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new ProductivityService();
                }
            }
        }

        private ProductivityService()
        {
            _dispatcher = DispatcherQueue.GetForCurrentThread();
            InitializeDefaultData();
        }

        private void InitializeDefaultData()
        {
            // Sample tasks for today
            TodayTasks.Add(new ProductivityTask
            {
                Id = Guid.NewGuid(),
                Title = "Review dashboard implementation",
                Priority = TaskPriority.High,
                Status = TaskStatus.InProgress,
                CreatedAt = DateTime.Now,
                EstimatedMinutes = 60,
                Category = "Development",
                Tags = new List<string> { "coding", "review" }
            });

            TodayTasks.Add(new ProductivityTask
            {
                Id = Guid.NewGuid(),
                Title = "Complete wellbeing metrics analysis",
                Priority = TaskPriority.Medium,
                Status = TaskStatus.NotStarted,
                CreatedAt = DateTime.Now,
                EstimatedMinutes = 30,
                Category = "Analysis"
            });

            TodayTasks.Add(new ProductivityTask
            {
                Id = Guid.NewGuid(),
                Title = "Plan next sprint goals",
                Priority = TaskPriority.Medium,
                Status = TaskStatus.NotStarted,
                CreatedAt = DateTime.Now,
                DueDate = DateTime.Today.AddHours(17),
                EstimatedMinutes = 45,
                Category = "Planning"
            });

            // Active goals
            ActiveGoals.Add(new ProductivityGoal
            {
                Id = Guid.NewGuid(),
                Title = "Complete 5 focus sessions daily",
                Type = GoalType.Daily,
                TargetValue = 5,
                CurrentValue = 2,
                Unit = "sessions",
                StartDate = DateTime.Today,
                EndDate = DateTime.Today.AddDays(1),
                Status = GoalStatus.Active,
                IconGlyph = "\uE73E"
            });

            ActiveGoals.Add(new ProductivityGoal
            {
                Id = Guid.NewGuid(),
                Title = "Achieve 120 minutes of deep work",
                Type = GoalType.Daily,
                TargetValue = 120,
                CurrentValue = 50,
                Unit = "minutes",
                StartDate = DateTime.Today,
                EndDate = DateTime.Today.AddDays(1),
                Status = GoalStatus.Active,
                IconGlyph = "\uE7C5"
            });

            // Sample schedule blocks
            var now = DateTime.Now;
            TodaySchedule.Add(new TimeBlock
            {
                Id = Guid.NewGuid(),
                Title = "Deep Work Block",
                StartTime = new DateTime(now.Year, now.Month, now.Day, 9, 0, 0),
                EndTime = new DateTime(now.Year, now.Month, now.Day, 11, 0, 0),
                Type = BlockType.Focus,
                Color = "#0078D4"
            });

            TodaySchedule.Add(new TimeBlock
            {
                Id = Guid.NewGuid(),
                Title = "Team Sync",
                StartTime = new DateTime(now.Year, now.Month, now.Day, 14, 0, 0),
                EndTime = new DateTime(now.Year, now.Month, now.Day, 14, 30, 0),
                Type = BlockType.Meeting,
                Color = "#8E8CD8"
            });
        }

        #region Task Management

        public void AddTask(string title, TaskPriority priority = TaskPriority.Medium, string category = "General")
        {
            var task = new ProductivityTask
            {
                Id = Guid.NewGuid(),
                Title = title,
                Priority = priority,
                Status = TaskStatus.NotStarted,
                CreatedAt = DateTime.Now,
                Category = category
            };

            TodayTasks.Add(task);
        }

        public void CompleteTask(Guid taskId)
        {
            var task = TodayTasks.FirstOrDefault(t => t.Id == taskId);
            if (task != null)
            {
                task.Status = TaskStatus.Completed;
                task.CompletedAt = DateTime.Now;

                NotificationService.Instance.ShowSimpleNotification(
                    "Task Completed!",
                    $"Great job completing: {task.Title}");

                UpdateGoalProgress();
            }
        }

        public void DeleteTask(Guid taskId)
        {
            var task = TodayTasks.FirstOrDefault(t => t.Id == taskId);
            if (task != null)
            {
                TodayTasks.Remove(task);
            }
        }

        public void UpdateTaskStatus(Guid taskId, TaskStatus status)
        {
            var task = TodayTasks.FirstOrDefault(t => t.Id == taskId);
            if (task != null)
            {
                task.Status = status;
            }
        }

        #endregion

        #region Focus Sessions

        public void StartFocusSession(SessionType type = SessionType.Focus, string name = "Focus Session")
        {
            if (_currentSession != null)
            {
                EndFocusSession();
            }

            int plannedMinutes = type switch
            {
                SessionType.Focus => 25,
                SessionType.ShortBreak => 5,
                SessionType.LongBreak => 15,
                SessionType.DeepWork => 90,
                _ => 25
            };

            _currentSession = new FocusSession
            {
                Id = Guid.NewGuid(),
                Name = name,
                Type = type,
                PlannedMinutes = plannedMinutes,
                StartTime = DateTime.Now
            };

            _sessionStartTime = DateTime.Now;

            // Start timer for session end
            _sessionTimer = new System.Threading.Timer(
                OnSessionTimerElapsed,
                null,
                TimeSpan.FromMinutes(plannedMinutes),
                TimeSpan.FromMilliseconds(-1)); // One-time timer

            NotificationService.Instance.ShowSimpleNotification(
                $"{name} Started",
                $"{plannedMinutes} minute session beginning now. Stay focused!");
        }

        private void OnSessionTimerElapsed(object? state)
        {
            _dispatcher?.TryEnqueue(() =>
            {
                if (_currentSession != null)
                {
                    NotificationService.Instance.ShowSimpleNotification(
                        "Focus Session Complete!",
                        $"You completed a {_currentSession.PlannedMinutes} minute session. Take a break!");

                    EndFocusSession(false);
                }
            });
        }

        public void EndFocusSession(bool wasInterrupted = false)
        {
            if (_currentSession != null)
            {
                _currentSession.EndTime = DateTime.Now;
                _currentSession.ActualMinutes = (int)(DateTime.Now - _sessionStartTime).TotalMinutes;
                _currentSession.WasInterrupted = wasInterrupted;

                FocusSessions.Add(_currentSession);
                UpdateGoalProgress();

                _currentSession = null;
                _sessionTimer?.Dispose();
                _sessionTimer = null;
            }
        }

        public FocusSession? GetCurrentSession() => _currentSession;

        public bool IsSessionActive() => _currentSession != null;

        public int GetSessionTimeRemaining()
        {
            if (_currentSession == null) return 0;

            var elapsed = (int)(DateTime.Now - _sessionStartTime).TotalMinutes;
            return Math.Max(0, _currentSession.PlannedMinutes - elapsed);
        }

        #endregion

        #region Productivity Analytics

        public ProductivitySummary GetTodaySummary()
        {
            var today = DateTime.Today;
            var todaySessions = FocusSessions.Where(s => s.StartTime.Date == today).ToList();

            return new ProductivitySummary
            {
                Date = today,
                TotalFocusMinutes = todaySessions.Sum(s => s.ActualMinutes),
                TasksCompleted = TodayTasks.Count(t => t.Status == TaskStatus.Completed),
                TasksCreated = TodayTasks.Count,
                FocusSessionsCompleted = todaySessions.Count(s => !s.WasInterrupted),
                DistractionsCount = todaySessions.Count(s => s.WasInterrupted),
                ProductivityScore = CalculateProductivityScore(),
                CategoryBreakdown = TodayTasks
                    .Where(t => t.Status == TaskStatus.Completed)
                    .GroupBy(t => t.Category)
                    .ToDictionary(g => g.Key, g => g.Count())
            };
        }

        private double CalculateProductivityScore()
        {
            double score = 0;

            // Tasks completed (40 points)
            var completedTasks = TodayTasks.Count(t => t.Status == TaskStatus.Completed);
            var totalTasks = TodayTasks.Count;
            if (totalTasks > 0)
            {
                score += (completedTasks / (double)totalTasks) * 40;
            }

            // Focus sessions (30 points)
            var todaySessions = FocusSessions.Where(s => s.StartTime.Date == DateTime.Today).ToList();
            var successfulSessions = todaySessions.Count(s => !s.WasInterrupted);
            if (successfulSessions > 0)
            {
                score += Math.Min(successfulSessions * 6, 30); // Up to 5 sessions
            }

            // Focus time (30 points)
            var focusMinutes = todaySessions.Sum(s => s.ActualMinutes);
            score += Math.Min((focusMinutes / 120.0) * 30, 30); // Up to 2 hours

            return Math.Round(score, 1);
        }

        public ProductivityStreak GetCurrentStreak()
        {
            // Simple streak calculation (would be database-backed in production)
            return new ProductivityStreak
            {
                CurrentStreak = 7,
                LongestStreak = 14,
                LastProductiveDay = DateTime.Today,
                TotalProductiveDays = 42
            };
        }

        public Dictionary<string, double> GetTimeDistribution()
        {
            var distribution = new Dictionary<string, double>();

            var todaySessions = FocusSessions.Where(s => s.StartTime.Date == DateTime.Today).ToList();

            distribution["Deep Work"] = todaySessions
                .Where(s => s.Type == SessionType.DeepWork || s.Type == SessionType.Focus)
                .Sum(s => s.ActualMinutes);

            distribution["Breaks"] = todaySessions
                .Where(s => s.Type == SessionType.ShortBreak || s.Type == SessionType.LongBreak)
                .Sum(s => s.ActualMinutes);

            distribution["Other"] = 480 - distribution["Deep Work"] - distribution["Breaks"]; // 8 hour day

            return distribution;
        }

        #endregion

        #region Goal Management

        private void UpdateGoalProgress()
        {
            foreach (var goal in ActiveGoals.Where(g => g.Status == GoalStatus.Active))
            {
                if (goal.Type == GoalType.Daily && goal.StartDate.Date != DateTime.Today)
                {
                    // Reset daily goals
                    goal.CurrentValue = 0;
                    goal.StartDate = DateTime.Today;
                    goal.EndDate = DateTime.Today.AddDays(1);
                }

                // Update goal values based on type
                if (goal.Title.Contains("focus sessions"))
                {
                    goal.CurrentValue = FocusSessions.Count(s =>
                        s.StartTime.Date == DateTime.Today && !s.WasInterrupted);
                }
                else if (goal.Title.Contains("deep work"))
                {
                    goal.CurrentValue = FocusSessions
                        .Where(s => s.StartTime.Date == DateTime.Today)
                        .Sum(s => s.ActualMinutes);
                }

                // Check if goal is complete
                if (goal.CurrentValue >= goal.TargetValue && goal.Status == GoalStatus.Active)
                {
                    goal.Status = GoalStatus.Completed;

                    NotificationService.Instance.ShowAchievementNotification(
                        "Goal Achieved! 🎉",
                        $"Congratulations! You completed: {goal.Title}");
                }
            }
        }

        #endregion

        public void Cleanup()
        {
            _sessionTimer?.Dispose();
        }
    }
}
