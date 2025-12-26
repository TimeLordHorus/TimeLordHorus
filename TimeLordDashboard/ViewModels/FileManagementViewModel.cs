using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using TimeLordDashboard.Models;
using TimeLordDashboard.Services;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace TimeLordDashboard.ViewModels
{
    public partial class FileManagementViewModel : ObservableObject
    {
        private readonly FileManagementService _fileService;

        [ObservableProperty]
        private ObservableCollection<FileContainer> containers;

        [ObservableProperty]
        private FileContainer? selectedContainer;

        [ObservableProperty]
        private ObservableCollection<FileItem> currentItems;

        [ObservableProperty]
        private string searchQuery = string.Empty;

        [ObservableProperty]
        private bool isLoading;

        [ObservableProperty]
        private string currentPath = string.Empty;

        public FileManagementViewModel()
        {
            _fileService = FileManagementService.Instance;
            containers = _fileService.Containers;
            currentItems = new ObservableCollection<FileItem>();

            // Select first container by default
            if (containers.Any())
            {
                SelectedContainer = containers.First();
            }
        }

        partial void OnSelectedContainerChanged(FileContainer? value)
        {
            if (value != null)
            {
                LoadContainerItems(value);
            }
        }

        private void LoadContainerItems(FileContainer container)
        {
            CurrentItems.Clear();

            foreach (var item in container.Items)
            {
                CurrentItems.Add(item);
            }

            container.LastAccessedAt = DateTime.Now;
        }

        [RelayCommand]
        private async Task BrowseFolderAsync()
        {
            try
            {
                IsLoading = true;

                var picker = new FolderPicker();
                picker.FileTypeFilter.Add("*");

                // Get the current window handle
                var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
                WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);

                var folder = await picker.PickSingleFolderAsync();

                if (folder != null)
                {
                    CurrentPath = folder.Path;
                    var items = await _fileService.BrowseFolderAsync(folder);

                    CurrentItems.Clear();
                    foreach (var item in items)
                    {
                        CurrentItems.Add(item);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error browsing folder: {ex.Message}");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task LoadRecentFilesAsync()
        {
            try
            {
                IsLoading = true;

                var items = await _fileService.GetRecentFilesAsync();

                CurrentItems.Clear();
                foreach (var item in items)
                {
                    CurrentItems.Add(item);
                }

                CurrentPath = "Recent Files";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading recent files: {ex.Message}");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task SearchFilesAsync()
        {
            if (string.IsNullOrWhiteSpace(SearchQuery))
            {
                return;
            }

            try
            {
                IsLoading = true;

                // Search in Documents folder
                var documentsFolder = await StorageFolder.GetFolderFromPathAsync(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments));

                var items = await _fileService.SearchFilesAsync(documentsFolder, SearchQuery);

                CurrentItems.Clear();
                foreach (var item in items)
                {
                    CurrentItems.Add(item);
                }

                CurrentPath = $"Search Results for '{SearchQuery}'";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error searching files: {ex.Message}");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private void AddToFavorites(FileItem item)
        {
            var favoritesContainer = Containers.FirstOrDefault(c => c.Type == ContainerType.Favorites);
            if (favoritesContainer != null && !favoritesContainer.Items.Contains(item))
            {
                item.IsStarred = true;
                _fileService.AddFileToContainer(favoritesContainer.Id, item);
            }
        }

        [RelayCommand]
        private void CreateNewContainer()
        {
            var newContainer = _fileService.CreateContainer(
                "New Container",
                "Custom file container",
                "#8E8CD8");

            SelectedContainer = newContainer;
        }

        [RelayCommand]
        private void DeleteContainer(FileContainer container)
        {
            if (container.Type == ContainerType.Custom)
            {
                Containers.Remove(container);

                if (SelectedContainer == container)
                {
                    SelectedContainer = Containers.FirstOrDefault();
                }
            }
        }

        [RelayCommand]
        private void OpenFile(FileItem item)
        {
            try
            {
                // Open file with default application
                var process = new System.Diagnostics.Process
                {
                    StartInfo = new System.Diagnostics.ProcessStartInfo(item.Path)
                    {
                        UseShellExecute = true
                    }
                };
                process.Start();

                item.LastAccessedDate = DateTime.Now;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error opening file: {ex.Message}");
            }
        }
    }
}
