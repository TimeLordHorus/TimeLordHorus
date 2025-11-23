#!/usr/bin/env python3
"""
TL Linux Desktop Environment
Bottom tray UI with file manager and app drawer
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("Installing required dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "tk"], check=False)
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog


class TLDesktopEnvironment:
    """Main desktop environment with bottom tray"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux Desktop")
        self.root.attributes('-fullscreen', True)

        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load theme
        self.load_theme()

        # Running applications
        self.running_apps = []

        # Setup UI
        self.setup_desktop()
        self.setup_tray()

    def load_theme(self):
        """Load current theme settings"""
        theme_file = self.config_dir / 'user_profile.json'
        if theme_file.exists():
            with open(theme_file, 'r') as f:
                profile = json.load(f)
                self.current_theme = profile.get('preferences', {}).get('theme', 'retro')
        else:
            self.current_theme = 'retro'

        # Theme colors
        self.themes = {
            'retro': {
                'bg': '#000000',
                'fg': '#00FF00',
                'tray_bg': '#0a0a0a',
                'button_bg': '#1a1a1a',
                'accent': '#FF00FF'
            },
            'neon': {
                'bg': '#0a0a1a',
                'fg': '#FFFFFF',
                'tray_bg': '#16213e',
                'button_bg': '#1a1a2e',
                'accent': '#FF006E'
            },
            'lightning': {
                'bg': '#000033',
                'fg': '#FFFFFF',
                'tray_bg': '#000d1a',
                'button_bg': '#001a33',
                'accent': '#FFFF00'
            },
            'splash': {
                'bg': '#F7FAFC',
                'fg': '#2D3748',
                'tray_bg': '#EDF2F7',
                'button_bg': '#FFFFFF',
                'accent': '#667EEA'
            }
        }

        self.colors = self.themes.get(self.current_theme, self.themes['retro'])

    def setup_desktop(self):
        """Setup main desktop area"""
        self.desktop_frame = tk.Frame(
            self.root,
            bg=self.colors['bg']
        )
        self.desktop_frame.pack(fill=tk.BOTH, expand=True)

        # Welcome message
        welcome_label = tk.Label(
            self.desktop_frame,
            text="🐙 Welcome to TL Linux",
            font=("Monospace", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        welcome_label.pack(expand=True)

        # Desktop icons (simplified for now)
        self.create_desktop_icons()

    def create_desktop_icons(self):
        """Create desktop shortcut icons"""
        icon_frame = tk.Frame(self.desktop_frame, bg=self.colors['bg'])
        icon_frame.pack(side=tk.LEFT, padx=20, pady=20)

        icons = [
            ("📁", "Files", self.open_file_manager),
            ("⚙️", "Settings", self.open_settings),
            ("💻", "Terminal", self.open_terminal),
            ("🎮", "Games", self.open_games),
        ]

        for emoji, label, command in icons:
            icon_btn = tk.Button(
                icon_frame,
                text=f"{emoji}\n{label}",
                command=command,
                bg=self.colors['button_bg'],
                fg=self.colors['fg'],
                font=("Sans", 10),
                relief=tk.FLAT,
                padx=20,
                pady=10,
                cursor="hand2"
            )
            icon_btn.pack(pady=5, fill=tk.X)

    def setup_tray(self):
        """Setup bottom application tray"""
        self.tray_frame = tk.Frame(
            self.root,
            bg=self.colors['tray_bg'],
            height=60
        )
        self.tray_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.tray_frame.pack_propagate(False)

        # Left section - App drawer button
        self.app_drawer_btn = tk.Button(
            self.tray_frame,
            text="⚡ TL",
            command=self.toggle_app_drawer,
            bg=self.colors['accent'],
            fg='#000000',
            font=("Sans", 12, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.app_drawer_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Middle section - Running apps
        self.running_apps_frame = tk.Frame(
            self.tray_frame,
            bg=self.colors['tray_bg']
        )
        self.running_apps_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Right section - System tray
        self.system_tray_frame = tk.Frame(
            self.tray_frame,
            bg=self.colors['tray_bg']
        )
        self.system_tray_frame.pack(side=tk.RIGHT, padx=10)

        # Clock
        self.clock_label = tk.Label(
            self.system_tray_frame,
            font=("Monospace", 10),
            bg=self.colors['tray_bg'],
            fg=self.colors['fg']
        )
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        self.update_clock()

        # System buttons
        tk.Button(
            self.system_tray_frame,
            text="🔊",
            command=self.open_volume,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            font=("Sans", 12),
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=2)

        tk.Button(
            self.system_tray_frame,
            text="📶",
            command=self.open_network,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            font=("Sans", 12),
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=2)

    def update_clock(self):
        """Update clock display"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        self.clock_label.config(text=f"{date_str} {time_str}")
        self.root.after(1000, self.update_clock)

    def toggle_app_drawer(self):
        """Toggle application drawer"""
        drawer = tk.Toplevel(self.root)
        drawer.title("Applications")
        drawer.geometry("400x600")
        drawer.configure(bg=self.colors['bg'])

        # Search bar
        search_frame = tk.Frame(drawer, bg=self.colors['bg'])
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            search_frame,
            text="🔍",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Sans", 14)
        ).pack(side=tk.LEFT)

        search_entry = tk.Entry(
            search_frame,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            font=("Sans", 11),
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # App categories
        categories = {
            "🚀 Productivity": ["Calculator", "Calendar", "Notes", "Files"],
            "💻 Development": ["TL IDE", "Terminal", "Git Client", "Database Manager"],
            "🎮 Gaming": ["Emulator Hub", "Steam (Wine)", "Lutris"],
            "🌐 Internet": ["Web Browser", "Email", "Messenger"],
            "🎨 Creative": ["Image Editor", "Video Editor", "Music Player"],
            "⚙️ System": ["Settings", "Task Manager", "Disk Manager", "Software Center"]
        }

        # Scrollable app list
        canvas = tk.Canvas(drawer, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(drawer, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for category, apps in categories.items():
            cat_label = tk.Label(
                scrollable_frame,
                text=category,
                bg=self.colors['bg'],
                fg=self.colors['accent'],
                font=("Sans", 12, "bold"),
                anchor="w"
            )
            cat_label.pack(fill=tk.X, padx=10, pady=(10, 5))

            for app in apps:
                app_btn = tk.Button(
                    scrollable_frame,
                    text=f"  {app}",
                    command=lambda a=app: self.launch_app(a, drawer),
                    bg=self.colors['button_bg'],
                    fg=self.colors['fg'],
                    font=("Sans", 10),
                    relief=tk.FLAT,
                    anchor="w",
                    padx=20,
                    pady=8,
                    cursor="hand2"
                )
                app_btn.pack(fill=tk.X, padx=20, pady=2)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def launch_app(self, app_name, drawer=None):
        """Launch an application"""
        if drawer:
            drawer.destroy()

        # Add to running apps
        if app_name not in self.running_apps:
            self.running_apps.append(app_name)
            self.add_tray_button(app_name)

        messagebox.showinfo("Launch", f"Launching {app_name}...")

    def add_tray_button(self, app_name):
        """Add button to tray for running app"""
        btn = tk.Button(
            self.running_apps_frame,
            text=app_name[:10],
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        btn.pack(side=tk.LEFT, padx=2)

    def open_file_manager(self):
        """Open file manager"""
        self.launch_app("Files")

    def open_settings(self):
        """Open settings"""
        self.launch_app("Settings")

    def open_terminal(self):
        """Open terminal"""
        self.launch_app("Terminal")

    def open_games(self):
        """Open games/emulator hub"""
        self.launch_app("Emulator Hub")

    def open_volume(self):
        """Open volume control"""
        messagebox.showinfo("Volume", "Volume control opening...")

    def open_network(self):
        """Open network settings"""
        messagebox.showinfo("Network", "Network settings opening...")

    def run(self):
        """Start the desktop environment"""
        # Add exit binding
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.mainloop()


if __name__ == '__main__':
    desktop = TLDesktopEnvironment()
    desktop.run()
