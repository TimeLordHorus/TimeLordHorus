using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using TimeLordDashboard.Models;
using TimeLordDashboard.Services;

namespace TimeLordDashboard.ViewModels
{
    public partial class WellbeingViewModel : ObservableObject
    {
        private readonly WellbeingService _wellbeingService;

        [ObservableProperty]
        private ObservableCollection<WellbeingMetric> metrics;

        [ObservableProperty]
        private ObservableCollection<WellbeingReminder> reminders;

        [ObservableProperty]
        private WellbeingMetric? selectedMetric;

        [ObservableProperty]
        private bool isBreathingExerciseActive;

        [ObservableProperty]
        private int breathingPhase; // 0=inhale, 1=hold, 2=exhale

        [ObservableProperty]
        private int breathingCountdown;

        [ObservableProperty]
        private string breathingInstruction = "Click 'Start Breathing Exercise' to begin";

        public WellbeingViewModel()
        {
            _wellbeingService = WellbeingService.Instance;
            metrics = _wellbeingService.Metrics;
            reminders = _wellbeingService.Reminders;

            // Select screen time metric by default
            SelectedMetric = metrics.FirstOrDefault(m => m.Type == MetricType.ScreenTime);
        }

        [RelayCommand]
        private void UpdateHydration()
        {
            _wellbeingService.UpdateMetric(MetricType.Hydration,
                _wellbeingService.Metrics.First(m => m.Type == MetricType.Hydration).CurrentValue + 1);
        }

        [RelayCommand]
        private void LogBreak(string durationString)
        {
            if (int.TryParse(durationString, out int duration))
            {
                _wellbeingService.LogBreak(duration);
            }
        }

        [RelayCommand]
        private void ToggleReminder(WellbeingReminder reminder)
        {
            reminder.IsEnabled = !reminder.IsEnabled;
        }

        [RelayCommand]
        private async void StartBreathingExercise()
        {
            IsBreathingExerciseActive = true;
            BreathingPhase = 0;

            var exercise = new BreathingExercise
            {
                Name = "4-4-4 Breathing",
                InhaleSeconds = 4,
                HoldSeconds = 4,
                ExhaleSeconds = 4,
                Cycles = 5
            };

            for (int cycle = 0; cycle < exercise.Cycles && IsBreathingExerciseActive; cycle++)
            {
                // Inhale
                BreathingPhase = 0;
                BreathingInstruction = "Breathe In...";
                await CountdownAsync(exercise.InhaleSeconds);

                // Hold
                BreathingPhase = 1;
                BreathingInstruction = "Hold...";
                await CountdownAsync(exercise.HoldSeconds);

                // Exhale
                BreathingPhase = 2;
                BreathingInstruction = "Breathe Out...";
                await CountdownAsync(exercise.ExhaleSeconds);
            }

            if (IsBreathingExerciseActive)
            {
                BreathingInstruction = "Great job! Exercise complete.";
                await System.Threading.Tasks.Task.Delay(2000);
            }

            IsBreathingExerciseActive = false;
            BreathingInstruction = "Click 'Start Breathing Exercise' to begin";
        }

        private async System.Threading.Tasks.Task CountdownAsync(int seconds)
        {
            for (int i = seconds; i > 0 && IsBreathingExerciseActive; i--)
            {
                BreathingCountdown = i;
                await System.Threading.Tasks.Task.Delay(1000);
            }
        }

        [RelayCommand]
        private void StopBreathingExercise()
        {
            IsBreathingExerciseActive = false;
            BreathingInstruction = "Exercise stopped.";
        }

        [RelayCommand]
        private void UpdateStressLevel(double level)
        {
            _wellbeingService.UpdateMetric(MetricType.StressLevel, level);
        }

        [RelayCommand]
        private void UpdatePostureScore(double score)
        {
            _wellbeingService.UpdateMetric(MetricType.Posture, score);
        }

        [RelayCommand]
        private void ViewMetricHistory(WellbeingMetric metric)
        {
            SelectedMetric = metric;
        }

        public double GetTodayAverage(MetricType type)
        {
            return _wellbeingService.GetAverageMetric(type, TimeSpan.FromHours(24));
        }

        public double GetWeekAverage(MetricType type)
        {
            return _wellbeingService.GetAverageMetric(type, TimeSpan.FromDays(7));
        }
    }
}
