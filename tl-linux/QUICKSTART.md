# 🚀 TL Linux Quick Start Guide

## Installation (3 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/tl-linux.git
cd tl-linux

# 2. Run the installer
chmod +x install.sh
./install.sh

# 3. Launch TL Linux
python3 tl_linux.py
```

## First Launch

On first launch, you'll experience:

1. **🐙 Boot Animation** - Watch the pixelated cephalopod float in a sea of pixels
2. **👋 Onboarding** - 7-step setup process (~3 minutes)
   - Introduction
   - Experience level selection
   - Theme selection
   - App preferences
   - System tour
   - Compatibility setup
   - Finalization

3. **🖥️ Desktop Launch** - Your personalized TL Linux desktop

## Quick Commands

### Launch Applications

```bash
# Launch desktop environment
python3 tl_linux.py

# Launch with text menu
python3 tl_linux.py --menu

# Individual apps
python3 apps/tl_ide.py          # IDE
python3 apps/calculator.py      # Calculator
python3 apps/calendar.py        # Calendar
python3 apps/emulator_hub.py    # Games
python3 settings/settings_manager.py  # Settings
```

### Desktop Navigation

- **App Drawer**: Click "⚡ TL" button in bottom-left
- **Running Apps**: Appear in bottom tray
- **System Tray**: Clock, volume, network in bottom-right
- **Desktop Icons**: Quick access to Files, Settings, Terminal, Games
- **Exit**: Press ESC key

## Key Features at a Glance

### 🎨 Change Theme
1. Click Settings icon or press Settings in app drawer
2. Go to Appearance
3. Select theme: Retro, Neon, Lightning, or Splash
4. Enable "Auto Theme" for ML-powered selection

### 📁 File Management
1. Click Files icon on desktop
2. Navigate with file tree on left
3. Double-click to open files in TL IDE

### 🎮 Play Retro Games
1. Open Emulator Hub from app drawer
2. Select gaming system (NES, SNES, etc.)
3. Install emulator if prompted
4. Add ROMs to ~/ROMs/[system]/
5. Double-click ROM to play

### 💻 Code Development
1. Launch TL IDE
2. File > New or Open
3. Write code with syntax highlighting
4. Press F5 to run
5. View output in bottom panel

### 🧮 Quick Calculator
1. Launch Calculator app
2. Click buttons or type on keyboard
3. Use scientific functions: sin, cos, tan, √, x², log
4. Press C to clear

### 📅 Manage Events
1. Open Calendar
2. Navigate months with ◀ ▶
3. Click "Today" to return to current month
4. Click "+ Add Event" to create events
5. Click dates to view events

## Compatibility

### Run Windows Apps
```bash
# Launch .exe files
python3 compat/compatibility_layer.py app.exe
```

### Run Android Apps
```bash
# Install .apk files
python3 compat/compatibility_layer.py app.apk
```

### Install from Flatpak
```bash
flatpak install flathub com.app.name
flatpak run com.app.name
```

## Customization

### Configuration Files
- User profile: `~/.config/tl-linux/user_profile.json`
- Settings: `~/.config/tl-linux/settings.json`
- ML data: `~/.config/tl-linux/ml_theme_data.json`
- Events: `~/.config/tl-linux/calendar_events.json`

### ROMs Location
```
~/ROMs/
  ├── NES/
  ├── SNES/
  ├── GB/
  ├── GBA/
  └── [other systems]/
```

## Tips & Tricks

1. **ML Personalization**: The more you use TL Linux, the better it adapts
2. **Keyboard Shortcuts**:
   - Desktop: ESC to exit
   - IDE: Ctrl+N (new), Ctrl+O (open), Ctrl+S (save), F5 (run)
3. **Theme Changes**: Themes auto-adapt based on time of day with ML
4. **Quick Launch**: Create `~/bin/tl` symlink for faster access
5. **ROM Organization**: Keep ROMs organized by system for easier management

## Troubleshooting

### Desktop Won't Launch
```bash
# Use menu mode instead
python3 tl_linux.py --menu
```

### Missing Dependencies
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Arch
sudo pacman -S tk

# Fedora
sudo dnf install python3-tkinter
```

### Compatibility Layer Not Working
```bash
# Install Wine
sudo apt install wine winetricks

# Install Waydroid
sudo apt install waydroid
sudo waydroid init

# Install Flatpak
sudo apt install flatpak
```

### Reset to Defaults
```bash
# Delete config directory
rm -rf ~/.config/tl-linux

# Relaunch TL Linux
python3 tl_linux.py
```

## Getting Help

1. Check README.md for detailed documentation
2. Run onboarding again: Select option 7 in menu
3. Visit Settings > About for feature overview
4. Create issue on GitHub

## What's Next?

- Explore all four themes
- Try different emulator systems
- Build a project in TL IDE
- Customize your desktop layout
- Install compatibility layers
- Share your experience!

---

**Welcome to TL Linux!** 🐙⏰💻

Enjoy your Time Lord computing experience!
