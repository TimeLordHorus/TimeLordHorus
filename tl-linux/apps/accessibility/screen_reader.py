#!/usr/bin/env python3
"""
TL Linux - Screen Reader with Text-to-Speech
Accessibility tool for visually impaired users
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import threading
import subprocess
import time

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

class ScreenReader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("👁️ TL Screen Reader")
        self.root.geometry("800x600")

        self.config_file = Path.home() / '.config' / 'tl-linux' / 'screen_reader.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self.load_config()

        # TTS Engine
        self.tts_engine = None
        self.is_enabled = False
        self.is_speaking = False

        # Reading state
        self.reading_mode = 'auto'  # auto, manual, continuous
        self.current_element = None

        self.initialize_tts()
        self.setup_ui()
        self.setup_keyboard_shortcuts()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'enabled': False,
            'voice_rate': 150,
            'voice_volume': 0.9,
            'voice_pitch': 1.0,
            'voice_id': None,
            'auto_start': False,
            'read_on_focus': True,
            'read_on_hover': False,
            'read_typed_chars': False,
            'keyboard_echo': True,
            'punctuation_level': 'some',  # none, some, all
            'verbosity': 'normal'  # brief, normal, verbose
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def initialize_tts(self):
        """Initialize TTS engine"""
        if HAS_PYTTSX3:
            try:
                self.tts_engine = pyttsx3.init()

                # Set properties
                self.tts_engine.setProperty('rate', self.config.get('voice_rate', 150))
                self.tts_engine.setProperty('volume', self.config.get('voice_volume', 0.9))

                # Set voice if specified
                voice_id = self.config.get('voice_id')
                if voice_id:
                    self.tts_engine.setProperty('voice', voice_id)

            except Exception as e:
                print(f"Error initializing TTS: {e}")
                HAS_PYTTSX3 = False

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Read Clipboard", command=self.read_clipboard)
        tools_menu.add_command(label="Read Window Title", command=self.read_window_title)
        tools_menu.add_command(label="Spell Last Word", command=self.spell_last_word)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Quick Start Guide", command=self.show_guide)

        # Header
        header = tk.Frame(self.root, bg='#34495e', pady=20)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="👁️ TL Screen Reader",
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack()

        # Status indicator
        status_frame = tk.Frame(header, bg='#34495e')
        status_frame.pack(pady=(10, 0))

        tk.Label(status_frame, text="Status:", bg='#34495e', fg='white', font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        self.status_indicator = tk.Label(status_frame, text="●", font=('Arial', 16), bg='#34495e', fg='#e74c3c')
        self.status_indicator.pack(side=tk.LEFT)

        self.status_label = tk.Label(status_frame, text="Disabled", bg='#34495e', fg='white', font=('Arial', 11))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Main controls
        controls_frame = tk.Frame(self.root, bg='white', pady=20)
        controls_frame.pack(fill=tk.X)

        # Enable/Disable toggle
        self.toggle_btn = tk.Button(
            controls_frame,
            text="▶️ Enable Screen Reader",
            command=self.toggle_screen_reader,
            bg='#27ae60',
            fg='white',
            font=('Arial', 14, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=15
        )
        self.toggle_btn.pack(pady=10)

        # Quick actions
        actions_frame = tk.Frame(self.root, bg='#ecf0f1', pady=20)
        actions_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(actions_frame, text="Quick Actions", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=(0, 15))

        buttons_grid = tk.Frame(actions_frame, bg='#ecf0f1')
        buttons_grid.pack()

        actions = [
            ("📋 Read Clipboard", self.read_clipboard),
            ("🪟 Read Window", self.read_window_title),
            ("📄 Read Text Area", self.read_text_area),
            ("🔤 Spell Word", self.spell_last_word),
            ("⏸️ Stop Speaking", self.stop_speaking),
            ("⚙️ Settings", self.show_settings)
        ]

        for idx, (text, command) in enumerate(actions):
            row = idx // 2
            col = idx % 2

            tk.Button(
                buttons_grid,
                text=text,
                command=command,
                bg='#3498db',
                fg='white',
                font=('Arial', 11),
                relief=tk.FLAT,
                padx=20,
                pady=10,
                width=20
            ).grid(row=row, column=col, padx=10, pady=5)

        # Text input for testing
        test_frame = tk.Frame(self.root, bg='white', pady=10)
        test_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(test_frame, text="Test Speech:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10)

        text_input_frame = tk.Frame(test_frame, bg='white')
        text_input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.test_text = tk.Text(text_input_frame, height=5, font=('Arial', 11))
        self.test_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = tk.Scrollbar(text_input_frame, command=self.test_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.test_text.config(yscrollcommand=scrollbar.set)

        tk.Button(
            test_frame,
            text="🔊 Speak This Text",
            command=self.speak_test_text,
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(pady=5)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Screen Reader ready" + ("" if HAS_PYTTSX3 else " - Warning: pyttsx3 not installed"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Check TTS availability
        if not HAS_PYTTSX3:
            self.show_installation_guide()

    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        # Within application shortcuts
        self.root.bind('<Control-r>', lambda e: self.toggle_screen_reader())
        self.root.bind('<Control-s>', lambda e: self.stop_speaking())
        self.root.bind('<Control-c>', lambda e: self.read_clipboard())
        self.root.bind('<Control-w>', lambda e: self.read_window_title())
        self.root.bind('<Control-t>', lambda e: self.speak_test_text())

        # TODO: Set up system-wide shortcuts (requires additional libraries)

    def toggle_screen_reader(self):
        """Toggle screen reader on/off"""
        if not HAS_PYTTSX3:
            messagebox.showerror(
                "TTS Not Available",
                "pyttsx3 is required for text-to-speech.\n\n"
                "Install with: pip install pyttsx3"
            )
            return

        self.is_enabled = not self.is_enabled
        self.config['enabled'] = self.is_enabled
        self.save_config()

        if self.is_enabled:
            self.status_indicator.config(fg='#27ae60')
            self.status_label.config(text="Enabled")
            self.toggle_btn.config(text="⏸️ Disable Screen Reader", bg='#e74c3c')
            self.speak("Screen reader enabled")
        else:
            self.status_indicator.config(fg='#e74c3c')
            self.status_label.config(text="Disabled")
            self.toggle_btn.config(text="▶️ Enable Screen Reader", bg='#27ae60')
            self.speak("Screen reader disabled")

    def speak(self, text, interrupt=True):
        """Speak text using TTS"""
        if not HAS_PYTTSX3 or not self.tts_engine:
            print(f"[TTS] {text}")
            return

        def speak_thread():
            try:
                if interrupt and self.is_speaking:
                    self.tts_engine.stop()

                self.is_speaking = True
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.is_speaking = False
            except Exception as e:
                print(f"TTS error: {e}")
                self.is_speaking = False

        threading.Thread(target=speak_thread, daemon=True).start()

    def stop_speaking(self):
        """Stop current speech"""
        if HAS_PYTTSX3 and self.tts_engine:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
                self.status_bar.config(text="Speech stopped")
            except:
                pass

    def read_clipboard(self):
        """Read clipboard contents"""
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text:
                self.speak(f"Clipboard contains: {clipboard_text}")
            else:
                self.speak("Clipboard is empty")
        except:
            self.speak("Unable to read clipboard")

    def read_window_title(self):
        """Read current window title"""
        title = self.root.title()
        self.speak(f"Window title: {title}")

    def read_text_area(self):
        """Read text from test area"""
        text = self.test_text.get('1.0', 'end-1c')
        if text.strip():
            self.speak(text)
        else:
            self.speak("Text area is empty")

    def spell_last_word(self):
        """Spell the last word"""
        text = self.test_text.get('1.0', 'end-1c')
        words = text.split()

        if words:
            last_word = words[-1]
            spelled = ', '.join(list(last_word))
            self.speak(f"Spelling: {spelled}")
        else:
            self.speak("No text to spell")

    def speak_test_text(self):
        """Speak text from test area"""
        self.read_text_area()

    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Screen Reader Settings")
        settings_window.geometry("600x500")
        settings_window.transient(self.root)

        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Voice settings
        voice_frame = tk.Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(voice_frame, text="Voice")

        # Speech rate
        tk.Label(voice_frame, text="Speech Rate:", bg='white', font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=10)

        rate_frame = tk.Frame(voice_frame, bg='white')
        rate_frame.grid(row=0, column=1, sticky='ew', pady=10)

        self.rate_var = tk.IntVar(value=self.config.get('voice_rate', 150))
        rate_slider = tk.Scale(
            rate_frame,
            from_=50,
            to=300,
            orient=tk.HORIZONTAL,
            variable=self.rate_var,
            bg='white'
        )
        rate_slider.pack(fill=tk.X)

        # Volume
        tk.Label(voice_frame, text="Volume:", bg='white', font=('Arial', 11)).grid(row=1, column=0, sticky='w', pady=10)

        volume_frame = tk.Frame(voice_frame, bg='white')
        volume_frame.grid(row=1, column=1, sticky='ew', pady=10)

        self.volume_var = tk.DoubleVar(value=self.config.get('voice_volume', 0.9))
        volume_slider = tk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            bg='white'
        )
        volume_slider.pack(fill=tk.X)

        # Voice selection
        if HAS_PYTTSX3 and self.tts_engine:
            tk.Label(voice_frame, text="Voice:", bg='white', font=('Arial', 11)).grid(row=2, column=0, sticky='w', pady=10)

            voices = self.tts_engine.getProperty('voices')
            voice_names = [v.name for v in voices]

            current_voice = self.config.get('voice_id')
            current_index = 0
            if current_voice:
                for idx, v in enumerate(voices):
                    if v.id == current_voice:
                        current_index = idx
                        break

            self.voice_combo = ttk.Combobox(voice_frame, values=voice_names, state='readonly')
            self.voice_combo.current(current_index)
            self.voice_combo.grid(row=2, column=1, sticky='ew', pady=10)

        # Test button
        tk.Button(
            voice_frame,
            text="🔊 Test Voice",
            command=lambda: self.test_voice_settings(settings_window),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).grid(row=3, column=0, columnspan=2, pady=20)

        # Behavior settings
        behavior_frame = tk.Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(behavior_frame, text="Behavior")

        self.auto_start_var = tk.BooleanVar(value=self.config.get('auto_start', False))
        tk.Checkbutton(
            behavior_frame,
            text="Auto-start screen reader on boot",
            variable=self.auto_start_var,
            bg='white',
            font=('Arial', 10)
        ).pack(anchor='w', pady=5)

        self.read_focus_var = tk.BooleanVar(value=self.config.get('read_on_focus', True))
        tk.Checkbutton(
            behavior_frame,
            text="Read elements on focus",
            variable=self.read_focus_var,
            bg='white',
            font=('Arial', 10)
        ).pack(anchor='w', pady=5)

        self.read_hover_var = tk.BooleanVar(value=self.config.get('read_on_hover', False))
        tk.Checkbutton(
            behavior_frame,
            text="Read elements on mouse hover",
            variable=self.read_hover_var,
            bg='white',
            font=('Arial', 10)
        ).pack(anchor='w', pady=5)

        self.keyboard_echo_var = tk.BooleanVar(value=self.config.get('keyboard_echo', True))
        tk.Checkbutton(
            behavior_frame,
            text="Echo typed characters",
            variable=self.keyboard_echo_var,
            bg='white',
            font=('Arial', 10)
        ).pack(anchor='w', pady=5)

        # Punctuation level
        tk.Label(behavior_frame, text="Punctuation Level:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(20, 5))

        self.punctuation_var = tk.StringVar(value=self.config.get('punctuation_level', 'some'))

        for level in ['none', 'some', 'all']:
            tk.Radiobutton(
                behavior_frame,
                text=level.capitalize(),
                variable=self.punctuation_var,
                value=level,
                bg='white',
                font=('Arial', 10)
            ).pack(anchor='w', padx=20)

        # Verbosity
        tk.Label(behavior_frame, text="Verbosity:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(20, 5))

        self.verbosity_var = tk.StringVar(value=self.config.get('verbosity', 'normal'))

        for level in ['brief', 'normal', 'verbose']:
            tk.Radiobutton(
                behavior_frame,
                text=level.capitalize(),
                variable=self.verbosity_var,
                value=level,
                bg='white',
                font=('Arial', 10)
            ).pack(anchor='w', padx=20)

        # Buttons
        button_frame = tk.Frame(settings_window, bg='white', pady=10)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Save Settings",
            command=lambda: self.save_settings(settings_window),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=8
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            button_frame,
            text="Cancel",
            command=settings_window.destroy,
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=8
        ).pack(side=tk.RIGHT)

    def test_voice_settings(self, settings_window):
        """Test current voice settings"""
        if HAS_PYTTSX3 and self.tts_engine:
            # Apply temporary settings
            self.tts_engine.setProperty('rate', self.rate_var.get())
            self.tts_engine.setProperty('volume', self.volume_var.get())

            if hasattr(self, 'voice_combo'):
                voices = self.tts_engine.getProperty('voices')
                selected_index = self.voice_combo.current()
                if 0 <= selected_index < len(voices):
                    self.tts_engine.setProperty('voice', voices[selected_index].id)

            self.speak("This is a test of the screen reader voice settings. How does this sound?")

    def save_settings(self, settings_window):
        """Save settings"""
        self.config['voice_rate'] = self.rate_var.get()
        self.config['voice_volume'] = self.volume_var.get()
        self.config['auto_start'] = self.auto_start_var.get()
        self.config['read_on_focus'] = self.read_focus_var.get()
        self.config['read_on_hover'] = self.read_hover_var.get()
        self.config['keyboard_echo'] = self.keyboard_echo_var.get()
        self.config['punctuation_level'] = self.punctuation_var.get()
        self.config['verbosity'] = self.verbosity_var.get()

        if hasattr(self, 'voice_combo') and HAS_PYTTSX3 and self.tts_engine:
            voices = self.tts_engine.getProperty('voices')
            selected_index = self.voice_combo.current()
            if 0 <= selected_index < len(voices):
                self.config['voice_id'] = voices[selected_index].id

        self.save_config()

        # Apply settings
        if HAS_PYTTSX3 and self.tts_engine:
            self.tts_engine.setProperty('rate', self.config['voice_rate'])
            self.tts_engine.setProperty('volume', self.config['voice_volume'])
            if self.config.get('voice_id'):
                self.tts_engine.setProperty('voice', self.config['voice_id'])

        settings_window.destroy()
        self.speak("Settings saved")

    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
Keyboard Shortcuts:

Global:
  Super+S        - Toggle screen reader
  Ctrl+R         - Enable/disable reader
  Ctrl+S         - Stop speaking

Reading:
  Ctrl+C         - Read clipboard
  Ctrl+W         - Read window title
  Ctrl+T         - Read text area

Navigation:
  Tab            - Next element
  Shift+Tab      - Previous element
  Ctrl+Home      - Start of document
  Ctrl+End       - End of document
"""

        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
        self.speak("Showing keyboard shortcuts")

    def show_guide(self):
        """Show quick start guide"""
        guide_text = """
Quick Start Guide:

1. Click 'Enable Screen Reader' to activate
2. Use Tab to navigate between elements
3. Screen reader will announce focused items
4. Use Ctrl+S to stop speaking at any time
5. Configure voice and behavior in Settings

For full documentation, see:
/docs/ACCESSIBILITY.md
"""

        messagebox.showinfo("Quick Start Guide", guide_text)
        self.speak("Showing quick start guide")

    def show_installation_guide(self):
        """Show installation guide for dependencies"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Installation Required")
        guide_window.geometry("600x400")

        text = tk.Text(guide_window, wrap=tk.WORD, padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)

        guide_text = """Screen Reader Installation Guide

The TL Screen Reader requires pyttsx3 for text-to-speech functionality.

Installation Steps:

1. Open a terminal

2. Install pyttsx3:
   pip install pyttsx3

   OR if using system Python:
   sudo apt-get install python3-pip
   pip3 install pyttsx3

3. Additional TTS engines (optional):

   For better quality on Linux:
   sudo apt-get install espeak espeak-ng

   For Festival:
   sudo apt-get install festival

4. Restart the Screen Reader

Features (once installed):
• Text-to-speech for all UI elements
• Customizable voice, rate, and volume
• Read clipboard, windows, and documents
• Keyboard shortcuts for quick access
• Multiple voice options
• Punctuation and verbosity control

For more information, visit:
https://pyttsx3.readthedocs.io/
"""

        text.insert('1.0', guide_text)
        text.config(state=tk.DISABLED)

        tk.Button(guide_window, text="Close", command=guide_window.destroy, padx=20, pady=10).pack(pady=10)

    def run(self):
        """Run screen reader"""
        self.root.mainloop()

if __name__ == '__main__':
    reader = ScreenReader()
    reader.run()
