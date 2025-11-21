#!/usr/bin/env python3
"""
TL Linux - Voice Control System
Control OS and applications with voice commands using wake word detection
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import threading
import time
import subprocess
import os
import re

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

class VoiceControl:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 TL Voice Control")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')

        self.config_file = Path.home() / '.config' / 'tl-linux' / 'voice_control.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self.load_config()

        # Voice recognition
        self.recognizer = sr.Recognizer() if HAS_SR else None
        self.microphone = None
        self.tts_engine = None

        # State
        self.is_enabled = False
        self.is_listening = False
        self.is_wake_word_mode = True
        self.last_command = ""
        self.command_history = []

        # Wake words
        self.wake_words = ['hey tl', 'computer', 'hey computer', 'tl linux']

        # Command mappings
        self.commands = self.build_command_mappings()

        self.initialize_engines()
        self.setup_ui()

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
            'wake_word_enabled': True,
            'wake_words': ['hey tl', 'computer'],
            'voice_feedback': True,
            'show_confidence': True,
            'language': 'en-US',
            'energy_threshold': 4000,
            'dynamic_energy': True,
            'pause_threshold': 0.8,
            'auto_start': False
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def initialize_engines(self):
        """Initialize speech recognition and TTS"""
        if HAS_SR:
            try:
                self.microphone = sr.Microphone()

                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Set recognition parameters
                self.recognizer.energy_threshold = self.config.get('energy_threshold', 4000)
                self.recognizer.dynamic_energy_threshold = self.config.get('dynamic_energy', True)
                self.recognizer.pause_threshold = self.config.get('pause_threshold', 0.8)

            except Exception as e:
                print(f"Error initializing microphone: {e}")

        if HAS_TTS:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 175)
                self.tts_engine.setProperty('volume', 0.9)
            except Exception as e:
                print(f"Error initializing TTS: {e}")

    def build_command_mappings(self):
        """Build command pattern mappings"""
        return {
            # System control
            r'open (.+)': self.cmd_open_app,
            r'close (.+)': self.cmd_close_app,
            r'launch (.+)': self.cmd_open_app,
            r'start (.+)': self.cmd_open_app,

            # Window management
            r'minimize( window)?': self.cmd_minimize_window,
            r'maximize( window)?': self.cmd_maximize_window,
            r'close window': self.cmd_close_window,
            r'full screen': self.cmd_fullscreen,

            # System operations
            r'lock screen': self.cmd_lock_screen,
            r'shut down': self.cmd_shutdown,
            r'restart': self.cmd_restart,
            r'sleep': self.cmd_sleep,
            r'screenshot': self.cmd_screenshot,

            # Navigation
            r'go back': self.cmd_go_back,
            r'go forward': self.cmd_go_forward,
            r'go home': self.cmd_go_home,
            r'search (for )?(.+)': self.cmd_search,
            r'show desktop': self.cmd_show_desktop,

            # Volume control
            r'volume up': self.cmd_volume_up,
            r'volume down': self.cmd_volume_down,
            r'mute': self.cmd_mute,
            r'unmute': self.cmd_unmute,
            r'volume (\d+)': self.cmd_set_volume,

            # Media control
            r'play': self.cmd_media_play,
            r'pause': self.cmd_media_pause,
            r'stop': self.cmd_media_stop,
            r'next track': self.cmd_media_next,
            r'previous track': self.cmd_media_previous,

            # Text editing
            r'type (.+)': self.cmd_type_text,
            r'select all': self.cmd_select_all,
            r'copy': self.cmd_copy,
            r'paste': self.cmd_paste,
            r'undo': self.cmd_undo,
            r'redo': self.cmd_redo,

            # Accessibility
            r'enable screen reader': self.cmd_enable_screen_reader,
            r'disable screen reader': self.cmd_disable_screen_reader,
            r'read screen': self.cmd_read_screen,

            # System queries
            r'what time is it': self.cmd_tell_time,
            r'what is the date': self.cmd_tell_date,
            r'(what|how) is the weather': self.cmd_tell_weather,

            # Voice control
            r'stop listening': self.cmd_stop_listening,
            r'enable voice control': self.cmd_enable_voice,
            r'disable voice control': self.cmd_disable_voice,
        }

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', pady=20)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🎤 TL Voice Control",
            font=('Arial', 22, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack()

        # Status
        status_frame = tk.Frame(header, bg='#2c3e50')
        status_frame.pack(pady=(10, 0))

        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=('Arial', 20),
            bg='#2c3e50',
            fg='#e74c3c'
        )
        self.status_indicator.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(
            status_frame,
            text="Voice Control Disabled",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        self.status_label.pack(side=tk.LEFT)

        # Main control
        control_frame = tk.Frame(self.root, bg='#34495e', pady=30)
        control_frame.pack(fill=tk.X)

        self.toggle_btn = tk.Button(
            control_frame,
            text="🎤 Enable Voice Control",
            command=self.toggle_voice_control,
            bg='#27ae60',
            fg='white',
            font=('Arial', 16, 'bold'),
            relief=tk.FLAT,
            padx=40,
            pady=20,
            cursor='hand2'
        )
        self.toggle_btn.pack()

        # Wake word indicator
        wake_frame = tk.Frame(self.root, bg='#1e1e1e', pady=15)
        wake_frame.pack(fill=tk.X)

        self.wake_word_label = tk.Label(
            wake_frame,
            text='Say "Hey TL" or "Computer" to activate',
            font=('Arial', 11),
            bg='#1e1e1e',
            fg='#95a5a6'
        )
        self.wake_word_label.pack()

        # Listening visualization
        viz_frame = tk.Frame(self.root, bg='#1e1e1e', pady=20)
        viz_frame.pack(fill=tk.BOTH, expand=True)

        self.listening_canvas = tk.Canvas(
            viz_frame,
            bg='#1e1e1e',
            height=150,
            highlightthickness=0
        )
        self.listening_canvas.pack(fill=tk.X, padx=50)

        # Draw initial waveform
        self.draw_waveform(0)

        # Last command display
        command_frame = tk.Frame(self.root, bg='#2c3e50', pady=15)
        command_frame.pack(fill=tk.X)

        tk.Label(
            command_frame,
            text="Last Command:",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack()

        self.last_command_label = tk.Label(
            command_frame,
            text="-",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='white',
            wraplength=700
        )
        self.last_command_label.pack(pady=(5, 0))

        self.confidence_label = tk.Label(
            command_frame,
            text="",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        self.confidence_label.pack()

        # Command history
        history_frame = tk.Frame(self.root, bg='#1e1e1e')
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        tk.Label(
            history_frame,
            text="Command History",
            font=('Arial', 12, 'bold'),
            bg='#1e1e1e',
            fg='white'
        ).pack(anchor='w', pady=(0, 10))

        # History listbox
        history_list_frame = tk.Frame(history_frame)
        history_list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(history_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(
            history_list_frame,
            bg='#2c3e50',
            fg='white',
            font=('Arial', 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Bottom controls
        bottom_frame = tk.Frame(self.root, bg='#34495e', pady=10)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(
            bottom_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            bottom_frame,
            text="📋 Commands List",
            command=self.show_commands_list,
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            bottom_frame,
            text="🔄 Clear History",
            command=self.clear_history,
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=10)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready" + ("" if HAS_SR else " - Warning: speech_recognition not installed"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Check dependencies
        if not HAS_SR:
            self.show_installation_guide()

    def draw_waveform(self, intensity):
        """Draw listening visualization waveform"""
        self.listening_canvas.delete('all')

        width = self.listening_canvas.winfo_width()
        height = 150
        center_y = height // 2

        if width <= 1:
            width = 800

        # Draw waveform
        num_bars = 50
        bar_width = width // num_bars

        import random
        for i in range(num_bars):
            if self.is_listening:
                bar_height = random.randint(5, int(50 * (intensity + 0.2)))
            else:
                bar_height = 3

            x = i * bar_width
            color = '#3498db' if self.is_listening else '#95a5a6'

            self.listening_canvas.create_rectangle(
                x, center_y - bar_height,
                x + bar_width - 2, center_y + bar_height,
                fill=color,
                outline=''
            )

    def toggle_voice_control(self):
        """Toggle voice control"""
        if not HAS_SR:
            messagebox.showerror(
                "Speech Recognition Not Available",
                "speech_recognition library is required.\n\n"
                "Install with: pip install SpeechRecognition pyaudio"
            )
            return

        self.is_enabled = not self.is_enabled
        self.config['enabled'] = self.is_enabled
        self.save_config()

        if self.is_enabled:
            self.status_indicator.config(fg='#27ae60')
            self.status_label.config(text="Voice Control Active - Listening for wake word")
            self.toggle_btn.config(text="🔴 Disable Voice Control", bg='#e74c3c')
            self.wake_word_label.config(text='Say "Hey TL" or "Computer" to activate', fg='#3498db')

            # Start listening thread
            self.start_listening()

            if self.config.get('voice_feedback'):
                self.speak("Voice control enabled")
        else:
            self.status_indicator.config(fg='#e74c3c')
            self.status_label.config(text="Voice Control Disabled")
            self.toggle_btn.config(text="🎤 Enable Voice Control", bg='#27ae60')
            self.wake_word_label.config(text='Voice control is disabled', fg='#95a5a6')
            self.is_listening = False

            if self.config.get('voice_feedback'):
                self.speak("Voice control disabled")

    def start_listening(self):
        """Start listening for commands"""
        def listen_thread():
            while self.is_enabled:
                try:
                    if self.is_wake_word_mode:
                        # Listen for wake word
                        self.listen_for_wake_word()
                    else:
                        # Listen for command
                        self.listen_for_command()

                except Exception as e:
                    print(f"Listening error: {e}")
                    time.sleep(0.5)

        threading.Thread(target=listen_thread, daemon=True).start()

    def listen_for_wake_word(self):
        """Listen for wake word"""
        if not self.microphone or not self.recognizer:
            return

        try:
            with self.microphone as source:
                self.is_listening = True
                self.root.after(0, lambda: self.draw_waveform(0.3))

                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)

                self.is_listening = False
                self.root.after(0, lambda: self.draw_waveform(0))

            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.config.get('language', 'en-US')).lower()

            # Check for wake word
            for wake_word in self.wake_words:
                if wake_word in text:
                    self.root.after(0, lambda: self.wake_word_detected())
                    return

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"Wake word error: {e}")

    def wake_word_detected(self):
        """Handle wake word detection"""
        self.is_wake_word_mode = False
        self.wake_word_label.config(text="🎤 Listening for command...", fg='#27ae60')

        if self.config.get('voice_feedback'):
            self.speak("Yes?")

        # Listen for command with timeout
        threading.Timer(10.0, self.reset_to_wake_word_mode).start()

    def listen_for_command(self):
        """Listen for voice command"""
        if not self.microphone or not self.recognizer:
            return

        try:
            with self.microphone as source:
                self.is_listening = True
                self.root.after(0, lambda: self.draw_waveform(0.6))

                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                self.is_listening = False
                self.root.after(0, lambda: self.draw_waveform(0))

            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.config.get('language', 'en-US'))
            confidence = 0.9  # Google API doesn't return confidence

            # Process command
            self.root.after(0, lambda: self.process_command(text, confidence))

        except sr.WaitTimeoutError:
            self.root.after(0, self.reset_to_wake_word_mode)
        except sr.UnknownValueError:
            self.root.after(0, lambda: self.speak("Sorry, I didn't understand that"))
            self.root.after(0, self.reset_to_wake_word_mode)
        except Exception as e:
            print(f"Command listening error: {e}")
            self.root.after(0, self.reset_to_wake_word_mode)

    def reset_to_wake_word_mode(self):
        """Reset to listening for wake word"""
        self.is_wake_word_mode = True
        self.wake_word_label.config(text='Say "Hey TL" or "Computer" to activate', fg='#3498db')

    def process_command(self, text, confidence):
        """Process voice command"""
        self.last_command = text
        self.last_command_label.config(text=text)

        if self.config.get('show_confidence'):
            self.confidence_label.config(text=f"Confidence: {confidence:.0%}")

        # Add to history
        timestamp = time.strftime("%H:%M:%S")
        self.command_history.insert(0, f"[{timestamp}] {text}")
        self.history_listbox.insert(0, f"[{timestamp}] {text}")

        if len(self.command_history) > 50:
            self.command_history.pop()
            self.history_listbox.delete(50)

        # Match command
        command_matched = False
        for pattern, handler in self.commands.items():
            match = re.match(pattern, text.lower(), re.IGNORECASE)
            if match:
                try:
                    handler(*match.groups())
                    command_matched = True
                    break
                except Exception as e:
                    self.speak(f"Error executing command: {str(e)}")
                    print(f"Command error: {e}")

        if not command_matched:
            self.speak("Sorry, I don't recognize that command")

        # Reset to wake word mode
        time.sleep(1)
        self.reset_to_wake_word_mode()

    def speak(self, text):
        """Speak response"""
        if self.tts_engine and self.config.get('voice_feedback'):
            def speak_thread():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"TTS error: {e}")

            threading.Thread(target=speak_thread, daemon=True).start()

    # Command handlers
    def cmd_open_app(self, app_name):
        """Open application"""
        self.speak(f"Opening {app_name}")
        # TODO: Implement app launching
        subprocess.Popen(['xdg-open', app_name], stderr=subprocess.DEVNULL)

    def cmd_close_app(self, app_name):
        """Close application"""
        self.speak(f"Closing {app_name}")
        subprocess.run(['pkill', '-f', app_name], stderr=subprocess.DEVNULL)

    def cmd_minimize_window(self, *args):
        """Minimize window"""
        self.speak("Minimizing window")
        subprocess.run(['xdotool', 'getactivewindow', 'windowminimize'], stderr=subprocess.DEVNULL)

    def cmd_maximize_window(self, *args):
        """Maximize window"""
        self.speak("Maximizing window")
        subprocess.run(['xdotool', 'getactivewindow', 'windowmaximize'], stderr=subprocess.DEVNULL)

    def cmd_close_window(self):
        """Close current window"""
        self.speak("Closing window")
        subprocess.run(['xdotool', 'getactivewindow', 'windowclose'], stderr=subprocess.DEVNULL)

    def cmd_fullscreen(self):
        """Toggle fullscreen"""
        self.speak("Full screen")
        subprocess.run(['xdotool', 'key', 'F11'], stderr=subprocess.DEVNULL)

    def cmd_lock_screen(self):
        """Lock screen"""
        self.speak("Locking screen")
        subprocess.run(['xdg-screensaver', 'lock'], stderr=subprocess.DEVNULL)

    def cmd_shutdown(self):
        """Shutdown system"""
        self.speak("Shutting down")
        subprocess.run(['systemctl', 'poweroff'], stderr=subprocess.DEVNULL)

    def cmd_restart(self):
        """Restart system"""
        self.speak("Restarting")
        subprocess.run(['systemctl', 'reboot'], stderr=subprocess.DEVNULL)

    def cmd_sleep(self):
        """Sleep system"""
        self.speak("Going to sleep")
        subprocess.run(['systemctl', 'suspend'], stderr=subprocess.DEVNULL)

    def cmd_screenshot(self):
        """Take screenshot"""
        self.speak("Taking screenshot")
        subprocess.run(['gnome-screenshot'], stderr=subprocess.DEVNULL)

    def cmd_go_back(self):
        """Go back"""
        self.speak("Going back")
        subprocess.run(['xdotool', 'key', 'Alt+Left'], stderr=subprocess.DEVNULL)

    def cmd_go_forward(self):
        """Go forward"""
        self.speak("Going forward")
        subprocess.run(['xdotool', 'key', 'Alt+Right'], stderr=subprocess.DEVNULL)

    def cmd_go_home(self):
        """Go home"""
        self.speak("Going home")
        subprocess.run(['xdotool', 'key', 'Alt+Home'], stderr=subprocess.DEVNULL)

    def cmd_search(self, for_word, query):
        """Search"""
        self.speak(f"Searching for {query}")
        # TODO: Implement search

    def cmd_show_desktop(self):
        """Show desktop"""
        self.speak("Showing desktop")
        subprocess.run(['xdotool', 'key', 'Super+d'], stderr=subprocess.DEVNULL)

    def cmd_volume_up(self):
        """Increase volume"""
        self.speak("Volume up")
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'], stderr=subprocess.DEVNULL)

    def cmd_volume_down(self):
        """Decrease volume"""
        self.speak("Volume down")
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%'], stderr=subprocess.DEVNULL)

    def cmd_mute(self):
        """Mute volume"""
        self.speak("Muting")
        subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '1'], stderr=subprocess.DEVNULL)

    def cmd_unmute(self):
        """Unmute volume"""
        self.speak("Unmuting")
        subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0'], stderr=subprocess.DEVNULL)

    def cmd_set_volume(self, level):
        """Set volume level"""
        self.speak(f"Setting volume to {level} percent")
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{level}%'], stderr=subprocess.DEVNULL)

    def cmd_media_play(self):
        """Play media"""
        self.speak("Playing")
        subprocess.run(['playerctl', 'play'], stderr=subprocess.DEVNULL)

    def cmd_media_pause(self):
        """Pause media"""
        self.speak("Pausing")
        subprocess.run(['playerctl', 'pause'], stderr=subprocess.DEVNULL)

    def cmd_media_stop(self):
        """Stop media"""
        self.speak("Stopping")
        subprocess.run(['playerctl', 'stop'], stderr=subprocess.DEVNULL)

    def cmd_media_next(self):
        """Next track"""
        self.speak("Next track")
        subprocess.run(['playerctl', 'next'], stderr=subprocess.DEVNULL)

    def cmd_media_previous(self):
        """Previous track"""
        self.speak("Previous track")
        subprocess.run(['playerctl', 'previous'], stderr=subprocess.DEVNULL)

    def cmd_type_text(self, text):
        """Type text"""
        subprocess.run(['xdotool', 'type', text], stderr=subprocess.DEVNULL)

    def cmd_select_all(self):
        """Select all"""
        self.speak("Select all")
        subprocess.run(['xdotool', 'key', 'ctrl+a'], stderr=subprocess.DEVNULL)

    def cmd_copy(self):
        """Copy"""
        self.speak("Copying")
        subprocess.run(['xdotool', 'key', 'ctrl+c'], stderr=subprocess.DEVNULL)

    def cmd_paste(self):
        """Paste"""
        self.speak("Pasting")
        subprocess.run(['xdotool', 'key', 'ctrl+v'], stderr=subprocess.DEVNULL)

    def cmd_undo(self):
        """Undo"""
        self.speak("Undo")
        subprocess.run(['xdotool', 'key', 'ctrl+z'], stderr=subprocess.DEVNULL)

    def cmd_redo(self):
        """Redo"""
        self.speak("Redo")
        subprocess.run(['xdotool', 'key', 'ctrl+y'], stderr=subprocess.DEVNULL)

    def cmd_enable_screen_reader(self):
        """Enable screen reader"""
        self.speak("Enabling screen reader")
        # TODO: Launch screen reader

    def cmd_disable_screen_reader(self):
        """Disable screen reader"""
        self.speak("Disabling screen reader")

    def cmd_read_screen(self):
        """Read screen"""
        self.speak("Reading screen")

    def cmd_tell_time(self):
        """Tell current time"""
        current_time = time.strftime("%I:%M %p")
        self.speak(f"The time is {current_time}")

    def cmd_tell_date(self):
        """Tell current date"""
        current_date = time.strftime("%A, %B %d, %Y")
        self.speak(f"Today is {current_date}")

    def cmd_tell_weather(self, *args):
        """Tell weather"""
        self.speak("Weather information is not available yet")

    def cmd_stop_listening(self):
        """Stop listening"""
        self.speak("Stopping")
        self.reset_to_wake_word_mode()

    def cmd_enable_voice(self):
        """Enable voice control"""
        if not self.is_enabled:
            self.toggle_voice_control()

    def cmd_disable_voice(self):
        """Disable voice control"""
        if self.is_enabled:
            self.toggle_voice_control()

    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        messagebox.showinfo("Settings", "Settings dialog coming soon!")

    def show_commands_list(self):
        """Show list of available commands"""
        commands_text = """Available Voice Commands:

System Control:
  • Open [app name]
  • Close [app name]
  • Minimize window
  • Maximize window
  • Full screen
  • Screenshot

System Operations:
  • Lock screen
  • Shut down
  • Restart
  • Sleep

Volume:
  • Volume up/down
  • Mute/Unmute
  • Volume [0-100]

Media:
  • Play/Pause/Stop
  • Next track
  • Previous track

Text Editing:
  • Type [text]
  • Select all
  • Copy/Paste
  • Undo/Redo

Information:
  • What time is it
  • What is the date

Voice Control:
  • Stop listening
  • Disable voice control
"""

        dialog = tk.Toplevel(self.root)
        dialog.title("Voice Commands")
        dialog.geometry("500x600")
        dialog.configure(bg='white')

        text = tk.Text(dialog, wrap=tk.WORD, padx=20, pady=20, font=('Arial', 10))
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', commands_text)
        text.config(state=tk.DISABLED)

        tk.Button(dialog, text="Close", command=dialog.destroy, bg='#3498db', fg='white', padx=20, pady=8).pack(pady=10)

    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.history_listbox.delete(0, tk.END)
        self.speak("History cleared")

    def show_installation_guide(self):
        """Show installation guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Installation Required")
        guide_window.geometry("600x450")

        text = tk.Text(guide_window, wrap=tk.WORD, padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)

        guide_text = """Voice Control Installation Guide

TL Voice Control requires speech recognition libraries.

Installation Steps:

1. Install SpeechRecognition:
   pip install SpeechRecognition

2. Install PyAudio for microphone input:

   On Ubuntu/Debian:
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio

   On other systems:
   pip install pyaudio

3. Install pyttsx3 for voice feedback:
   pip install pyttsx3

4. Optional - Install system dependencies:
   sudo apt-get install xdotool playerctl

5. Restart Voice Control

Features:
• Wake word detection ("Hey TL", "Computer")
• Natural language command processing
• Voice feedback
• Command history
• System control (apps, windows, volume)
• Media playback control
• Text input via voice
• Customizable settings

For more information, visit:
https://pypi.org/project/SpeechRecognition/
"""

        text.insert('1.0', guide_text)
        text.config(state=tk.DISABLED)

        tk.Button(guide_window, text="Close", command=guide_window.destroy, padx=20, pady=10).pack(pady=10)

    def run(self):
        """Run voice control"""
        self.root.mainloop()

if __name__ == '__main__':
    app = VoiceControl()
    app.run()
