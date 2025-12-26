using Microsoft.UI.Xaml.Controls;
using TimeLordDashboard.ViewModels;

namespace TimeLordDashboard.Views
{
    public sealed partial class WellbeingPage : Page
    {
        public WellbeingViewModel ViewModel { get; }

        public WellbeingPage()
        {
            this.InitializeComponent();
            ViewModel = new WellbeingViewModel();
        }
    }
}
