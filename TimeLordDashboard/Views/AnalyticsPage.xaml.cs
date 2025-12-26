using Microsoft.UI.Xaml.Controls;
using TimeLordDashboard.ViewModels;

namespace TimeLordDashboard.Views
{
    public sealed partial class AnalyticsPage : Page
    {
        public AnalyticsViewModel ViewModel { get; }

        public AnalyticsPage()
        {
            this.InitializeComponent();
            ViewModel = new AnalyticsViewModel();
        }

        private void TimePeriod_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.AddedItems.Count > 0 && e.AddedItems[0] is string period)
            {
                ViewModel.ChangeTimePeriodCommand.Execute(period);
            }
        }
    }
}
