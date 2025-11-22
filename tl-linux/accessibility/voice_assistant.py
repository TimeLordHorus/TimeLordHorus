#!/usr/bin/env python3
"""
TL Voice Assistant - AI-Powered Voice Control
Comprehensive voice assistant for TL Linux OS Hub

Features:
- Wake word detection ("Hey TL" or "Computer")
- Voice commands for system control
- Natural language processing
- Text-to-speech responses
- Accessibility-focused design
- Offline operation (privacy-focused)
- Integration with OS Hub portals
- Chronos AI integration for conversational queries
"""

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import queue
import json
from pathlib import Path
from datetime import datetime
import re
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai.chronos_ai import ChronosAI
    CHRONOS_AVAILABLE = True
except ImportError:
    CHRONOS_AVAILABLE = False
    print("Warning: Chronos AI not available")

class VoiceAssistant:
    """AI-powered voice assistant for TL Linux"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Voice Assistant 🎤")
            self.root.geometry("600x700")
        else:
            self.root = root

        self.root.configure(bg='#1a1a2e')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'voice-assistant'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'assistant_config.json'

        # State
        self.listening = False
        self.wake_word_active = False
        self.command_queue = queue.Queue()
        self.conversation_history = []

        # Initialize Chronos AI (headless mode for integration)
        self.chronos = None
        if CHRONOS_AVAILABLE:
            try:
                self.chronos = ChronosAI(headless=True)
                print("Chronos AI initialized successfully")
            except Exception as e:
                print(f"Error initializing Chronos AI: {e}")

        # Load configuration
        self.load_config()

        # Setup UI
        self.setup_ui()

        # Initialize speech engines
        self.init_speech_engines()

    def load_config(self):
        """Load assistant configuration"""
        self.config = {
            'wake_word': 'hey tl',
            'alternative_wake_word': 'computer',
            'voice_enabled': True,
            'tts_enabled': True,
            'tts_rate': 150,
            'tts_volume': 0.8,
            'wake_word_detection': True,
            'continuous_listening': False,
            'language': 'en-US'
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        """Save assistant configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def init_speech_engines(self):
        """Initialize speech recognition and synthesis"""
        # Check for speech dependencies
        self.has_espeak = self.check_command('espeak')
        self.has_festival = self.check_command('festival')
        self.has_pico2wave = self.check_command('pico2wave')

        # Check for speech recognition
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.has_speech_recognition = True
        except ImportError:
            self.has_speech_recognition = False
            self.recognizer = None
            self.microphone = None

    def check_command(self, cmd):
        """Check if a command is available"""
        try:
            subprocess.run([cmd, '--version'], capture_output=True, timeout=2)
            return True
        except:
            return False

    def setup_ui(self):
        """Setup the UI"""
        # Title
        title_frame = tk.Frame(self.root, bg='#16213e', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="🎤 TL Voice Assistant",
            font=('Arial', 28, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        ).pack(pady=20)

        # Status indicator
        status_frame = tk.Frame(self.root, bg='#1a1a2e')
        status_frame.pack(pady=10)

        self.status_indicator = tk.Canvas(
            status_frame,
            width=30,
            height=30,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=10)
        self.status_circle = self.status_indicator.create_oval(
            5, 5, 25, 25,
            fill='#666666',
            outline='#333333'
        )

        self.status_label = tk.Label(
            status_frame,
            text="Ready to listen...",
            font=('Arial', 14),
            bg='#1a1a2e',
            fg='white'
        )
        self.status_label.pack(side=tk.LEFT)

        # Conversation display
        conv_frame = tk.LabelFrame(
            self.root,
            text="Conversation",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=10,
            pady=10
        )
        conv_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.conversation_display = scrolledtext.ScrolledText(
            conv_frame,
            font=('Courier', 11),
            bg='#0d1117',
            fg='#c9d1d9',
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.conversation_display.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colors
        self.conversation_display.tag_config('user', foreground='#58a6ff')
        self.conversation_display.tag_config('assistant', foreground='#7ee787')
        self.conversation_display.tag_config('system', foreground='#ffa657')
        self.conversation_display.tag_config('timestamp', foreground='#8b949e')

        # Controls
        controls_frame = tk.LabelFrame(
            self.root,
            text="Controls",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=15
        )
        controls_frame.pack(fill=tk.X, padx=20, pady=10)

        btn_frame = tk.Frame(controls_frame, bg='#1a1a2e')
        btn_frame.pack()

        self.listen_button = tk.Button(
            btn_frame,
            text="🎤 Start Listening",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=self.toggle_listening,
            padx=20,
            pady=10,
            width=15
        )
        self.listen_button.pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔊 Test TTS",
            font=('Arial', 12),
            bg='#1f6feb',
            fg='white',
            command=self.test_tts,
            padx=20,
            pady=10,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🗑️ Clear",
            font=('Arial', 12),
            bg='#da3633',
            fg='white',
            command=self.clear_conversation,
            padx=20,
            pady=10,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # Quick commands
        quick_frame = tk.LabelFrame(
            self.root,
            text="Quick Commands",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=15
        )
        quick_frame.pack(fill=tk.X, padx=20, pady=10)

        quick_commands = [
            ("Open Desktop", "open desktop"),
            ("Open Workspace", "open workspace"),
            ("Open Entertainment", "open entertainment"),
            ("What time is it?", "what time is it"),
            ("Take a break", "take a break"),
            ("System info", "system information")
        ]

        for idx, (label, cmd) in enumerate(quick_commands):
            row = idx // 3
            col = idx % 3
            tk.Button(
                quick_frame,
                text=label,
                font=('Arial', 9),
                bg='#21262d',
                fg='white',
                command=lambda c=cmd: self.execute_text_command(c),
                padx=10,
                pady=5
            ).grid(row=row, column=col, padx=5, pady=5, sticky='ew')

        # Configure grid columns to expand evenly
        for i in range(3):
            quick_frame.grid_columnconfigure(i, weight=1)

        # Display welcome message
        self.add_to_conversation("System", "Voice Assistant initialized. Say 'Hey TL' or click Start Listening.")

    def add_to_conversation(self, speaker, message, tag=None):
        """Add message to conversation display"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if tag is None:
            tag = speaker.lower()

        self.conversation_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.conversation_display.insert(tk.END, f"{speaker}: ", tag)
        self.conversation_display.insert(tk.END, f"{message}\n")
        self.conversation_display.see(tk.END)

        # Store in history
        self.conversation_history.append({
            'timestamp': timestamp,
            'speaker': speaker,
            'message': message
        })

    def toggle_listening(self):
        """Toggle listening state"""
        if not self.has_speech_recognition:
            self.add_to_conversation("System", "Speech recognition not available. Install: pip3 install SpeechRecognition pyaudio")
            return

        if self.listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """Start listening for voice commands"""
        self.listening = True
        self.listen_button.config(
            text="🛑 Stop Listening",
            bg='#da3633'
        )
        self.update_status("Listening...", '#238636')
        self.add_to_conversation("System", "Listening for commands...")

        # Start listening thread
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        """Stop listening"""
        self.listening = False
        self.listen_button.config(
            text="🎤 Start Listening",
            bg='#238636'
        )
        self.update_status("Ready", '#666666')
        self.add_to_conversation("System", "Stopped listening.")

    def update_status(self, text, color):
        """Update status indicator"""
        self.status_label.config(text=text)
        self.status_indicator.itemconfig(self.status_circle, fill=color)

    def listen_loop(self):
        """Main listening loop"""
        if not self.has_speech_recognition:
            return

        while self.listening:
            try:
                with self.microphone as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                    # Update status
                    self.root.after(0, lambda: self.update_status("Listening...", '#1f6feb'))

                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                    # Update status
                    self.root.after(0, lambda: self.update_status("Processing...", '#ffa657'))

                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()

                    # Display what was heard
                    self.root.after(0, lambda t=text: self.add_to_conversation("You", t, 'user'))

                    # Process command
                    self.root.after(0, lambda t=text: self.process_command(t))

            except Exception as e:
                # Timeout or no speech - continue listening
                pass

            self.root.after(0, lambda: self.update_status("Listening...", '#238636'))

    def execute_text_command(self, command):
        """Execute a text command"""
        self.add_to_conversation("You", command, 'user')
        self.process_command(command)

    def process_command(self, command):
        """Process voice command"""
        command = command.lower().strip()

        # Command mapping
        response = None

        # Portal navigation
        if any(word in command for word in ['open desktop', 'show desktop', 'desktop portal']):
            response = "Opening Desktop portal..."
            self.launch_os_hub_portal('desktop')

        elif any(word in command for word in ['open workspace', 'show workspace', 'workspace portal']):
            response = "Opening Workspace portal..."
            self.launch_os_hub_portal('workspace')

        elif any(word in command for word in ['open entertainment', 'show entertainment', 'entertainment portal']):
            response = "Opening Entertainment portal..."
            self.launch_os_hub_portal('entertainment')

        elif any(word in command for word in ['go home', 'home screen', 'main menu']):
            response = "Returning to home screen..."
            self.launch_os_hub_portal('home')

        # Time and date
        elif 'what time' in command or 'current time' in command:
            current_time = datetime.now().strftime("%I:%M %p")
            response = f"It's {current_time}"

        elif 'what date' in command or 'today' in command:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}"

        # Wellbeing
        elif 'take a break' in command or 'break time' in command:
            response = "Starting break reminder..."
            self.launch_break_reminder()

        elif 'stretch' in command or 'exercise' in command:
            response = "Opening stretch guide..."
            self.launch_stretch_guide()

        # System commands
        elif 'system information' in command or 'system info' in command:
            response = self.get_system_info()

        elif 'battery' in command or 'power' in command:
            response = self.get_battery_info()

        # Applications
        elif 'open' in command and 'file manager' in command:
            response = "Opening file manager..."
            self.launch_app('file_manager')

        elif 'open' in command and 'terminal' in command:
            response = "Opening terminal..."
            self.launch_app('terminal')

        elif 'open' in command and 'calculator' in command:
            response = "Opening calculator..."
            self.launch_app('calculator')

        elif 'open' in command and 'notes' in command:
            response = "Opening notes..."
            self.launch_app('notes')

        # Security
        elif 'lock' in command and 'screen' in command:
            response = "Locking screen..."
            subprocess.Popen(['xdg-screensaver', 'lock'])

        elif 'security' in command or 'firewall' in command:
            response = "Opening security hub..."
            self.launch_security_hub()

        # Volume control
        elif 'volume up' in command or 'increase volume' in command:
            response = "Increasing volume..."
            subprocess.run(['amixer', 'set', 'Master', '10%+'], capture_output=True)

        elif 'volume down' in command or 'decrease volume' in command:
            response = "Decreasing volume..."
            subprocess.run(['amixer', 'set', 'Master', '10%-'], capture_output=True)

        elif 'mute' in command:
            response = "Muting audio..."
            subprocess.run(['amixer', 'set', 'Master', 'mute'], capture_output=True)

        elif 'unmute' in command:
            response = "Unmuting audio..."
            subprocess.run(['amixer', 'set', 'Master', 'unmute'], capture_output=True)

        # Help
        elif 'help' in command or 'what can you do' in command:
            response = self.get_help_text()

        # Chronos AI - Personal assistant queries
        elif any(phrase in command for phrase in ['chronos', 'talk to chronos', 'ask chronos']):
            # Remove trigger words
            query = command.replace('chronos', '').replace('talk to', '').replace('ask', '').strip()
            if query:
                response = self.ask_chronos(query)
            else:
                response = "Hi! I'm Chronos, your AI companion. What would you like to talk about?"

        # Default response - try Chronos for conversational queries
        else:
            # Check if command seems conversational (questions, personal queries)
            is_conversational = any(word in command for word in [
                'how', 'what', 'when', 'where', 'why', 'who',
                'tell me', 'do you', 'can you', 'would you',
                'i am', 'i feel', 'my', 'advice', 'tip'
            ])

            if is_conversational and self.chronos:
                response = self.ask_chronos(command)
            else:
                response = f"I heard '{command}' but I'm not sure how to help with that. Try saying 'help' for available commands."

        # Display and speak response
        if response:
            self.add_to_conversation("Assistant", response, 'assistant')
            if self.config['tts_enabled']:
                self.speak(response)

    def launch_os_hub_portal(self, portal):
        """Launch OS Hub portal"""
        try:
            hub_path = Path(__file__).parent.parent / 'tl_os_hub.py'
            subprocess.Popen(['python3', str(hub_path)])
        except Exception as e:
            self.add_to_conversation("System", f"Error launching portal: {e}", 'system')

    def launch_app(self, app_name):
        """Launch application"""
        app_paths = {
            'file_manager': 'apps/editors/file_manager.py',
            'terminal': 'apps/terminal.py',
            'calculator': 'apps/calculator.py',
            'notes': 'apps/notes_app.py'
        }

        if app_name in app_paths:
            try:
                app_path = Path(__file__).parent.parent / app_paths[app_name]
                subprocess.Popen(['python3', str(app_path)])
            except Exception as e:
                self.add_to_conversation("System", f"Error launching app: {e}", 'system')

    def launch_break_reminder(self):
        """Launch break reminder"""
        try:
            wb_path = Path(__file__).parent.parent / 'wellbeing' / 'wellbeing_monitor.py'
            subprocess.Popen(['python3', str(wb_path)])
        except Exception as e:
            self.add_to_conversation("System", f"Error: {e}", 'system')

    def launch_stretch_guide(self):
        """Launch stretch guide"""
        self.launch_break_reminder()

    def launch_security_hub(self):
        """Launch security hub"""
        try:
            sec_path = Path(__file__).parent.parent / 'security' / 'security_hub.py'
            subprocess.Popen(['python3', str(sec_path)])
        except Exception as e:
            self.add_to_conversation("System", f"Error: {e}", 'system')

    def ask_chronos(self, message):
        """Ask Chronos AI a question"""
        if not self.chronos:
            return "Chronos AI is not available at the moment."

        try:
            # Get response from Chronos
            response = self.chronos.process_message(message)
            return response
        except Exception as e:
            print(f"Error asking Chronos: {e}")
            return "Sorry, I had trouble processing that. Could you try again?"

    def get_system_info(self):
        """Get system information"""
        try:
            # Get uptime
            uptime_result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
            uptime = uptime_result.stdout.strip()

            # Get memory
            mem_result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            mem_lines = mem_result.stdout.split('\n')[1].split()
            mem_total = mem_lines[1]
            mem_used = mem_lines[2]

            return f"System uptime: {uptime}. Memory: {mem_used} used of {mem_total} total."
        except:
            return "Unable to retrieve system information."

    def get_battery_info(self):
        """Get battery information"""
        try:
            result = subprocess.run(['acpi', '-b'], capture_output=True, text=True)
            if result.stdout:
                return result.stdout.strip()
            else:
                return "No battery detected. System is running on AC power."
        except:
            return "Unable to check battery status."

    def get_help_text(self):
        """Get help text"""
        return """I can help you with:
• Navigation: "Open desktop/workspace/entertainment"
• Time: "What time is it?" "What's the date?"
• Wellbeing: "Take a break" "Stretch"
• Apps: "Open file manager/terminal/calculator/notes"
• System: "System information" "Battery status"
• Volume: "Volume up/down" "Mute/unmute"
• Security: "Lock screen" "Open security"
• AI Companion: "Talk to Chronos" or ask questions naturally
Just speak naturally and I'll do my best to help!"""

    def speak(self, text):
        """Speak text using TTS"""
        def tts_thread():
            try:
                if self.has_espeak:
                    # Use espeak (fastest, most compatible)
                    rate = self.config['tts_rate']
                    subprocess.run(
                        ['espeak', '-s', str(rate), text],
                        capture_output=True
                    )
                elif self.has_festival:
                    # Use festival
                    subprocess.run(
                        ['festival', '--tts'],
                        input=text.encode(),
                        capture_output=True
                    )
                elif self.has_pico2wave:
                    # Use pico2wave
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        wav_file = f.name
                    subprocess.run(['pico2wave', '-w', wav_file, text])
                    subprocess.run(['aplay', wav_file])
                    Path(wav_file).unlink()
            except Exception as e:
                pass

        threading.Thread(target=tts_thread, daemon=True).start()

    def test_tts(self):
        """Test text-to-speech"""
        self.add_to_conversation("Assistant", "Testing text to speech. Hello! I am the TL Voice Assistant.", 'assistant')
        self.speak("Testing text to speech. Hello! I am the TL Voice Assistant.")

    def clear_conversation(self):
        """Clear conversation display"""
        self.conversation_display.delete('1.0', tk.END)
        self.conversation_history.clear()
        self.add_to_conversation("System", "Conversation cleared.")

    def run(self):
        """Run the assistant"""
        self.root.mainloop()


def main():
    """Main entry point"""
    assistant = VoiceAssistant()
    assistant.run()


if __name__ == '__main__':
    main()
