using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using TimeLordDashboard.Models;
using TimeLordDashboard.Services;

namespace TimeLordDashboard.Controls
{
    public sealed partial class FocusSessionPanel : UserControl
    {
        private DispatcherTimer? _updateTimer;
        private readonly ProductivityService _productivityService;
        private int _selectedMinutes = 25;

        public FocusSessionPanel()
        {
            this.InitializeComponent();
            _productivityService = ProductivityService.Instance;

            _updateTimer = new DispatcherTimer();
            _updateTimer.Interval = TimeSpan.FromSeconds(1);
            _updateTimer.Tick += UpdateTimer_Tick;
        }

        private void StartButton_Click(object sender, RoutedEventArgs e)
        {
            var sessionType = _selectedMinutes switch
            {
                5 => SessionType.ShortBreak,
                15 => SessionType.LongBreak,
                90 => SessionType.DeepWork,
                _ => SessionType.Focus
            };

            _productivityService.StartFocusSession(sessionType, SessionTypeComboBox.SelectedValue?.ToString() ?? "Focus Session");

            StartButton.IsEnabled = false;
            StopButton.IsEnabled = true;
            SessionTypeComboBox.IsEnabled = false;
            StatusText.Text = "Session in progress...";

            _updateTimer?.Start();
        }

        private void StopButton_Click(object sender, RoutedEventArgs e)
        {
            _productivityService.EndFocusSession(true);

            StartButton.IsEnabled = true;
            StopButton.IsEnabled = false;
            SessionTypeComboBox.IsEnabled = true;
            StatusText.Text = "Ready to focus";

            _updateTimer?.Stop();
            TimerText.Text = $"{_selectedMinutes}:00";
        }

        private void UpdateTimer_Tick(object? sender, object e)
        {
            var remaining = _productivityService.GetSessionTimeRemaining();

            if (remaining <= 0)
            {
                StopButton_Click(this, new RoutedEventArgs());
                return;
            }

            TimerText.Text = $"{remaining}:00";
        }

        private void SessionType_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.AddedItems.Count > 0 && e.AddedItems[0] is ComboBoxItem item)
            {
                if (int.TryParse(item.Tag?.ToString(), out int minutes))
                {
                    _selectedMinutes = minutes;
                    TimerText.Text = $"{minutes}:00";

                    SessionTypeText.Text = minutes switch
                    {
                        5 => "Short break - relax and recharge",
                        15 => "Long break - take a walk or stretch",
                        90 => "Deep work - eliminate all distractions",
                        _ => "Pomodoro focus - 25 minutes of concentration"
                    };
                }
            }
        }
    }
}
