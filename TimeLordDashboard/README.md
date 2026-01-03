# TimeLord Dashboard - Windows 11 Desktop Application

A modern Windows 11 desktop application built with WinUI 3 that combines personal wellbeing monitoring and intelligent file management into a unified productivity hub.

## Features

### 🗂️ File Management System
- **Smart Containers**: Organize files into customizable containers (Recent, Favorites, Work, Personal)
- **Quick Access**: Browse, search, and access files across your system
- **Drag & Drop Support**: Intuitive file organization
- **Recent Files Tracking**: Automatically track recently accessed files
- **Custom Categories**: Create your own file organization schemes

### 🧘 Wellbeing Monitoring
- **Health Metrics Tracking**:
  - Screen time monitoring
  - Break time tracking
  - Hydration tracking (water intake)
  - Posture score monitoring
  - Stress level tracking

- **Smart Reminders**:
  - Customizable break reminders
  - Eye rest notifications (20-20-20 rule)
  - Hydration reminders
  - Posture check alerts

- **Mindfulness Tools**:
  - Guided breathing exercises (4-4-4 breathing technique)
  - Visual breathing guides
  - Progress tracking

### 📊 Analytics & Insights
- Visual charts and graphs for tracking trends
- Productivity insights
- Wellbeing score calculations
- Activity heatmaps
- Personalized recommendations

### ⚙️ Customization
- Theme selection (Light, Dark, System)
- Configurable reminder intervals
- Adjustable health goals
- Customizable dashboard layout
- Privacy controls

## Technology Stack

### Platform & Framework
- **WinUI 3** - Modern Windows UI framework
- **.NET 7** - Latest .NET runtime
- **Windows 11** - Target platform with Fluent Design

### Architecture
- **MVVM Pattern** - Clean separation of concerns using CommunityToolkit.Mvvm
- **Windows.Storage APIs** - Native file system integration
- **SQLite** - Local data persistence
- **LiveCharts2** - Data visualization

### Key Libraries
- `Microsoft.WindowsAppSDK` (1.4.x) - WinUI 3 framework
- `CommunityToolkit.Mvvm` (8.2.2) - MVVM helpers
- `CommunityToolkit.WinUI.UI.Controls` (7.1.2) - Additional UI controls
- `Microsoft.Data.Sqlite` (7.0.14) - Database support
- `LiveChartsCore.SkiaSharpView.WinUI` (2.0.0-rc2) - Charts and graphs

## Project Structure

```
TimeLordDashboard/
├── Models/                      # Data models
│   ├── FileContainer.cs         # File management models
│   ├── WellbeingMetric.cs      # Health tracking models
│   └── UserPreferences.cs      # Settings models
│
├── ViewModels/                  # MVVM ViewModels
│   ├── DashboardViewModel.cs
│   ├── FileManagementViewModel.cs
│   └── WellbeingViewModel.cs
│
├── Views/                       # XAML Pages
│   ├── DashboardPage.xaml      # Main dashboard
│   ├── FileManagementPage.xaml # File browser
│   ├── WellbeingPage.xaml      # Health tracking
│   ├── AnalyticsPage.xaml      # Charts & insights
│   └── SettingsPage.xaml       # App settings
│
├── Services/                    # Business logic
│   ├── DatabaseService.cs      # SQLite operations
│   ├── FileManagementService.cs # File system operations
│   └── WellbeingService.cs     # Health tracking logic
│
├── Helpers/                     # Utilities
│   └── InverseBooleanConverter.cs
│
├── Assets/                      # Images, icons
├── Controls/                    # Custom controls
├── App.xaml                     # Application resources
├── MainWindow.xaml              # Main window
└── Package.appxmanifest         # App manifest

```

## Prerequisites

- **Windows 11** (version 10.0.22000.0 or higher)
- **Visual Studio 2022** (17.4 or later)
  - Workload: ".NET Desktop Development"
  - Workload: "Universal Windows Platform development"
  - Individual component: "Windows App SDK"
- **.NET 7 SDK** or later

## Building the Project

### Using Visual Studio 2022

1. Open Visual Studio 2022
2. Select "Open a project or solution"
3. Navigate to `TimeLordDashboard/TimeLordDashboard.csproj`
4. Press F5 to build and run in Debug mode
   - Or select Build > Build Solution

### Using Command Line

```bash
# Navigate to project directory
cd TimeLordDashboard

# Restore NuGet packages
dotnet restore

# Build the project
dotnet build

# Run the application
dotnet run
```

### Publishing

To create a production build:

```bash
# Publish for Windows 11 x64
dotnet publish -c Release -r win10-x64

# Publish for Windows 11 ARM64
dotnet publish -c Release -r win10-arm64
```

## Database

The application uses SQLite for local data storage. The database file (`timelord.db`) is automatically created in the local application data folder:

```
%LOCALAPPDATA%\Packages\TimeLordDashboard_[hash]\LocalState\timelord.db
```

### Database Schema

- **FileContainers** - Custom file organization containers
- **FileItems** - Tracked files and folders
- **WellbeingMetrics** - Health metrics and current values
- **MetricDataPoints** - Historical metric data
- **WellbeingReminders** - User-configured reminders
- **UserPreferences** - Application settings

## Key Features Implementation

### File Management
Uses Windows.Storage APIs to:
- Browse folders with `StorageFolder.GetFilesAsync()`
- Track recent files via Windows Recent folder
- Search files using `QueryOptions` and `CommonFileQuery`
- Get file metadata with `BasicProperties`

### Wellbeing Tracking
- Background service tracks screen time continuously
- Timer-based reminder system
- Metric history with configurable retention (7 days default)
- Data visualization ready for LiveCharts integration

### Fluent Design
- Acrylic/Mica materials (when transparency enabled)
- Rounded corners (CardCornerRadius: 12px)
- Windows 11 color palette
- Responsive layouts with Grid and StackPanel
- Icon-based navigation using Segoe MDL2 Assets

## Privacy & Security

- All data stored locally on device
- No cloud synchronization (future feature)
- User controls for data collection
- Export and delete data options
- No external API calls (except future health integrations)

## Future Enhancements

### Planned Features (Not Yet Implemented)
- [ ] **Cloud Integration**: OneDrive API for cloud file management
- [ ] **Health API Integration**:
  - Fitbit SDK
  - Garmin Health API
  - Microsoft Health integration
- [ ] **Advanced Analytics**:
  - LiveCharts implementation for all visualizations
  - Machine learning insights
  - Productivity pattern detection
- [ ] **Additional Wellbeing Tools**:
  - Posture detection via webcam
  - Meditation guides
  - Sleep tracking integration
- [ ] **Gamification**:
  - Achievement system
  - Streak tracking
  - Leaderboards (optional)

### Technical Improvements
- [ ] Implement comprehensive unit tests
- [ ] Add integration tests for services
- [ ] Performance optimization for large file sets
- [ ] Accessibility improvements (screen reader support)
- [ ] Localization (multi-language support)

## Development Guidelines

### MVVM Pattern
- ViewModels use `CommunityToolkit.Mvvm` attributes
- `[ObservableProperty]` for data binding
- `[RelayCommand]` for commands
- ViewModels are completely UI-agnostic

### Code Style
- Use nullable reference types
- Follow C# naming conventions
- XML documentation for public APIs
- Async/await for I/O operations

### UI/UX
- Follow Windows 11 Fluent Design guidelines
- Maintain 8px spacing grid
- Use theme resources for colors
- Ensure keyboard navigation support

## Troubleshooting

### Build Errors

**Error: WindowsAppSDK not found**
- Install Windows App SDK via Visual Studio Installer
- Or install via: `winget install Microsoft.WindowsAppRuntime.1.4`

**Error: Target platform version not found**
- Update Windows SDK in Visual Studio Installer
- Set `TargetPlatformMinVersion` in .csproj if needed

### Runtime Issues

**Database not created**
- Ensure app has LocalFolder access
- Check Package.appxmanifest capabilities
- Run Visual Studio as Administrator (first time only)

**File access denied**
- Grant required permissions in Settings > Privacy
- Check Package.appxmanifest capabilities (documentsLibrary, etc.)

## Contributing

This is a personal productivity application. Contributions are welcome for:
- Bug fixes
- Performance improvements
- New wellbeing features
- UI/UX enhancements
- Documentation updates

## License

This project is for personal use. See repository license for details.

## Acknowledgments

- **Microsoft** - WinUI 3 framework and Windows App SDK
- **CommunityToolkit** - MVVM and UI controls
- **LiveCharts** - Data visualization library
- **Windows 11 Design Team** - Fluent Design System

---

Built with ❤️ for Windows 11 | TimeLord Dashboard v1.0.0
