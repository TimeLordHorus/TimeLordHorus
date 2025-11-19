# TimeLord Browser 🌐

A lightweight, feature-rich Progressive Web App (PWA) browser built with vanilla JavaScript. Experience fast, modern browsing with offline capabilities and a clean, intuitive interface.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PWA](https://img.shields.io/badge/PWA-enabled-orange.svg)

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
├── manifest.json       # PWA manifest
├── sw.js              # Service worker
└── README.md          # Documentation
```

### Key Technologies
- **IndexedDB**: Client-side database for persistent storage
- **Service Worker**: Offline functionality and caching
- **Web App Manifest**: PWA installation and configuration
- **CSS Custom Properties**: Dynamic theming
- **LocalStorage**: Settings persistence
- **iframe sandbox**: Secure content rendering

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
- [ ] Download manager
- [ ] Password manager
- [ ] Extensions support
- [ ] Tab groups
- [ ] Reading mode
- [ ] PDF viewer
- [ ] Screenshot tool
- [ ] Sync across devices
- [ ] Private browsing mode
- [ ] Ad blocker

## License

MIT License - feel free to use this project for learning or as a base for your own browser!

## Acknowledgments

Built with passion for creating lightweight, privacy-focused web applications.

---

**Made with ❤️ by TimeLordHorus**

*Exploring the web, one tab at a time!*
