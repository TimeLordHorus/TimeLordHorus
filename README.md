# TimeLord Browser 🌐

A lightweight, feature-rich Progressive Web App (PWA) browser built with vanilla JavaScript. Experience fast, modern browsing with offline capabilities, Bluetooth file sharing, cloud file management, code execution VM, split-screen browsing, and a clean, intuitive interface.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PWA](https://img.shields.io/badge/PWA-enabled-orange.svg)
![Bluetooth](https://img.shields.io/badge/Bluetooth-enabled-blue.svg)
![VM](https://img.shields.io/badge/Code_VM-enabled-purple.svg)

## Features

### Core Browsing
- **Multi-tab Browsing**: Open and manage multiple tabs simultaneously
- **Smart Address Bar**: Enter URLs or search queries directly
- **Navigation Controls**: Back, forward, refresh, and home buttons
- **URL Protocol Indicator**: Visual feedback for secure (HTTPS) vs non-secure connections

### Data Management
- **Bookmark System**: Save and organize your favorite sites with IndexedDB
- **History Tracking**: Keep track of visited pages with full history management
- **Persistent Storage**: All data stored locally using IndexedDB

### BlueDrop - Wireless Sharing
- **Bluetooth Sharing**: Share files, links, and text via Web Bluetooth API
- **Web Share Integration**: Native system sharing on mobile devices
- **Multiple Methods**: Automatic fallback to clipboard for maximum compatibility
- **Transfer History**: Track all shared items with timestamps
- **Progress Tracking**: Real-time transfer progress indicators

### Customization
- **Theme Support**: Toggle between light and dark themes
- **Auto Theme**: Automatically match system color preference
- **Custom Homepage**: Set your preferred homepage URL
- **Search Engine Selection**: Choose from Google, DuckDuckGo, Bing, or Brave Search

### Progressive Web App
- **Offline Support**: Service worker enables offline functionality
- **Installable**: Install as a standalone app on any device
- **Fast Loading**: Cached assets for instant load times
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

### Privacy & Security
- **Local Storage**: All data stored locally in your browser
- **Privacy Controls**: Option to disable history tracking
- **Clear Data**: Easy clearing of history and bookmarks
- **Secure Indicators**: Visual feedback for connection security

### User Experience
- **Keyboard Shortcuts**: Efficient navigation with hotkeys
- **Toast Notifications**: Non-intrusive feedback messages
- **Quick Links**: Fast access to popular websites
- **Welcome Screen**: Beautiful landing page with feature highlights

## Installation

### Option 1: Use Online (PWA)
1. Visit the hosted URL in your browser
2. Click the install icon in your browser's address bar
3. Click "Install" to add TimeLord Browser to your device

### Option 2: Local Development
1. Clone this repository:
   ```bash
   git clone https://github.com/TimeLordHorus/TimeLordHorus.git
   cd TimeLordHorus
   ```

2. Serve the files using any HTTP server:
   ```bash
   # Using Python 3
   python -m http.server 8000

   # Using Node.js http-server
   npx http-server -p 8000

   # Using PHP
   php -S localhost:8000
   ```

3. Open your browser and navigate to `http://localhost:8000`

## Usage

### Basic Navigation
- **Open URL**: Type a URL in the address bar and press Enter or click "Go"
- **Search**: Type search terms in the address bar to search using your default search engine
- **New Tab**: Click the "+" button or press `Ctrl/Cmd + T`
- **Close Tab**: Click the "✕" on a tab or press `Ctrl/Cmd + W`
- **Switch Tabs**: Click on any tab to switch to it

### Bookmarks
- **Add Bookmark**: Click the star (⭐) button while viewing a page
- **View Bookmarks**: Right-click the star button or click it from the sidebar
- **Delete Bookmark**: Click the trash icon next to any bookmark
- **Navigate to Bookmark**: Click on any bookmark to open it in the current tab

### History
- **View History**: Click the history (📜) button
- **Navigate from History**: Click any history item to visit that page
- **Clear History**: Go to Settings → Privacy → Clear History

### BlueDrop - Bluetooth Sharing
BlueDrop is a revolutionary feature that allows you to wirelessly share files, links, and text using Bluetooth or Web Share API.

#### How to Use BlueDrop:
1. **Open BlueDrop**: Click the BlueDrop (📡) button in the navigation bar
2. **Enable Bluetooth**: Click "Enable Bluetooth" to connect to a device
3. **Select Device**: Choose a nearby Bluetooth device from the list
4. **Share Content**:
   - **Share Current Page**: Share the URL of the page you're viewing
   - **Share File**: Select and share files from your device
   - **Share Text**: Share custom text or notes

#### Sharing Methods:
- **Bluetooth**: Direct peer-to-peer transfer via Web Bluetooth API
- **Web Share API**: System sharing (mobile and supported desktop browsers)
- **Clipboard**: Automatic fallback for links and text

#### Features:
- Share files, links, and text wirelessly
- Secure Bluetooth connection
- Transfer progress tracking
- Share history with timestamps
- Multiple sharing method support
- Automatic fallback options

#### Browser Requirements:
- **Full Support**: Chrome/Edge 90+ (Bluetooth + Web Share)
- **Partial Support**: Firefox (Web Share API only)
- **Mobile**: Full support on Android Chrome
- **iOS Safari**: Web Share API support

#### Troubleshooting:
- Ensure Bluetooth is enabled on your device
- Grant Bluetooth permissions when prompted
- Some devices may not support the custom service UUID
- Large files (>512 bytes) use Web Share API instead of Bluetooth
- If Bluetooth fails, links/text are automatically copied to clipboard

### File Manager & Cloud Storage
Access powerful file management with both local and cloud storage support.

#### How to Use File Manager:
1. **Open File Manager**: Click the File Manager (📁) button in the navigation bar
2. **Select Storage Provider**: Choose between Local Files, Google Drive, Dropbox, or OneDrive
3. **Upload Files**: Click "Upload" to add files from your device
4. **Manage Files**: View, download, share, or delete files
5. **Create Folders**: Organize files with custom folders

#### Features:
- Local file storage with IndexedDB
- Cloud storage integration (Google Drive, Dropbox, OneDrive)
- File upload/download capabilities
- File sharing via BlueDrop
- Storage quota visualization
- Breadcrumb navigation
- File preview for images
- Folder organization

#### Supported Operations:
- **Upload**: Add files from your device
- **Download**: Save files to your device
- **Share**: Share files via BlueDrop
- **Delete**: Remove unwanted files
- **Create Folder**: Organize with directories
- **Refresh**: Update file list

### Code Runner VM
Run code directly in your browser with the built-in virtual machine.

#### How to Use Code Runner:
1. **Open Code Runner**: Click the Code Runner (💻) button in the navigation bar
2. **Select Language**: Choose JavaScript, HTML/CSS, Python, or TypeScript
3. **Write Code**: Enter your code in the editor
4. **Run**: Click "Run Code" to execute
5. **View Output**: See results in the console

#### Supported Languages:
- **JavaScript**: Full ES6+ support with console output
- **HTML/CSS**: Live preview in new tab
- **Python**: Pyodide WASM interpreter (loaded on-demand)
- **TypeScript**: Automatic transpilation to JavaScript

#### Features:
- Syntax-aware code editor
- Real-time console output
- Error handling and display
- Code snippet save/load
- Import code from files
- Isolated execution environment
- Multiple console types (log, error, warn, info)

#### Code Snippets:
- Save frequently used code
- Organize by language
- Quick load from saved library
- Import from external files
- Export and share snippets

### Split View Browsing
Browse multiple pages simultaneously with split-screen support.

#### How to Use Split View:
1. **Enable Split View**: Click the Split View (⚡) button
2. **Choose Split Type**:
   - **Horizontal Split** (⬌): Side-by-side panes
   - **Vertical Split** (⬍): Top-and-bottom panes
3. **Resize Panes**: Drag the resize handle between panes
4. **Close Split**: Click the close button (✕) in split controls

#### Features:
- Horizontal and vertical split modes
- Resizable panes with drag handle
- Independent browsing in each pane
- Smooth split animations
- Keyboard shortcuts support
- Layout save/restore (planned)

#### Keyboard Shortcuts:
- `Ctrl/Cmd + Shift + S` - Toggle split view controls
- `Ctrl/Cmd + Shift + H` - Horizontal split
- `Ctrl/Cmd + Shift + V` - Vertical split

#### Use Cases:
- Compare two websites side-by-side
- Reference documentation while coding
- Monitor multiple dashboards
- Research across multiple sources
- Split workflow between tasks

### Settings
Access settings by clicking the gear (⚙️) icon:

- **Homepage**: Set your preferred homepage URL
- **Search Engine**: Choose your default search engine
- **Privacy**: Toggle history tracking on/off
- **Theme**: Toggle between light and dark themes
- **Clear Data**: Remove all history or bookmarks

### Keyboard Shortcuts
- `Ctrl/Cmd + T` - New tab
- `Ctrl/Cmd + W` - Close current tab
- `Ctrl/Cmd + R` - Refresh page
- `Ctrl/Cmd + L` - Focus address bar

## Technical Details

### Architecture
- **Frontend**: Pure HTML5, CSS3, and vanilla JavaScript (no frameworks)
- **Storage**: IndexedDB for bookmarks, history, and settings
- **PWA**: Service Worker for offline caching and fast loading
- **Responsive**: CSS Grid and Flexbox for adaptive layouts

### Browser Support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

### File Structure
```
TimeLordHorus/
├── index.html          # Main HTML structure
├── styles.css          # All styling and themes
├── app.js              # Core browser functionality
├── bluedrop.js        # BlueDrop Bluetooth sharing service
├── filemanager.js     # File Manager with cloud storage
├── coderunner.js      # Code Runner VM engine
├── splitview.js       # Split view manager
├── manifest.json       # PWA manifest
├── sw.js              # Service worker
├── .gitignore         # Git ignore configuration
└── README.md          # Documentation
```

### Key Technologies
- **IndexedDB**: Client-side database for persistent storage
- **Service Worker**: Offline functionality and caching
- **Web Bluetooth API**: Device-to-device wireless communication
- **Web Share API**: Native system sharing integration
- **File System Access API**: Local file management
- **Pyodide**: Python WASM interpreter for browser-based code execution
- **Web Workers**: Isolated code execution for VM
- **Sandboxed iframes**: Secure code and content rendering
- **Web App Manifest**: PWA installation and configuration
- **CSS Custom Properties**: Dynamic theming
- **LocalStorage**: Settings and snippet persistence
- **Cloud Storage APIs**: Google Drive, Dropbox, OneDrive integration

## Features in Detail

### Tab Management
Each tab maintains its own:
- Navigation history
- Current URL
- Page title
- Forward/back stack

### Search Integration
Automatically detects if input is a URL or search query:
- Valid URLs (with dots, no spaces) → Direct navigation
- Everything else → Search using default engine

### Theme System
Two beautiful themes:
- **Light Theme**: Clean, minimal design for daytime use
- **Dark Theme**: Easy on the eyes for low-light environments

Themes use CSS custom properties for instant switching without page reload.

### Offline Capability
The service worker caches:
- Application shell (HTML, CSS, JS)
- Static assets
- Visited pages (optional)

This enables:
- Instant loading on repeat visits
- Offline access to cached pages
- Background sync (when supported)

## Security Considerations

### Iframe Sandbox
Content is loaded in sandboxed iframes with restrictions:
- `allow-same-origin`: Allows content to access its own origin
- `allow-scripts`: Enables JavaScript execution
- `allow-popups`: Allows pop-ups (required for some sites)
- `allow-forms`: Enables form submission

### Data Privacy
- All data stored locally in your browser
- No external servers or tracking
- Clear data options available
- Optional history tracking

### Content Security
- Protocol indicators show connection security
- HTTPS preferred for all connections
- Warning for non-secure HTTP connections

## Limitations

As a web-based browser running in another browser:
- Cannot access system-level features
- Some websites may block iframe embedding
- Limited to browser security sandbox
- Network requests subject to CORS policies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Future Enhancements

Potential features for future versions:
- [x] Bluetooth file sharing (✅ Implemented in v1.1.0)
- [x] File Manager with cloud storage (✅ Implemented in v2.0.0)
- [x] Code Runner VM (✅ Implemented in v2.0.0)
- [x] Split View browsing (✅ Implemented in v2.0.0)
- [ ] Download manager with progress tracking
- [ ] Password manager with encryption
- [ ] Extensions support
- [ ] Tab groups
- [ ] Reading mode with article extraction
- [ ] Built-in PDF viewer and editor
- [ ] Screenshot and screen recording tool
- [ ] Private browsing mode with encryption
- [ ] Ad blocker with custom filter lists
- [ ] Enhanced Bluetooth features (larger file transfers, device pairing memory)
- [ ] QR code generation and sharing
- [ ] Tab drag-and-drop between split panes
- [ ] Synchronized scrolling in split view
- [ ] Code collaboration features
- [ ] Cloud-based snippet sync

## License

MIT License - feel free to use this project for learning or as a base for your own browser!

## Acknowledgments

Built with passion for creating lightweight, privacy-focused web applications.

---

**Made with ❤️ by TimeLordHorus**

*Exploring the web, one tab at a time!*
