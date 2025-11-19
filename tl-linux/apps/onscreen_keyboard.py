#!/usr/bin/env python3
"""
TL Linux - On-Screen Keyboard
Accessible virtual keyboard with word prediction and multiple layouts
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import json
import os

class OnScreenKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - On-Screen Keyboard")
        self.root.configure(bg='#2b2b2b')
        self.root.attributes('-topmost', True)

        # Settings
        self.config_file = os.path.expanduser('~/.tl-linux/osk_config.json')
        self.config = self.load_config()

        # State
        self.shift_pressed = False
        self.caps_lock = False
        self.current_layout = 'letters'  # letters, numbers, symbols

        # Key size
        self.key_width = self.config.get('key_width', 60)
        self.key_height = self.config.get('key_height', 50)
        self.font_size = self.config.get('font_size', 14)

        # Word prediction
        self.prediction_enabled = self.config.get('prediction_enabled', False)
        self.current_word = ""

        self.setup_ui()

        # Prevent keyboard from taking focus
        self.root.focus_force()

    def load_config(self):
        """Load configuration"""
        default_config = {
            'key_width': 60,
            'key_height': 50,
            'font_size': 14,
            'click_sound': True,
            'hover_time': 0,  # milliseconds, 0 = disabled
            'prediction_enabled': False,
            'stay_on_top': True
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
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Title bar
        titlebar = tk.Frame(self.root, bg='#1a1a1a', height=30)
        titlebar.pack(fill=tk.X)
        titlebar.pack_propagate(False)

        tk.Label(
            titlebar,
            text="⌨️ Keyboard",
            font=('Arial', 10, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=10)

        # Layout switcher
        tk.Button(
            titlebar,
            text="ABC",
            command=lambda: self.switch_layout('letters'),
            font=('Arial', 8),
            bg='#3a3a3a',
            fg='white',
            bd=0,
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT, padx=2)

        tk.Button(
            titlebar,
            text="123",
            command=lambda: self.switch_layout('numbers'),
            font=('Arial', 8),
            bg='#3a3a3a',
            fg='white',
            bd=0,
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT, padx=2)

        tk.Button(
            titlebar,
            text="#+=",
            command=lambda: self.switch_layout('symbols'),
            font=('Arial', 8),
            bg='#3a3a3a',
            fg='white',
            bd=0,
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT, padx=2)

        # Close button
        tk.Button(
            titlebar,
            text="✕",
            command=self.root.quit,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888',
            bd=0,
            padx=8
        ).pack(side=tk.RIGHT, padx=5)

        # Word prediction bar (if enabled)
        if self.prediction_enabled:
            self.prediction_frame = tk.Frame(self.root, bg='#2b2b2b')
            self.prediction_frame.pack(fill=tk.X, padx=5, pady=5)

            self.prediction_buttons = []
            for i in range(3):
                btn = tk.Button(
                    self.prediction_frame,
                    text="",
                    command=lambda i=i: self.insert_prediction(i),
                    font=('Arial', 10),
                    bg='#3a3a3a',
                    fg='white',
                    bd=0,
                    padx=15,
                    pady=5
                )
                btn.pack(side=tk.LEFT, padx=5)
                self.prediction_buttons.append(btn)

        # Keyboard container
        self.keyboard_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.keyboard_frame.pack(padx=5, pady=5)

        # Build keyboard
        self.build_keyboard()

    def build_keyboard(self):
        """Build the keyboard layout"""
        # Clear existing
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        if self.current_layout == 'letters':
            self.build_letters_layout()
        elif self.current_layout == 'numbers':
            self.build_numbers_layout()
        elif self.current_layout == 'symbols':
            self.build_symbols_layout()

    def build_letters_layout(self):
        """Build QWERTY letter layout"""
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'Backspace'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '?'],
            ['Ctrl', 'Alt', 'Space', 'Left', 'Right', 'Up', 'Down']
        ]

        for row_idx, row in enumerate(rows):
            row_frame = tk.Frame(self.keyboard_frame, bg='#2b2b2b')
            row_frame.pack()

            for key in row:
                self.create_key(row_frame, key)

    def build_numbers_layout(self):
        """Build numbers layout"""
        rows = [
            ['1', '2', '3', 'Backspace'],
            ['4', '5', '6', '+'],
            ['7', '8', '9', '-'],
            ['0', '.', '=', 'Enter']
        ]

        for row in rows:
            row_frame = tk.Frame(self.keyboard_frame, bg='#2b2b2b')
            row_frame.pack()

            for key in row:
                width = self.key_width * 2 if key in ['Backspace', 'Enter'] else self.key_width
                self.create_key(row_frame, key, width=width)

    def build_symbols_layout(self):
        """Build symbols layout"""
        rows = [
            ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')'],
            ['[', ']', '{', '}', '\\', '|', ';', ':', "'", '"'],
            ['<', '>', '/', '?', '~', '`', '_', '+', '=', '-'],
            ['Backspace', 'Space', 'Enter']
        ]

        for row in rows:
            row_frame = tk.Frame(self.keyboard_frame, bg='#2b2b2b')
            row_frame.pack()

            for key in row:
                width = self.key_width * 3 if key in ['Backspace', 'Space', 'Enter'] else self.key_width
                self.create_key(row_frame, key, width=width)

    def create_key(self, parent, label, width=None):
        """Create a keyboard key button"""
        if width is None:
            width = self.key_width

        # Special key widths
        if label == 'Space':
            width = self.key_width * 6
        elif label in ['Backspace', 'Enter', 'Shift']:
            width = self.key_width * 1.5
        elif label in ['Ctrl', 'Alt']:
            width = self.key_width * 1.2

        # Display text
        display_text = label
        if label == 'Space':
            display_text = '␣ Space'
        elif label == 'Backspace':
            display_text = '⌫'
        elif label == 'Enter':
            display_text = '↵'
        elif label == 'Shift':
            display_text = '⇧'
        elif label == 'Up':
            display_text = '↑'
        elif label == 'Down':
            display_text = '↓'
        elif label == 'Left':
            display_text = '←'
        elif label == 'Right':
            display_text = '→'

        # Apply shift/caps
        if self.current_layout == 'letters':
            if len(label) == 1 and label.isalpha():
                if self.shift_pressed or self.caps_lock:
                    display_text = label.upper()
                else:
                    display_text = label.lower()

        btn = tk.Button(
            parent,
            text=display_text,
            command=lambda: self.key_pressed(label),
            font=('Arial', self.font_size, 'bold'),
            bg='#3a3a3a',
            fg='white',
            activebackground='#4a9eff',
            activeforeground='white',
            bd=1,
            relief=tk.RAISED
        )

        btn.pack(side=tk.LEFT, padx=2, pady=2, ipadx=width//4, ipady=self.key_height//4)

        # Highlight special keys
        if label in ['Shift', 'Ctrl', 'Alt']:
            btn.config(bg='#4a4a4a')
        elif label in ['Enter', 'Backspace']:
            btn.config(bg='#4a9eff')
        elif label == 'Space':
            btn.config(bg='#2a2a2a')

    def key_pressed(self, key):
        """Handle key press"""
        # Play click sound if enabled
        if self.config.get('click_sound'):
            self.play_click()

        # Handle special keys
        if key == 'Shift':
            self.shift_pressed = not self.shift_pressed
            if not self.caps_lock:
                self.build_keyboard()
            return
        elif key == 'Caps':
            self.caps_lock = not self.caps_lock
            self.build_keyboard()
            return
        elif key == 'Ctrl':
            # Would handle Ctrl modifier
            return
        elif key == 'Alt':
            # Would handle Alt modifier
            return

        # Type the key using xdotool
        self.type_key(key)

        # Reset shift if not caps lock
        if self.shift_pressed and not self.caps_lock:
            self.shift_pressed = False
            self.build_keyboard()

    def type_key(self, key):
        """Type a key using xdotool"""
        try:
            # Map special keys
            key_map = {
                'Space': 'space',
                'Backspace': 'BackSpace',
                'Enter': 'Return',
                'Up': 'Up',
                'Down': 'Down',
                'Left': 'Left',
                'Right': 'Right',
                'Tab': 'Tab',
                'Esc': 'Escape'
            }

            xdo_key = key_map.get(key, key)

            # Apply shift for uppercase
            if len(key) == 1 and key.isalpha():
                if self.shift_pressed or self.caps_lock:
                    xdo_key = key.upper()
                else:
                    xdo_key = key.lower()

            # Type using xdotool
            subprocess.run(['xdotool', 'key', xdo_key], stderr=subprocess.DEVNULL)

            # Update word prediction
            if self.prediction_enabled:
                if key == 'Space':
                    self.current_word = ""
                    self.update_predictions()
                elif key == 'Backspace':
                    if self.current_word:
                        self.current_word = self.current_word[:-1]
                        self.update_predictions()
                elif len(key) == 1 and key.isalpha():
                    self.current_word += key.lower()
                    self.update_predictions()

        except FileNotFoundError:
            # xdotool not installed
            print(f"Key press: {key}")
        except Exception as e:
            print(f"Error typing key: {e}")

    def switch_layout(self, layout):
        """Switch keyboard layout"""
        self.current_layout = layout
        self.build_keyboard()

    def play_click(self):
        """Play click sound"""
        try:
            subprocess.Popen(
                ['paplay', '/usr/share/sounds/freedesktop/stereo/button-pressed.oga'],
                stderr=subprocess.DEVNULL
            )
        except:
            pass

    def update_predictions(self):
        """Update word predictions"""
        # Simple prediction - would use actual dictionary
        predictions = self.get_predictions(self.current_word)

        for i, btn in enumerate(self.prediction_buttons):
            if i < len(predictions):
                btn.config(text=predictions[i])
                btn.pack()
            else:
                btn.pack_forget()

    def get_predictions(self, prefix):
        """Get word predictions (simple implementation)"""
        if not prefix:
            return []

        # Common words starting with prefix
        words = ['the', 'that', 'this', 'then', 'there', 'their', 'they',
                 'and', 'are', 'also', 'about', 'after', 'all',
                 'was', 'with', 'will', 'would', 'what', 'when', 'where',
                 'can', 'could', 'come', 'call',
                 'for', 'from', 'first', 'find',
                 'have', 'has', 'had', 'how', 'her', 'him', 'his',
                 'you', 'your', 'yes']

        matches = [w for w in words if w.startswith(prefix.lower())]
        return matches[:3]

    def insert_prediction(self, index):
        """Insert predicted word"""
        if index < len(self.prediction_buttons):
            word = self.prediction_buttons[index]['text']
            if word:
                # Clear current word
                for _ in range(len(self.current_word)):
                    self.type_key('Backspace')

                # Type predicted word
                for char in word:
                    subprocess.run(['xdotool', 'key', char])

                self.type_key('Space')
                self.current_word = ""
                self.update_predictions()

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = OnScreenKeyboard()
    app.run()

if __name__ == '__main__':
    main()
