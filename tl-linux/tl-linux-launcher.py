#!/usr/bin/env python3
"""
TL Linux - Main Application Launcher
Central hub for accessing all TL Linux applications and features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
from pathlib import Path
import json

class TLLinuxLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Application Launcher")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')

        # Configuration
        self.config_dir = Path.home() / '.tl-linux'
        self.config_file = self.config_dir / 'launcher_config.json'
        self.config_dir.mkdir(exist_ok=True)

        # Application paths
        self.app_dir = Path(__file__).parent / 'apps'
        self.system_dir = Path(__file__).parent / 'system'

        # Favorites
        self.favorites = []

        # Application catalog
        self.applications = {
            'Accessibility': [
                ('Screen Reader', 'screen_reader.py', 'Professional text-to-speech screen reader', '📖'),
                ('Screen Magnifier', 'screen_magnifier.py', 'Zoom and enhance screen areas', '🔍'),
                ('Motor Accessibility', 'motor_accessibility.py', 'Sticky Keys, Mouse Keys, Slow Keys', '⌨️'),
                ('Voice Control', 'voice_control.py', 'AI-powered voice commands', '🎤'),
                ('Focus Mode', 'focus_mode.py', 'Distraction-free workspace', '🎯'),
            ],
            'ADHD Support': [
                ('Pomodoro Timer', 'pomodoro_timer.py', 'Time management with breaks', '⏱️'),
                ('Body Doubling', 'body_doubling.py', 'Virtual co-working companion', '👥'),
                ('Routine Manager', 'routine_manager.py', 'Visual routine scheduler', '📅'),
                ('Task Manager', 'task_manager.py', 'ADHD-friendly task organization', '✓'),
                ('Habit Tracker', 'habit_tracker.py', 'Build and maintain habits', '📊'),
            ],
            'Productivity': [
                ('Notes', 'notes_app.py', 'Rich text notes with organization', '📝'),
                ('Text Editor', 'text_editor.py', 'Multi-tab editor with syntax highlighting', '📄'),
                ('Calendar', 'calendar_app.py', 'Event scheduling and reminders', '📆'),
                ('Calculator', 'calculator.py', 'Scientific calculator', '🔢'),
                ('Timer & Stopwatch', 'timer_stopwatch.py', 'Countdown timer and stopwatch', '⏲️'),
            ],
            'Media': [
                ('Video Player', 'video_player.py', 'Play videos with subtitle support', '🎬'),
                ('Music Player', 'music_player.py', 'Audio player with playlists', '🎵'),
                ('Image Viewer', 'image_viewer.py', 'View images with slideshow', '🖼️'),
                ('PDF Viewer', 'pdf_viewer.py', 'Read PDF documents', '📄'),
                ('Media Library', 'media_library.py', 'Organize all media files', '📚'),
            ],
            'Internet': [
                ('Web Browser', 'web_browser.py', 'Browse the internet', '🌐'),
                ('Email Client', 'email_client.py', 'Manage email accounts', '✉️'),
                ('Download Manager', 'download_manager.py', 'Manage file downloads', '⬇️'),
                ('RSS Reader', 'rss_reader.py', 'Read news feeds', '📰'),
            ],
            'System': [
                ('System Monitor', 'system_monitor.py', 'Monitor CPU, memory, processes', '📊'),
                ('Software Center', 'software_center.py', 'Install and manage applications', '📦'),
                ('Firewall Manager', 'firewall_manager.py', 'Configure system firewall', '🔥'),
                ('Terminal', 'terminal.py', 'Modern terminal emulator', '💻'),
                ('File Manager', 'file_manager.py', 'Browse and manage files', '📁'),
                ('Backup & Restore', 'backup_restore.py', 'Backup system and files', '💾'),
                ('System Settings', 'system_settings.py', 'Configure system preferences', '⚙️'),
                ('Log Viewer', 'log_viewer.py', 'View system logs', '📋'),
            ],
            'Utilities': [
                ('Screenshot Tool', 'screenshot_tool.py', 'Capture and annotate screenshots', '📸'),
                ('Archive Manager', 'archive_manager.py', 'Create and extract archives', '🗜️'),
                ('Disk Usage Analyzer', 'disk_usage.py', 'Analyze disk space usage', '💿'),
                ('Password Manager', 'password_manager.py', 'Secure password storage', '🔐'),
                ('Color Picker', 'color_picker.py', 'Pick and save colors', '🎨'),
                ('Unit Converter', 'unit_converter.py', 'Convert units and currencies', '🔄'),
            ],
            'Gaming & Fun': [
                ('Game Library', 'game_library.py', 'Browse and launch games', '🎮'),
                ('Puzzle Games', 'puzzle_games.py', 'Brain training puzzles', '🧩'),
                ('Relaxation', 'relaxation.py', 'Breathing exercises and sounds', '🧘'),
            ]
        }

        self.load_config()
        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Logo and title
        title_frame = tk.Frame(header, bg='#2b2b2b')
        title_frame.pack(side=tk.LEFT, padx=30, pady=20)

        tk.Label(
            title_frame,
            text="⏰ TL Linux",
            font=('Arial', 24, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(anchor='w')

        tk.Label(
            title_frame,
            text="The Accessible Operating System",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(anchor='w')

        # Quick actions
        actions_frame = tk.Frame(header, bg='#2b2b2b')
        actions_frame.pack(side=tk.RIGHT, padx=30)

        tk.Button(
            actions_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="📖 Help",
            command=self.show_help,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="⏻ Power",
            command=self.show_power_menu,
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left sidebar - Categories
        sidebar = tk.Frame(main_container, bg='#2b2b2b', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Categories",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=(20, 10), padx=20)

        # Search
        search_frame = tk.Frame(sidebar, bg='#2b2b2b')
        search_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        tk.Label(search_frame, text="🔍", bg='#2b2b2b', fg='white').pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_apps())

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            bd=0,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        # Category buttons
        self.category_buttons = {}
        categories = ['⭐ Favorites', 'All Apps'] + list(self.applications.keys())

        for category in categories:
            btn = tk.Button(
                sidebar,
                text=category,
                command=lambda c=category: self.show_category(c),
                bg='#2b2b2b',
                fg='white',
                activebackground='#4a9eff',
                activeforeground='white',
                bd=0,
                anchor='w',
                padx=20,
                pady=12,
                font=('Arial', 11)
            )
            btn.pack(fill=tk.X)
            self.category_buttons[category] = btn

        # System info at bottom
        info_frame = tk.Frame(sidebar, bg='#2b2b2b')
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)

        self.system_info_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 8),
            bg='#2b2b2b',
            fg='#888888',
            justify=tk.LEFT
        )
        self.system_info_label.pack()

        self.update_system_info()

        # Right panel - Application grid
        right_panel = tk.Frame(main_container, bg='#1a1a1a')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Category title
        self.category_title = tk.Label(
            right_panel,
            text="All Applications",
            font=('Arial', 18, 'bold'),
            bg='#1a1a1a',
            fg='white',
            anchor='w'
        )
        self.category_title.pack(fill=tk.X, pady=(0, 20))

        # Scrollable app container
        canvas_frame = tk.Frame(right_panel, bg='#1a1a1a')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)

        self.apps_container = tk.Frame(canvas, bg='#1a1a1a')

        canvas.create_window((0, 0), window=self.apps_container, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.apps_container.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Show all apps by default
        self.show_category('All Apps')

    def create_app_card(self, parent, name, script, description, icon, category=''):
        """Create an application card"""
        card = tk.Frame(parent, bg='#2b2b2b', relief=tk.RAISED, bd=1)

        # Icon
        tk.Label(
            card,
            text=icon,
            font=('Arial', 36),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(20, 10))

        # Name
        tk.Label(
            card,
            text=name,
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=(0, 5))

        # Description
        tk.Label(
            card,
            text=description,
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#888888',
            wraplength=200,
            justify=tk.CENTER
        ).pack(pady=(0, 15), padx=10)

        # Buttons
        btn_frame = tk.Frame(card, bg='#2b2b2b')
        btn_frame.pack(pady=(0, 15))

        # Launch button
        tk.Button(
            btn_frame,
            text="Launch",
            command=lambda: self.launch_app(script, name),
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=6,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        # Favorite button
        is_fav = f"{category}/{name}" in self.favorites
        fav_text = "★" if is_fav else "☆"

        tk.Button(
            btn_frame,
            text=fav_text,
            command=lambda: self.toggle_favorite(f"{category}/{name}"),
            bg='#6272a4',
            fg='#f1fa8c',
            bd=0,
            padx=10,
            pady=6,
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=2)

        return card

    def show_category(self, category):
        """Show applications for a category"""
        # Update button colors
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.config(bg='#4a9eff')
            else:
                btn.config(bg='#2b2b2b')

        # Clear current apps
        for widget in self.apps_container.winfo_children():
            widget.destroy()

        # Update title
        self.category_title.config(text=category)

        # Get apps to display
        apps_to_show = []

        if category == '⭐ Favorites':
            # Show favorites
            for fav in self.favorites:
                parts = fav.split('/')
                if len(parts) == 2:
                    cat_name, app_name = parts
                    if cat_name in self.applications:
                        for app in self.applications[cat_name]:
                            if app[0] == app_name:
                                apps_to_show.append((app[0], app[1], app[2], app[3], cat_name))

        elif category == 'All Apps':
            # Show all apps
            for cat_name, apps in self.applications.items():
                for app in apps:
                    apps_to_show.append((app[0], app[1], app[2], app[3], cat_name))

        else:
            # Show specific category
            if category in self.applications:
                for app in self.applications[category]:
                    apps_to_show.append((app[0], app[1], app[2], app[3], category))

        # Create grid of app cards
        cols = 4
        for i, app in enumerate(apps_to_show):
            row = i // cols
            col = i % cols

            card = self.create_app_card(
                self.apps_container,
                app[0], app[1], app[2], app[3], app[4]
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Configure grid weights
        for i in range(cols):
            self.apps_container.grid_columnconfigure(i, weight=1)

    def filter_apps(self):
        """Filter applications by search term"""
        search_term = self.search_var.get().lower()

        if not search_term:
            self.show_category('All Apps')
            return

        # Clear current apps
        for widget in self.apps_container.winfo_children():
            widget.destroy()

        self.category_title.config(text=f"Search: {search_term}")

        # Find matching apps
        apps_to_show = []
        for cat_name, apps in self.applications.items():
            for app in apps:
                if search_term in app[0].lower() or search_term in app[2].lower():
                    apps_to_show.append((app[0], app[1], app[2], app[3], cat_name))

        # Create grid
        cols = 4
        for i, app in enumerate(apps_to_show):
            row = i // cols
            col = i % cols

            card = self.create_app_card(
                self.apps_container,
                app[0], app[1], app[2], app[3], app[4]
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        for i in range(cols):
            self.apps_container.grid_columnconfigure(i, weight=1)

        if not apps_to_show:
            tk.Label(
                self.apps_container,
                text=f"No applications found for '{search_term}'",
                font=('Arial', 12),
                bg='#1a1a1a',
                fg='#888888'
            ).pack(pady=50)

    def launch_app(self, script, name):
        """Launch an application"""
        # Try apps directory first
        app_path = self.app_dir / script
        if not app_path.exists():
            # Try system directory
            app_path = self.system_dir / script

        if not app_path.exists():
            messagebox.showinfo(
                "Coming Soon",
                f"{name} is not yet installed.\n\n"
                "This application is part of the TL Linux roadmap."
            )
            return

        try:
            subprocess.Popen(['python3', str(app_path)])
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch {name}:\n{str(e)}")

    def toggle_favorite(self, app_id):
        """Toggle favorite status"""
        if app_id in self.favorites:
            self.favorites.remove(app_id)
        else:
            self.favorites.append(app_id)

        self.save_config()

        # Refresh current view
        current_category = None
        for cat, btn in self.category_buttons.items():
            if btn.cget('bg') == '#4a9eff':
                current_category = cat
                break

        if current_category:
            self.show_category(current_category)

    def update_system_info(self):
        """Update system information display"""
        try:
            # Get uptime
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])

            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            # Get memory
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()

            mem_info = {}
            for line in lines:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = int(parts[1].strip().split()[0])
                    mem_info[key] = value

            total_gb = mem_info.get('MemTotal', 0) / 1024 / 1024
            available_gb = mem_info.get('MemAvailable', 0) / 1024 / 1024

            info_text = f"Uptime: {hours}h {minutes}m\n"
            info_text += f"Memory: {available_gb:.1f}GB / {total_gb:.1f}GB free"

            self.system_info_label.config(text=info_text)

        except:
            self.system_info_label.config(text="TL Linux 1.0.0")

        # Update every 30 seconds
        self.root.after(30000, self.update_system_info)

    def open_settings(self):
        """Open system settings"""
        self.launch_app('system_settings.py', 'System Settings')

    def show_help(self):
        """Show help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("TL Linux Help")
        help_window.geometry("600x500")
        help_window.configure(bg='#1a1a1a')

        tk.Label(
            help_window,
            text="TL Linux Help",
            font=('Arial', 18, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=20)

        help_text = """
Welcome to TL Linux - The Accessible Operating System

Getting Started:
• Browse applications by category in the left sidebar
• Click on any app card to launch it
• Star your favorite apps for quick access
• Use the search box to find apps quickly

Accessibility Features:
• Press Alt+F1 to open accessibility menu
• Press Alt+F2 to activate voice control
• Press Alt+F3 to toggle screen magnifier
• Press Alt+F4 to activate screen reader

Keyboard Shortcuts:
• Ctrl+Alt+T: Open terminal
• Super+E: Open file manager
• Print Screen: Take screenshot
• Super+L: Lock screen

ADHD Support:
• Pomodoro Timer for focused work sessions
• Body Doubling for virtual co-working
• Routine Manager for daily schedules
• Focus Mode to minimize distractions

For more help, visit the documentation or
contact support@tl-linux.org
        """

        text_widget = tk.Text(
            help_window,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10),
            wrap=tk.WORD,
            bd=0,
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)

        tk.Button(
            help_window,
            text="Close",
            command=help_window.destroy,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=30,
            pady=10,
            font=('Arial', 10)
        ).pack(pady=(0, 20))

    def show_power_menu(self):
        """Show power options menu"""
        power_window = tk.Toplevel(self.root)
        power_window.title("Power Options")
        power_window.geometry("300x250")
        power_window.configure(bg='#1a1a1a')

        tk.Label(
            power_window,
            text="Power Options",
            font=('Arial', 16, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=20)

        tk.Button(
            power_window,
            text="🔒 Lock Screen",
            command=lambda: self.power_action('lock'),
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 11),
            width=20
        ).pack(pady=5)

        tk.Button(
            power_window,
            text="🔄 Restart",
            command=lambda: self.power_action('restart'),
            bg='#f1fa8c',
            fg='black',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 11),
            width=20
        ).pack(pady=5)

        tk.Button(
            power_window,
            text="⏻ Shutdown",
            command=lambda: self.power_action('shutdown'),
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 11),
            width=20
        ).pack(pady=5)

        tk.Button(
            power_window,
            text="Cancel",
            command=power_window.destroy,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 11),
            width=20
        ).pack(pady=10)

    def power_action(self, action):
        """Execute power action"""
        messagebox.showinfo(
            "Demo Mode",
            f"In a real system, this would {action} the computer.\n\n"
            "This is a demonstration of the TL Linux launcher."
        )

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.favorites = config.get('favorites', [])
            except:
                pass

    def save_config(self):
        """Save configuration"""
        config = {
            'favorites': self.favorites
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        self.save_config()
        self.root.destroy()

def main():
    launcher = TLLinuxLauncher()
    launcher.run()

if __name__ == '__main__':
    main()
