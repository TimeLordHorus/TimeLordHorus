# TL OS Hub - Portable Operating System Hub

![TL OS Hub](https://img.shields.io/badge/TL%20OS%20Hub-v1.0-blue)
![Platform](https://img.shields.io/badge/platform-Linux-green)
![License](https://img.shields.io/badge/license-Open%20Source-brightgreen)

## 🎯 Overview

**TL OS Hub** is a secure, versatile, and accessible portable operating system hub built on TL Linux. It's designed to run from a USB storage device and provides a full-screen unified interface with three main portals: **Desktop**, **Workspace**, and **Entertainment**.

Inspired by ChromeOS and built with accessibility, mental/physical wellbeing, and security at its core, TL OS Hub runs on a Unix backbone with XFCE desktop integration.

---

## ✨ Key Features

### 🌐 Three Main Portals

#### 🖥️ **Desktop Portal**
- Full XFCE desktop environment
- Comprehensive system applications
- File management and system tools
- Terminal and system monitor
- Complete desktop experience

#### 💼 **Workspace Portal**
- **ADHD-Friendly Productivity Tools**
  - Distraction-free note-taking
  - Task management with visual cues
  - Focus mode with distraction blocking
  - Body doubling (virtual co-working)
- **Professional Applications**
  - IDE for development
  - Document and spreadsheet editors
  - Calendar and scheduling
- **Wellbeing Integration**
  - Break timers and reminders
  - Posture alerts
  - Eye care (20-20-20 rule)

#### 🎮 **Entertainment Portal**
- **Media Center**
  - Music player with playlist management
  - Video player with codec support
  - Image viewer and gallery
- **Gaming**
  - Emulator hub (NES, SNES, GB, GBA, N64, PS1, etc.)
  - Casual games collection
- **Relaxation Tools**
  - Meditation and mindfulness
  - CBT/DBT/ACT therapy tools
  - Reading mode for e-books

### 🔒 Security Features

- **Encryption**
  - File encryption (AES-256)
  - Full disk encryption (LUKS support)
  - Secure file deletion (multi-pass overwrite)
- **Firewall Management**
  - UFW firewall integration
  - Visual firewall control
  - Port monitoring
- **Privacy Tools**
  - Browser history clearing
  - Tracker blocking
  - VPN support
  - Anonymous browsing (Tor)
- **Password Management**
  - Secure password generator
  - Password strength checker
  - Clipboard integration
- **Security Auditing**
  - Comprehensive system scans
  - Vulnerability detection
  - Security recommendations

### 🧘 Wellbeing & Accessibility

- **Physical Wellbeing**
  - Break reminders (customizable intervals)
  - Eye care alerts (20-20-20 rule)
  - Posture monitoring and alerts
  - Hydration reminders
  - Movement tracking
- **Mental Wellbeing**
  - ADHD support features
  - Autism-friendly interface
  - Stress management tools
  - CBT/DBT/ACT therapy integration
- **Accessibility**
  - Screen reader support (Orca)
  - Voice control
  - On-screen keyboard
  - High contrast themes
  - Keyboard navigation throughout
  - Motor impairment support

### 💾 Portable & Persistent

- **USB Drive Operation**
  - Boots from any USB 3.0+ drive
  - Full persistence - all changes saved
  - Works on any compatible computer
  - No installation required on host
- **Cross-Platform Support**
  - UEFI and Legacy BIOS boot
  - Debian 12/13 base
  - Linux kernel 6.1+

---

## 🚀 Getting Started

### Prerequisites

- **USB Drive**: 16GB minimum (32GB+ recommended)
- **Host System**: Any computer with USB boot support
- **RAM**: 2GB minimum (4GB+ recommended)
- **Boot Support**: UEFI or Legacy BIOS

### Installation

#### Option 1: Automated USB Setup (Recommended)

```bash
# Download TL Linux
git clone https://github.com/TimeLordHorus/TimeLordHorus.git
cd TimeLordHorus

# Run USB setup script (replace /dev/sdX with your USB device)
sudo ./portable-usb-setup.sh /dev/sdX

# Install TL Linux to USB
make usb USB_DEVICE=/dev/sdX
```

#### Option 2: Manual Installation

```bash
# 1. Create partitions on USB drive
sudo parted /dev/sdX mklabel gpt
sudo parted /dev/sdX mkpart ESP fat32 1MiB 513MiB
sudo parted /dev/sdX mkpart ROOT ext4 513MiB 100%

# 2. Format partitions
sudo mkfs.vfat -F32 /dev/sdX1
sudo mkfs.ext4 /dev/sdX2

# 3. Install TL Linux
sudo ./installer/install-tl-linux.sh --usb /dev/sdX
```

### First Boot

1. **Insert USB drive** into target computer
2. **Restart** and press boot menu key (F12, F2, ESC, or DEL)
3. **Select USB drive** from boot menu
4. **TL OS Hub launches** automatically in fullscreen
5. **Complete onboarding** (first-run setup)

---

## 🎮 Usage Guide

### Launching TL OS Hub

```bash
# Start OS Hub
python3 /path/to/tl-linux/tl_os_hub.py

# Or from TL Linux environment
tl-os-hub
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt+H` | Return to home screen |
| `Alt+D` | Open Desktop portal |
| `Alt+W` | Open Workspace portal |
| `Alt+E` | Open Entertainment portal |
| `Ctrl+Q` | Quit OS Hub |
| `Esc` or `F11` | Toggle fullscreen |

### Navigation

- **Home Screen**: Three large portal cards for easy selection
- **Portal Screens**: Grid of application buttons with descriptions
- **Back Button**: Always visible to return to home
- **Footer**: System info, settings, help, and exit buttons

---

## 🔧 Components

### Main Applications

1. **tl_os_hub.py** - Main OS Hub launcher (806 lines)
   - Full-screen interface
   - Three-portal navigation
   - Application launcher integration
   - Wellbeing integration

2. **security/security_hub.py** - Security management (1200+ lines)
   - File and disk encryption
   - Firewall control
   - Privacy tools
   - Password management
   - Security auditing

3. **wellbeing/wellbeing_monitor.py** - Wellbeing system (600+ lines)
   - Break reminders
   - Eye care (20-20-20 rule)
   - Posture monitoring
   - Hydration tracking
   - Statistics and analytics

### Supporting Scripts

- **portable-usb-setup.sh** - USB drive setup automation
  - GPT partition creation
  - Filesystem formatting
  - Persistence configuration
  - Boot setup

---

## 📁 Directory Structure

```
TimeLordHorus/
├── tl-linux/
│   ├── tl_os_hub.py              # Main OS Hub (NEW)
│   ├── security/
│   │   └── security_hub.py       # Security tools (NEW)
│   ├── wellbeing/
│   │   └── wellbeing_monitor.py  # Wellbeing features (NEW)
│   ├── desktop/
│   │   └── desktop_environment.py # XFCE desktop
│   ├── apps/                     # 45+ applications
│   │   ├── wellness/            # ADHD, autism, therapy tools
│   │   ├── accessibility/       # Screen reader, voice control
│   │   ├── editors/             # Text, document, image editors
│   │   └── ...
│   ├── themes/                   # Theme engine
│   └── system/                   # System services
├── portable-usb-setup.sh         # USB setup script (NEW)
└── TL-OS-HUB-README.md          # This file (NEW)
```

---

## 🔐 Security Considerations

### Encryption Recommendations

1. **Full Disk Encryption** (Recommended for sensitive data)
   ```bash
   sudo cryptsetup luksFormat /dev/sdX2
   sudo cryptsetup luksOpen /dev/sdX2 tl_root
   ```

2. **Home Partition Encryption**
   ```bash
   sudo cryptsetup luksFormat /dev/sdX4
   ```

3. **File-Level Encryption**
   - Use Security Hub's file encryption for individual files
   - AES-256 encryption with password protection

### Privacy Best Practices

- Enable firewall on first boot
- Use VPN on public networks
- Regularly clear browser data
- Enable auto-lock in privacy settings
- Use strong passwords (check strength in Security Hub)

---

## 🧘 Wellbeing Configuration

### Customizing Reminders

Edit `~/.config/tl-linux/wellbeing/wellbeing_config.json`:

```json
{
  "break_interval": 30,        // Minutes between breaks
  "break_duration": 5,         // Break length in minutes
  "eye_break_interval": 20,    // Eye care frequency (20-20-20 rule)
  "hydration_interval": 60,    // Water reminder frequency
  "posture_alert_interval": 45, // Posture check frequency
  "enabled": true,
  "eye_care_enabled": true,
  "hydration_enabled": true,
  "posture_enabled": true
}
```

### Disable Wellbeing Features

- Launch Wellbeing Monitor
- Uncheck features in Settings section
- Or set `"enabled": false` in config file

---

## 🎨 Customization

### Themes

TL OS Hub integrates with TL Linux's ML-powered theme system:

- **Retro**: Classic terminal aesthetic
- **Neon**: Cyberpunk hot pink/cyan
- **Lightning**: High contrast yellow/white
- **Splash**: Modern light theme

Change theme in Desktop portal → System Settings → Themes

### Adding Applications

Applications are automatically discovered from:
- `/path/to/tl-linux/apps/`
- Custom apps in `~/.local/share/tl-linux/apps/`

---

## 🔧 Troubleshooting

### OS Hub Won't Start

```bash
# Check dependencies
python3 --version  # Should be 3.11+
python3 -m tkinter  # Should open Tk window

# Install missing dependencies
sudo apt install python3-tk python3-pil
```

### USB Boot Issues

1. **Check BIOS settings**
   - Enable USB boot
   - Disable Secure Boot (if necessary)
   - Set USB as first boot device

2. **Verify partition table**
   ```bash
   sudo parted /dev/sdX print
   ```

3. **Check boot flags**
   ```bash
   sudo parted /dev/sdX set 1 esp on
   ```

### Performance Optimization

For USB 2.0 drives:
```bash
# Disable journaling for better performance
sudo tune2fs -O ^has_journal /dev/sdX2
```

---

## 🚀 Advanced Features

### A/B Partition System

TL Linux includes an Android-style A/B partition system for:
- Automatic failover on boot failure
- Zero-downtime updates
- Self-healing capabilities

Located in: `tl-linux/system/ab_system_manager.py`

### Machine Learning Theme Adaptation

Themes adapt based on:
- Time of day
- Usage patterns
- User preferences
- Context-aware suggestions

Located in: `tl-linux/themes/theme_engine.py`

### Compatibility Layers

Run applications from other platforms:
- **Windows** apps via Wine
- **Android** apps via Waydroid
- **Flatpak** and **AppImage** support

Located in: `tl-linux/compat/compatibility_layer.py`

---

## 📊 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **USB Drive** | 16GB, USB 2.0 |
| **RAM** | 2GB |
| **Processor** | 64-bit x86 CPU |
| **Boot** | UEFI or Legacy BIOS |

### Recommended Specifications

| Component | Recommendation |
|-----------|----------------|
| **USB Drive** | 32GB+, USB 3.0+ |
| **RAM** | 4GB+ |
| **Processor** | Multi-core 64-bit x86 |
| **Boot** | UEFI with Secure Boot |

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional accessibility features
- More therapy tool integrations
- Enhanced security features
- Performance optimizations
- Documentation improvements
- Bug fixes and testing

---

## 📝 License

TL Linux and TL OS Hub are open source projects. See individual component licenses for details.

---

## 🙏 Acknowledgments

Built on top of:
- **Debian GNU/Linux** - Rock-solid base
- **XFCE** - Lightweight desktop environment
- **Python/Tkinter** - Cross-platform GUI
- **LUKS** - Disk encryption
- **UFW** - Firewall management

Inspired by:
- **ChromeOS** - Simplicity and portability
- **Tails** - Security and privacy focus
- **Accessibility-first design** principles

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/TimeLordHorus/TimeLordHorus/issues)
- **Documentation**: See `README.md` and `FEATURES.md`
- **Quick Start**: See `QUICKSTART.md`

---

## 🎯 Use Cases

### Students
- Portable study environment
- Access files anywhere
- Focus tools for productivity
- No installation needed on school computers

### Professionals
- Secure work environment
- Carry your desktop everywhere
- Development tools on the go
- Privacy-focused computing

### Accessibility Users
- Consistent accessible environment
- ADHD and autism support
- Screen reader and voice control
- Motor impairment assistance

### Security-Conscious Users
- Encrypted portable system
- No trace on host computer
- Privacy tools built-in
- Secure communications

### Digital Nomads
- Work from any computer
- Entertainment on the go
- Cloud-free file storage
- Complete independence

---

## 🔮 Roadmap

- [ ] Mobile device support (tablets)
- [ ] Cloud sync integration (optional)
- [ ] Additional therapy tools
- [ ] Gamification of wellbeing features
- [ ] Improved emulation support
- [ ] Voice assistant integration
- [ ] Biometric authentication
- [ ] Hardware acceleration optimization

---

**TL OS Hub** - Your portable, accessible, wellness-focused operating system. Take it anywhere. ⏰

---

*Last Updated: 2025-11-21*
*Version: 1.0.0*
