#!/usr/bin/env python3
"""
TL Linux - App Store
GUI application manager replacing command-line package installation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import json
from pathlib import Path
import threading
import time
import re

class AppStore:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛍️ TL App Store")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')

        self.config_file = Path.home() / '.config' / 'tl-linux' / 'app_store.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self.load_config()

        # App database
        self.app_catalog = self.load_app_catalog()
        self.installed_apps = []
        self.featured_apps = []
        self.search_results = []

        self.setup_ui()
        self.load_installed_apps()
        self.load_featured_apps()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'auto_update': True,
            'show_suggestions': True,
            'download_updates_auto': False,
            'install_recommendations': True
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_app_catalog(self):
        """Load application catalog"""
        return {
            'productivity': [
                {
                    'id': 'libreoffice',
                    'name': 'LibreOffice',
                    'package': 'libreoffice',
                    'description': 'Complete office suite with word processor, spreadsheet, and presentation tools',
                    'icon': '📄',
                    'category': 'Productivity',
                    'rating': 4.5,
                    'size': '350 MB',
                    'featured': True
                },
                {
                    'id': 'gimp',
                    'name': 'GIMP',
                    'package': 'gimp',
                    'description': 'Professional image editing software, free alternative to Photoshop',
                    'icon': '🎨',
                    'category': 'Productivity',
                    'rating': 4.3,
                    'size': '140 MB',
                    'featured': True
                },
                {
                    'id': 'inkscape',
                    'name': 'Inkscape',
                    'package': 'inkscape',
                    'description': 'Vector graphics editor for creating illustrations, diagrams, and logos',
                    'icon': '✏️',
                    'category': 'Productivity',
                    'rating': 4.4,
                    'size': '95 MB'
                }
            ],
            'development': [
                {
                    'id': 'vscode',
                    'name': 'Visual Studio Code',
                    'package': 'code',
                    'description': 'Powerful code editor with extensions for all major programming languages',
                    'icon': '💻',
                    'category': 'Development',
                    'rating': 4.8,
                    'size': '220 MB',
                    'featured': True,
                    'snap': True
                },
                {
                    'id': 'git',
                    'name': 'Git',
                    'package': 'git',
                    'description': 'Distributed version control system for tracking code changes',
                    'icon': '🔀',
                    'category': 'Development',
                    'rating': 4.7,
                    'size': '12 MB'
                },
                {
                    'id': 'docker',
                    'name': 'Docker',
                    'package': 'docker.io',
                    'description': 'Platform for developing, shipping, and running applications in containers',
                    'icon': '🐋',
                    'category': 'Development',
                    'rating': 4.6,
                    'size': '280 MB'
                }
            ],
            'internet': [
                {
                    'id': 'firefox',
                    'name': 'Firefox',
                    'package': 'firefox',
                    'description': 'Fast, private web browser from Mozilla',
                    'icon': '🦊',
                    'category': 'Internet',
                    'rating': 4.5,
                    'size': '185 MB',
                    'featured': True
                },
                {
                    'id': 'chrome',
                    'name': 'Google Chrome',
                    'package': 'google-chrome-stable',
                    'description': 'Fast, simple, and secure web browser from Google',
                    'icon': '🌐',
                    'category': 'Internet',
                    'rating': 4.4,
                    'size': '210 MB',
                    'external': True
                },
                {
                    'id': 'thunderbird',
                    'name': 'Thunderbird',
                    'package': 'thunderbird',
                    'description': 'Email client with calendar and contacts',
                    'icon': '📧',
                    'category': 'Internet',
                    'rating': 4.2,
                    'size': '175 MB'
                }
            ],
            'media': [
                {
                    'id': 'vlc',
                    'name': 'VLC Media Player',
                    'package': 'vlc',
                    'description': 'Versatile media player that plays most multimedia files',
                    'icon': '🎬',
                    'category': 'Media',
                    'rating': 4.7,
                    'size': '95 MB',
                    'featured': True
                },
                {
                    'id': 'audacity',
                    'name': 'Audacity',
                    'package': 'audacity',
                    'description': 'Audio recording and editing software',
                    'icon': '🎵',
                    'category': 'Media',
                    'rating': 4.3,
                    'size': '45 MB'
                },
                {
                    'id': 'obs',
                    'name': 'OBS Studio',
                    'package': 'obs-studio',
                    'description': 'Video recording and live streaming software',
                    'icon': '📹',
                    'category': 'Media',
                    'rating': 4.6,
                    'size': '180 MB'
                }
            ],
            'games': [
                {
                    'id': 'steam',
                    'name': 'Steam',
                    'package': 'steam',
                    'description': 'Gaming platform with thousands of games',
                    'icon': '🎮',
                    'category': 'Games',
                    'rating': 4.5,
                    'size': '320 MB',
                    'featured': True
                }
            ],
            'utilities': [
                {
                    'id': 'timeshift',
                    'name': 'Timeshift',
                    'package': 'timeshift',
                    'description': 'System restore tool for creating snapshots',
                    'icon': '⏱️',
                    'category': 'Utilities',
                    'rating': 4.6,
                    'size': '25 MB'
                },
                {
                    'id': 'htop',
                    'name': 'htop',
                    'package': 'htop',
                    'description': 'Interactive process viewer and system monitor',
                    'icon': '📊',
                    'category': 'Utilities',
                    'rating': 4.4,
                    'size': '2 MB'
                }
            ]
        }

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg='#2c3e50')
        header_content.pack(expand=True)

        tk.Label(
            header_content,
            text="🛍️ TL App Store",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

        # Search bar
        search_frame = tk.Frame(header_content, bg='white', relief=tk.FLAT)
        search_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(search_frame, text="🔍", bg='white', font=('Arial', 14)).pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 12),
            width=30,
            bd=0,
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Navigation
        nav_frame = tk.Frame(self.root, bg='#34495e', pady=10)
        nav_frame.pack(fill=tk.X)

        self.current_view = tk.StringVar(value='featured')

        nav_buttons = [
            ('⭐ Featured', 'featured'),
            ('💼 Productivity', 'productivity'),
            ('💻 Development', 'development'),
            ('🌐 Internet', 'internet'),
            ('🎬 Media', 'media'),
            ('🎮 Games', 'games'),
            ('🔧 Utilities', 'utilities'),
            ('📦 Installed', 'installed')
        ]

        for text, value in nav_buttons:
            btn = tk.Radiobutton(
                nav_frame,
                text=text,
                variable=self.current_view,
                value=value,
                bg='#34495e',
                fg='white',
                selectcolor='#2c3e50',
                font=('Arial', 11),
                indicatoron=0,
                padx=15,
                pady=5,
                command=lambda v=value: self.change_view(v)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Main content
        self.content_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10,
            pady=5,
            bg='#ecf0f1'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Show featured by default
        self.show_featured()

    def change_view(self, view):
        """Change current view"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view == 'featured':
            self.show_featured()
        elif view == 'installed':
            self.show_installed()
        else:
            self.show_category(view)

    def show_featured(self):
        """Show featured apps"""
        tk.Label(
            self.content_frame,
            text="Featured Applications",
            font=('Arial', 18, 'bold'),
            bg='#f5f5f5'
        ).pack(anchor='w', pady=(0, 20))

        # Featured apps grid
        apps_frame = tk.Frame(self.content_frame, bg='#f5f5f5')
        apps_frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        col = 0

        for category, apps in self.app_catalog.items():
            for app in apps:
                if app.get('featured', False):
                    card = self.create_app_card(apps_frame, app, large=True)
                    card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1

        # Configure grid
        for i in range(3):
            apps_frame.grid_columnconfigure(i, weight=1)

    def show_category(self, category):
        """Show apps in category"""
        category_name = category.capitalize()

        tk.Label(
            self.content_frame,
            text=f"{category_name} Applications",
            font=('Arial', 18, 'bold'),
            bg='#f5f5f5'
        ).pack(anchor='w', pady=(0, 20))

        # Apps list
        apps_frame = tk.Frame(self.content_frame, bg='#f5f5f5')
        apps_frame.pack(fill=tk.BOTH, expand=True)

        if category in self.app_catalog:
            for idx, app in enumerate(self.app_catalog[category]):
                card = self.create_app_card(apps_frame, app, large=False)
                card.pack(fill=tk.X, pady=5)

    def show_installed(self):
        """Show installed apps"""
        tk.Label(
            self.content_frame,
            text="Installed Applications",
            font=('Arial', 18, 'bold'),
            bg='#f5f5f5'
        ).pack(anchor='w', pady=(0, 20))

        if not self.installed_apps:
            tk.Label(
                self.content_frame,
                text="Loading installed applications...",
                font=('Arial', 12),
                bg='#f5f5f5',
                fg='#7f8c8d'
            ).pack(pady=50)
        else:
            apps_frame = tk.Frame(self.content_frame, bg='#f5f5f5')
            apps_frame.pack(fill=tk.BOTH, expand=True)

            for app_id in self.installed_apps:
                app = self.find_app_by_id(app_id)
                if app:
                    card = self.create_app_card(apps_frame, app, large=False, installed=True)
                    card.pack(fill=tk.X, pady=5)

    def create_app_card(self, parent, app, large=False, installed=False):
        """Create app card"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)

        if large:
            # Large card for featured apps
            icon_label = tk.Label(
                card,
                text=app['icon'],
                font=('Arial', 48),
                bg='white'
            )
            icon_label.pack(pady=(20, 10))

            tk.Label(
                card,
                text=app['name'],
                font=('Arial', 14, 'bold'),
                bg='white'
            ).pack()

            tk.Label(
                card,
                text=app['description'],
                font=('Arial', 10),
                bg='white',
                fg='#7f8c8d',
                wraplength=250
            ).pack(pady=10, padx=10)

            # Rating
            rating_text = '⭐' * int(app['rating']) + f" {app['rating']}"
            tk.Label(
                card,
                text=rating_text,
                font=('Arial', 10),
                bg='white'
            ).pack()

            # Install button
            is_installed = app['id'] in self.installed_apps

            btn_text = "✓ Installed" if is_installed else "Install"
            btn_color = '#95a5a6' if is_installed else '#27ae60'

            tk.Button(
                card,
                text=btn_text,
                command=lambda a=app: self.install_app(a) if not is_installed else None,
                bg=btn_color,
                fg='white',
                font=('Arial', 11, 'bold'),
                relief=tk.FLAT,
                padx=20,
                pady=8,
                state=tk.DISABLED if is_installed else tk.NORMAL
            ).pack(pady=(10, 20))

        else:
            # Compact card for list view
            card.config(padx=15, pady=10)

            top_frame = tk.Frame(card, bg='white')
            top_frame.pack(fill=tk.X)

            # Icon and name
            tk.Label(
                top_frame,
                text=app['icon'],
                font=('Arial', 32),
                bg='white'
            ).pack(side=tk.LEFT, padx=(0, 15))

            info_frame = tk.Frame(top_frame, bg='white')
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                info_frame,
                text=app['name'],
                font=('Arial', 14, 'bold'),
                bg='white'
            ).pack(anchor='w')

            tk.Label(
                info_frame,
                text=app['description'],
                font=('Arial', 10),
                bg='white',
                fg='#7f8c8d',
                wraplength=600
            ).pack(anchor='w')

            # Metadata
            meta_text = f"⭐ {app['rating']} • 📦 {app['size']} • {app['category']}"
            tk.Label(
                info_frame,
                text=meta_text,
                font=('Arial', 9),
                bg='white',
                fg='#95a5a6'
            ).pack(anchor='w', pady=(5, 0))

            # Action button
            is_installed = app['id'] in self.installed_apps

            if installed:
                tk.Button(
                    top_frame,
                    text="🗑️ Uninstall",
                    command=lambda a=app: self.uninstall_app(a),
                    bg='#e74c3c',
                    fg='white',
                    relief=tk.FLAT,
                    padx=15,
                    pady=8
                ).pack(side=tk.RIGHT, padx=5)
            else:
                btn_text = "✓ Installed" if is_installed else "Install"
                btn_color = '#95a5a6' if is_installed else '#27ae60'

                tk.Button(
                    top_frame,
                    text=btn_text,
                    command=lambda a=app: self.install_app(a) if not is_installed else None,
                    bg=btn_color,
                    fg='white',
                    relief=tk.FLAT,
                    padx=15,
                    pady=8,
                    state=tk.DISABLED if is_installed else tk.NORMAL
                ).pack(side=tk.RIGHT)

        return card

    def install_app(self, app):
        """Install application"""
        if messagebox.askyesno("Install Application", f"Install {app['name']}?\n\nSize: {app['size']}"):
            self.status_bar.config(text=f"Installing {app['name']}...")

            def install_thread():
                try:
                    # Update package list
                    subprocess.run(['sudo', 'apt-get', 'update'],
                                 capture_output=True, timeout=60)

                    # Install package
                    if app.get('snap'):
                        result = subprocess.run(
                            ['sudo', 'snap', 'install', app['package']],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                    else:
                        result = subprocess.run(
                            ['sudo', 'apt-get', 'install', '-y', app['package']],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )

                    if result.returncode == 0:
                        self.installed_apps.append(app['id'])
                        self.root.after(0, lambda: self.status_bar.config(text=f"✓ {app['name']} installed successfully"))
                        self.root.after(0, lambda: messagebox.showinfo("Success", f"{app['name']} has been installed!"))
                        self.root.after(0, lambda: self.change_view(self.current_view.get()))
                    else:
                        self.root.after(0, lambda: self.status_bar.config(text=f"✗ Failed to install {app['name']}"))
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to install {app['name']}\n\n{result.stderr[:200]}"))

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Installation error: {e}"))

            threading.Thread(target=install_thread, daemon=True).start()

    def uninstall_app(self, app):
        """Uninstall application"""
        if messagebox.askyesno("Uninstall Application", f"Uninstall {app['name']}?"):
            self.status_bar.config(text=f"Uninstalling {app['name']}...")

            def uninstall_thread():
                try:
                    result = subprocess.run(
                        ['sudo', 'apt-get', 'remove', '-y', app['package']],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        if app['id'] in self.installed_apps:
                            self.installed_apps.remove(app['id'])
                        self.root.after(0, lambda: self.status_bar.config(text=f"✓ {app['name']} uninstalled"))
                        self.root.after(0, lambda: messagebox.showinfo("Success", f"{app['name']} has been uninstalled"))
                        self.root.after(0, lambda: self.change_view('installed'))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to uninstall {app['name']}"))

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Uninstall error: {e}"))

            threading.Thread(target=uninstall_thread, daemon=True).start()

    def on_search(self, *args):
        """Handle search"""
        query = self.search_var.get().lower()

        if len(query) < 2:
            return

        # Search through all apps
        self.search_results = []

        for category, apps in self.app_catalog.items():
            for app in apps:
                if query in app['name'].lower() or query in app['description'].lower():
                    self.search_results.append(app)

        # Show search results
        if self.search_results:
            self.show_search_results()

    def show_search_results(self):
        """Show search results"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.content_frame,
            text=f"Search Results ({len(self.search_results)} found)",
            font=('Arial', 18, 'bold'),
            bg='#f5f5f5'
        ).pack(anchor='w', pady=(0, 20))

        apps_frame = tk.Frame(self.content_frame, bg='#f5f5f5')
        apps_frame.pack(fill=tk.BOTH, expand=True)

        for app in self.search_results:
            card = self.create_app_card(apps_frame, app, large=False)
            card.pack(fill=tk.X, pady=5)

    def load_installed_apps(self):
        """Load list of installed apps"""
        def load_thread():
            # Check which apps from catalog are installed
            for category, apps in self.app_catalog.items():
                for app in apps:
                    try:
                        result = subprocess.run(
                            ['dpkg', '-s', app['package']],
                            capture_output=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            self.installed_apps.append(app['id'])
                    except:
                        pass

            self.root.after(0, lambda: self.status_bar.config(text=f"Loaded {len(self.installed_apps)} installed apps"))

        threading.Thread(target=load_thread, daemon=True).start()

    def load_featured_apps(self):
        """Load featured apps"""
        for category, apps in self.app_catalog.items():
            for app in apps:
                if app.get('featured', False):
                    self.featured_apps.append(app)

    def find_app_by_id(self, app_id):
        """Find app by ID"""
        for category, apps in self.app_catalog.items():
            for app in apps:
                if app['id'] == app_id:
                    return app
        return None

    def run(self):
        """Run app store"""
        self.root.mainloop()

if __name__ == '__main__':
    store = AppStore()
    store.run()
