using Microsoft.Data.Sqlite;
using System;
using System.IO;
using Windows.Storage;

namespace TimeLordDashboard.Services
{
    /// <summary>
    /// Manages SQLite database operations
    /// </summary>
    public class DatabaseService
    {
        private static DatabaseService? _instance;
        private static readonly object _lock = new();
        private SqliteConnection? _connection;
        private string _dbPath = string.Empty;

        public static DatabaseService Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new DatabaseService();
                }
            }
        }

        private DatabaseService() { }

        public void Initialize()
        {
            try
            {
                // Get local application data folder
                string localFolder = ApplicationData.Current.LocalFolder.Path;
                _dbPath = Path.Combine(localFolder, "timelord.db");

                _connection = new SqliteConnection($"Data Source={_dbPath}");
                _connection.Open();

                CreateTables();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Database initialization error: {ex.Message}");
                throw;
            }
        }

        private void CreateTables()
        {
            if (_connection == null) return;

            // FileContainers table
            ExecuteNonQuery(@"
                CREATE TABLE IF NOT EXISTS FileContainers (
                    Id TEXT PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Description TEXT,
                    IconGlyph TEXT,
                    Color TEXT,
                    Type INTEGER,
                    CreatedAt TEXT,
                    LastAccessedAt TEXT,
                    SortOrder INTEGER,
                    IsPinned INTEGER,
                    Metadata TEXT
                )");

            // FileItems table
            ExecuteNonQuery(@"
                CREATE TABLE IF NOT EXISTS FileItems (
                    Id TEXT PRIMARY KEY,
                    ContainerId TEXT,
                    Name TEXT NOT NULL,
                    Path TEXT NOT NULL,
                    Type INTEGER,
                    Size INTEGER,
                    CreatedDate TEXT,
                    ModifiedDate TEXT,
                    LastAccessedDate TEXT,
                    IconGlyph TEXT,
                    IsStarred INTEGER,
                    Tags TEXT,
                    ThumbnailPath TEXT,
                    FOREIGN KEY (ContainerId) REFERENCES FileContainers(Id)
                )");

            // WellbeingMetrics table
            ExecuteNonQuery(@"
                CREATE TABLE IF NOT EXISTS WellbeingMetrics (
                    Id TEXT PRIMARY KEY,
                    Type INTEGER,
                    Name TEXT NOT NULL,
                    Unit TEXT,
                    CurrentValue REAL,
                    TargetValue REAL,
                    MinValue REAL,
                    MaxValue REAL,
                    LastUpdated TEXT,
                    IconGlyph TEXT,
                    Color TEXT
                )");

            // MetricDataPoints table
            ExecuteNonQuery(@"
                CREATE TABLE IF NOT EXISTS MetricDataPoints (
                    Id TEXT PRIMARY KEY,
                    MetricId TEXT,
                    Timestamp TEXT,
                    Value REAL,
                    Note TEXT,
                    FOREIGN KEY (MetricId) REFERENCES WellbeingMetrics(Id)
                )");

            // WellbeingReminders table
            ExecuteNonQuery(@"
                CREATE TABLE IF NOT EXISTS WellbeingReminders (
                    Id TEXT PRIMARY KEY,
                    Title TEXT NOT NULL,
                    Description TEXT,
                    Type INTEGER,
                    IntervalMinutes INTEGER,
                    LastTriggered TEXT,
                    IsEnabled INTEGER,
                    IconGlyph TEXT
                )");

            // UserPreferences table
            ExecuteNonQuery(@"
                CREATE TABLE IF NOT EXISTS UserPreferences (
                    UserId TEXT PRIMARY KEY,
                    UserName TEXT,
                    Theme INTEGER,
                    NotificationsEnabled INTEGER,
                    WellbeingRemindersEnabled INTEGER,
                    BreakReminderInterval INTEGER,
                    CustomSettings TEXT
                )");
        }

        public void ExecuteNonQuery(string sql, params SqliteParameter[] parameters)
        {
            if (_connection == null) return;

            using var command = _connection.CreateCommand();
            command.CommandText = sql;
            if (parameters != null)
            {
                command.Parameters.AddRange(parameters);
            }
            command.ExecuteNonQuery();
        }

        public SqliteDataReader? ExecuteReader(string sql, params SqliteParameter[] parameters)
        {
            if (_connection == null) return null;

            var command = _connection.CreateCommand();
            command.CommandText = sql;
            if (parameters != null)
            {
                command.Parameters.AddRange(parameters);
            }
            return command.ExecuteReader();
        }

        public void Close()
        {
            _connection?.Close();
            _connection?.Dispose();
        }
    }
}
