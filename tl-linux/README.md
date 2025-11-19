# 🐙 TL Linux - Time Lord Operating System

![TL Linux](https://img.shields.io/badge/TL_Linux-v1.0.0-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge&logo=linux)

A comprehensive personal computing solution featuring a pixelated cephalopod boot animation, ML-powered personalization, and extensive cross-platform application support.

## ✨ Features

### 🎨 Adaptive Themes
TL Linux features four beautiful ML-powered themes that adapt to your usage patterns:
- **🎮 Retro** - Classic computing aesthetics with pixel art and CRT effects
- **🌈 Neon** - Vibrant cyberpunk-inspired colors with glow effects
- **⚡ Lightning** - High contrast, energetic interface for productivity
- **💧 Splash** - Fluid, modern, and colorful design

### 🖥️ Desktop Environment
- **Bottom Application Tray** - Quick access to running applications
- **File Manager** - Intuitive file management with cross-platform support
- **App Drawer** - Organized application launcher
- **System Tray** - Network, volume, and system controls

### 🔄 Multi-Platform Application Support
Run applications from multiple platforms seamlessly:
- ✅ **Native Linux** - .AppImage, .deb, .rpm, executables
- ✅ **Windows** - via Wine/Proton compatibility layer
- ✅ **Android** - via Waydroid integration
- ✅ **Ubuntu** - Full Ubuntu package compatibility
- ✅ **Flatpak** - Universal Linux applications
- ✅ **Snap** - Containerized applications

### 📦 Built-in Applications

#### 💻 TL IDE
Full-featured integrated development environment:
- Syntax highlighting
- File explorer
- Code execution
- Terminal integration
- Multi-language support

#### 🧮 Calculator
Advanced calculator with:
- Basic arithmetic
- Scientific functions (sin, cos, tan, log, square root)
- Keyboard shortcuts
- Clean retro interface

#### 📅 Calendar
Event management system:
- Monthly view
- Event creation and management
- Reminders
- Persistent storage

#### 🎮 Emulator Hub
Play classic games from multiple platforms:
- NES, SNES, Game Boy, GBA
- Nintendo 64, Sega Genesis
- PlayStation 1, Arcade (MAME)
- DOS Games
- ROM management
- One-click emulator installation

#### ⚙️ Settings Manager
Comprehensive system configuration:
- Appearance customization
- Desktop preferences
- System settings
- Privacy controls
- Compatibility layer management

### 🤖 Machine Learning Personalization
TL Linux learns from your usage patterns to:
- Automatically select optimal themes based on time of day
- Predict your preferred applications
- Adapt interface elements to your workflow
- Provide intelligent suggestions

### 🚀 Onboarding System
Comprehensive first-time setup that:
- Introduces you to TL Linux features
- Configures your preferences
- Sets up compatibility layers
- Personalizes your experience

## 📋 Requirements

### Minimum System Requirements
- **OS**: Any modern Linux distribution (Debian, Ubuntu, Arch, Fedora, etc.)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 5GB free space
- **Display**: 1024x768 minimum resolution

### Dependencies
Python packages (automatically installed):
- tkinter (usually pre-installed)
- json, pathlib (standard library)

Optional compatibility layers:
- Wine (for Windows apps)
- Waydroid (for Android apps)
- Flatpak (for universal apps)

## 🛠️ Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/tl-linux.git
cd tl-linux

# Make executable
chmod +x install.sh

# Run installer
./install.sh
```

### Manual Installation

```bash
# Ensure Python 3.8+ is installed
python3 --version

# Install tkinter if not present (Debian/Ubuntu)
sudo apt install python3-tk

# Run TL Linux
python3 tl_linux.py
```

### Install Compatibility Layers

```bash
# Install Wine (Windows app support)
sudo apt install wine winetricks

# Install Waydroid (Android support)
sudo apt install waydroid
sudo waydroid init

# Install Flatpak
sudo apt install flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

## 🚀 Usage

### Launch TL Linux

```bash
# Launch with GUI desktop
python3 tl_linux.py

# Launch with text menu
python3 tl_linux.py --menu
```

### Launch Individual Applications

```bash
# TL IDE
python3 apps/tl_ide.py

# Calculator
python3 apps/calculator.py

# Calendar
python3 apps/calendar.py

# Emulator Hub
python3 apps/emulator_hub.py

# Settings
python3 settings/settings_manager.py
```

### First Run
On first launch, TL Linux will:
1. Display the pixelated cephalopod boot animation
2. Guide you through comprehensive onboarding
3. Configure your preferences
4. Set up compatibility layers
5. Launch the desktop environment

## 📁 Project Structure

```
tl-linux/
├── boot/
│   └── cephalopod_animation.py    # Boot animation
├── core/
│   └── system files
├── desktop/
│   └── desktop_environment.py     # Main desktop UI
├── onboarding/
│   └── onboarding_system.py       # First-time setup
├── themes/
│   └── theme_engine.py            # ML-powered themes
├── apps/
│   ├── calculator.py              # Calculator app
│   ├── calendar.py                # Calendar app
│   ├── tl_ide.py                  # IDE
│   └── emulator_hub.py            # Gaming emulators
├── compat/
│   └── compatibility_layer.py     # Multi-platform support
├── settings/
│   └── settings_manager.py        # Settings interface
├── docs/
│   └── documentation
├── build/
│   └── build scripts
├── tl_linux.py                    # Main launcher
├── install.sh                     # Installation script
└── README.md                      # This file
```

## 🎨 Themes

### Retro Theme
Classic green-on-black terminal aesthetic with:
- CRT scanline effects
- Pixel-perfect borders
- Retro sound effects
- Monospace fonts

### Neon Theme
Cyberpunk-inspired design with:
- Hot pink and cyan colors
- Glow effects
- Gradient backgrounds
- Modern fonts

### Lightning Theme
High-energy interface with:
- Electric yellow accents
- High contrast
- Fast animations
- Sharp corners

### Splash Theme
Modern and fluid with:
- Colorful gradients
- Glass effects
- Rounded corners
- Light color scheme

## 🔧 Configuration

Settings are stored in `~/.config/tl-linux/`:
- `user_profile.json` - User preferences and onboarding data
- `settings.json` - System settings
- `ml_theme_data.json` - ML learning data
- `calendar_events.json` - Calendar events

## 🎮 Emulator Support

### Supported Systems
- **NES** - Nintendo Entertainment System
- **SNES** - Super Nintendo
- **GB/GBC** - Game Boy / Game Boy Color
- **GBA** - Game Boy Advance
- **N64** - Nintendo 64
- **Genesis** - Sega Genesis / Mega Drive
- **PS1** - PlayStation 1
- **Arcade** - MAME arcade games
- **DOS** - Classic DOS games

### ROM Storage
ROMs are stored in `~/ROMs/` organized by system:
```
~/ROMs/
├── NES/
├── SNES/
├── GB/
├── GBA/
└── ...
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, create issues, or suggest new features.

## 📄 License

TL Linux is open-source software. See LICENSE file for details.

## 🙏 Acknowledgments

- Python Tkinter for GUI framework
- Wine project for Windows compatibility
- Waydroid for Android support
- Flatpak for universal packaging
- All the emulator developers

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Run the help command: `python3 tl_linux.py --help`

## 🗺️ Roadmap

- [ ] Web browser integration
- [ ] Email client
- [ ] Music player
- [ ] Video player
- [ ] Software center
- [ ] System monitoring tools
- [ ] Backup utilities
- [ ] Cloud integration
- [ ] Mobile companion app
- [ ] Plugin system

---

**TL Linux** - *Where Time Lords Compute* 🐙⏰💻

Made with 💜 by the TL Linux team
