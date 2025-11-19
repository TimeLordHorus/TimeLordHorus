#!/usr/bin/env python3
"""
TL Linux - Accessibility Themes Manager
High contrast themes, color filters, and visual accessibility settings
"""

import tkinter as tk
from tkinter import ttk, colorchooser
import json
import os

class AccessibilityThemesManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Accessibility Themes")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')

        self.config_dir = os.path.expanduser('~/.tl-linux/accessibility')
        self.config_file = os.path.join(self.config_dir, 'theme_config.json')

        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

        self.setup_ui()

    def load_config(self):
        """Load accessibility theme configuration"""
        default_config = {
            'current_theme': 'default',
            'high_contrast_enabled': False,
            'color_filter': 'none',  # none, protanopia, deuteranopia, tritanopia, grayscale, invert
            'text_size_multiplier': 1.0,
            'cursor_size': 'normal',  # small, normal, large, extra-large
            'cursor_color': '#ffffff',
            'focus_highlight_enabled': True,
            'focus_highlight_color': '#ff0000',
            'reduce_motion': False,
            'reduce_transparency': False
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except:
            pass

        return default_config

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="♿ Accessibility Themes",
            font=('Arial', 20, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=20)

        # Content
        content = tk.Frame(self.root, bg='#2b2b2b')
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # High Contrast Themes
        self.create_high_contrast_section(content)

        # Color Filters
        self.create_color_filter_section(content)

        # Text Settings
        self.create_text_settings_section(content)

        # Cursor Settings
        self.create_cursor_settings_section(content)

        # Other Visual Settings
        self.create_other_settings_section(content)

        # Preview
        self.create_preview_section(content)

        # Save button
        tk.Button(
            self.root,
            text="💾 Apply Changes",
            command=self.apply_changes,
            font=('Arial', 13, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=40,
            pady=12,
            bd=0
        ).pack(pady=20)

    def create_high_contrast_section(self, parent):
        """Create high contrast themes section"""
        section = tk.LabelFrame(
            parent,
            text="High Contrast Themes",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            bd=2,
            relief=tk.GROOVE
        )
        section.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(section, bg='#2b2b2b')
        inner.pack(fill=tk.X, padx=15, pady=15)

        # Theme buttons
        themes = [
            ("Default", "default", {'bg': '#2b2b2b', 'fg': '#ffffff'}),
            ("High Contrast Black", "hc_black", {'bg': '#000000', 'fg': '#ffffff'}),
            ("High Contrast White", "hc_white", {'bg': '#ffffff', 'fg': '#000000'}),
            ("High Contrast #1", "hc_1", {'bg': '#000000', 'fg': '#ffff00'}),
            ("High Contrast #2", "hc_2", {'bg': '#000000', 'fg': '#00ff00'})
        ]

        self.theme_var = tk.StringVar(value=self.config.get('current_theme', 'default'))

        for i, (name, value, colors) in enumerate(themes):
            row = i // 2
            col = i % 2

            frame = tk.Frame(inner, bg=colors['bg'], bd=2, relief=tk.RAISED)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')

            tk.Radiobutton(
                frame,
                text=name,
                variable=self.theme_var,
                value=value,
                font=('Arial', 11),
                bg=colors['bg'],
                fg=colors['fg'],
                selectcolor=colors['bg'],
                activebackground=colors['bg'],
                activeforeground=colors['fg']
            ).pack(pady=10, padx=20)

        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

    def create_color_filter_section(self, parent):
        """Create color filter section"""
        section = tk.LabelFrame(
            parent,
            text="Color Filters (Color Blindness Support)",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            bd=2,
            relief=tk.GROOVE
        )
        section.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(section, bg='#2b2b2b')
        inner.pack(fill=tk.X, padx=15, pady=15)

        tk.Label(
            inner,
            text="Apply color filter to entire screen:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(anchor='w', pady=(0, 10))

        filters = [
            ("None (Normal Vision)", "none"),
            ("Protanopia (Red-Blind)", "protanopia"),
            ("Deuteranopia (Green-Blind)", "deuteranopia"),
            ("Tritanopia (Blue-Blind)", "tritanopia"),
            ("Grayscale", "grayscale"),
            ("Inverted Colors", "invert")
        ]

        self.filter_var = tk.StringVar(value=self.config.get('color_filter', 'none'))

        for name, value in filters:
            tk.Radiobutton(
                inner,
                text=name,
                variable=self.filter_var,
                value=value,
                font=('Arial', 10),
                bg='#2b2b2b',
                fg='#cccccc',
                selectcolor='#1a1a1a',
                activebackground='#2b2b2b'
            ).pack(anchor='w', pady=2)

    def create_text_settings_section(self, parent):
        """Create text settings section"""
        section = tk.LabelFrame(
            parent,
            text="Text Settings",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            bd=2,
            relief=tk.GROOVE
        )
        section.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(section, bg='#2b2b2b')
        inner.pack(fill=tk.X, padx=15, pady=15)

        tk.Label(
            inner,
            text="Text Size Multiplier:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc'
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.text_size_var = tk.DoubleVar(value=self.config.get('text_size_multiplier', 1.0))

        text_scale = tk.Scale(
            inner,
            from_=0.8,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.text_size_var,
            bg='#2b2b2b',
            fg='white',
            highlightthickness=0,
            length=300
        )
        text_scale.grid(row=0, column=1, padx=10, pady=5)

        self.text_size_label = tk.Label(
            inner,
            text="1.0x",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white'
        )
        self.text_size_label.grid(row=0, column=2, padx=5)

        text_scale.config(command=lambda v: self.text_size_label.config(text=f"{float(v):.1f}x"))

    def create_cursor_settings_section(self, parent):
        """Create cursor settings section"""
        section = tk.LabelFrame(
            parent,
            text="Cursor Settings",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            bd=2,
            relief=tk.GROOVE
        )
        section.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(section, bg='#2b2b2b')
        inner.pack(fill=tk.X, padx=15, pady=15)

        # Cursor size
        tk.Label(
            inner,
            text="Cursor Size:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc'
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.cursor_size_var = tk.StringVar(value=self.config.get('cursor_size', 'normal'))

        cursor_sizes = [("Small", "small"), ("Normal", "normal"), ("Large", "large"), ("Extra Large", "extra-large")]

        cursor_frame = tk.Frame(inner, bg='#2b2b2b')
        cursor_frame.grid(row=0, column=1, sticky='w', padx=10)

        for text, value in cursor_sizes:
            tk.Radiobutton(
                cursor_frame,
                text=text,
                variable=self.cursor_size_var,
                value=value,
                font=('Arial', 9),
                bg='#2b2b2b',
                fg='#cccccc',
                selectcolor='#1a1a1a'
            ).pack(side=tk.LEFT, padx=5)

        # Cursor color
        tk.Label(
            inner,
            text="Cursor Color:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc'
        ).grid(row=1, column=0, sticky='w', pady=10)

        self.cursor_color_btn = tk.Button(
            inner,
            text="Choose Color",
            command=self.choose_cursor_color,
            font=('Arial', 9),
            bg=self.config.get('cursor_color', '#ffffff'),
            fg='#000000',
            padx=15,
            pady=5
        )
        self.cursor_color_btn.grid(row=1, column=1, sticky='w', padx=10)

    def create_other_settings_section(self, parent):
        """Create other visual settings section"""
        section = tk.LabelFrame(
            parent,
            text="Other Visual Settings",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            bd=2,
            relief=tk.GROOVE
        )
        section.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(section, bg='#2b2b2b')
        inner.pack(fill=tk.X, padx=15, pady=15)

        # Focus highlight
        self.focus_highlight_var = tk.BooleanVar(value=self.config.get('focus_highlight_enabled', True))
        tk.Checkbutton(
            inner,
            text="Enhanced Focus Highlighting (helps track where you are)",
            variable=self.focus_highlight_var,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            selectcolor='#1a1a1a'
        ).pack(anchor='w', pady=5)

        # Reduce motion
        self.reduce_motion_var = tk.BooleanVar(value=self.config.get('reduce_motion', False))
        tk.Checkbutton(
            inner,
            text="Reduce Motion (disable animations for vestibular disorders)",
            variable=self.reduce_motion_var,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            selectcolor='#1a1a1a'
        ).pack(anchor='w', pady=5)

        # Reduce transparency
        self.reduce_transparency_var = tk.BooleanVar(value=self.config.get('reduce_transparency', False))
        tk.Checkbutton(
            inner,
            text="Reduce Transparency (improve contrast and readability)",
            variable=self.reduce_transparency_var,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            selectcolor='#1a1a1a'
        ).pack(anchor='w', pady=5)

    def create_preview_section(self, parent):
        """Create preview section"""
        section = tk.LabelFrame(
            parent,
            text="Preview",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            bd=2,
            relief=tk.GROOVE
        )
        section.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(section, bg='#2b2b2b')
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.preview_frame = tk.Frame(inner, bg='#2b2b2b', height=100)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        self.preview_frame.pack_propagate(False)

        tk.Label(
            self.preview_frame,
            text="Sample Text",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=10)

        tk.Label(
            self.preview_frame,
            text="This is how text will appear with your accessibility settings.",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#cccccc',
            wraplength=700
        ).pack(pady=5)

        tk.Button(
            self.preview_frame,
            text="Sample Button",
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8
        ).pack(pady=10)

    def choose_cursor_color(self):
        """Choose cursor color"""
        color = colorchooser.askcolor(
            title="Choose Cursor Color",
            initialcolor=self.config.get('cursor_color', '#ffffff')
        )

        if color[1]:
            self.config['cursor_color'] = color[1]
            self.cursor_color_btn.config(bg=color[1])

    def apply_changes(self):
        """Apply theme changes"""
        # Save config
        self.config['current_theme'] = self.theme_var.get()
        self.config['color_filter'] = self.filter_var.get()
        self.config['text_size_multiplier'] = self.text_size_var.get()
        self.config['cursor_size'] = self.cursor_size_var.get()
        self.config['focus_highlight_enabled'] = self.focus_highlight_var.get()
        self.config['reduce_motion'] = self.reduce_motion_var.get()
        self.config['reduce_transparency'] = self.reduce_transparency_var.get()

        self.save_config()

        # Apply theme (would integrate with system theme in production)
        self.apply_theme()

        from tkinter import messagebox
        messagebox.showinfo(
            "Settings Applied",
            "Accessibility theme settings have been applied!\n\nSome changes may require logging out and back in to take full effect."
        )

    def apply_theme(self):
        """Apply selected theme to system"""
        theme = self.config['current_theme']

        print(f"Applying theme: {theme}")
        print(f"Color filter: {self.config['color_filter']}")
        print(f"Text size: {self.config['text_size_multiplier']}x")
        print(f"Cursor size: {self.config['cursor_size']}")

        # In production, would:
        # 1. Update GTK theme
        # 2. Update Qt theme
        # 3. Update X11 resources
        # 4. Apply color filters via compositor
        # 5. Adjust cursor theme and size
        # 6. Update system-wide font scaling

    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    app = AccessibilityThemesManager()
    app.run()

if __name__ == '__main__':
    main()
