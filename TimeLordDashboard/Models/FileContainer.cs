using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;

namespace TimeLordDashboard.Models
{
    /// <summary>
    /// Represents a custom container for organizing files and folders
    /// </summary>
    public class FileContainer
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string IconGlyph { get; set; } = "\uE8B7"; // Folder icon
        public string Color { get; set; } = "#0078D4";
        public ContainerType Type { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime LastAccessedAt { get; set; }
        public ObservableCollection<FileItem> Items { get; set; } = new();
        public int SortOrder { get; set; }
        public bool IsPinned { get; set; }
        public Dictionary<string, string> Metadata { get; set; } = new();
    }

    public enum ContainerType
    {
        Recent,
        Favorites,
        Work,
        Personal,
        Projects,
        Documents,
        Media,
        Custom
    }

    /// <summary>
    /// Represents a file or folder item within a container
    /// </summary>
    public class FileItem
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public FileItemType Type { get; set; }
        public long Size { get; set; }
        public DateTime CreatedDate { get; set; }
        public DateTime ModifiedDate { get; set; }
        public DateTime LastAccessedDate { get; set; }
        public string IconGlyph { get; set; } = "\uE8A5"; // Document icon
        public bool IsStarred { get; set; }
        public List<string> Tags { get; set; } = new();
        public string? ThumbnailPath { get; set; }
    }

    public enum FileItemType
    {
        File,
        Folder,
        CloudFile,
        RecentFile
    }
}
