using Microsoft.UI;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Windows.UI;

namespace TimeLordDashboard.Controls
{
    public sealed partial class MetricCard : UserControl
    {
        public static readonly DependencyProperty MetricNameProperty =
            DependencyProperty.Register(nameof(MetricName), typeof(string), typeof(MetricCard),
                new PropertyMetadata(string.Empty, OnMetricNameChanged));

        public static readonly DependencyProperty IconGlyphProperty =
            DependencyProperty.Register(nameof(IconGlyph), typeof(string), typeof(MetricCard),
                new PropertyMetadata("\uE95E", OnIconGlyphChanged));

        public static readonly DependencyProperty CurrentValueProperty =
            DependencyProperty.Register(nameof(CurrentValue), typeof(double), typeof(MetricCard),
                new PropertyMetadata(0.0, OnCurrentValueChanged));

        public static readonly DependencyProperty TargetValueProperty =
            DependencyProperty.Register(nameof(TargetValue), typeof(double), typeof(MetricCard),
                new PropertyMetadata(100.0, OnTargetValueChanged));

        public static readonly DependencyProperty UnitProperty =
            DependencyProperty.Register(nameof(Unit), typeof(string), typeof(MetricCard),
                new PropertyMetadata(string.Empty, OnUnitChanged));

        public static readonly DependencyProperty AccentColorProperty =
            DependencyProperty.Register(nameof(AccentColor), typeof(Color), typeof(MetricCard),
                new PropertyMetadata(Colors.Blue, OnAccentColorChanged));

        public string MetricName
        {
            get => (string)GetValue(MetricNameProperty);
            set => SetValue(MetricNameProperty, value);
        }

        public string IconGlyph
        {
            get => (string)GetValue(IconGlyphProperty);
            set => SetValue(IconGlyphProperty, value);
        }

        public double CurrentValue
        {
            get => (double)GetValue(CurrentValueProperty);
            set => SetValue(CurrentValueProperty, value);
        }

        public double TargetValue
        {
            get => (double)GetValue(TargetValueProperty);
            set => SetValue(TargetValueProperty, value);
        }

        public string Unit
        {
            get => (string)GetValue(UnitProperty);
            set => SetValue(UnitProperty, value);
        }

        public Color AccentColor
        {
            get => (Color)GetValue(AccentColorProperty);
            set => SetValue(AccentColorProperty, value);
        }

        public MetricCard()
        {
            this.InitializeComponent();
            UpdateUI();
        }

        private static void OnMetricNameChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is MetricCard card)
            {
                card.MetricName.Text = e.NewValue as string ?? string.Empty;
            }
        }

        private static void OnIconGlyphChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is MetricCard card)
            {
                card.MetricIcon.Glyph = e.NewValue as string ?? "\uE95E";
            }
        }

        private static void OnCurrentValueChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is MetricCard card)
            {
                card.UpdateCurrentValue();
            }
        }

        private static void OnTargetValueChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is MetricCard card)
            {
                card.UpdateTargetValue();
            }
        }

        private static void OnUnitChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is MetricCard card)
            {
                card.UpdateUnit();
            }
        }

        private static void OnAccentColorChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is MetricCard card && e.NewValue is Color color)
            {
                card.UpdateAccentColor(color);
            }
        }

        private void UpdateUI()
        {
            UpdateCurrentValue();
            UpdateTargetValue();
            UpdateUnit();
            UpdateAccentColor(AccentColor);
        }

        private void UpdateCurrentValue()
        {
            CurrentValueRun.Text = CurrentValue.ToString("F1");
            ProgressBar.Value = CurrentValue;
        }

        private void UpdateTargetValue()
        {
            TargetValueRun.Text = TargetValue.ToString("F0");
            ProgressBar.Maximum = TargetValue;
        }

        private void UpdateUnit()
        {
            UnitText.Text = Unit;
            TargetUnitRun.Text = Unit;
        }

        private void UpdateAccentColor(Color color)
        {
            var brush = new SolidColorBrush(color);
            MetricIcon.Foreground = brush;
            ProgressBar.Foreground = brush;
        }
    }
}
