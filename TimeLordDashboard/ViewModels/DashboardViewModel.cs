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

        [ObservableProperty]
        private ObservableCollection<FileContainer> recentContainers;

        [ObservableProperty]
        private ObservableCollection<WellbeingMetric> activeMetrics;

        [ObservableProperty]
        private string greetingMessage;

        [ObservableProperty]
        private double todayScreenTime;

        [ObservableProperty]
        private int todayBreaks;

        [ObservableProperty]
        private double todayHydration;

        public DashboardViewModel()
        {
            _fileService = FileManagementService.Instance;
            _wellbeingService = WellbeingService.Instance;

            recentContainers = new ObservableCollection<FileContainer>(
                _fileService.Containers.Take(4));

            activeMetrics = new ObservableCollection<WellbeingMetric>(
                _wellbeingService.Metrics.Take(6));

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
    }
}
