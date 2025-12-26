using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using TimeLordDashboard.Models;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace TimeLordDashboard.Services
{
    /// <summary>
    /// Service for exporting and importing user data
    /// </summary>
    public class ExportImportService
    {
        private static ExportImportService? _instance;
        private static readonly object _lock = new();

        private readonly WellbeingService _wellbeingService;
        private readonly FileManagementService _fileService;
        private readonly SettingsService _settingsService;

        public static ExportImportService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new ExportImportService();
                }
            }
        }

        private ExportImportService()
        {
            _wellbeingService = WellbeingService.Instance;
            _fileService = FileManagementService.Instance;
            _settingsService = SettingsService.Instance;
        }

        /// <summary>
        /// Export all user data to JSON file
        /// </summary>
        public async Task<bool> ExportAllDataAsync(StorageFile file)
        {
            try
            {
                var exportData = new ExportData
                {
                    ExportDate = DateTime.Now,
                    Version = "1.0.0",
                    WellbeingMetrics = _wellbeingService.Metrics.ToList(),
                    WellbeingReminders = _wellbeingService.Reminders.ToList(),
                    FileContainers = _fileService.Containers.ToList(),
                    UserPreferences = _settingsService.CurrentPreferences
                };

                var json = JsonSerializer.Serialize(exportData, new JsonSerializerOptions
                {
                    WriteIndented = true
                });

                await FileIO.WriteTextAsync(file, json);

                System.Diagnostics.Debug.WriteLine($"Data exported successfully to {file.Path}");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Export error: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Import user data from JSON file
        /// </summary>
        public async Task<bool> ImportAllDataAsync(StorageFile file)
        {
            try
            {
                var json = await FileIO.ReadTextAsync(file);
                var importData = JsonSerializer.Deserialize<ExportData>(json);

                if (importData == null)
                {
                    throw new InvalidDataException("Invalid import file format");
                }

                // Import metrics
                if (importData.WellbeingMetrics != null)
                {
                    _wellbeingService.Metrics.Clear();
                    foreach (var metric in importData.WellbeingMetrics)
                    {
                        _wellbeingService.Metrics.Add(metric);
                    }
                }

                // Import reminders
                if (importData.WellbeingReminders != null)
                {
                    _wellbeingService.Reminders.Clear();
                    foreach (var reminder in importData.WellbeingReminders)
                    {
                        _wellbeingService.Reminders.Add(reminder);
                    }
                }

                // Import containers (but not file items - they may not exist on this system)
                if (importData.FileContainers != null)
                {
                    _fileService.Containers.Clear();
                    foreach (var container in importData.FileContainers)
                    {
                        container.Items.Clear(); // Don't import file paths
                        _fileService.Containers.Add(container);
                    }
                }

                System.Diagnostics.Debug.WriteLine($"Data imported successfully from {file.Path}");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Import error: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Export wellbeing metrics to CSV
        /// </summary>
        public async Task<bool> ExportMetricsToCsvAsync(StorageFile file)
        {
            try
            {
                var csv = new System.Text.StringBuilder();
                csv.AppendLine("Metric,Type,Current Value,Target Value,Unit,Last Updated");

                foreach (var metric in _wellbeingService.Metrics)
                {
                    csv.AppendLine($"\"{metric.Name}\",{metric.Type},{metric.CurrentValue}," +
                                 $"{metric.TargetValue},\"{metric.Unit}\",{metric.LastUpdated:yyyy-MM-dd HH:mm:ss}");
                }

                // Add history data
                csv.AppendLine();
                csv.AppendLine("Metric History");
                csv.AppendLine("Metric,Timestamp,Value,Note");

                foreach (var metric in _wellbeingService.Metrics)
                {
                    foreach (var dataPoint in metric.History)
                    {
                        csv.AppendLine($"\"{metric.Name}\",{dataPoint.Timestamp:yyyy-MM-dd HH:mm:ss}," +
                                     $"{dataPoint.Value},\"{dataPoint.Note ?? ""}\"");
                    }
                }

                await FileIO.WriteTextAsync(file, csv.ToString());

                System.Diagnostics.Debug.WriteLine($"Metrics exported to CSV: {file.Path}");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"CSV export error: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Show file picker for export
        /// </summary>
        public async Task<StorageFile?> PickExportFileAsync(string suggestedFileName, string fileTypeLabel, string fileExtension)
        {
            try
            {
                var savePicker = new FileSavePicker();
                savePicker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
                savePicker.FileTypeChoices.Add(fileTypeLabel, new List<string> { fileExtension });
                savePicker.SuggestedFileName = suggestedFileName;

                // Get window handle for picker
                var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
                WinRT.Interop.InitializeWithWindow.Initialize(savePicker, hwnd);

                return await savePicker.PickSaveFileAsync();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"File picker error: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Show file picker for import
        /// </summary>
        public async Task<StorageFile?> PickImportFileAsync(string fileTypeLabel, params string[] fileExtensions)
        {
            try
            {
                var openPicker = new FileOpenPicker();
                openPicker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
                openPicker.FileTypeFilter.Add("*");

                foreach (var extension in fileExtensions)
                {
                    openPicker.FileTypeFilter.Add(extension);
                }

                // Get window handle for picker
                var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
                WinRT.Interop.InitializeWithWindow.Initialize(openPicker, hwnd);

                return await openPicker.PickSingleFileAsync();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"File picker error: {ex.Message}");
                return null;
            }
        }
    }

    /// <summary>
    /// Data structure for export/import
    /// </summary>
    public class ExportData
    {
        public DateTime ExportDate { get; set; }
        public string Version { get; set; } = "1.0.0";
        public List<WellbeingMetric>? WellbeingMetrics { get; set; }
        public List<WellbeingReminder>? WellbeingReminders { get; set; }
        public List<FileContainer>? FileContainers { get; set; }
        public UserPreferences? UserPreferences { get; set; }
    }
}
