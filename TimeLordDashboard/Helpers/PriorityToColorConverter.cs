using Microsoft.UI;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Media;
using System;
using TimeLordDashboard.Models;

namespace TimeLordDashboard.Helpers;

public class PriorityToColorConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, string language)
    {
        if (value is TaskPriority priority)
        {
            return priority switch
            {
                TaskPriority.Urgent => new SolidColorBrush(Color.FromArgb(255, 255, 0, 64)), // Plasma Red
                TaskPriority.High => new SolidColorBrush(Color.FromArgb(255, 255, 107, 0)), // Neon Orange
                TaskPriority.Medium => new SolidColorBrush(Color.FromArgb(255, 255, 182, 0)), // Neon Gold
                TaskPriority.Low => new SolidColorBrush(Color.FromArgb(255, 0, 128, 255)), // Electric Blue
                _ => new SolidColorBrush(Color.FromArgb(255, 113, 121, 126)) // Iron Gray
            };
        }

        // Fallback for string representation
        if (value is string priorityStr)
        {
            return priorityStr.ToLower() switch
            {
                "urgent" => new SolidColorBrush(Color.FromArgb(255, 255, 0, 64)),
                "high" => new SolidColorBrush(Color.FromArgb(255, 255, 107, 0)),
                "medium" => new SolidColorBrush(Color.FromArgb(255, 255, 182, 0)),
                "low" => new SolidColorBrush(Color.FromArgb(255, 0, 128, 255)),
                _ => new SolidColorBrush(Color.FromArgb(255, 113, 121, 126))
            };
        }

        return new SolidColorBrush(Color.FromArgb(255, 113, 121, 126));
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}
