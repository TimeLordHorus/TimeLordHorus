using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Animation;
using System;

namespace TimeLordDashboard.Controls
{
    public sealed partial class BreathingCircle : UserControl
    {
        private Storyboard? _currentAnimation;

        public static readonly DependencyProperty CountdownProperty =
            DependencyProperty.Register(nameof(Countdown), typeof(int), typeof(BreathingCircle),
                new PropertyMetadata(0, OnCountdownChanged));

        public static readonly DependencyProperty InstructionProperty =
            DependencyProperty.Register(nameof(Instruction), typeof(string), typeof(BreathingCircle),
                new PropertyMetadata(string.Empty, OnInstructionChanged));

        public static readonly DependencyProperty PhaseProperty =
            DependencyProperty.Register(nameof(Phase), typeof(BreathingPhase), typeof(BreathingCircle),
                new PropertyMetadata(BreathingPhase.Idle, OnPhaseChanged));

        public int Countdown
        {
            get => (int)GetValue(CountdownProperty);
            set => SetValue(CountdownProperty, value);
        }

        public string Instruction
        {
            get => (string)GetValue(InstructionProperty);
            set => SetValue(InstructionProperty, value);
        }

        public BreathingPhase Phase
        {
            get => (BreathingPhase)GetValue(PhaseProperty);
            set => SetValue(PhaseProperty, value);
        }

        public BreathingCircle()
        {
            this.InitializeComponent();
        }

        private static void OnCountdownChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is BreathingCircle circle)
            {
                circle.CountdownText.Text = e.NewValue.ToString();
            }
        }

        private static void OnInstructionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is BreathingCircle circle)
            {
                circle.InstructionText.Text = e.NewValue as string ?? string.Empty;
            }
        }

        private static void OnPhaseChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is BreathingCircle circle && e.NewValue is BreathingPhase phase)
            {
                circle.AnimatePhase(phase);
            }
        }

        private void AnimatePhase(BreathingPhase phase)
        {
            _currentAnimation?.Stop();
            _currentAnimation = new Storyboard();

            DoubleAnimation scaleAnimation;
            DoubleAnimation opacityAnimation;

            switch (phase)
            {
                case BreathingPhase.Inhale:
                    // Expand circle
                    scaleAnimation = CreateScaleAnimation(1.0, 1.5, 4.0);
                    opacityAnimation = CreateOpacityAnimation(0.6, 0.9, 4.0);
                    break;

                case BreathingPhase.Hold:
                    // Keep circle at current size
                    scaleAnimation = CreateScaleAnimation(1.5, 1.5, 4.0);
                    opacityAnimation = CreateOpacityAnimation(0.9, 0.9, 4.0);
                    break;

                case BreathingPhase.Exhale:
                    // Contract circle
                    scaleAnimation = CreateScaleAnimation(1.5, 1.0, 4.0);
                    opacityAnimation = CreateOpacityAnimation(0.9, 0.6, 4.0);
                    break;

                default: // Idle
                    // Gentle pulse
                    scaleAnimation = CreateScaleAnimation(1.0, 1.1, 2.0, true);
                    opacityAnimation = CreateOpacityAnimation(0.6, 0.7, 2.0, true);
                    break;
            }

            Storyboard.SetTarget(scaleAnimation, BreathingScale);
            Storyboard.SetTargetProperty(scaleAnimation, "ScaleX");
            _currentAnimation.Children.Add(scaleAnimation);

            var scaleYAnimation = CreateScaleAnimation(scaleAnimation.From ?? 1.0, scaleAnimation.To ?? 1.0,
                scaleAnimation.Duration.TimeSpan.TotalSeconds, scaleAnimation.RepeatBehavior.HasDuration == false);
            Storyboard.SetTarget(scaleYAnimation, BreathingScale);
            Storyboard.SetTargetProperty(scaleYAnimation, "ScaleY");
            _currentAnimation.Children.Add(scaleYAnimation);

            Storyboard.SetTarget(opacityAnimation, BreathingEllipse);
            Storyboard.SetTargetProperty(opacityAnimation, "Opacity");
            _currentAnimation.Children.Add(opacityAnimation);

            _currentAnimation.Begin();
        }

        private DoubleAnimation CreateScaleAnimation(double from, double to, double durationSeconds, bool repeat = false)
        {
            return new DoubleAnimation
            {
                From = from,
                To = to,
                Duration = TimeSpan.FromSeconds(durationSeconds),
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseInOut },
                RepeatBehavior = repeat ? RepeatBehavior.Forever : new RepeatBehavior(1),
                AutoReverse = repeat
            };
        }

        private DoubleAnimation CreateOpacityAnimation(double from, double to, double durationSeconds, bool repeat = false)
        {
            return new DoubleAnimation
            {
                From = from,
                To = to,
                Duration = TimeSpan.FromSeconds(durationSeconds),
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseInOut },
                RepeatBehavior = repeat ? RepeatBehavior.Forever : new RepeatBehavior(1),
                AutoReverse = repeat
            };
        }

        public void Reset()
        {
            _currentAnimation?.Stop();
            BreathingScale.ScaleX = 1.0;
            BreathingScale.ScaleY = 1.0;
            BreathingEllipse.Opacity = 0.6;
            Phase = BreathingPhase.Idle;
        }
    }

    public enum BreathingPhase
    {
        Idle,
        Inhale,
        Hold,
        Exhale
    }
}
