using Microsoft.UI.Xaml.Controls;
using TimeLordDashboard.ViewModels;

namespace TimeLordDashboard.Views
{
    public sealed partial class SettingsPage : Page
    {
        public SettingsViewModel ViewModel { get; }

        public SettingsPage()
        {
            this.InitializeComponent();
            ViewModel = new SettingsViewModel();
        }
    }
}
