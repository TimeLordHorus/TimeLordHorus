# CLAUDE.md - AI Assistant Guide for TL Linux Development

> **Last Updated**: 2025-11-20
> **Version**: 1.0.0 "Chronos"
> **Purpose**: Guide for AI assistants working with the TL Linux codebase

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Development Workflows](#development-workflows)
4. [Build System](#build-system)
5. [Code Conventions](#code-conventions)
6. [Accessibility Principles](#accessibility-principles)
7. [Common Development Tasks](#common-development-tasks)
8. [Testing Guidelines](#testing-guidelines)
9. [Important Files Reference](#important-files-reference)
10. [Project Status & Roadmap](#project-status--roadmap)

---

## Project Overview

### What is TL Linux?

**TL Linux (Time Lord Linux)** is an accessibility-first Linux distribution designed specifically for users with disabilities and neurodivergent individuals. Version 1.0.0 "Chronos" aims to be the world's most accessible operating system.

### Mission Statement

Making computing accessible to **everyone**, regardless of ability, with specific focus on:
- ADHD and Autism Spectrum users
- Motor impairments (limited dexterity, tremors)
- Visual disabilities (low vision, color blindness)
- Cognitive differences
- General accessibility needs

### Key Differentiators

1. **Industry First**: Only desktop Linux with Android-style A/B dual partition system
2. **Neurodivergent Focus**: First OS with comprehensive ADHD/Autism support tools
3. **Reliability**: Zero-downtime updates, self-healing, impossible to brick
4. **Privacy-First**: All AI/ML learning happens locally, no telemetry
5. **Planned Stability**: Gets better with age (vs planned obsolescence)

### Technical Foundation

- **Base OS**: Debian 12 "Bookworm" or Debian 13 "Trixie"
- **Desktop Environment**: XFCE 4.18 (lightweight, customizable)
- **Primary Language**: Python 3.11+ (73 files, 31,347+ lines)
- **GUI Framework**: tkinter (Python's standard library)
- **Display Server**: X11 (Wayland planned)
- **Init System**: systemd

---

## Codebase Architecture

### Directory Structure

```
tl-linux/
├── apps/                        # 35+ GUI Applications
│   ├── accessibility/          # Screen reader, voice control, dictation
│   ├── editors/                # Text, image, PDF, spreadsheet editors
│   ├── wellness/               # CBT, ACT, DBT, ADHD, Autism support
│   ├── accessibility_hub.py
│   ├── adhd_shutdown_assistant.py  # UNIQUE: World-first feature
│   ├── app_store.py
│   ├── body_doubling.py
│   ├── calculator.py
│   ├── calendar.py
│   ├── emulator_hub.py
│   ├── file_manager.py
│   ├── focus_mode.py           # ADHD distraction blocker
│   ├── media_player.py
│   ├── routine_manager.py
│   ├── system_monitor.py
│   ├── system_settings.py
│   ├── task_manager.py
│   ├── terminal.py
│   └── [30+ more apps]
│
├── boot/                        # Boot system
│   └── cephalopod_animation.py # Pixelated octopus boot animation
│
├── compat/                      # Compatibility layer
│   └── compatibility_layer.py  # Wine, Waydroid, Flatpak support
│
├── desktop/                     # Desktop environment
│   └── desktop_environment.py  # App tray, drawer, system tray
│
├── docs/                        # Comprehensive documentation
│   ├── ACCESSIBILITY.md
│   ├── FEATURES.md
│   ├── IMPLEMENTATION_ROADMAP.md
│   ├── MISSING_FEATURES.md
│   ├── SUSTAINABILITY.md
│   ├── SYSTEM_STATUS.md
│   └── WELLNESS.md
│
├── installer/                   # System installer
│   └── install-tl-linux.sh
│
├── onboarding/                  # First-run experience
│   └── onboarding_system.py    # 7-step wizard
│
├── settings/                    # Settings management
│   └── settings_manager.py
│
├── storage/                     # Decentralized storage
│   └── ipfs_node.py
│
├── system/                      # System services (15+ services)
│   ├── ab_system_manager.py    # A/B partition manager (UNIQUE!)
│   ├── auto_maintenance.py     # Self-healing system
│   ├── backup_manager.py
│   ├── driver_manager.py
│   ├── keyboard_accessibility.py
│   ├── mouse_keys.py
│   ├── notification_daemon.py
│   ├── trash_manager.py
│   └── user_learning_model.py  # AI personalization (local)
│
├── themes/                      # Theme engine
│   └── theme_engine.py         # 4 themes with ML adaptation
│
├── build-iso.sh                 # Main ISO builder (450+ lines)
├── quick-test-iso.sh            # Fast test ISO (5-10 min)
├── install-build-deps.sh        # Dependency installer
├── diagnose-system.sh           # System diagnostics
├── debian-13-fix.sh             # Debian 13 compatibility
├── fix-repositories.sh          # APT repository fixer
├── quick-fix.sh                 # Ubuntu 24.04 fixes
│
├── Makefile                     # Build automation (250+ lines)
├── tl-linux-launcher.py         # GUI launcher (23K+ lines)
├── tl_linux.py                  # Main entry point
│
└── README.md                    # Main documentation (650+ lines)
```

### Component Categories

1. **Core System**: Boot, desktop, onboarding, settings, themes
2. **Accessibility Suite**: Screen reader, voice control, magnifier, keyboard aids
3. **ADHD/Autism Support**: Shutdown assistant, focus mode, routine manager, body doubling
4. **Wellness Tools**: CBT, ACT, DBT therapeutic applications
5. **Editors Suite**: Text, data, image, document, spreadsheet, PDF
6. **Productivity Apps**: File manager, terminal, calculator, calendar
7. **System Tools**: A/B manager, backup, driver manager, task manager
8. **Advanced Features**: IPFS storage, AI learning model, compatibility layer

---

## Development Workflows

### Local Development & Testing

#### Testing Individual Applications
```bash
cd tl-linux
python3 tl_linux.py                      # Test main launcher
python3 apps/[app_name].py               # Test specific app
python3 apps/accessibility/voice_control.py  # Example
```

#### Testing System Components
```bash
python3 system/ab_system_manager.py      # Test A/B system
python3 desktop/desktop_environment.py   # Test desktop
python3 onboarding/onboarding_system.py  # Test onboarding
```

### Build & Test Cycle

#### Quick Testing (Recommended for Development)
```bash
# 1. Check system prerequisites
sudo make diagnose

# 2. Install dependencies (if needed)
sudo make install-deps

# 3. Build quick test ISO (~5-10 minutes)
sudo make test-iso

# 4. Test in QEMU virtual machine
make test-vm
```

#### Production Build
```bash
# Full production ISO (~20-30 minutes)
sudo make iso              # Debian 12 (default)
sudo make iso-debian13     # Debian 13

# Verify build integrity
make verify

# Create bootable USB
sudo make usb
```

### Development Iteration Pattern

1. **Code**: Edit Python files in `apps/`, `system/`, or `desktop/`
2. **Test Locally**: Run Python file directly to test GUI/logic
3. **Test in ISO**: Build quick-test-iso to verify in live environment
4. **Test in VM**: Use QEMU to test full boot process
5. **Commit**: Create meaningful commit messages
6. **Push**: Push to feature branch (`claude/feature-name-[id]`)

### Git Workflow

```bash
# Feature branches follow pattern: claude/feature-name-[session-id]
git checkout -b claude/new-feature-01ABC123xyz

# Commit changes
git add .
git commit -m "Add new accessibility feature for X"

# Push to remote (CRITICAL: branch must start with 'claude/' and end with session ID)
git push -u origin claude/new-feature-01ABC123xyz

# If network errors occur, retry with exponential backoff (2s, 4s, 8s, 16s)
```

---

## Build System

### Makefile Targets

```bash
# Diagnostics & Setup
make diagnose          # Check system prerequisites
make install-deps      # Auto-install build dependencies
make fix-repos         # Fix broken APT repositories

# Building
make iso               # Full production ISO (Debian 12, 20-30 min)
make iso-debian13      # Full production ISO (Debian 13)
make test-iso          # Quick test ISO (minimal, 5-10 min)
make package           # Create distribution package
make release           # Full release build with verification

# Testing
make test-vm           # Test ISO in QEMU virtual machine
make verify            # Verify ISO checksums

# Distribution
make usb               # Write ISO to USB drive
make clean             # Clean build artifacts

# Information
make info              # Project statistics
```

### Build Scripts Explained

#### build-iso.sh - Main ISO Builder
```bash
# What it does:
# 1. Creates Debian base system using debootstrap
# 2. Sets up chroot environment
# 3. Installs XFCE desktop environment
# 4. Copies all TL Linux apps to /opt/tl-linux/
# 5. Configures system services
# 6. Creates squashfs compressed filesystem
# 7. Generates UEFI + BIOS bootable ISO

sudo ./build-iso.sh
```

#### quick-test-iso.sh - Fast Test Build
```bash
# For rapid development/testing
# Minimal Debian Live build (~500MB vs ~2-3GB)
# Omits some packages for speed

sudo ./quick-test-iso.sh
```

#### install-build-deps.sh - Dependency Installer
```bash
# Auto-detects distribution (Debian/Ubuntu/Arch/Fedora)
# Installs all required build packages
# Run once per development machine

sudo ./install-build-deps.sh
```

### Build Dependencies

**Core Build Tools:**
- `debootstrap` - Bootstrap Debian base system
- `squashfs-tools` - Create compressed filesystem
- `xorriso`/`genisoimage` - ISO creation
- `grub-pc-bin` - GRUB bootloader (BIOS)
- `grub-efi-amd64-bin` - GRUB bootloader (UEFI)
- `mtools`, `dosfstools` - Filesystem tools
- `qemu-system-x86` - Virtual machine testing

**See**: `install-build-deps.sh` for complete list

---

## Code Conventions

### Python Style Guide

#### File Organization
```python
#!/usr/bin/env python3
"""
Brief description of module purpose.

Longer description if needed, explaining key functionality.
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DEFAULT_THEME = "retro"

# Classes
class MyApp:
    """Main application class."""

    def __init__(self, parent):
        """Initialize application."""
        self.parent = parent
        # ...

    def create_widgets(self):
        """Create GUI widgets."""
        # ...

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
```

#### Naming Conventions
- **Files**: `snake_case.py` (e.g., `screen_reader.py`)
- **Shell Scripts**: `kebab-case.sh` (e.g., `build-iso.sh`)
- **Classes**: `PascalCase` (e.g., `ScreenReader`)
- **Functions/Methods**: `snake_case()` (e.g., `load_settings()`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_THEME`)
- **Variables**: `snake_case` (e.g., `user_profile`)

#### Tkinter GUI Pattern

**Standard Window Structure:**
```python
import tkinter as tk
from tkinter import ttk

class MyApp:
    def __init__(self, parent=None):
        """Initialize application window."""
        if parent is None:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel(parent)

        self.window.title("App Name - TL Linux")
        self.window.geometry("800x600")

        # Apply theme
        self.load_theme()

        # Create GUI
        self.create_widgets()

    def load_theme(self):
        """Load and apply current theme."""
        try:
            config_path = Path.home() / ".config" / "tl-linux" / "user_profile.json"
            if config_path.exists():
                with open(config_path) as f:
                    profile = json.load(f)
                    theme = profile.get("theme", "retro")
                    # Apply theme colors...
        except Exception:
            pass  # Use defaults

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add widgets...
```

#### Configuration Storage
```python
from pathlib import Path
import json

def load_user_config():
    """Load user configuration."""
    config_dir = Path.home() / ".config" / "tl-linux"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "user_profile.json"
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {}

def save_user_config(config):
    """Save user configuration."""
    config_dir = Path.home() / ".config" / "tl-linux"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "user_profile.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
```

### Shell Script Conventions

```bash
#!/usr/bin/env bash

# Script description
# Usage: ./script.sh [options]

set -e  # Exit on error
set -u  # Exit on undefined variable

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="/etc/tl-linux.conf"

# Functions
function check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "Error: This script must be run as root"
        exit 1
    fi
}

# Main execution
main() {
    check_root
    # ...
}

main "$@"
```

---

## Accessibility Principles

### Core Accessibility Requirements

**Every feature MUST consider:**

1. **Keyboard Navigation**
   - All functionality accessible via keyboard
   - Logical tab order
   - Visible focus indicators
   - Standard keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)

2. **Screen Reader Compatibility**
   - Meaningful widget labels
   - Proper ARIA attributes (when using web tech)
   - Announce state changes
   - Descriptive button text (not just icons)

3. **Visual Accessibility**
   - High contrast themes available
   - Minimum font size: 12pt (scalable to 24pt+)
   - Color is never the only indicator
   - Support for color blindness filters

4. **Motor Accessibility**
   - Large click targets (minimum 44x44 pixels)
   - Sticky Keys, Slow Keys, Bounce Keys support
   - Mouse Keys for keyboard-only mouse control
   - Configurable input sensitivity

5. **Cognitive Accessibility**
   - Clear, simple language
   - Visual task breakdown
   - Consistent UI patterns
   - Minimize distractions
   - Provide context and help

### ADHD/Autism Design Patterns

#### Focus Mode Implementation
```python
# When implementing focus features:
# - Block distracting websites/apps
# - Provide gentle reminders (not interruptions)
# - Allow "hyperfocus protection" (don't interrupt deep work)
# - Use visual timers (Pomodoro technique)
# - Celebrate accomplishments
```

#### Sensory Considerations
```python
# Configurable sensory settings:
# - Animation speed (off, slow, normal, fast)
# - Sound effects (off, subtle, normal)
# - Visual effects (minimal, normal, enhanced)
# - Haptic feedback (if available)
# - Notification style (visual only, sound, both)
```

#### Executive Function Support
```python
# Break tasks into steps:
# 1. Show overall goal
# 2. Break into subtasks
# 3. Provide progress indicators
# 4. Offer encouragement
# 5. Celebrate completion
```

### Testing Accessibility

**Before submitting code, verify:**

1. **Keyboard Test**: Can you navigate entire UI with Tab/Arrow keys?
2. **Screen Reader Test**: Run with Orca, does it make sense?
3. **High Contrast Test**: Switch to high contrast theme, is everything visible?
4. **Magnification Test**: Zoom to 200%, does layout work?
5. **Color Blindness Test**: Apply color filters, is information still clear?

---

## Common Development Tasks

### Adding a New Application

1. **Create application file**:
   ```bash
   cd tl-linux/apps/
   touch my_new_app.py
   chmod +x my_new_app.py
   ```

2. **Use standard template**:
   ```python
   #!/usr/bin/env python3
   """
   My New App - Brief description.

   Part of TL Linux accessibility suite.
   """

   import tkinter as tk
   from tkinter import ttk
   from pathlib import Path
   import json

   class MyNewApp:
       def __init__(self, parent=None):
           if parent is None:
               self.window = tk.Tk()
           else:
               self.window = tk.Toplevel(parent)

           self.window.title("My New App - TL Linux")
           self.window.geometry("800x600")

           self.create_widgets()

       def create_widgets(self):
           main_frame = ttk.Frame(self.window, padding=20)
           main_frame.pack(fill=tk.BOTH, expand=True)

           # Add your widgets here

   if __name__ == "__main__":
       app = MyNewApp()
       if hasattr(app, 'window'):
           app.window.mainloop()
   ```

3. **Add to launcher** (`tl-linux-launcher.py`):
   ```python
   # In launcher_data dictionary:
   "my_new_app": {
       "name": "My New App",
       "description": "Brief description",
       "icon": "🎯",
       "category": "Productivity",  # or Accessibility, Wellness, etc.
       "script": "apps/my_new_app.py"
   }
   ```

4. **Test locally**:
   ```bash
   python3 apps/my_new_app.py
   ```

5. **Test in ISO**:
   ```bash
   sudo make test-iso
   make test-vm
   ```

### Modifying Existing Applications

1. **Read the file first**:
   ```bash
   cat apps/existing_app.py  # or use your editor
   ```

2. **Test before changes**:
   ```bash
   python3 apps/existing_app.py
   ```

3. **Make changes** following existing patterns

4. **Test after changes**:
   ```bash
   python3 apps/existing_app.py
   ```

5. **Build test ISO** to verify in live environment

### Adding System Service

1. **Create service script** in `system/`:
   ```python
   #!/usr/bin/env python3
   """System service description."""

   import time
   import logging

   def main():
       logging.basicConfig(level=logging.INFO)
       logger = logging.getLogger(__name__)

       while True:
           # Service logic
           time.sleep(60)  # Adjust as needed

   if __name__ == "__main__":
       main()
   ```

2. **Create systemd unit file**:
   ```bash
   # In build-iso.sh, add:
   cat > "$CHROOT_DIR/etc/systemd/system/my-service.service" << 'EOF'
   [Unit]
   Description=My Service
   After=network.target

   [Service]
   Type=simple
   ExecStart=/usr/bin/python3 /opt/tl-linux/system/my_service.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   EOF

   chroot "$CHROOT_DIR" systemctl enable my-service
   ```

### Updating Documentation

1. **Keep docs in sync** - Update relevant docs when adding features:
   - `README.md` - Main documentation
   - `FEATURES.md` - Feature list
   - `docs/SYSTEM_STATUS.md` - Implementation status
   - `docs/IMPLEMENTATION_ROADMAP.md` - Roadmap

2. **Document accessibility features** in `docs/ACCESSIBILITY.md`

3. **Update this CLAUDE.md** when architecture changes

### Building for Different Debian Versions

```bash
# Debian 12 (default, stable)
sudo make iso

# Debian 13 (testing)
sudo make iso-debian13

# Custom build
sudo DEBIAN_VERSION=12 ./build-iso.sh
```

---

## Testing Guidelines

### Unit Testing (Local)

```bash
# Test individual applications
cd tl-linux
python3 apps/calculator.py
python3 apps/file_manager.py
python3 apps/accessibility/screen_reader.py

# Test system components
python3 system/ab_system_manager.py
python3 desktop/desktop_environment.py

# Test with different themes
# Edit ~/.config/tl-linux/user_profile.json
# Set "theme": "retro" | "neon" | "lightning" | "splash"
```

### Integration Testing (ISO)

```bash
# 1. Build quick test ISO
sudo make test-iso

# 2. Test in QEMU
make test-vm

# 3. Test specific scenarios:
#    - Boot process
#    - Onboarding wizard
#    - Application launching
#    - System settings
#    - Accessibility features
#    - Theme switching
```

### Accessibility Testing Checklist

- [ ] **Keyboard Navigation**: Tab through all UI elements
- [ ] **Screen Reader**: Test with Orca enabled
- [ ] **High Contrast**: Switch to high contrast theme
- [ ] **Magnification**: Test at 200% zoom
- [ ] **Color Blindness**: Apply color filters
- [ ] **Sticky Keys**: Test with accessibility features on
- [ ] **Large Cursor**: Test with magnified cursor
- [ ] **Voice Control**: Test voice commands (if applicable)

### Build Verification

```bash
# Verify ISO integrity
make verify

# Check ISO contents
mkdir -p /tmp/iso_mount
sudo mount -o loop tl-linux.iso /tmp/iso_mount
ls -lah /tmp/iso_mount
sudo umount /tmp/iso_mount

# Test bootability
make test-vm  # QEMU
# Or create bootable USB and test on real hardware
```

### Performance Testing

```bash
# Monitor resource usage
python3 apps/system_monitor.py

# Check boot time
# Boot in VM and time to desktop

# Check memory footprint
# Aim for < 1GB RAM usage at idle
```

---

## Important Files Reference

### Configuration Files

```bash
# User configuration
~/.config/tl-linux/user_profile.json      # User profile and preferences
~/.config/tl-linux/settings.json          # Application settings
~/.config/tl-linux/ml_theme_data.json     # ML learning data
~/.config/tl-linux/calendar_events.json   # Calendar events
~/.config/tl-linux/routines.json          # Routine manager data
~/.config/tl-linux/focus_blocklist.json   # Focus mode blocked sites/apps

# System configuration
/etc/tl-linux-ab.conf                     # A/B partition configuration
/opt/tl-linux/                            # Installation directory
```

### Key Source Files

```bash
# Entry points
tl-linux/tl_linux.py                      # Main entry point
tl-linux/tl-linux-launcher.py             # GUI launcher (23K+ lines)

# Core system
tl-linux/desktop/desktop_environment.py   # Desktop environment
tl-linux/onboarding/onboarding_system.py  # First-run wizard
tl-linux/themes/theme_engine.py           # Theme system
tl-linux/settings/settings_manager.py     # Settings management

# Build system
tl-linux/Makefile                         # Build automation
tl-linux/build-iso.sh                     # Main ISO builder
tl-linux/quick-test-iso.sh                # Quick test ISO
tl-linux/install-build-deps.sh            # Dependency installer

# System services
tl-linux/system/ab_system_manager.py      # A/B partition manager
tl-linux/system/auto_maintenance.py       # Self-healing
tl-linux/system/backup_manager.py         # Backup system
tl-linux/system/user_learning_model.py    # AI personalization
```

### Documentation Files

```bash
tl-linux/README.md                        # Main documentation (START HERE)
tl-linux/FEATURES.md                      # Complete feature list
tl-linux/QUICKSTART.md                    # Quick start guide
tl-linux/BUILD-ISO-README.md              # ISO build guide
tl-linux/LAUNCHER-README.md               # Launcher documentation

# Detailed docs
tl-linux/docs/ACCESSIBILITY.md            # Accessibility features
tl-linux/docs/WELLNESS.md                 # Wellness/therapy tools
tl-linux/docs/SYSTEM_STATUS.md            # Implementation status
tl-linux/docs/IMPLEMENTATION_ROADMAP.md   # Development roadmap
tl-linux/docs/MISSING_FEATURES.md         # Planned features
tl-linux/docs/SUSTAINABILITY.md           # Sustainability approach
tl-linux/docs/IPFS.md                     # Decentralized storage

# Troubleshooting
tl-linux/ISO-BUILD-FIX.md                 # Build troubleshooting
tl-linux/TROUBLESHOOTING-CHROOT.md        # Chroot issues
```

---

## Project Status & Roadmap

### Current Version: 1.0.0 "Chronos"

**Overall Completion**: ~75%

### Completed Features (100%)

#### Critical Features ✅
- [x] ADHD/Autism support suite
- [x] Motor accessibility features
- [x] Visual accessibility features
- [x] Cognitive accessibility features
- [x] A/B dual partition system
- [x] System installer
- [x] Bootable ISO creation

#### High Priority (86%)
- [x] Professional screen reader integration
- [x] AI voice control system
- [x] AI dictation system
- [x] Modern terminal emulator
- [x] Archive manager
- [x] Screenshot tool
- [x] Complete backup system
- [x] Firmware management
- [x] Wellness suite (CBT, ACT, DBT)
- [ ] Display/Login Manager (in progress)
- [ ] Enhanced keyboard accessibility (in progress)

#### Medium Priority (60%)
- [x] IPFS decentralized storage
- [x] Theme engine with ML
- [x] Comprehensive editor suite
- [x] Emulator hub
- [ ] Body doubling mode (in progress)
- [ ] Routine manager (in progress)
- [ ] Cloud sync (planned)

#### Low Priority (31%)
- [x] Custom boot animation
- [x] System diagnostics
- [ ] Plugin architecture (planned)
- [ ] Mobile companion app (planned)
- [ ] Community marketplace (planned)

### In Active Development

1. **Display/Login Manager** - Custom login screen
2. **Enhanced Keyboard Accessibility** - Additional input methods
3. **Firewall GUI** - User-friendly security management
4. **Body Doubling Mode** - Virtual co-working implementation
5. **Routine Manager** - Advanced scheduling

### Future Roadmap (v2.0+)

- Wayland display server support
- ARM64 architecture (Raspberry Pi support)
- Mobile companion application
- Plugin architecture for extensibility
- Community marketplace
- Advanced eye-tracking integration
- Enterprise support and partnerships
- Multi-language support (i18n)

### Known Issues & Limitations

1. **Build System**:
   - Requires 20GB+ free disk space
   - Build time: 20-30 minutes for full ISO
   - Debian 13 support is experimental

2. **Hardware Support**:
   - x86_64 only (ARM64 planned)
   - Some proprietary drivers need manual installation
   - NVIDIA graphics may require additional setup

3. **Feature Limitations**:
   - X11 only (Wayland coming in v2.0)
   - Some accessibility features require additional packages
   - IPFS integration is basic (enhanced version planned)

4. **Testing Needs**:
   - More real hardware testing
   - User testing with target accessibility communities
   - Performance optimization on older hardware

---

## AI Assistant Guidelines

### When Working on This Project

1. **Always Consider Accessibility**:
   - Every change must maintain/improve accessibility
   - Test with keyboard navigation
   - Ensure screen reader compatibility
   - Use clear, simple language

2. **Follow Established Patterns**:
   - Use existing code as templates
   - Maintain consistent naming conventions
   - Keep documentation in sync
   - Don't reinvent solved problems

3. **Test Thoroughly**:
   - Test locally before building ISO
   - Use quick-test-iso for rapid iteration
   - Verify in VM before marking complete
   - Check accessibility features

4. **Document Changes**:
   - Update relevant README files
   - Update SYSTEM_STATUS.md for new features
   - Add comments for complex logic
   - Keep this CLAUDE.md current

5. **Respect the Mission**:
   - This OS is for people who need it
   - Accessibility is not optional
   - Privacy and local-first are core values
   - Stability and reliability are paramount

### Common Pitfalls to Avoid

1. ❌ **Don't**: Add features without accessibility considerations
   ✅ **Do**: Design accessibility-first from the start

2. ❌ **Don't**: Use complex language or jargon
   ✅ **Do**: Use clear, simple, friendly language

3. ❌ **Don't**: Hardcode paths or configurations
   ✅ **Do**: Use Path, config files, and environment variables

4. ❌ **Don't**: Assume mouse/visual interaction
   ✅ **Do**: Ensure full keyboard/screen reader support

5. ❌ **Don't**: Add telemetry or cloud dependencies
   ✅ **Do**: Keep everything local and privacy-respecting

6. ❌ **Don't**: Break existing functionality
   ✅ **Do**: Test thoroughly and maintain backward compatibility

### Quick Command Reference

```bash
# Development
python3 tl_linux.py                  # Run launcher
python3 apps/[app_name].py          # Test app

# Building
sudo make diagnose                   # Check system
sudo make install-deps               # Install dependencies
sudo make test-iso                   # Quick test build
sudo make iso                        # Production build
make test-vm                         # Test in QEMU

# Testing
make verify                          # Verify ISO
sudo make usb                        # Write to USB

# Information
make info                            # Project stats
git log -10 --oneline               # Recent commits
```

---

## Getting Help

### Documentation Priority

1. **This file** (CLAUDE.md) - AI development guide
2. **README.md** - User and developer documentation
3. **QUICKSTART.md** - Getting started quickly
4. **BUILD-ISO-README.md** - ISO building guide
5. **docs/** - Detailed feature documentation

### Understanding the Codebase

- Start with `tl_linux.py` and `tl-linux-launcher.py`
- Read existing app code for patterns
- Check `docs/SYSTEM_STATUS.md` for implementation status
- Review recent commits for context

### Common Questions

**Q: How do I add a new app?**
A: See [Adding a New Application](#adding-a-new-application)

**Q: How do I build an ISO?**
A: `sudo make test-iso` for testing, `sudo make iso` for production

**Q: How do I test accessibility?**
A: See [Accessibility Testing Checklist](#accessibility-testing-checklist)

**Q: Where are user settings stored?**
A: `~/.config/tl-linux/user_profile.json`

**Q: How do I contribute?**
A: Create feature branch, make changes, test thoroughly, submit PR

---

## Project Statistics

- **Total Python Files**: 73
- **Total Python Lines**: 31,347+
- **Total Shell Scripts**: 10
- **Total Applications**: 35+
- **System Services**: 15+
- **Documentation Files**: 14+ markdown files
- **ISO Size**: ~2-3 GB (full), ~500 MB (test)
- **Build Time**: 20-30 min (full), 5-10 min (test)

---

## Contact & Resources

- **Repository**: TimeLordHorus/TimeLordHorus
- **Branch Pattern**: `claude/feature-name-[session-id]`
- **Main Branch**: (for PR targets)
- **License**: [Specified in repository]
- **Version**: 1.0.0 "Chronos"

---

## Revision History

- **2025-11-20**: Initial creation of CLAUDE.md
  - Comprehensive codebase analysis
  - Documentation of architecture and workflows
  - Accessibility guidelines
  - Development task guides

---

**Remember**: TL Linux exists to make computing accessible to everyone. Every line of code, every feature, every decision should serve that mission. When in doubt, choose accessibility, simplicity, and user empowerment.

**Welcome to the Time Lord Linux development team! 🐙**
