using System;
using System.Collections.Generic;

namespace TimeLordDashboard.Helpers
{
    /// <summary>
    /// Helper class for determining file types and appropriate icons
    /// </summary>
    public static class FileTypeHelper
    {
        private static readonly Dictionary<string, FileTypeInfo> _fileTypes = new()
        {
            // Documents
            { ".txt", new FileTypeInfo("Text Document", "\uE8A5", "Document", "#0078D4") },
            { ".doc", new FileTypeInfo("Word Document", "\uE8A5", "Document", "#2B579A") },
            { ".docx", new FileTypeInfo("Word Document", "\uE8A5", "Document", "#2B579A") },
            { ".pdf", new FileTypeInfo("PDF Document", "\uE8A5", "Document", "#E81123") },
            { ".rtf", new FileTypeInfo("Rich Text", "\uE8A5", "Document", "#0078D4") },
            { ".odt", new FileTypeInfo("OpenDocument Text", "\uE8A5", "Document", "#0078D4") },

            // Spreadsheets
            { ".xls", new FileTypeInfo("Excel Spreadsheet", "\uE8A5", "Spreadsheet", "#107C10") },
            { ".xlsx", new FileTypeInfo("Excel Spreadsheet", "\uE8A5", "Spreadsheet", "#107C10") },
            { ".csv", new FileTypeInfo("CSV File", "\uE8A5", "Spreadsheet", "#107C10") },
            { ".ods", new FileTypeInfo("OpenDocument Spreadsheet", "\uE8A5", "Spreadsheet", "#107C10") },

            // Presentations
            { ".ppt", new FileTypeInfo("PowerPoint", "\uE8A5", "Presentation", "#D83B01") },
            { ".pptx", new FileTypeInfo("PowerPoint", "\uE8A5", "Presentation", "#D83B01") },
            { ".odp", new FileTypeInfo("OpenDocument Presentation", "\uE8A5", "Presentation", "#D83B01") },

            // Images
            { ".jpg", new FileTypeInfo("JPEG Image", "\uEB9F", "Image", "#00B7C3") },
            { ".jpeg", new FileTypeInfo("JPEG Image", "\uEB9F", "Image", "#00B7C3") },
            { ".png", new FileTypeInfo("PNG Image", "\uEB9F", "Image", "#00B7C3") },
            { ".gif", new FileTypeInfo("GIF Image", "\uEB9F", "Image", "#00B7C3") },
            { ".bmp", new FileTypeInfo("Bitmap Image", "\uEB9F", "Image", "#00B7C3") },
            { ".svg", new FileTypeInfo("SVG Image", "\uEB9F", "Image", "#00B7C3") },
            { ".ico", new FileTypeInfo("Icon", "\uEB9F", "Image", "#00B7C3") },
            { ".webp", new FileTypeInfo("WebP Image", "\uEB9F", "Image", "#00B7C3") },

            // Videos
            { ".mp4", new FileTypeInfo("MP4 Video", "\uE8B2", "Video", "#8E8CD8") },
            { ".avi", new FileTypeInfo("AVI Video", "\uE8B2", "Video", "#8E8CD8") },
            { ".mov", new FileTypeInfo("QuickTime Video", "\uE8B2", "Video", "#8E8CD8") },
            { ".wmv", new FileTypeInfo("Windows Media Video", "\uE8B2", "Video", "#8E8CD8") },
            { ".mkv", new FileTypeInfo("Matroska Video", "\uE8B2", "Video", "#8E8CD8") },
            { ".webm", new FileTypeInfo("WebM Video", "\uE8B2", "Video", "#8E8CD8") },

            // Audio
            { ".mp3", new FileTypeInfo("MP3 Audio", "\uE8D6", "Audio", "#FFB900") },
            { ".wav", new FileTypeInfo("WAV Audio", "\uE8D6", "Audio", "#FFB900") },
            { ".flac", new FileTypeInfo("FLAC Audio", "\uE8D6", "Audio", "#FFB900") },
            { ".m4a", new FileTypeInfo("M4A Audio", "\uE8D6", "Audio", "#FFB900") },
            { ".wma", new FileTypeInfo("Windows Media Audio", "\uE8D6", "Audio", "#FFB900") },
            { ".ogg", new FileTypeInfo("OGG Audio", "\uE8D6", "Audio", "#FFB900") },

            // Archives
            { ".zip", new FileTypeInfo("ZIP Archive", "\uE8B5", "Archive", "#8E8CD8") },
            { ".rar", new FileTypeInfo("RAR Archive", "\uE8B5", "Archive", "#8E8CD8") },
            { ".7z", new FileTypeInfo("7-Zip Archive", "\uE8B5", "Archive", "#8E8CD8") },
            { ".tar", new FileTypeInfo("TAR Archive", "\uE8B5", "Archive", "#8E8CD8") },
            { ".gz", new FileTypeInfo("GZIP Archive", "\uE8B5", "Archive", "#8E8CD8") },

            // Code
            { ".cs", new FileTypeInfo("C# Source", "\uE943", "Code", "#00B7C3") },
            { ".js", new FileTypeInfo("JavaScript", "\uE943", "Code", "#FFB900") },
            { ".ts", new FileTypeInfo("TypeScript", "\uE943", "Code", "#0078D4") },
            { ".py", new FileTypeInfo("Python Script", "\uE943", "Code", "#FFB900") },
            { ".java", new FileTypeInfo("Java Source", "\uE943", "Code", "#E81123") },
            { ".cpp", new FileTypeInfo("C++ Source", "\uE943", "Code", "#005A9E") },
            { ".c", new FileTypeInfo("C Source", "\uE943", "Code", "#005A9E") },
            { ".h", new FileTypeInfo("C/C++ Header", "\uE943", "Code", "#005A9E") },
            { ".html", new FileTypeInfo("HTML Document", "\uE943", "Code", "#E81123") },
            { ".css", new FileTypeInfo("CSS Stylesheet", "\uE943", "Code", "#0078D4") },
            { ".xml", new FileTypeInfo("XML File", "\uE943", "Code", "#107C10") },
            { ".json", new FileTypeInfo("JSON File", "\uE943", "Code", "#FFB900") },
            { ".xaml", new FileTypeInfo("XAML File", "\uE943", "Code", "#8E8CD8") },

            // Executables
            { ".exe", new FileTypeInfo("Application", "\uE7C1", "Executable", "#E81123") },
            { ".msi", new FileTypeInfo("Installer", "\uE7C1", "Executable", "#0078D4") },
            { ".dll", new FileTypeInfo("Library", "\uE7C1", "Executable", "#8E8CD8") },
            { ".bat", new FileTypeInfo("Batch File", "\uE7C1", "Executable", "#0078D4") },
            { ".ps1", new FileTypeInfo("PowerShell Script", "\uE7C1", "Executable", "#0078D4") },

            // Other
            { ".md", new FileTypeInfo("Markdown", "\uE8A5", "Document", "#0078D4") },
            { ".log", new FileTypeInfo("Log File", "\uE8A5", "Log", "#8E8CD8") },
            { ".db", new FileTypeInfo("Database", "\uE8A5", "Database", "#107C10") },
            { ".sqlite", new FileTypeInfo("SQLite Database", "\uE8A5", "Database", "#107C10") },
        };

        /// <summary>
        /// Get file type information for a file extension
        /// </summary>
        public static FileTypeInfo GetFileTypeInfo(string extension)
        {
            extension = extension.ToLower();

            if (_fileTypes.TryGetValue(extension, out var info))
            {
                return info;
            }

            // Default for unknown types
            return new FileTypeInfo("File", "\uE8A5", "Unknown", "#8E8CD8");
        }

        /// <summary>
        /// Get icon glyph for file extension
        /// </summary>
        public static string GetIconGlyph(string extension)
        {
            return GetFileTypeInfo(extension).IconGlyph;
        }

        /// <summary>
        /// Get color for file extension
        /// </summary>
        public static string GetColor(string extension)
        {
            return GetFileTypeInfo(extension).Color;
        }

        /// <summary>
        /// Check if file is an image
        /// </summary>
        public static bool IsImage(string extension)
        {
            return GetFileTypeInfo(extension).Category == "Image";
        }

        /// <summary>
        /// Check if file is a video
        /// </summary>
        public static bool IsVideo(string extension)
        {
            return GetFileTypeInfo(extension).Category == "Video";
        }

        /// <summary>
        /// Check if file is audio
        /// </summary>
        public static bool IsAudio(string extension)
        {
            return GetFileTypeInfo(extension).Category == "Audio";
        }

        /// <summary>
        /// Check if file is code
        /// </summary>
        public static bool IsCode(string extension)
        {
            return GetFileTypeInfo(extension).Category == "Code";
        }

        /// <summary>
        /// Check if file is a document
        /// </summary>
        public static bool IsDocument(string extension)
        {
            return GetFileTypeInfo(extension).Category == "Document";
        }

        /// <summary>
        /// Get all supported image extensions
        /// </summary>
        public static string[] GetImageExtensions()
        {
            return new[] { ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp" };
        }

        /// <summary>
        /// Get all supported video extensions
        /// </summary>
        public static string[] GetVideoExtensions()
        {
            return new[] { ".mp4", ".avi", ".mov", ".wmv", ".mkv", ".webm" };
        }

        /// <summary>
        /// Get all supported audio extensions
        /// </summary>
        public static string[] GetAudioExtensions()
        {
            return new[] { ".mp3", ".wav", ".flac", ".m4a", ".wma", ".ogg" };
        }
    }

    /// <summary>
    /// Information about a file type
    /// </summary>
    public class FileTypeInfo
    {
        public string Description { get; set; }
        public string IconGlyph { get; set; }
        public string Category { get; set; }
        public string Color { get; set; }

        public FileTypeInfo(string description, string iconGlyph, string category, string color)
        {
            Description = description;
            IconGlyph = iconGlyph;
            Category = category;
            Color = color;
        }
    }
}
