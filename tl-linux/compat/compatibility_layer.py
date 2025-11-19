#!/usr/bin/env python3
"""
TL Linux Application Compatibility Layer
Support for Windows, Linux, Android, and Ubuntu applications
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from enum import Enum

class AppPlatform(Enum):
    """Supported application platforms"""
    NATIVE_LINUX = "native_linux"
    WINDOWS = "windows"
    ANDROID = "android"
    UBUNTU = "ubuntu"
    FLATPAK = "flatpak"
    APPIMAGE = "appimage"
    SNAP = "snap"

class CompatibilityLayer:
    """Manages cross-platform application compatibility"""

    def __init__(self):
        self.wine_prefix = Path.home() / '.wine'
        self.android_data = Path.home() / '.local' / 'share' / 'waydroid'
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'compat'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Check available compatibility tools
        self.available_tools = self.detect_tools()

    def detect_tools(self):
        """Detect installed compatibility tools"""
        tools = {
            'wine': shutil.which('wine') is not None,
            'proton': Path.home() / '.steam' / 'steam' / 'steamapps' / 'common' / 'Proton',
            'waydroid': shutil.which('waydroid') is not None,
            'anbox': shutil.which('anbox') is not None,
            'flatpak': shutil.which('flatpak') is not None,
            'snap': shutil.which('snap') is not None,
            'appimage': True,  # Always available
        }
        return tools

    def install_wine(self):
        """Install Wine for Windows application support"""
        print("Installing Wine compatibility layer...")
        try:
            # Check distribution
            if Path('/etc/debian_version').exists():
                subprocess.run(['sudo', 'dpkg', '--add-architecture', 'i386'], check=True)
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'wine', 'wine32', 'wine64', 'winetricks'], check=True)
            elif Path('/etc/arch-release').exists():
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'wine', 'winetricks'], check=True)
            elif Path('/etc/fedora-release').exists():
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'wine', 'winetricks'], check=True)

            print("✓ Wine installed successfully")
            self.available_tools['wine'] = True
            return True
        except Exception as e:
            print(f"✗ Failed to install Wine: {e}")
            return False

    def install_waydroid(self):
        """Install Waydroid for Android application support"""
        print("Installing Waydroid for Android support...")
        try:
            if Path('/etc/debian_version').exists():
                subprocess.run(['sudo', 'apt', 'install', '-y', 'waydroid'], check=True)
            elif Path('/etc/arch-release').exists():
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'waydroid'], check=True)

            # Initialize Waydroid
            subprocess.run(['sudo', 'waydroid', 'init'], check=True)
            print("✓ Waydroid installed successfully")
            self.available_tools['waydroid'] = True
            return True
        except Exception as e:
            print(f"✗ Failed to install Waydroid: {e}")
            return False

    def install_flatpak(self):
        """Install Flatpak support"""
        print("Installing Flatpak...")
        try:
            if Path('/etc/debian_version').exists():
                subprocess.run(['sudo', 'apt', 'install', '-y', 'flatpak'], check=True)
            elif Path('/etc/arch-release').exists():
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'flatpak'], check=True)

            # Add Flathub repository
            subprocess.run(['flatpak', 'remote-add', '--if-not-exists', 'flathub',
                          'https://flathub.org/repo/flathub.flatpakrepo'], check=True)

            print("✓ Flatpak installed successfully")
            self.available_tools['flatpak'] = True
            return True
        except Exception as e:
            print(f"✗ Failed to install Flatpak: {e}")
            return False

    def detect_app_type(self, app_path):
        """Detect application type from file"""
        app_path = Path(app_path)

        if not app_path.exists():
            return None

        # Check file extension
        suffix = app_path.suffix.lower()

        if suffix == '.exe' or suffix == '.msi':
            return AppPlatform.WINDOWS
        elif suffix == '.apk':
            return AppPlatform.ANDROID
        elif suffix == '.appimage':
            return AppPlatform.APPIMAGE
        elif suffix == '.deb' or suffix == '.rpm':
            return AppPlatform.NATIVE_LINUX
        elif suffix == '.flatpakref':
            return AppPlatform.FLATPAK
        elif suffix == '.snap':
            return AppPlatform.SNAP

        # Check if it's an executable
        if os.access(app_path, os.X_OK):
            return AppPlatform.NATIVE_LINUX

        return None

    def run_windows_app(self, app_path, args=None):
        """Run Windows application via Wine"""
        if not self.available_tools['wine']:
            print("Wine is not installed. Installing...")
            if not self.install_wine():
                return False

        cmd = ['wine', str(app_path)]
        if args:
            cmd.extend(args)

        try:
            print(f"Running Windows app: {app_path}")
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            print(f"Failed to run Windows app: {e}")
            return False

    def run_android_app(self, app_path):
        """Run Android application via Waydroid"""
        if not self.available_tools['waydroid']:
            print("Waydroid is not installed. Installing...")
            if not self.install_waydroid():
                return False

        try:
            # Install APK
            print(f"Installing Android app: {app_path}")
            subprocess.run(['waydroid', 'app', 'install', str(app_path)], check=True)

            # Launch Waydroid session
            subprocess.Popen(['waydroid', 'session', 'start'])
            return True
        except Exception as e:
            print(f"Failed to run Android app: {e}")
            return False

    def run_appimage(self, app_path):
        """Run AppImage application"""
        app_path = Path(app_path)

        # Make executable
        app_path.chmod(0o755)

        try:
            print(f"Running AppImage: {app_path}")
            subprocess.Popen([str(app_path)])
            return True
        except Exception as e:
            print(f"Failed to run AppImage: {e}")
            return False

    def run_flatpak(self, app_id):
        """Run Flatpak application"""
        if not self.available_tools['flatpak']:
            print("Flatpak is not installed. Installing...")
            if not self.install_flatpak():
                return False

        try:
            print(f"Running Flatpak app: {app_id}")
            subprocess.Popen(['flatpak', 'run', app_id])
            return True
        except Exception as e:
            print(f"Failed to run Flatpak app: {e}")
            return False

    def run_native(self, app_path, args=None):
        """Run native Linux application"""
        cmd = [str(app_path)]
        if args:
            cmd.extend(args)

        try:
            print(f"Running native app: {app_path}")
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            print(f"Failed to run native app: {e}")
            return False

    def launch_app(self, app_path, platform=None, args=None):
        """Universal app launcher - auto-detect and run"""
        if platform is None:
            platform = self.detect_app_type(app_path)

        if platform is None:
            print(f"Could not detect application type for: {app_path}")
            return False

        print(f"Detected platform: {platform.value}")

        # Route to appropriate launcher
        if platform == AppPlatform.WINDOWS:
            return self.run_windows_app(app_path, args)
        elif platform == AppPlatform.ANDROID:
            return self.run_android_app(app_path)
        elif platform == AppPlatform.APPIMAGE:
            return self.run_appimage(app_path)
        elif platform == AppPlatform.FLATPAK:
            return self.run_flatpak(app_path)
        elif platform in [AppPlatform.NATIVE_LINUX, AppPlatform.UBUNTU]:
            return self.run_native(app_path, args)
        else:
            print(f"Unsupported platform: {platform}")
            return False

    def setup_all_compatibility(self):
        """Setup all compatibility layers"""
        print("=" * 60)
        print("Setting up TL Linux Compatibility Layers")
        print("=" * 60)

        # Wine for Windows apps
        if not self.available_tools['wine']:
            print("\n[1/3] Installing Wine (Windows support)...")
            self.install_wine()
        else:
            print("\n[1/3] ✓ Wine already installed")

        # Waydroid for Android apps
        if not self.available_tools['waydroid']:
            print("\n[2/3] Installing Waydroid (Android support)...")
            self.install_waydroid()
        else:
            print("\n[2/3] ✓ Waydroid already installed")

        # Flatpak for universal apps
        if not self.available_tools['flatpak']:
            print("\n[3/3] Installing Flatpak (Universal apps)...")
            self.install_flatpak()
        else:
            print("\n[3/3] ✓ Flatpak already installed")

        print("\n" + "=" * 60)
        print("Compatibility setup complete!")
        print("=" * 60)

    def get_status(self):
        """Get compatibility layer status"""
        status = {
            'Windows (Wine)': '✓' if self.available_tools['wine'] else '✗',
            'Android (Waydroid)': '✓' if self.available_tools['waydroid'] else '✗',
            'Flatpak': '✓' if self.available_tools['flatpak'] else '✗',
            'AppImage': '✓',  # Always supported
            'Snap': '✓' if self.available_tools['snap'] else '✗',
        }
        return status

if __name__ == '__main__':
    compat = CompatibilityLayer()

    print("TL Linux Compatibility Layer Status:")
    print("=" * 40)
    for platform, status in compat.get_status().items():
        print(f"{platform:.<30} {status}")
    print("=" * 40)

    if len(sys.argv) > 1:
        app_path = sys.argv[1]
        compat.launch_app(app_path)
