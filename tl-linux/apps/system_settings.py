#!/usr/bin/env python3
"""
TL Linux - System Settings Hub
Central control panel for all system settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os
import subprocess

class SystemSettings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - System Settings")
        self.root.geometry("1100x750")
        self.root.configure(bg='#2b2b2b')

        self.config_dir = os.path.expanduser('~/.tl-linux/settings')
        os.makedirs(self.config_dir, exist_ok=True)

        self.settings_file = os.path.join(self.config_dir, 'system_settings.json')
        self.settings = self.load_settings()

        self.setup_ui()

    def load_settings(self):
        """Load system settings"""
        default_settings = {
            'appearance': {
                'theme': 'dark',
                'accent_color': '#4a9eff',
                'font_size': 'medium',
                'animations': True
            },
            'display': {
                'resolution': 'auto',
                'scaling': 100,
                'night_light': False,
                'night_light_start': '20:00',
                'night_light_end': '06:00'
            },
            'sound': {
                'output_device': 'default',
                'output_volume': 75,
                'input_device': 'default',
                'input_volume': 80,
                'system_sounds': True
            },
            'power': {
                'screen_timeout': 10,  # minutes
                'sleep_timeout': 30,
                'power_profile': 'balanced',
                'lid_action': 'sleep'
            },
            'privacy': {
                'location_services': False,
                'telemetry': False,
                'crash_reports': True
            },
            'keyboard': {
                'layout': 'us',
                'repeat_delay': 300,
                'repeat_rate': 30,
                'shortcuts_enabled': True
            },
            'mouse': {
                'speed': 50,
                'acceleration': True,
                'natural_scrolling': False,
                'primary_button': 'left'
            }
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for category in default_settings:
                        if category in loaded:
                            default_settings[category].update(loaded[category])
        except:
            pass

        return default_settings

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Left sidebar with categories
        sidebar = tk.Frame(self.root, bg='#1a1a1a', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Header
        tk.Label(
            sidebar,
            text="⚙️ Settings",
            font=('Arial', 18, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=30)

        # Categories
        categories = [
            ("🎨", "Appearance", self.show_appearance),
            ("🖥️", "Display", self.show_display),
            ("🔊", "Sound", self.show_sound),
            ("⚡", "Power", self.show_power),
            ("🔒", "Privacy & Security", self.show_privacy),
            ("⌨️", "Keyboard", self.show_keyboard),
            ("🖱️", "Mouse & Touchpad", self.show_mouse),
            ("🌐", "Network", self.show_network),
            ("👤", "Users & Accounts", self.show_users),
            ("📅", "Date & Time", self.show_datetime),
            ("🌍", "Language & Region", self.show_language),
            ("♿", "Accessibility", self.show_accessibility),
            ("📦", "Applications", self.show_applications),
            ("ℹ️", "About System", self.show_about)
        ]

        self.category_buttons = []
        for emoji, label, command in categories:
            btn = tk.Button(
                sidebar,
                text=f"{emoji}  {label}",
                command=command,
                font=('Arial', 11),
                bg='#1a1a1a',
                fg='white',
                activebackground='#4a9eff',
                activeforeground='white',
                bd=0,
                padx=20,
                pady=12,
                anchor='w',
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.category_buttons.append(btn)

        # Right content area
        self.content_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Default view
        self.show_appearance()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_section(self, parent, title):
        """Create a settings section"""
        section = tk.Frame(parent, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        section.pack(fill=tk.X, padx=30, pady=15)

        tk.Label(
            section,
            text=title,
            font=('Arial', 13, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(anchor='w', padx=20, pady=15)

        content = tk.Frame(section, bg='#1a1a1a')
        content.pack(fill=tk.BOTH, padx=20, pady=(0, 20))

        return content

    def show_appearance(self):
        """Show appearance settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎨 Appearance",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        # Theme
        section = self.create_section(self.content_frame, "Theme")

        tk.Label(
            section,
            text="Color Theme:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=0, column=0, sticky='w', pady=10)

        theme_var = tk.StringVar(value=self.settings['appearance']['theme'])
        themes = ['Dark', 'Light', 'Retro', 'Neon', 'Lightning', 'Splash']

        for i, theme in enumerate(themes):
            tk.Radiobutton(
                section,
                text=theme,
                variable=theme_var,
                value=theme.lower(),
                font=('Arial', 10),
                bg='#1a1a1a',
                fg='#cccccc',
                selectcolor='#2b2b2b'
            ).grid(row=0, column=i+1, padx=10)

        # Accent color
        tk.Label(
            section,
            text="Accent Color:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=1, column=0, sticky='w', pady=10)

        accent_btn = tk.Button(
            section,
            text="Choose Color",
            command=self.choose_accent_color,
            font=('Arial', 10),
            bg=self.settings['appearance']['accent_color'],
            fg='white',
            padx=15,
            pady=5
        )
        accent_btn.grid(row=1, column=1, sticky='w', pady=10)

        # Font size
        tk.Label(
            section,
            text="Font Size:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=2, column=0, sticky='w', pady=10)

        font_size_var = tk.StringVar(value=self.settings['appearance']['font_size'])
        sizes = [('Small', 'small'), ('Medium', 'medium'), ('Large', 'large'), ('Extra Large', 'xlarge')]

        for i, (label, value) in enumerate(sizes):
            tk.Radiobutton(
                section,
                text=label,
                variable=font_size_var,
                value=value,
                font=('Arial', 10),
                bg='#1a1a1a',
                fg='#cccccc',
                selectcolor='#2b2b2b'
            ).grid(row=2, column=i+1, padx=10)

        # Animations
        animations_var = tk.BooleanVar(value=self.settings['appearance']['animations'])
        tk.Checkbutton(
            section,
            text="Enable animations and transitions",
            variable=animations_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).grid(row=3, column=0, columnspan=3, sticky='w', pady=10)

        # Save button
        tk.Button(
            self.content_frame,
            text="💾 Save Changes",
            command=self.save_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0
        ).pack(pady=20, padx=30, anchor='e')

    def show_display(self):
        """Show display settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🖥️ Display",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        # Resolution
        section = self.create_section(self.content_frame, "Screen Resolution")

        tk.Label(
            section,
            text="Resolution:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=0, column=0, sticky='w', pady=10)

        resolutions = ['Auto', '1920x1080', '1680x1050', '1600x900', '1440x900', '1366x768', '1280x720']
        resolution_combo = ttk.Combobox(section, values=resolutions, state='readonly', width=15)
        resolution_combo.set(self.settings['display'].get('resolution', 'Auto'))
        resolution_combo.grid(row=0, column=1, sticky='w', pady=10)

        # Scaling
        tk.Label(
            section,
            text="Display Scaling:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=1, column=0, sticky='w', pady=10)

        scaling_var = tk.IntVar(value=self.settings['display']['scaling'])
        scaling_scale = tk.Scale(
            section,
            from_=100,
            to=200,
            orient=tk.HORIZONTAL,
            variable=scaling_var,
            bg='#1a1a1a',
            fg='white',
            highlightthickness=0,
            length=300
        )
        scaling_scale.grid(row=1, column=1, sticky='w', pady=10)

        tk.Label(
            section,
            text="100% - 200%",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        ).grid(row=1, column=2, sticky='w', padx=10)

        # Night Light
        night_section = self.create_section(self.content_frame, "Night Light")

        night_var = tk.BooleanVar(value=self.settings['display']['night_light'])
        tk.Checkbutton(
            night_section,
            text="Enable Night Light (reduces blue light)",
            variable=night_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).grid(row=0, column=0, columnspan=3, sticky='w', pady=10)

        # Save button
        tk.Button(
            self.content_frame,
            text="💾 Apply Changes",
            command=self.save_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0
        ).pack(pady=20, padx=30, anchor='e')

    def show_sound(self):
        """Show sound settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🔊 Sound",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        # Output
        section = self.create_section(self.content_frame, "Output")

        tk.Label(
            section,
            text="Output Device:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=0, column=0, sticky='w', pady=10)

        devices = ['Built-in Audio', 'HDMI Audio', 'USB Audio', 'Bluetooth Headphones']
        device_combo = ttk.Combobox(section, values=devices, state='readonly', width=25)
        device_combo.set('Built-in Audio')
        device_combo.grid(row=0, column=1, sticky='w', pady=10)

        tk.Label(
            section,
            text="Output Volume:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=1, column=0, sticky='w', pady=10)

        volume_var = tk.IntVar(value=self.settings['sound']['output_volume'])
        volume_scale = tk.Scale(
            section,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=volume_var,
            bg='#1a1a1a',
            fg='white',
            highlightthickness=0,
            length=300
        )
        volume_scale.grid(row=1, column=1, sticky='w', pady=10)

        # Input
        input_section = self.create_section(self.content_frame, "Input")

        tk.Label(
            input_section,
            text="Input Device:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=0, column=0, sticky='w', pady=10)

        input_devices = ['Built-in Microphone', 'USB Microphone', 'Bluetooth Headset']
        input_combo = ttk.Combobox(input_section, values=input_devices, state='readonly', width=25)
        input_combo.set('Built-in Microphone')
        input_combo.grid(row=0, column=1, sticky='w', pady=10)

        # System sounds
        sounds_var = tk.BooleanVar(value=self.settings['sound']['system_sounds'])
        tk.Checkbutton(
            input_section,
            text="Play system sounds and alerts",
            variable=sounds_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).grid(row=1, column=0, columnspan=2, sticky='w', pady=10)

        # Save button
        tk.Button(
            self.content_frame,
            text="💾 Save Changes",
            command=self.save_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0
        ).pack(pady=20, padx=30, anchor='e')

    def show_power(self):
        """Show power settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="⚡ Power Management",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        # Power profile
        section = self.create_section(self.content_frame, "Power Profile")

        profiles = [
            ("🔋 Power Saver", "Maximize battery life", "power-saver"),
            ("⚖️ Balanced", "Balance performance and battery", "balanced"),
            ("⚡ Performance", "Maximum performance", "performance")
        ]

        profile_var = tk.StringVar(value=self.settings['power']['power_profile'])

        for i, (title, desc, value) in enumerate(profiles):
            frame = tk.Frame(section, bg='#2b2b2b', bd=1, relief=tk.SOLID)
            frame.grid(row=i, column=0, sticky='ew', pady=5)

            tk.Radiobutton(
                frame,
                text=title,
                variable=profile_var,
                value=value,
                font=('Arial', 11, 'bold'),
                bg='#2b2b2b',
                fg='white',
                selectcolor='#1a1a1a'
            ).pack(anchor='w', padx=10, pady=5)

            tk.Label(
                frame,
                text=desc,
                font=('Arial', 9),
                bg='#2b2b2b',
                fg='#888888'
            ).pack(anchor='w', padx=30)

        # Timeouts
        timeout_section = self.create_section(self.content_frame, "Screen & Sleep")

        tk.Label(
            timeout_section,
            text="Turn off screen after:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=0, column=0, sticky='w', pady=10)

        screen_timeout = ttk.Combobox(
            timeout_section,
            values=['Never', '5 minutes', '10 minutes', '15 minutes', '30 minutes'],
            state='readonly',
            width=15
        )
        screen_timeout.set('10 minutes')
        screen_timeout.grid(row=0, column=1, sticky='w', pady=10)

        tk.Label(
            timeout_section,
            text="Sleep after:",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=1, column=0, sticky='w', pady=10)

        sleep_timeout = ttk.Combobox(
            timeout_section,
            values=['Never', '15 minutes', '30 minutes', '1 hour', '2 hours'],
            state='readonly',
            width=15
        )
        sleep_timeout.set('30 minutes')
        sleep_timeout.grid(row=1, column=1, sticky='w', pady=10)

        # Save button
        tk.Button(
            self.content_frame,
            text="💾 Save Changes",
            command=self.save_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0
        ).pack(pady=20, padx=30, anchor='e')

    def show_privacy(self):
        """Show privacy settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🔒 Privacy & Security",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        section = self.create_section(self.content_frame, "Privacy Settings")

        privacy_options = [
            ("location_services", "Location Services", "Allow apps to access your location"),
            ("telemetry", "Usage Analytics", "Send anonymous usage data to improve TL Linux"),
            ("crash_reports", "Crash Reports", "Automatically send crash reports")
        ]

        for i, (key, title, desc) in enumerate(privacy_options):
            var = tk.BooleanVar(value=self.settings['privacy'].get(key, False))

            tk.Checkbutton(
                section,
                text=title,
                variable=var,
                font=('Arial', 11, 'bold'),
                bg='#1a1a1a',
                fg='white',
                selectcolor='#2b2b2b'
            ).grid(row=i*2, column=0, sticky='w', pady=(10, 0))

            tk.Label(
                section,
                text=desc,
                font=('Arial', 9),
                bg='#1a1a1a',
                fg='#888888'
            ).grid(row=i*2+1, column=0, sticky='w', padx=30, pady=(0, 10))

        # Save button
        tk.Button(
            self.content_frame,
            text="💾 Save Changes",
            command=self.save_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0
        ).pack(pady=20, padx=30, anchor='e')

    def show_keyboard(self):
        """Show keyboard settings"""
        self.clear_content()
        self.show_placeholder("⌨️ Keyboard Settings")

    def show_mouse(self):
        """Show mouse settings"""
        self.clear_content()
        self.show_placeholder("🖱️ Mouse & Touchpad Settings")

    def show_network(self):
        """Show network settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🌐 Network Settings",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        tk.Label(
            self.content_frame,
            text="Use the Network Manager for detailed network configuration",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(pady=10, padx=30, anchor='w')

        tk.Button(
            self.content_frame,
            text="🌐 Open Network Manager",
            command=self.open_network_manager,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=15,
            bd=0
        ).pack(pady=20, padx=30, anchor='w')

    def show_users(self):
        """Show users and accounts"""
        self.clear_content()
        self.show_placeholder("👤 Users & Accounts")

    def show_datetime(self):
        """Show date and time settings"""
        self.clear_content()
        self.show_placeholder("📅 Date & Time Settings")

    def show_language(self):
        """Show language and region"""
        self.clear_content()
        self.show_placeholder("🌍 Language & Region")

    def show_accessibility(self):
        """Show accessibility settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="♿ Accessibility",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        tk.Label(
            self.content_frame,
            text="Use the Accessibility Hub for comprehensive accessibility features",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(pady=10, padx=30, anchor='w')

        tk.Button(
            self.content_frame,
            text="♿ Open Accessibility Hub",
            command=self.open_accessibility_hub,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=15,
            bd=0
        ).pack(pady=20, padx=30, anchor='w')

    def show_applications(self):
        """Show applications settings"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="📦 Applications",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        tk.Label(
            self.content_frame,
            text="Manage installed applications and default programs",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(pady=10, padx=30, anchor='w')

        tk.Button(
            self.content_frame,
            text="📦 Open App Store",
            command=self.open_app_store,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=15,
            bd=0
        ).pack(pady=20, padx=30, anchor='w')

    def show_about(self):
        """Show about system"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="ℹ️ About TL Linux",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        about_text = """
TL Linux - Time Lord Linux
Version 1.0.0

A comprehensive personal computing solution designed for
accessibility, sustainability, and user empowerment.

Features:
• AI-powered personalization and learning
• Complete accessibility suite
• Automatic maintenance and updates
• ADHD/Autism support tools
• Decentralized IPFS storage
• Planned stability architecture

Powered by: Ubuntu, Python 3, Machine Learning
License: Open Source

© 2025 TL Linux Project
"""

        tk.Label(
            self.content_frame,
            text=about_text,
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#cccccc',
            justify=tk.LEFT
        ).pack(pady=20, padx=50, anchor='w')

    def show_placeholder(self, title):
        """Show placeholder for unimplemented sections"""
        tk.Label(
            self.content_frame,
            text=title,
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=30, padx=30, anchor='w')

        tk.Label(
            self.content_frame,
            text="This settings panel will be implemented soon.",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(pady=20, padx=30)

    def choose_accent_color(self):
        """Open color chooser for accent color"""
        color = colorchooser.askcolor(
            title="Choose Accent Color",
            initialcolor=self.settings['appearance']['accent_color']
        )
        if color[1]:
            self.settings['appearance']['accent_color'] = color[1]

    def open_network_manager(self):
        """Launch network manager"""
        try:
            subprocess.Popen(['python3', os.path.expanduser('~/tl-linux/apps/network_manager.py')])
        except:
            messagebox.showerror("Error", "Could not open Network Manager")

    def open_accessibility_hub(self):
        """Launch accessibility hub"""
        try:
            subprocess.Popen(['python3', os.path.expanduser('~/tl-linux/apps/accessibility_hub.py')])
        except:
            messagebox.showerror("Error", "Could not open Accessibility Hub")

    def open_app_store(self):
        """Launch app store"""
        try:
            subprocess.Popen(['python3', os.path.expanduser('~/tl-linux/apps/app_store.py')])
        except:
            messagebox.showerror("Error", "Could not open App Store")

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = SystemSettings()
    app.run()

if __name__ == '__main__':
    main()
