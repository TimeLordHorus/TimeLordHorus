using Microsoft.UI.Xaml.Data;
using System;
using TimeLordDashboard.Models;

namespace TimeLordDashboard.Helpers;

public class TaskStatusToBoolConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, string language)
    {
        if (value is TaskStatus status)
        {
            return status == TaskStatus.Completed;
        }
        return false;
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        if (value is bool isChecked)
        {
            return isChecked ? TaskStatus.Completed : TaskStatus.InProgress;
        }
        return TaskStatus.NotStarted;
    }
}
