using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using TimeLordDashboard.Models;

namespace TimeLordDashboard.Controls
{
    public sealed partial class ProductivityScorePanel : UserControl
    {
        public static readonly DependencyProperty SummaryProperty =
            DependencyProperty.Register(nameof(Summary), typeof(ProductivitySummary), typeof(ProductivityScorePanel),
                new PropertyMetadata(null, OnSummaryChanged));

        public ProductivitySummary? Summary
        {
            get => (ProductivitySummary?)GetValue(SummaryProperty);
            set => SetValue(SummaryProperty, value);
        }

        public ProductivityScorePanel()
        {
            this.InitializeComponent();
        }

        private static void OnSummaryChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is ProductivityScorePanel panel && e.NewValue is ProductivitySummary summary)
            {
                panel.UpdateUI(summary);
            }
        }

        private void UpdateUI(ProductivitySummary summary)
        {
            // Update subtitle
            SubtitleText.Text = $"Today • {summary.Date:MMM d}";

            // Update score
            ScoreText.Text = summary.ProductivityScore.ToString("F0");

            // Update score color based on value
            var color = summary.ProductivityScore switch
            {
                >= 80 => Application.Current.Resources["SuccessBrush"],
                >= 60 => Application.Current.Resources["AccentBrush"],
                >= 40 => Application.Current.Resources["WarningBrush"],
                _ => Application.Current.Resources["ErrorBrush"]
            };

            if (color is Microsoft.UI.Xaml.Media.SolidColorBrush brush)
            {
                ScoreText.Foreground = brush;
                ProgressRing.Stroke = brush;
            }

            // Update stats
            TasksCompletedText.Text = $"{summary.TasksCompleted}/{summary.TasksCreated}";
            SessionsCompletedText.Text = summary.FocusSessionsCompleted.ToString();
            FocusTimeText.Text = summary.TotalFocusMinutes.ToString();
        }
    }
}
