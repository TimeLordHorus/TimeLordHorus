using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using SkiaSharp;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using TimeLordDashboard.Models;
using TimeLordDashboard.Services;

namespace TimeLordDashboard.ViewModels
{
    public partial class AnalyticsViewModel : ObservableObject
    {
        private readonly WellbeingService _wellbeingService;

        [ObservableProperty]
        private ObservableCollection<ISeries> screenTimeSeries;

        [ObservableProperty]
        private ObservableCollection<ISeries> wellbeingMetricsSeries;

        [ObservableProperty]
        private ObservableCollection<Axis> xAxes;

        [ObservableProperty]
        private ObservableCollection<Axis> yAxes;

        [ObservableProperty]
        private string selectedTimePeriod = "This Week";

        [ObservableProperty]
        private double totalScreenTime;

        [ObservableProperty]
        private int totalBreaks;

        [ObservableProperty]
        private double averageWellbeingScore;

        [ObservableProperty]
        private int filesOrganized;

        [ObservableProperty]
        private double screenTimeChange;

        [ObservableProperty]
        private double breaksChange;

        [ObservableProperty]
        private double wellbeingChange;

        public ObservableCollection<string> TimePeriods { get; } = new()
        {
            "Today",
            "This Week",
            "This Month",
            "Last 3 Months"
        };

        public AnalyticsViewModel()
        {
            _wellbeingService = WellbeingService.Instance;

            screenTimeSeries = new ObservableCollection<ISeries>();
            wellbeingMetricsSeries = new ObservableCollection<ISeries>();
            xAxes = new ObservableCollection<Axis>();
            yAxes = new ObservableCollection<Axis>();

            InitializeCharts();
            CalculateSummaryStats();
        }

        private void InitializeCharts()
        {
            // Screen Time Chart (Last 7 Days)
            var screenTimeData = GenerateScreenTimeData();

            ScreenTimeSeries = new ObservableCollection<ISeries>
            {
                new LineSeries<double>
                {
                    Values = screenTimeData,
                    Name = "Screen Time (hours)",
                    Fill = null,
                    GeometrySize = 8,
                    Stroke = new SolidColorPaint(SKColors.DodgerBlue) { StrokeThickness = 3 },
                    GeometryStroke = new SolidColorPaint(SKColors.DodgerBlue) { StrokeThickness = 3 }
                }
            };

            // Wellbeing Metrics (Multiple Lines)
            var hydrationData = GenerateMetricData(MetricType.Hydration);
            var stressData = GenerateMetricData(MetricType.StressLevel);
            var postureData = GenerateMetricData(MetricType.Posture);

            WellbeingMetricsSeries = new ObservableCollection<ISeries>
            {
                new LineSeries<double>
                {
                    Values = hydrationData,
                    Name = "Hydration",
                    Fill = null,
                    GeometrySize = 6,
                    Stroke = new SolidColorPaint(SKColors.DeepSkyBlue) { StrokeThickness = 2 }
                },
                new LineSeries<double>
                {
                    Values = stressData,
                    Name = "Stress Level",
                    Fill = null,
                    GeometrySize = 6,
                    Stroke = new SolidColorPaint(SKColors.OrangeRed) { StrokeThickness = 2 }
                },
                new LineSeries<double>
                {
                    Values = postureData,
                    Name = "Posture Score",
                    Fill = null,
                    GeometrySize = 6,
                    Stroke = new SolidColorPaint(SKColors.MediumPurple) { StrokeThickness = 2 }
                }
            };

            // Configure axes
            XAxes = new ObservableCollection<Axis>
            {
                new Axis
                {
                    Name = "Days",
                    Labels = new[] { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" },
                    LabelsRotation = 0,
                    LabelsPaint = new SolidColorPaint(SKColors.Gray)
                }
            };

            YAxes = new ObservableCollection<Axis>
            {
                new Axis
                {
                    Name = "Hours",
                    LabelsPaint = new SolidColorPaint(SKColors.Gray),
                    MinLimit = 0
                }
            };
        }

        private List<double> GenerateScreenTimeData()
        {
            // Generate sample data for the last 7 days
            // In production, this would come from the WellbeingService
            var screenTimeMetric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == MetricType.ScreenTime);

            if (screenTimeMetric != null && screenTimeMetric.History.Any())
            {
                var last7Days = screenTimeMetric.History
                    .Where(dp => dp.Timestamp >= DateTime.Now.AddDays(-7))
                    .GroupBy(dp => dp.Timestamp.Date)
                    .Select(g => g.Sum(dp => dp.Value) / 60.0) // Convert minutes to hours
                    .ToList();

                // Ensure we have 7 data points
                while (last7Days.Count < 7)
                {
                    last7Days.Insert(0, 0);
                }

                return last7Days.TakeLast(7).ToList();
            }

            // Sample data for demonstration
            return new List<double> { 4.5, 5.2, 4.8, 6.1, 5.5, 4.2, 3.8 };
        }

        private List<double> GenerateMetricData(MetricType metricType)
        {
            var metric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == metricType);

            if (metric != null && metric.History.Any())
            {
                var last7Days = metric.History
                    .Where(dp => dp.Timestamp >= DateTime.Now.AddDays(-7))
                    .GroupBy(dp => dp.Timestamp.Date)
                    .Select(g => g.Average(dp => dp.Value))
                    .ToList();

                while (last7Days.Count < 7)
                {
                    last7Days.Insert(0, 0);
                }

                return last7Days.TakeLast(7).ToList();
            }

            // Sample data based on metric type
            return metricType switch
            {
                MetricType.Hydration => new List<double> { 6, 7, 5, 8, 6, 7, 8 },
                MetricType.StressLevel => new List<double> { 4, 3, 5, 4, 3, 2, 3 },
                MetricType.Posture => new List<double> { 75, 80, 78, 85, 82, 88, 90 },
                _ => new List<double> { 0, 0, 0, 0, 0, 0, 0 }
            };
        }

        private void CalculateSummaryStats()
        {
            // Calculate total screen time for the selected period
            var screenTimeMetric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == MetricType.ScreenTime);
            if (screenTimeMetric != null)
            {
                var weekData = screenTimeMetric.History
                    .Where(dp => dp.Timestamp >= DateTime.Now.AddDays(-7))
                    .Sum(dp => dp.Value);

                TotalScreenTime = weekData / 60.0; // Convert to hours

                // Calculate change from previous week
                var previousWeekData = screenTimeMetric.History
                    .Where(dp => dp.Timestamp >= DateTime.Now.AddDays(-14) && dp.Timestamp < DateTime.Now.AddDays(-7))
                    .Sum(dp => dp.Value) / 60.0;

                if (previousWeekData > 0)
                {
                    ScreenTimeChange = ((TotalScreenTime - previousWeekData) / previousWeekData) * 100;
                }
            }
            else
            {
                // Sample data
                TotalScreenTime = 32.5;
                ScreenTimeChange = -12;
            }

            // Calculate total breaks
            var breakMetric = _wellbeingService.Metrics.FirstOrDefault(m => m.Type == MetricType.BreakTime);
            if (breakMetric != null)
            {
                TotalBreaks = (int)(breakMetric.CurrentValue / 5); // Assuming 5 min breaks
                BreaksChange = 8; // Sample percentage change
            }
            else
            {
                TotalBreaks = 42;
                BreaksChange = 8;
            }

            // Calculate average wellbeing score
            AverageWellbeingScore = CalculateWellbeingScore();
            WellbeingChange = 5;

            // Files organized (would come from FileManagementService)
            FilesOrganized = 156;
        }

        private double CalculateWellbeingScore()
        {
            // Calculate overall wellbeing score based on all metrics
            double totalScore = 0;
            int metricCount = 0;

            foreach (var metric in _wellbeingService.Metrics)
            {
                if (metric.TargetValue > 0)
                {
                    var percentage = (metric.CurrentValue / metric.TargetValue) * 100;

                    // Invert for metrics where lower is better (like stress)
                    if (metric.Type == MetricType.StressLevel)
                    {
                        percentage = 100 - percentage;
                    }

                    totalScore += Math.Min(percentage, 100);
                    metricCount++;
                }
            }

            return metricCount > 0 ? (totalScore / metricCount) / 10.0 : 0; // Scale to 0-10
        }

        [RelayCommand]
        private void ChangeTimePeriod(string period)
        {
            SelectedTimePeriod = period;
            RefreshData();
        }

        [RelayCommand]
        private void RefreshData()
        {
            InitializeCharts();
            CalculateSummaryStats();
        }

        [RelayCommand]
        private void ExportData()
        {
            // TODO: Implement data export functionality
            System.Diagnostics.Debug.WriteLine("Exporting analytics data...");
        }
    }
}
