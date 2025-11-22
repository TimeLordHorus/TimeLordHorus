#!/usr/bin/env python3
"""
TL Linux Unified Settings Manager
Central configuration management for all TL Linux components

Provides a single interface to manage:
- OS Hub settings
- Wellbeing preferences
- Security configuration
- Theme settings
- Auto-start options
- Cloud sync
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

class UnifiedSettingsManager:
    """Unified settings manager for TL Linux"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Linux Settings ⚙️")
            self.root.geometry("900x700")
        else:
            self.root = root

        self.root.configure(bg='#0d1117')

        # Configuration directory
        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load all configurations
        self.load_all_configs()

        # Setup UI
        self.setup_ui()

    def load_all_configs(self):
        """Load all configuration files"""
        self.configs = {}

        # OS Hub config
        self.configs['os_hub'] = self.load_config('os_hub_config.json', {
            'wellbeing_enabled': True,
            'theme': 'default'
        })

        # Wellbeing config
        self.configs['wellbeing'] = self.load_config('wellbeing/wellbeing_config.json', {
            'break_interval': 30,
            'eye_care_enabled': True,
            'hydration_enabled': True,
            'posture_enabled': True
        })

        # Auto-start config
        self.configs['autostart'] = self.load_config('autostart_config.json', {
            'enabled': True,
            'start_wellbeing_monitor': True,
            'start_gamification': False
        })

        # Theme config
        self.configs['theme'] = self.load_config('ml_theme_data.json', {
            'current_theme': 'retro'
        })

    def load_config(self, relative_path, defaults):
        """Load a configuration file"""
        config_file = self.config_dir / relative_path
        config_file.parent.mkdir(parents=True, exist_ok=True)

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in defaults.items():
                        if key not in config:
                            config[key] = value
                    return config
            except:
                return defaults.copy()
        return defaults.copy()

    def save_config(self, config_name, relative_path):
        """Save a configuration file"""
        config_file = self.config_dir / relative_path
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(self.configs[config_name], f, indent=2)

    def setup_ui(self):
        """Setup the UI"""
        # Header
        header = tk.Frame(self.root, bg='#161b22', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙️ TL Linux Settings",
            font=('Arial', 28, 'bold'),
            bg='#161b22',
            fg='#58a6ff'
        ).pack(pady=20)

        # Tabs
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.configure('TNotebook', background='#0d1117')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))

        # Create tabs
        self.general_tab = tk.Frame(tab_container, bg='#0d1117')
        self.wellbeing_tab = tk.Frame(tab_container, bg='#0d1117')
        self.startup_tab = tk.Frame(tab_container, bg='#0d1117')
        self.appearance_tab = tk.Frame(tab_container, bg='#0d1117')

        tab_container.add(self.general_tab, text='🏠 General')
        tab_container.add(self.wellbeing_tab, text='🧘 Wellbeing')
        tab_container.add(self.startup_tab, text='🚀 Startup')
        tab_container.add(self.appearance_tab, text='🎨 Appearance')

        # Setup tabs
        self.setup_general_tab()
        self.setup_wellbeing_tab()
        self.setup_startup_tab()
        self.setup_appearance_tab()

        # Save button at bottom
        save_frame = tk.Frame(self.root, bg='#0d1117')
        save_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(
            save_frame,
            text="💾 Save All Settings",
            font=('Arial', 14, 'bold'),
            bg='#238636',
            fg='white',
            command=self.save_all_settings,
            padx=30,
            pady=12
        ).pack(side=tk.RIGHT)

        tk.Button(
            save_frame,
            text="↺ Reset to Defaults",
            font=('Arial', 12),
            bg='#6c757d',
            fg='white',
            command=self.reset_to_defaults,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT, padx=10)

    def setup_general_tab(self):
        """Setup general settings"""
        container = tk.Frame(self.general_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # OS Hub Settings
        os_hub_frame = tk.LabelFrame(
            container,
            text="OS Hub Settings",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        os_hub_frame.pack(fill=tk.X, pady=10)

        self.wellbeing_enabled_var = tk.BooleanVar(value=self.configs['os_hub']['wellbeing_enabled'])
        tk.Checkbutton(
            os_hub_frame,
            text="Enable wellbeing features",
            variable=self.wellbeing_enabled_var,
            font=('Arial', 11),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

        # System Info
        info_frame = tk.LabelFrame(
            container,
            text="System Information",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        info_frame.pack(fill=tk.X, pady=10)

        info_text = f"""
TL Linux - Portable OS Hub
Version: 1.0.0
Configuration: {self.config_dir}

Total Settings Files: {len(self.configs)}
        """

        tk.Label(
            info_frame,
            text=info_text,
            font=('Courier', 10),
            bg='#0d1117',
            fg='#8b949e',
            justify=tk.LEFT
        ).pack(anchor=tk.W)

    def setup_wellbeing_tab(self):
        """Setup wellbeing settings"""
        container = tk.Frame(self.wellbeing_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Break Settings
        breaks_frame = tk.LabelFrame(
            container,
            text="Break Reminders",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        breaks_frame.pack(fill=tk.X, pady=10)

        interval_frame = tk.Frame(breaks_frame, bg='#0d1117')
        interval_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            interval_frame,
            text="Break interval (minutes):",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(side=tk.LEFT)

        self.break_interval_var = tk.IntVar(value=self.configs['wellbeing']['break_interval'])
        tk.Spinbox(
            interval_frame,
            from_=5,
            to=120,
            textvariable=self.break_interval_var,
            font=('Arial', 11),
            width=10
        ).pack(side=tk.LEFT, padx=10)

        # Features
        features_frame = tk.LabelFrame(
            container,
            text="Wellbeing Features",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        features_frame.pack(fill=tk.X, pady=10)

        self.eye_care_var = tk.BooleanVar(value=self.configs['wellbeing']['eye_care_enabled'])
        tk.Checkbutton(
            features_frame,
            text="Eye care reminders (20-20-20 rule)",
            variable=self.eye_care_var,
            font=('Arial', 11),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

        self.hydration_var = tk.BooleanVar(value=self.configs['wellbeing']['hydration_enabled'])
        tk.Checkbutton(
            features_frame,
            text="Hydration reminders",
            variable=self.hydration_var,
            font=('Arial', 11),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

        self.posture_var = tk.BooleanVar(value=self.configs['wellbeing']['posture_enabled'])
        tk.Checkbutton(
            features_frame,
            text="Posture alerts",
            variable=self.posture_var,
            font=('Arial', 11),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

    def setup_startup_tab(self):
        """Setup startup settings"""
        container = tk.Frame(self.startup_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Auto-start Settings
        autostart_frame = tk.LabelFrame(
            container,
            text="Auto-Start Configuration",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        autostart_frame.pack(fill=tk.X, pady=10)

        self.autostart_enabled_var = tk.BooleanVar(value=self.configs['autostart']['enabled'])
        tk.Checkbutton(
            autostart_frame,
            text="Enable auto-start of TL Linux services",
            variable=self.autostart_enabled_var,
            font=('Arial', 11, 'bold'),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

        tk.Label(
            autostart_frame,
            text="Services to start automatically:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='#8b949e'
        ).pack(anchor=tk.W, pady=(10, 5))

        self.start_wellbeing_var = tk.BooleanVar(value=self.configs['autostart']['start_wellbeing_monitor'])
        tk.Checkbutton(
            autostart_frame,
            text="  Wellbeing Monitor (recommended)",
            variable=self.start_wellbeing_var,
            font=('Arial', 10),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=2, padx=20)

        self.start_gamification_var = tk.BooleanVar(value=self.configs['autostart']['start_gamification'])
        tk.Checkbutton(
            autostart_frame,
            text="  Gamification System",
            variable=self.start_gamification_var,
            font=('Arial', 10),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=2, padx=20)

        # Instructions
        tk.Label(
            autostart_frame,
            text="\nNote: Services run in background and use minimal resources.",
            font=('Arial', 9, 'italic'),
            bg='#0d1117',
            fg='#8b949e'
        ).pack(anchor=tk.W, pady=5)

    def setup_appearance_tab(self):
        """Setup appearance settings"""
        container = tk.Frame(self.appearance_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Theme Selection
        theme_frame = tk.LabelFrame(
            container,
            text="Theme Selection",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        theme_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            theme_frame,
            text="Choose your preferred theme:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(anchor=tk.W, pady=5)

        self.theme_var = tk.StringVar(value=self.configs['theme'].get('current_theme', 'retro'))

        themes = [
            ('Retro', 'retro', 'Classic green-on-black terminal aesthetic'),
            ('Neon', 'neon', 'Cyberpunk hot pink and cyan'),
            ('Lightning', 'lightning', 'High contrast yellow and white'),
            ('Splash', 'splash', 'Modern light theme with gradients')
        ]

        for name, value, desc in themes:
            frame = tk.Frame(theme_frame, bg='#0d1117')
            frame.pack(fill=tk.X, pady=5)

            tk.Radiobutton(
                frame,
                text=name,
                variable=self.theme_var,
                value=value,
                font=('Arial', 11, 'bold'),
                bg='#0d1117',
                fg='white',
                selectcolor='#161b22'
            ).pack(side=tk.LEFT)

            tk.Label(
                frame,
                text=f"- {desc}",
                font=('Arial', 9),
                bg='#0d1117',
                fg='#8b949e'
            ).pack(side=tk.LEFT, padx=10)

    def save_all_settings(self):
        """Save all settings"""
        try:
            # Update configs from UI
            self.configs['os_hub']['wellbeing_enabled'] = self.wellbeing_enabled_var.get()

            self.configs['wellbeing']['break_interval'] = self.break_interval_var.get()
            self.configs['wellbeing']['eye_care_enabled'] = self.eye_care_var.get()
            self.configs['wellbeing']['hydration_enabled'] = self.hydration_var.get()
            self.configs['wellbeing']['posture_enabled'] = self.posture_var.get()

            self.configs['autostart']['enabled'] = self.autostart_enabled_var.get()
            self.configs['autostart']['start_wellbeing_monitor'] = self.start_wellbeing_var.get()
            self.configs['autostart']['start_gamification'] = self.start_gamification_var.get()

            self.configs['theme']['current_theme'] = self.theme_var.get()

            # Save all configs
            self.save_config('os_hub', 'os_hub_config.json')
            self.save_config('wellbeing', 'wellbeing/wellbeing_config.json')
            self.save_config('autostart', 'autostart_config.json')
            self.save_config('theme', 'ml_theme_data.json')

            messagebox.showinfo("Success", "All settings saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.load_all_configs()
            # Reload UI with defaults
            self.wellbeing_enabled_var.set(self.configs['os_hub']['wellbeing_enabled'])
            self.break_interval_var.set(self.configs['wellbeing']['break_interval'])
            self.eye_care_var.set(self.configs['wellbeing']['eye_care_enabled'])
            self.hydration_var.set(self.configs['wellbeing']['hydration_enabled'])
            self.posture_var.set(self.configs['wellbeing']['posture_enabled'])
            self.autostart_enabled_var.set(self.configs['autostart']['enabled'])
            self.start_wellbeing_var.set(self.configs['autostart']['start_wellbeing_monitor'])
            self.start_gamification_var.set(self.configs['autostart']['start_gamification'])
            self.theme_var.set(self.configs['theme'].get('current_theme', 'retro'))

            messagebox.showinfo("Reset", "Settings reset to defaults!")

    def run(self):
        """Run the settings manager"""
        self.root.mainloop()


def main():
    """Main entry point"""
    manager = UnifiedSettingsManager()
    manager.run()


if __name__ == '__main__':
    main()
