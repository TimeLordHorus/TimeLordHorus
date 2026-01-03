using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using TimeLordDashboard.Models;
using Windows.Storage;
using Windows.Storage.FileProperties;
using Windows.Storage.Search;

namespace TimeLordDashboard.Services
{
    /// <summary>
    /// Manages file operations using Windows.Storage APIs
    /// </summary>
    public class FileManagementService
    {
        private static FileManagementService? _instance;
        private static readonly object _lock = new();

        public ObservableCollection<FileContainer> Containers { get; } = new();

        public static FileManagementService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new FileManagementService();
                }
            }
        }

        private FileManagementService()
        {
            InitializeDefaultContainers();
        }

        private void InitializeDefaultContainers()
        {
            // Add default containers
            Containers.Add(new FileContainer
            {
                Id = Guid.NewGuid(),
                Name = "Recent Files",
                Description = "Recently accessed files",
                Type = ContainerType.Recent,
                IconGlyph = "\uE823",
                Color = "#0078D4",
                CreatedAt = DateTime.Now,
                LastAccessedAt = DateTime.Now,
                IsPinned = true,
                SortOrder = 0
            });

            Containers.Add(new FileContainer
            {
                Id = Guid.NewGuid(),
                Name = "Favorites",
                Description = "Your favorite files and folders",
                Type = ContainerType.Favorites,
                IconGlyph = "\uE734",
                Color = "#FFB900",
                CreatedAt = DateTime.Now,
                LastAccessedAt = DateTime.Now,
                IsPinned = true,
                SortOrder = 1
            });

            Containers.Add(new FileContainer
            {
                Id = Guid.NewGuid(),
                Name = "Work Documents",
                Description = "Professional documents and projects",
                Type = ContainerType.Work,
                IconGlyph = "\uE821",
                Color = "#00B7C3",
                CreatedAt = DateTime.Now,
                LastAccessedAt = DateTime.Now,
                SortOrder = 2
            });

            Containers.Add(new FileContainer
            {
                Id = Guid.NewGuid(),
                Name = "Personal",
                Description = "Personal files and media",
                Type = ContainerType.Personal,
                IconGlyph = "\uE716",
                Color = "#8E8CD8",
                CreatedAt = DateTime.Now,
                LastAccessedAt = DateTime.Now,
                SortOrder = 3
            });
        }

        /// <summary>
        /// Browse files in a specific folder
        /// </summary>
        public async Task<List<FileItem>> BrowseFolderAsync(StorageFolder folder)
        {
            var items = new List<FileItem>();

            try
            {
                var files = await folder.GetFilesAsync();
                var folders = await folder.GetFoldersAsync();

                // Add folders
                foreach (var subfolder in folders)
                {
                    items.Add(new FileItem
                    {
                        Id = Guid.NewGuid(),
                        Name = subfolder.Name,
                        Path = subfolder.Path,
                        Type = FileItemType.Folder,
                        IconGlyph = "\uE8B7",
                        CreatedDate = subfolder.DateCreated.DateTime,
                        ModifiedDate = DateTime.Now
                    });
                }

                // Add files
                foreach (var file in files)
                {
                    var props = await file.GetBasicPropertiesAsync();

                    items.Add(new FileItem
                    {
                        Id = Guid.NewGuid(),
                        Name = file.Name,
                        Path = file.Path,
                        Type = FileItemType.File,
                        Size = (long)props.Size,
                        CreatedDate = file.DateCreated.DateTime,
                        ModifiedDate = props.DateModified.DateTime,
                        IconGlyph = GetFileIconGlyph(file.FileType)
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error browsing folder: {ex.Message}");
            }

            return items;
        }

        /// <summary>
        /// Get recent files from the system
        /// </summary>
        public async Task<List<FileItem>> GetRecentFilesAsync(int maxCount = 20)
        {
            var items = new List<FileItem>();

            try
            {
                var recentFolder = await StorageFolder.GetFolderFromPathAsync(
                    Environment.GetFolderPath(Environment.SpecialFolder.Recent));

                var queryOptions = new QueryOptions(CommonFileQuery.OrderByDate, new[] { "*" })
                {
                    FolderDepth = FolderDepth.Deep
                };

                var query = recentFolder.CreateFileQueryWithOptions(queryOptions);
                var files = await query.GetFilesAsync(0, (uint)maxCount);

                foreach (var file in files)
                {
                    var props = await file.GetBasicPropertiesAsync();

                    items.Add(new FileItem
                    {
                        Id = Guid.NewGuid(),
                        Name = file.Name,
                        Path = file.Path,
                        Type = FileItemType.RecentFile,
                        Size = (long)props.Size,
                        CreatedDate = file.DateCreated.DateTime,
                        ModifiedDate = props.DateModified.DateTime,
                        LastAccessedDate = DateTime.Now,
                        IconGlyph = GetFileIconGlyph(file.FileType)
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting recent files: {ex.Message}");
            }

            return items;
        }

        /// <summary>
        /// Search for files matching a query
        /// </summary>
        public async Task<List<FileItem>> SearchFilesAsync(StorageFolder folder, string searchQuery)
        {
            var items = new List<FileItem>();

            try
            {
                var queryOptions = new QueryOptions(CommonFileQuery.OrderByName, new[] { "*" })
                {
                    FolderDepth = FolderDepth.Deep,
                    UserSearchFilter = searchQuery
                };

                var query = folder.CreateFileQueryWithOptions(queryOptions);
                var files = await query.GetFilesAsync();

                foreach (var file in files.Take(50)) // Limit to 50 results
                {
                    var props = await file.GetBasicPropertiesAsync();

                    items.Add(new FileItem
                    {
                        Id = Guid.NewGuid(),
                        Name = file.Name,
                        Path = file.Path,
                        Type = FileItemType.File,
                        Size = (long)props.Size,
                        CreatedDate = file.DateCreated.DateTime,
                        ModifiedDate = props.DateModified.DateTime,
                        IconGlyph = GetFileIconGlyph(file.FileType)
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error searching files: {ex.Message}");
            }

            return items;
        }

        /// <summary>
        /// Get icon glyph based on file extension
        /// </summary>
        private string GetFileIconGlyph(string extension)
        {
            return extension.ToLower() switch
            {
                ".txt" => "\uE8A5",
                ".doc" or ".docx" => "\uE8A5",
                ".pdf" => "\uE8A5",
                ".jpg" or ".jpeg" or ".png" or ".gif" => "\uEB9F",
                ".mp4" or ".avi" or ".mov" => "\uE8B2",
                ".mp3" or ".wav" or ".flac" => "\uE8D6",
                ".zip" or ".rar" or ".7z" => "\uE8B5",
                ".exe" => "\uE7C1",
                ".cs" or ".js" or ".py" or ".java" => "\uE943",
                _ => "\uE8A5"
            };
        }

        /// <summary>
        /// Add file to a container
        /// </summary>
        public void AddFileToContainer(Guid containerId, FileItem file)
        {
            var container = Containers.FirstOrDefault(c => c.Id == containerId);
            if (container != null)
            {
                container.Items.Add(file);
                container.LastAccessedAt = DateTime.Now;
            }
        }

        /// <summary>
        /// Create a new custom container
        /// </summary>
        public FileContainer CreateContainer(string name, string description, string color)
        {
            var container = new FileContainer
            {
                Id = Guid.NewGuid(),
                Name = name,
                Description = description,
                Type = ContainerType.Custom,
                Color = color,
                CreatedAt = DateTime.Now,
                LastAccessedAt = DateTime.Now,
                SortOrder = Containers.Count
            };

            Containers.Add(container);
            return container;
        }
    }
}
