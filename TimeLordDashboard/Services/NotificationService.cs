using Microsoft.Windows.AppNotifications;
using Microsoft.Windows.AppNotifications.Builder;
using System;
using TimeLordDashboard.Models;

namespace TimeLordDashboard.Services
{
    /// <summary>
    /// Manages Windows toast notifications for wellbeing reminders
    /// </summary>
    public class NotificationService
    {
        private static NotificationService? _instance;
        private static readonly object _lock = new();
        private readonly AppNotificationManager _notificationManager;

        public static NotificationService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new NotificationService();
                }
            }
        }

        private NotificationService()
        {
            _notificationManager = AppNotificationManager.Default;
            _notificationManager.NotificationInvoked += OnNotificationInvoked;
            _notificationManager.Register();
        }

        /// <summary>
        /// Show a wellbeing reminder notification
        /// </summary>
        public void ShowReminderNotification(WellbeingReminder reminder)
        {
            try
            {
                var builder = new AppNotificationBuilder()
                    .AddText(reminder.Title)
                    .AddText(reminder.Description)
                    .SetScenario(AppNotificationScenario.Reminder);

                // Add action buttons based on reminder type
                switch (reminder.Type)
                {
                    case ReminderType.TakeBreak:
                        builder.AddButton(new AppNotificationButton("Take 5 min break")
                            .AddArgument("action", "break_5"));
                        builder.AddButton(new AppNotificationButton("Take 15 min break")
                            .AddArgument("action", "break_15"));
                        break;

                    case ReminderType.DrinkWater:
                        builder.AddButton(new AppNotificationButton("Logged!")
                            .AddArgument("action", "water_logged"));
                        break;

                    case ReminderType.EyeRest:
                        builder.AddButton(new AppNotificationButton("Start exercise")
                            .AddArgument("action", "eye_rest"));
                        break;

                    case ReminderType.PostureCheck:
                        builder.AddButton(new AppNotificationButton("Adjusted")
                            .AddArgument("action", "posture_check"));
                        break;
                }

                builder.AddButton(new AppNotificationButton("Dismiss")
                    .AddArgument("action", "dismiss"));

                var notification = builder.BuildNotification();
                _notificationManager.Show(notification);

                System.Diagnostics.Debug.WriteLine($"Notification shown: {reminder.Title}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error showing notification: {ex.Message}");
            }
        }

        /// <summary>
        /// Show a simple text notification
        /// </summary>
        public void ShowSimpleNotification(string title, string message)
        {
            try
            {
                var builder = new AppNotificationBuilder()
                    .AddText(title)
                    .AddText(message);

                var notification = builder.BuildNotification();
                _notificationManager.Show(notification);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error showing notification: {ex.Message}");
            }
        }

        /// <summary>
        /// Show a progress notification
        /// </summary>
        public void ShowProgressNotification(string title, double progress, string status)
        {
            try
            {
                var builder = new AppNotificationBuilder()
                    .AddText(title)
                    .AddText(status)
                    .AddProgressBar(new AppNotificationProgressBar()
                        .BindValue(progress.ToString("F2"))
                        .BindStatus(status));

                var notification = builder.BuildNotification();
                _notificationManager.Show(notification);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error showing progress notification: {ex.Message}");
            }
        }

        /// <summary>
        /// Show achievement notification
        /// </summary>
        public void ShowAchievementNotification(string title, string description, string imageUri = "")
        {
            try
            {
                var builder = new AppNotificationBuilder()
                    .AddText(title)
                    .AddText(description)
                    .SetScenario(AppNotificationScenario.Reminder);

                if (!string.IsNullOrEmpty(imageUri))
                {
                    builder.SetInlineImage(new Uri(imageUri));
                }

                var notification = builder.BuildNotification();
                _notificationManager.Show(notification);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error showing achievement notification: {ex.Message}");
            }
        }

        private void OnNotificationInvoked(AppNotificationManager sender, AppNotificationActivatedEventArgs args)
        {
            // Handle notification actions
            if (args.Arguments.TryGetValue("action", out string? action))
            {
                HandleNotificationAction(action);
            }
        }

        private void HandleNotificationAction(string action)
        {
            var wellbeingService = WellbeingService.Instance;

            switch (action)
            {
                case "break_5":
                    wellbeingService.LogBreak(5);
                    ShowSimpleNotification("Break Logged", "Enjoy your 5-minute break!");
                    break;

                case "break_15":
                    wellbeingService.LogBreak(15);
                    ShowSimpleNotification("Break Logged", "Enjoy your 15-minute break!");
                    break;

                case "water_logged":
                    wellbeingService.UpdateMetric(MetricType.Hydration,
                        wellbeingService.Metrics.First(m => m.Type == MetricType.Hydration).CurrentValue + 1);
                    ShowSimpleNotification("Hydration Logged", "Great job staying hydrated!");
                    break;

                case "eye_rest":
                    ShowSimpleNotification("Eye Rest", "Look at something 20 feet away for 20 seconds (20-20-20 rule)");
                    break;

                case "posture_check":
                    ShowSimpleNotification("Posture Adjusted", "Keep up the good posture!");
                    break;

                case "dismiss":
                    // Notification dismissed, no action needed
                    break;
            }

            System.Diagnostics.Debug.WriteLine($"Notification action handled: {action}");
        }

        public void Unregister()
        {
            _notificationManager.Unregister();
        }
    }
}
