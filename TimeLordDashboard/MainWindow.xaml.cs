using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using TimeLordDashboard.Views;

namespace TimeLordDashboard
{
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();

            // Set window size
            var hWnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
            var windowId = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(hWnd);
            var appWindow = Microsoft.UI.Windowing.AppWindow.GetFromWindowId(windowId);

            if (appWindow != null)
            {
                appWindow.Resize(new Windows.Graphics.SizeInt32(1400, 900));
            }

            // Navigate to Dashboard by default
            ContentFrame.Navigate(typeof(DashboardPage));
        }

        private void NavView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
        {
            if (args.SelectedItem is NavigationViewItem item)
            {
                string tag = item.Tag?.ToString() ?? string.Empty;

                Type? pageType = tag switch
                {
                    "Dashboard" => typeof(DashboardPage),
                    "FileManagement" => typeof(FileManagementPage),
                    "Wellbeing" => typeof(WellbeingPage),
                    "Analytics" => typeof(AnalyticsPage),
                    _ => null
                };

                if (pageType != null)
                {
                    ContentFrame.Navigate(pageType);
                }
            }
        }

        private void SettingsButton_Click(object sender, RoutedEventArgs e)
        {
            // Navigate to settings page
            ContentFrame.Navigate(typeof(SettingsPage));
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            // Refresh current page
            if (ContentFrame.Content != null)
            {
                Type currentPageType = ContentFrame.Content.GetType();
                ContentFrame.Navigate(currentPageType);
            }
        }
    }
}
