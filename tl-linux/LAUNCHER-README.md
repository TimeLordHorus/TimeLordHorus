# TL Linux Launcher

The main application launcher and control panel for TL Linux.

## Features

### Application Management
- **Browse by Category**: Access apps organized into logical categories
  - Accessibility (Screen Reader, Magnifier, Voice Control, etc.)
  - ADHD Support (Pomodoro, Body Doubling, Routines, etc.)
  - Productivity (Notes, Text Editor, Calendar, etc.)
  - Media (Video, Music, Images, PDF viewers)
  - Internet (Browser, Email, Downloads, RSS)
  - System (Monitor, Software Center, Firewall, Terminal)
  - Utilities (Screenshot, Archive Manager, Passwords, etc.)
  - Gaming & Fun

- **Favorites System**: Star your most-used apps for quick access
- **Search Functionality**: Find apps instantly by name or description
- **One-Click Launch**: Launch any application with a single click

### User Interface
- **Clean, Accessible Design**: Dark theme with high contrast (#1a1a1a background, #4a9eff accents)
- **Large Touch-Friendly Cards**: Easy to click app cards with icons and descriptions
- **Responsive Grid Layout**: Adapts to window size (4 columns by default)
- **Scrollable Content**: Handle dozens of applications smoothly

### System Integration
- **Real-Time System Info**: Display uptime and memory usage
- **Quick Settings Access**: Jump to system settings
- **Power Menu**: Lock, restart, or shutdown options
- **Help System**: Built-in help and keyboard shortcuts

## Usage

### Launch the Launcher
```bash
python3 tl-linux-launcher.py
```

Or run from desktop:
```bash
./tl-linux-launcher.py
```

### Keyboard Shortcuts
- **Search**: Start typing to filter apps
- **Alt+F1**: Accessibility menu
- **Alt+F2**: Voice control
- **Alt+F3**: Screen magnifier
- **Alt+F4**: Screen reader
- **Ctrl+Alt+T**: Terminal
- **Super+E**: File manager

### Navigate Categories
Click any category in the left sidebar:
- ⭐ **Favorites**: Quick access to starred apps
- **All Apps**: Browse everything
- **Accessibility**: Screen reader, magnifier, motor aids
- **ADHD Support**: Time management, routines, focus
- **Productivity**: Notes, editor, calendar
- **Media**: Video, music, images, PDFs
- **Internet**: Browser, email, downloads
- **System**: Monitor, settings, firewall
- **Utilities**: Screenshots, archives, passwords
- **Gaming & Fun**: Games, puzzles, relaxation

### Star Favorites
Click the ☆ button on any app card to add to favorites. Starred apps show ★ and appear in the Favorites category.

## Application Catalog

The launcher provides access to **47+ applications** across 9 categories:

### Accessibility (5 apps)
Screen reading, magnification, motor aids, voice control, focus mode

### ADHD Support (5 apps)
Pomodoro timer, body doubling, routines, tasks, habits

### Productivity (5 apps)
Rich text notes, syntax-highlighting editor, calendar, calculator, timers

### Media (5 apps)
Video player with subtitles, music player with playlists, image viewer with slideshow, PDF viewer, media library

### Internet (4 apps)
Web browser, email client, download manager, RSS feeds

### System (8 apps)
Real-time monitor, software center, firewall, terminal, file manager, backup, settings, logs

### Utilities (6 apps)
Screenshots, archives, disk analyzer, passwords, color picker, unit converter

### Gaming & Fun (3 apps)
Game library, puzzles, relaxation exercises

## Configuration

Settings are stored in `~/.tl-linux/launcher_config.json`:

```json
{
  "favorites": [
    "ADHD Support/Pomodoro Timer",
    "Media/Music Player",
    "Productivity/Notes"
  ]
}
```

## Design Philosophy

The launcher embodies TL Linux's core values:

1. **Accessibility First**: Large, clear interface with high contrast
2. **ADHD-Friendly**: Visual organization, favorites, quick search
3. **Discoverable**: Easy to explore and find new tools
4. **Consistent**: Matches TL Linux design language across all apps
5. **Efficient**: Fast launch times, responsive UI

## Technical Details

- **Framework**: Python 3.11+ with tkinter
- **Resolution**: 1400×900 default (resizable)
- **Grid Layout**: 4-column responsive grid
- **Scroll Support**: Mouse wheel and scrollbar
- **Process Management**: Subprocess launch for app isolation
- **Config Format**: JSON for easy editing

## Integration Points

The launcher integrates with:
- All TL Linux applications in `/apps/`
- System utilities in `/system/`
- Configuration in `~/.tl-linux/`
- Desktop environment for global shortcuts
- Power management for lock/restart/shutdown

## Future Enhancements

Planned features:
- App usage statistics
- Recommended apps based on usage
- Category customization
- Themes and appearance settings
- Update notifications
- Quick notes panel
- Widget support

## Accessibility Notes

- All interactive elements are keyboard accessible
- Tab navigation follows logical order
- High contrast ratios meet WCAG AAA standards
- Font sizes are configurable
- Screen reader compatible
- Works with motor accessibility features
- Voice control integration ready

## Support

For help with the launcher:
- Press the 📖 Help button
- Read the built-in help dialog
- Check keyboard shortcuts
- Visit TL Linux documentation

---

**TL Linux** - The Accessible Operating System
Version 1.0.0 "Chronos"
