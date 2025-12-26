using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using TimeLordDashboard.Models;
using TimeLordDashboard.ViewModels;

namespace TimeLordDashboard.Views
{
    public sealed partial class FileManagementPage : Page
    {
        public FileManagementViewModel ViewModel { get; }

        public FileManagementPage()
        {
            this.InitializeComponent();
            ViewModel = new FileManagementViewModel();
        }

        private void SearchBox_QuerySubmitted(AutoSuggestBox sender, AutoSuggestBoxQuerySubmittedEventArgs args)
        {
            ViewModel.SearchFilesCommand.Execute(null);
        }

        private void FileItem_DoubleTapped(object sender, DoubleTappedRoutedEventArgs e)
        {
            if (sender is Grid grid && grid.DataContext is FileItem item)
            {
                ViewModel.OpenFileCommand.Execute(item);
            }
        }
    }
}
