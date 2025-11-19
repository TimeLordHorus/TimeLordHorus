#!/usr/bin/env python3
"""
TL Linux Settings Manager
Comprehensive system configuration and customization
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from themes.theme_engine import ThemeEngine
except ImportError:
    ThemeEngine = None

class SettingsManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚙️ TL Linux Settings")
        self.root.geometry("900x650")

        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.config_dir / 'settings.json'

        self.settings = self.load_settings()
        self.theme_engine = ThemeEngine() if ThemeEngine else None

        self.setup_ui()

    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            'appearance': {
                'theme': 'retro',
                'auto_theme': False,
                'font_size': 10,
                'icon_size': 'medium',
                'animations': True
            },
            'system': {
                'auto_start_apps': [],
                'show_splash': True,
                'enable_ml': True,
                'save_session': True
            },
            'desktop': {
                'tray_position': 'bottom',
                'show_desktop_icons': True,
                'wallpaper': 'default',
                'transparency': False
            },
            'compatibility': {
                'wine_enabled': True,
                'android_enabled': True,
                'flatpak_enabled': True
            },
            'privacy': {
                'collect_usage_data': True,
                'personalization': True,
                'crash_reports': True
            }
        }

        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for category, options in default_settings.items():
                        if category in loaded:
                            options.update(loaded[category])
                    return default_settings
            except:
                pass

        return default_settings

    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

        messagebox.showinfo("Settings Saved", "Your settings have been saved!")

    def setup_ui(self):
        """Setup settings UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="⚙️ TL Linux Settings",
            font=('Sans', 20, 'bold'),
            bg='#1a1a1a',
            fg='#FF00FF'
        ).pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left sidebar - Categories
        sidebar = tk.Frame(main_container, bg='#1a1a1a', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        categories = [
            ('🎨', 'Appearance', self.show_appearance),
            ('🖥️', 'Desktop', self.show_desktop),
            ('⚡', 'System', self.show_system),
            ('🔄', 'Compatibility', self.show_compatibility),
            ('🔒', 'Privacy', self.show_privacy),
            ('ℹ️', 'About', self.show_about),
        ]

        for icon, name, command in categories:
            btn = tk.Button(
                sidebar,
                text=f"{icon} {name}",
                command=command,
                bg='#333333',
                fg='#00FF00',
                font=('Sans', 11),
                relief=tk.FLAT,
                anchor='w',
                padx=20,
                pady=12,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=10, pady=3)

        # Right panel - Settings content
        self.content_frame = tk.Frame(main_container, bg='#0a0a0a')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Bottom buttons
        bottom_bar = tk.Frame(self.root, bg='#1a1a1a', pady=10)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            bottom_bar,
            text="💾 Save Settings",
            command=self.save_settings,
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 11, 'bold'),
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            bottom_bar,
            text="↺ Reset to Defaults",
            command=self.reset_defaults,
            bg='#333333',
            fg='#00FF00',
            font=('Sans', 10),
            bd=0,
            padx=15,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=5)

        # Show first category
        self.show_appearance()

    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def add_section_header(self, text):
        """Add section header"""
        tk.Label(
            self.content_frame,
            text=text,
            font=('Sans', 14, 'bold'),
            bg='#0a0a0a',
            fg='#00FFFF',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 10))

    def add_option(self, label, widget, description=None):
        """Add option row"""
        frame = tk.Frame(self.content_frame, bg='#0a0a0a', pady=5)
        frame.pack(fill=tk.X, pady=3)

        tk.Label(
            frame,
            text=label,
            bg='#0a0a0a',
            fg='#00FF00',
            font=('Sans', 10),
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT)

        widget.pack(side=tk.LEFT, padx=10)

        if description:
            tk.Label(
                frame,
                text=f"ℹ️ {description}",
                bg='#0a0a0a',
                fg='#666666',
                font=('Sans', 8)
            ).pack(side=tk.LEFT, padx=10)

    def show_appearance(self):
        """Show appearance settings"""
        self.clear_content()
        self.add_section_header("🎨 Appearance Settings")

        # Theme selection
        theme_var = tk.StringVar(value=self.settings['appearance']['theme'])
        theme_combo = ttk.Combobox(
            self.content_frame,
            textvariable=theme_var,
            values=['retro', 'neon', 'lightning', 'splash'],
            state='readonly',
            width=15
        )

        def on_theme_change(event):
            self.settings['appearance']['theme'] = theme_var.get()
            if self.theme_engine:
                self.theme_engine.set_theme(theme_var.get())

        theme_combo.bind('<<ComboboxSelected>>', on_theme_change)
        self.add_option("Theme:", theme_combo, "Visual style of the interface")

        # Auto theme
        auto_theme_var = tk.BooleanVar(value=self.settings['appearance']['auto_theme'])
        auto_check = tk.Checkbutton(
            self.content_frame,
            variable=auto_theme_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['appearance'].update({'auto_theme': auto_theme_var.get()})
        )
        self.add_option("Auto Theme (ML):", auto_check, "Let ML choose theme based on usage")

        # Font size
        font_var = tk.IntVar(value=self.settings['appearance']['font_size'])
        font_scale = tk.Scale(
            self.content_frame,
            from_=8,
            to=16,
            orient=tk.HORIZONTAL,
            variable=font_var,
            bg='#1a1a1a',
            fg='#00FF00',
            highlightthickness=0,
            command=lambda v: self.settings['appearance'].update({'font_size': int(v)})
        )
        self.add_option("Font Size:", font_scale)

        # Icon size
        icon_var = tk.StringVar(value=self.settings['appearance']['icon_size'])
        icon_combo = ttk.Combobox(
            self.content_frame,
            textvariable=icon_var,
            values=['small', 'medium', 'large', 'extra-large'],
            state='readonly',
            width=15
        )
        icon_combo.bind('<<ComboboxSelected>>',
                       lambda e: self.settings['appearance'].update({'icon_size': icon_var.get()}))
        self.add_option("Icon Size:", icon_combo)

        # Animations
        anim_var = tk.BooleanVar(value=self.settings['appearance']['animations'])
        anim_check = tk.Checkbutton(
            self.content_frame,
            variable=anim_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['appearance'].update({'animations': anim_var.get()})
        )
        self.add_option("Enable Animations:", anim_check)

    def show_desktop(self):
        """Show desktop settings"""
        self.clear_content()
        self.add_section_header("🖥️ Desktop Settings")

        # Tray position
        tray_var = tk.StringVar(value=self.settings['desktop']['tray_position'])
        tray_combo = ttk.Combobox(
            self.content_frame,
            textvariable=tray_var,
            values=['top', 'bottom', 'left', 'right'],
            state='readonly',
            width=15
        )
        tray_combo.bind('<<ComboboxSelected>>',
                       lambda e: self.settings['desktop'].update({'tray_position': tray_var.get()}))
        self.add_option("Tray Position:", tray_combo)

        # Desktop icons
        icons_var = tk.BooleanVar(value=self.settings['desktop']['show_desktop_icons'])
        icons_check = tk.Checkbutton(
            self.content_frame,
            variable=icons_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['desktop'].update({'show_desktop_icons': icons_var.get()})
        )
        self.add_option("Show Desktop Icons:", icons_check)

        # Transparency
        trans_var = tk.BooleanVar(value=self.settings['desktop']['transparency'])
        trans_check = tk.Checkbutton(
            self.content_frame,
            variable=trans_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['desktop'].update({'transparency': trans_var.get()})
        )
        self.add_option("Window Transparency:", trans_check)

    def show_system(self):
        """Show system settings"""
        self.clear_content()
        self.add_section_header("⚡ System Settings")

        # Show splash
        splash_var = tk.BooleanVar(value=self.settings['system']['show_splash'])
        splash_check = tk.Checkbutton(
            self.content_frame,
            variable=splash_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['system'].update({'show_splash': splash_var.get()})
        )
        self.add_option("Show Boot Animation:", splash_check)

        # ML enabled
        ml_var = tk.BooleanVar(value=self.settings['system']['enable_ml'])
        ml_check = tk.Checkbutton(
            self.content_frame,
            variable=ml_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['system'].update({'enable_ml': ml_var.get()})
        )
        self.add_option("Enable ML Personalization:", ml_check, "Learn from your usage patterns")

        # Save session
        session_var = tk.BooleanVar(value=self.settings['system']['save_session'])
        session_check = tk.Checkbutton(
            self.content_frame,
            variable=session_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['system'].update({'save_session': session_var.get()})
        )
        self.add_option("Save Session on Exit:", session_check, "Restore apps on next login")

    def show_compatibility(self):
        """Show compatibility settings"""
        self.clear_content()
        self.add_section_header("🔄 Application Compatibility")

        # Wine
        wine_var = tk.BooleanVar(value=self.settings['compatibility']['wine_enabled'])
        wine_check = tk.Checkbutton(
            self.content_frame,
            variable=wine_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['compatibility'].update({'wine_enabled': wine_var.get()})
        )
        self.add_option("Windows Apps (Wine):", wine_check, "Run Windows applications")

        # Android
        android_var = tk.BooleanVar(value=self.settings['compatibility']['android_enabled'])
        android_check = tk.Checkbutton(
            self.content_frame,
            variable=android_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['compatibility'].update({'android_enabled': android_var.get()})
        )
        self.add_option("Android Apps (Waydroid):", android_check, "Run Android applications")

        # Flatpak
        flatpak_var = tk.BooleanVar(value=self.settings['compatibility']['flatpak_enabled'])
        flatpak_check = tk.Checkbutton(
            self.content_frame,
            variable=flatpak_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['compatibility'].update({'flatpak_enabled': flatpak_var.get()})
        )
        self.add_option("Flatpak Support:", flatpak_check, "Universal app support")

        # Status and tools
        tk.Label(
            self.content_frame,
            text="\n🔧 Compatibility Tools Status",
            font=('Sans', 12, 'bold'),
            bg='#0a0a0a',
            fg='#00FFFF',
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 10))

        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'compat'))
            from compatibility_layer import CompatibilityLayer
            compat = CompatibilityLayer()
            status = compat.get_status()

            for platform, stat in status.items():
                status_frame = tk.Frame(self.content_frame, bg='#0a0a0a')
                status_frame.pack(fill=tk.X, pady=2)

                tk.Label(
                    status_frame,
                    text=f"{platform}:",
                    bg='#0a0a0a',
                    fg='#00FF00',
                    font=('Monospace', 9),
                    width=30,
                    anchor='w'
                ).pack(side=tk.LEFT)

                color = '#00FF00' if stat == '✓' else '#FF3333'
                tk.Label(
                    status_frame,
                    text=stat,
                    bg='#0a0a0a',
                    fg=color,
                    font=('Sans', 10, 'bold')
                ).pack(side=tk.LEFT)
        except:
            tk.Label(
                self.content_frame,
                text="Unable to load compatibility status",
                bg='#0a0a0a',
                fg='#666666',
                font=('Sans', 9)
            ).pack()

    def show_privacy(self):
        """Show privacy settings"""
        self.clear_content()
        self.add_section_header("🔒 Privacy & Data")

        # Usage data
        usage_var = tk.BooleanVar(value=self.settings['privacy']['collect_usage_data'])
        usage_check = tk.Checkbutton(
            self.content_frame,
            variable=usage_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['privacy'].update({'collect_usage_data': usage_var.get()})
        )
        self.add_option("Collect Usage Data:", usage_check, "Help improve TL Linux")

        # Personalization
        personal_var = tk.BooleanVar(value=self.settings['privacy']['personalization'])
        personal_check = tk.Checkbutton(
            self.content_frame,
            variable=personal_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['privacy'].update({'personalization': personal_var.get()})
        )
        self.add_option("Personalization Data:", personal_check, "Store ML preferences locally")

        # Crash reports
        crash_var = tk.BooleanVar(value=self.settings['privacy']['crash_reports'])
        crash_check = tk.Checkbutton(
            self.content_frame,
            variable=crash_var,
            bg='#0a0a0a',
            fg='#00FF00',
            selectcolor='#1a1a1a',
            command=lambda: self.settings['privacy'].update({'crash_reports': crash_var.get()})
        )
        self.add_option("Send Crash Reports:", crash_check, "Anonymous crash diagnostics")

        tk.Label(
            self.content_frame,
            text="\n📝 Privacy Note:\nAll data is stored locally on your device.\n"
                 "TL Linux does not send data to external servers.",
            font=('Sans', 9),
            bg='#0a0a0a',
            fg='#666666',
            justify=tk.LEFT,
            anchor='w'
        ).pack(fill=tk.X, pady=20)

    def show_about(self):
        """Show about information"""
        self.clear_content()

        about_text = """
    ████████╗██╗         ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗
    ╚══██╔══╝██║         ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝
       ██║   ██║         ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝
       ██║   ██║         ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗
       ██║   ███████╗    ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗
       ╚═╝   ╚══════╝    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝

                    TL Linux - Time Lord Computing
                          Version 1.0.0

    A comprehensive personal computing solution with ML-powered
    personalization and cross-platform application support.

    ✨ Features:
    • ML-powered adaptive themes
    • Multi-platform app compatibility (Windows, Android, Linux)
    • Comprehensive productivity suite
    • Gaming emulator hub
    • Intelligent user experience

    🎨 Themes: Retro, Neon, Lightning, Splash

    💻 Built with love using Python and modern technologies

    © 2024 TL Linux Project
        """

        tk.Label(
            self.content_frame,
            text=about_text,
            font=('Monospace', 9),
            bg='#0a0a0a',
            fg='#00FF00',
            justify=tk.LEFT,
            anchor='nw'
        ).pack(expand=True, fill=tk.BOTH)

    def reset_defaults(self):
        """Reset to default settings"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.settings_file.unlink(missing_ok=True)
            self.settings = self.load_settings()
            messagebox.showinfo("Reset Complete", "Settings have been reset to defaults!")
            self.show_appearance()  # Refresh display

    def run(self):
        """Run settings manager"""
        self.root.mainloop()

if __name__ == '__main__':
    settings = SettingsManager()
    settings.run()
