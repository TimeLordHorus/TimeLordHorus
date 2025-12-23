using Microsoft.UI.Xaml;
using System;
using TimeLordDashboard.Services;

namespace TimeLordDashboard
{
    public partial class App : Application
    {
        private Window? m_window;

        public App()
        {
            this.InitializeComponent();
        }

        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            // Initialize services
            InitializeServices();

            m_window = new MainWindow();
            m_window.Activate();
        }

        private void InitializeServices()
        {
            // Initialize database
            DatabaseService.Instance.Initialize();

            // Initialize file management service
            _ = FileManagementService.Instance;

            // Initialize wellbeing service
            _ = WellbeingService.Instance;
        }

        public static Window? MainWindow { get; private set; }
    }
}
