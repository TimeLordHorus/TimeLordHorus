using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.Linq;
using TimeLordDashboard.Models;
using TimeLordDashboard.Services;

namespace TimeLordDashboard.ViewModels
{
    public partial class DashboardViewModel : ObservableObject
    {
        private readonly FileManagementService _fileService;
        private readonly WellbeingService _wellbeingService;
        private readonly ProductivityService _productivityService;

        [ObservableProperty]
        private ObservableCollection<FileContainer> recentContainers;

        [ObservableProperty]
        private ObservableCollection<WellbeingMetric> activeMetrics;

        [ObservableProperty]
        private ObservableCollection<ProductivityTask> todayTasks;

        [ObservableProperty]
        private ObservableCollection<ProductivityGoal> activeGoals;

        [ObservableProperty]
        private ProductivitySummary? todaySummary;

        [ObservableProperty]
        private ProductivityStreak? currentStreak;

        [ObservableProperty]
        private string greetingMessage;

        [ObservableProperty]
        private double todayScreenTime;

        [ObservableProperty]
        private int todayBreaks;

        [ObservableProperty]
        private double todayHydration;

        [ObservableProperty]
        private double productivityScore;

        [ObservableProperty]
        private int tasksCompleted;

        [ObservableProperty]
        private int totalTasks;

        [ObservableProperty]
        private int focusSessionsToday;

        public DashboardViewModel()
        {
            _fileService = FileManagementService.Instance;
            _wellbeingService = WellbeingService.Instance;
            _productivityService = ProductivityService.Instance;

            recentContainers = new ObservableCollection<FileContainer>(
                _fileService.Containers.Take(4));

            activeMetrics = new ObservableCollection<WellbeingMetric>(
                _wellbeingService.Metrics.Take(6));

            todayTasks = _productivityService.TodayTasks;
            activeGoals = _productivityService.ActiveGoals;

            greetingMessage = GetGreetingMessage();
            UpdateDashboardStats();
        }

        private string GetGreetingMessage()
        {
            var hour = System.DateTime.Now.Hour;

            return hour switch
            {
                < 12 => "Good Morning!",
                < 18 => "Good Afternoon!",
                _ => "Good Evening!"
            };
        }

        private void UpdateDashboardStats()
        {
            // Wellbeing stats
            var screenTimeMetric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == MetricType.ScreenTime);
            if (screenTimeMetric != null)
            {
                TodayScreenTime = screenTimeMetric.CurrentValue;
            }

            var breakMetric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == MetricType.BreakTime);
            if (breakMetric != null)
            {
                TodayBreaks = (int)(breakMetric.CurrentValue / 5); // Assuming 5 min breaks
            }

            var hydrationMetric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == MetricType.Hydration);
            if (hydrationMetric != null)
            {
                TodayHydration = hydrationMetric.CurrentValue;
            }

            // Productivity stats
            TodaySummary = _productivityService.GetTodaySummary();
            CurrentStreak = _productivityService.GetCurrentStreak();

            ProductivityScore = TodaySummary.ProductivityScore;
            TasksCompleted = TodaySummary.TasksCompleted;
            TotalTasks = TodaySummary.TasksCreated;
            FocusSessionsToday = TodaySummary.FocusSessionsCompleted;
        }

        [RelayCommand]
        private void RefreshDashboard()
        {
            UpdateDashboardStats();
            GreetingMessage = GetGreetingMessage();
        }

        [RelayCommand]
        private void QuickBreak()
        {
            _wellbeingService.LogBreak(5);
            UpdateDashboardStats();
        }

        [RelayCommand]
        private void LogWaterIntake()
        {
            _wellbeingService.UpdateMetric(MetricType.Hydration, TodayHydration + 1);
            UpdateDashboardStats();
        }

        [RelayCommand]
        private void CompleteTask(ProductivityTask task)
        {
            _productivityService.CompleteTask(task.Id);
            UpdateDashboardStats();
        }

        [RelayCommand]
        private void AddQuickTask(string title)
        {
            if (!string.IsNullOrWhiteSpace(title))
            {
                _productivityService.AddTask(title, TaskPriority.Medium);
                UpdateDashboardStats();
            }
        }
    }
}
