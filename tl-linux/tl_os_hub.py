#!/usr/bin/env python3
"""
TL OS Hub - Portable Operating System Hub
A secure, versatile, and accessible OS hub designed for wellbeing

This hub provides three main portals:
- Desktop: Full XFCE-based desktop environment
- Workspace: Productivity and work-focused tools
- Entertainment: Media, gaming, and relaxation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import threading

class TLOSHub:
    """Main OS Hub - Full screen portal for TL Linux"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL OS Hub - Your Portable Operating System")

        # Full screen setup
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#0a0e27')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'os_hub_config.json'

        # State
        self.current_section = None
        self.wellbeing_enabled = True
        self.last_break_time = datetime.now()
        self.session_start = datetime.now()

        # Load configuration
        self.load_config()

        # Setup UI
        self.setup_ui()

        # Start wellbeing monitor
        if self.wellbeing_enabled:
            self.start_wellbeing_monitor()

        # Keyboard shortcuts
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Control-q>', lambda e: self.quit_hub())
        self.root.bind('<Alt-d>', lambda e: self.switch_to_desktop())
        self.root.bind('<Alt-w>', lambda e: self.switch_to_workspace())
        self.root.bind('<Alt-e>', lambda e: self.switch_to_entertainment())
        self.root.bind('<Alt-h>', lambda e: self.show_home())

    def load_config(self):
        """Load hub configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.wellbeing_enabled = config.get('wellbeing_enabled', True)
            except:
                pass

    def save_config(self):
        """Save hub configuration"""
        config = {
            'wellbeing_enabled': self.wellbeing_enabled,
            'last_used': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def setup_ui(self):
        """Setup the main UI"""
        # Main container
        self.main_container = tk.Frame(self.root, bg='#0a0e27')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Show home screen
        self.show_home()

    def show_home(self):
        """Display the home screen with three main portals"""
        # Clear current content
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.current_section = 'home'

        # Header
        header = tk.Frame(self.main_container, bg='#0a0e27', height=100)
        header.pack(fill=tk.X, pady=20)

        title = tk.Label(
            header,
            text="⏰ TL OS Hub",
            font=('Arial', 48, 'bold'),
            bg='#0a0e27',
            fg='#00ffff'
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="Your Portable, Accessible, Wellness-Focused Operating System",
            font=('Arial', 16),
            bg='#0a0e27',
            fg='#66ffff'
        )
        subtitle.pack()

        # Quick Access Toolbar
        self.create_quick_access_toolbar()

        # Main portal grid
        portals_frame = tk.Frame(self.main_container, bg='#0a0e27')
        portals_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=30)

        # Configure grid
        portals_frame.grid_columnconfigure(0, weight=1)
        portals_frame.grid_columnconfigure(1, weight=1)
        portals_frame.grid_columnconfigure(2, weight=1)
        portals_frame.grid_rowconfigure(0, weight=1)

        # Desktop Portal
        self.create_portal_card(
            portals_frame,
            title="🖥️ Desktop",
            description="Full XFCE desktop environment\nwith all system applications",
            color="#4a90e2",
            command=self.switch_to_desktop,
            row=0, col=0
        )

        # Workspace Portal
        self.create_portal_card(
            portals_frame,
            title="💼 Workspace",
            description="Productivity tools, focus mode,\nand work management",
            color="#50c878",
            command=self.switch_to_workspace,
            row=0, col=1
        )

        # Entertainment Portal
        self.create_portal_card(
            portals_frame,
            title="🎮 Entertainment",
            description="Media center, games,\nand relaxation tools",
            color="#e24a90",
            command=self.switch_to_entertainment,
            row=0, col=2
        )

        # Footer with system info and controls
        self.create_footer()

    def create_quick_access_toolbar(self):
        """Create quick access toolbar for frequently used features"""
        toolbar = tk.Frame(self.main_container, bg='#16213e', height=60)
        toolbar.pack(fill=tk.X, pady=(10, 0))

        # Toolbar label
        tk.Label(
            toolbar,
            text="⚡ Quick Access:",
            font=('Arial', 11, 'bold'),
            bg='#16213e',
            fg='#66ffff'
        ).pack(side=tk.LEFT, padx=20)

        # Quick access buttons
        quick_actions = [
            ("🎤", "Voice", self.launch_voice_assistant),
            ("🤖", "Chronos", self.launch_chronos_ai),
            ("🏆", "Achievements", self.launch_gamification),
            ("📔", "Journal", self.launch_mindfulness_journal),
            ("🔒", "Security", self.launch_security_hub),
            ("⚡", "Optimize", self.launch_hardware_optimizer),
            ("🧘", "Break", self.show_break_reminder),
        ]

        for icon, label, command in quick_actions:
            btn = tk.Button(
                toolbar,
                text=f"{icon}\n{label}",
                font=('Arial', 9),
                bg='#2a2e47',
                fg='white',
                activebackground='#3a3e57',
                command=command,
                relief=tk.FLAT,
                padx=8,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=3)

            # Hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#3a3e57'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#2a2e47'))

    def create_portal_card(self, parent, title, description, color, command, row, col):
        """Create a portal card button"""
        card_frame = tk.Frame(
            parent,
            bg=color,
            relief=tk.RAISED,
            borderwidth=3
        )
        card_frame.grid(row=row, column=col, padx=20, pady=20, sticky='nsew')

        # Make the entire card clickable
        card_button = tk.Button(
            card_frame,
            text=f"{title}\n\n{description}",
            font=('Arial', 20, 'bold'),
            bg=color,
            fg='white',
            activebackground=self.lighten_color(color),
            activeforeground='white',
            command=command,
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=0,
            padx=30,
            pady=40
        )
        card_button.pack(fill=tk.BOTH, expand=True)

        # Hover effects
        card_button.bind('<Enter>', lambda e: card_button.config(
            font=('Arial', 22, 'bold'),
            bg=self.lighten_color(color)
        ))
        card_button.bind('<Leave>', lambda e: card_button.config(
            font=('Arial', 20, 'bold'),
            bg=color
        ))

    def lighten_color(self, color):
        """Lighten a hex color"""
        # Simple lightening by adding to RGB values
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'

    def create_footer(self):
        """Create footer with system info and controls"""
        footer = tk.Frame(self.main_container, bg='#0f1535', height=60)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        # Left side - session info
        session_time = (datetime.now() - self.session_start).seconds // 60
        info_label = tk.Label(
            footer,
            text=f"Session: {session_time} min | Wellbeing: {'ON' if self.wellbeing_enabled else 'OFF'}",
            font=('Arial', 12),
            bg='#0f1535',
            fg='#66ffff'
        )
        info_label.pack(side=tk.LEFT, padx=20)

        # Right side - controls
        controls_frame = tk.Frame(footer, bg='#0f1535')
        controls_frame.pack(side=tk.RIGHT, padx=20)

        # Settings button
        settings_btn = tk.Button(
            controls_frame,
            text="⚙️ Settings",
            font=('Arial', 12),
            bg='#2a2e47',
            fg='white',
            command=self.show_settings,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        settings_btn.pack(side=tk.LEFT, padx=5)

        # Help button
        help_btn = tk.Button(
            controls_frame,
            text="❓ Help",
            font=('Arial', 12),
            bg='#2a2e47',
            fg='white',
            command=self.show_help,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        help_btn.pack(side=tk.LEFT, padx=5)

        # Exit button
        exit_btn = tk.Button(
            controls_frame,
            text="🚪 Exit",
            font=('Arial', 12),
            bg='#e24a4a',
            fg='white',
            command=self.quit_hub,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        exit_btn.pack(side=tk.LEFT, padx=5)

    def switch_to_desktop(self):
        """Switch to Desktop portal"""
        self.current_section = 'desktop'
        self.show_desktop_portal()

    def switch_to_workspace(self):
        """Switch to Workspace portal"""
        self.current_section = 'workspace'
        self.show_workspace_portal()

    def switch_to_entertainment(self):
        """Switch to Entertainment portal"""
        self.current_section = 'entertainment'
        self.show_entertainment_portal()

    def show_desktop_portal(self):
        """Display Desktop portal"""
        # Clear current content
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Header
        self.create_section_header("🖥️ Desktop Environment", self.show_home)

        # Content area
        content = tk.Frame(self.main_container, bg='#0a0e27')
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Desktop options grid
        options_frame = tk.Frame(content, bg='#0a0e27')
        options_frame.pack(expand=True, fill=tk.BOTH)

        # Configure grid
        for i in range(3):
            options_frame.grid_columnconfigure(i, weight=1)
        for i in range(4):  # Updated for more items
            options_frame.grid_rowconfigure(i, weight=1)

        # Desktop options
        desktop_options = [
            ("🖥️ Full Desktop", "Launch complete desktop environment", self.launch_full_desktop),
            ("📱 App Launcher", "Quick access to all applications", self.launch_app_launcher),
            ("📁 File Manager", "Browse and manage files", self.launch_file_manager),
            ("⚙️ System Settings", "Configure system preferences", self.launch_system_settings),
            ("🔧 Terminal", "Access command line", self.launch_terminal),
            ("📊 System Monitor", "View system resources", self.launch_system_monitor),
            ("🎤 Voice Assistant", "AI voice control (NEW!)", self.launch_voice_assistant),
            ("🔒 Security Hub", "Encryption & security tools", self.launch_security_hub),
            ("⚡ Hardware Optimizer", "GPU/CPU optimization (NEW!)", self.launch_hardware_optimizer),
            ("🔐 Biometric Auth", "Fingerprint & face login (NEW!)", self.launch_biometric_auth),
            ("☁️ Cloud Sync", "Optional encrypted sync (NEW!)", self.launch_cloud_sync),
        ]

        for idx, (title, desc, cmd) in enumerate(desktop_options):
            row = idx // 3
            col = idx % 3
            self.create_option_button(options_frame, title, desc, cmd, row, col)

    def show_workspace_portal(self):
        """Display Workspace portal"""
        # Clear current content
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Header
        self.create_section_header("💼 Workspace", self.show_home)

        # Content area
        content = tk.Frame(self.main_container, bg='#0a0e27')
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Workspace options grid
        options_frame = tk.Frame(content, bg='#0a0e27')
        options_frame.pack(expand=True, fill=tk.BOTH)

        # Configure grid
        for i in range(3):
            options_frame.grid_columnconfigure(i, weight=1)
        for i in range(4):  # Updated for more items
            options_frame.grid_rowconfigure(i, weight=1)

        # Workspace options
        workspace_options = [
            ("📝 Notes & Writing", "Distraction-free writing", self.launch_notes),
            ("✅ Task Manager", "ADHD-friendly task management", self.launch_tasks),
            ("📅 Calendar", "Schedule and events", self.launch_calendar),
            ("💻 IDE", "Code development environment", self.launch_ide),
            ("📊 Spreadsheet", "Data and calculations", self.launch_spreadsheet),
            ("📄 Document Editor", "Professional documents", self.launch_document_editor),
            ("🎯 Focus Mode", "Eliminate distractions", self.launch_focus_mode),
            ("👥 Body Doubling", "Virtual co-working", self.launch_body_doubling),
            ("🧘 Break Timer", "Mindful work breaks", self.launch_break_timer),
            ("🤖 Chronos AI", "Your AI learning companion (NEW!)", self.launch_chronos_ai),
            ("🏆 Wellbeing Games", "Achievement system (NEW!)", self.launch_gamification),
            ("📔 Journal & Mood", "Daily journaling (NEW!)", self.launch_mindfulness_journal),
        ]

        for idx, (title, desc, cmd) in enumerate(workspace_options):
            row = idx // 3
            col = idx % 3
            self.create_option_button(options_frame, title, desc, cmd, row, col)

    def show_entertainment_portal(self):
        """Display Entertainment portal"""
        # Clear current content
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Header
        self.create_section_header("🎮 Entertainment Portal", self.show_home)

        # Content area
        content = tk.Frame(self.main_container, bg='#0a0e27')
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Entertainment options grid
        options_frame = tk.Frame(content, bg='#0a0e27')
        options_frame.pack(expand=True, fill=tk.BOTH)

        # Configure grid
        for i in range(3):
            options_frame.grid_columnconfigure(i, weight=1)
        for i in range(4):  # Updated for more items
            options_frame.grid_rowconfigure(i, weight=1)

        # Entertainment options
        entertainment_options = [
            ("🎵 Music Player", "Your music library", self.launch_music_player),
            ("🎬 Video Player", "Watch videos and movies", self.launch_video_player),
            ("🖼️ Image Viewer", "Photo gallery", self.launch_image_viewer),
            ("🎮 Emulator Hub", "Classic gaming", self.launch_emulator_hub),
            ("🧘 Wellness Hub", "CBT & therapy tools", self.launch_wellness_hub),
            ("📚 Reading Mode", "E-books and documents", self.launch_pdf_viewer),
            ("🎨 Creative Tools", "Art and image editing", self.launch_image_editor),
            ("🌐 Web Browser", "Browse the internet", self.launch_browser),
            ("🎯 Casual Games", "Quick relaxing games", self.launch_casual_games),
            ("🧘 Meditation", "Guided meditation (NEW!)", self.launch_meditation),
        ]

        for idx, (title, desc, cmd) in enumerate(entertainment_options):
            row = idx // 3
            col = idx % 3
            self.create_option_button(options_frame, title, desc, cmd, row, col)

    def create_section_header(self, title, back_command):
        """Create a section header with back button"""
        header = tk.Frame(self.main_container, bg='#0f1535', height=80)
        header.pack(fill=tk.X)

        # Back button
        back_btn = tk.Button(
            header,
            text="← Back",
            font=('Arial', 14),
            bg='#2a2e47',
            fg='white',
            command=back_command,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        back_btn.pack(side=tk.LEFT, padx=20, pady=15)

        # Title
        title_label = tk.Label(
            header,
            text=title,
            font=('Arial', 32, 'bold'),
            bg='#0f1535',
            fg='#00ffff'
        )
        title_label.pack(side=tk.LEFT, padx=20)

    def create_option_button(self, parent, title, description, command, row, col):
        """Create an option button in the grid"""
        frame = tk.Frame(parent, bg='#1a1e3a', relief=tk.RAISED, borderwidth=2)
        frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

        button = tk.Button(
            frame,
            text=f"{title}\n\n{description}",
            font=('Arial', 14, 'bold'),
            bg='#1a1e3a',
            fg='white',
            activebackground='#2a2e4a',
            activeforeground='white',
            command=command,
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=30,
            wraplength=250
        )
        button.pack(fill=tk.BOTH, expand=True)

        # Hover effect
        button.bind('<Enter>', lambda e: button.config(bg='#2a2e4a'))
        button.bind('<Leave>', lambda e: button.config(bg='#1a1e3a'))

    # Application launchers
    def launch_app(self, app_name, script_path=None):
        """Generic app launcher"""
        try:
            if script_path and Path(script_path).exists():
                subprocess.Popen(['python3', script_path])
            else:
                messagebox.showinfo("Launch", f"Launching {app_name}...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {app_name}: {e}")

    def launch_full_desktop(self):
        """Launch full desktop environment"""
        desktop_path = Path(__file__).parent / 'desktop' / 'desktop_environment.py'
        self.launch_app("Desktop Environment", str(desktop_path))

    def launch_app_launcher(self):
        """Launch application launcher"""
        launcher_path = Path(__file__).parent / 'tl-linux-launcher.py'
        self.launch_app("App Launcher", str(launcher_path))

    def launch_file_manager(self):
        """Launch file manager"""
        fm_path = Path(__file__).parent / 'apps' / 'editors' / 'file_manager.py'
        self.launch_app("File Manager", str(fm_path))

    def launch_system_settings(self):
        """Launch system settings"""
        settings_path = Path(__file__).parent / 'apps' / 'system_settings.py'
        self.launch_app("System Settings", str(settings_path))

    def launch_terminal(self):
        """Launch terminal"""
        term_path = Path(__file__).parent / 'apps' / 'terminal.py'
        self.launch_app("Terminal", str(term_path))

    def launch_system_monitor(self):
        """Launch system monitor"""
        monitor_path = Path(__file__).parent / 'apps' / 'system_monitor.py'
        self.launch_app("System Monitor", str(monitor_path))

    def launch_notes(self):
        """Launch notes app"""
        notes_path = Path(__file__).parent / 'apps' / 'notes_app.py'
        self.launch_app("Notes", str(notes_path))

    def launch_tasks(self):
        """Launch task manager"""
        tasks_path = Path(__file__).parent / 'apps' / 'task_manager.py'
        self.launch_app("Task Manager", str(tasks_path))

    def launch_calendar(self):
        """Launch calendar"""
        cal_path = Path(__file__).parent / 'apps' / 'calendar.py'
        self.launch_app("Calendar", str(cal_path))

    def launch_ide(self):
        """Launch IDE"""
        ide_path = Path(__file__).parent / 'apps' / 'tl_ide.py'
        self.launch_app("IDE", str(ide_path))

    def launch_spreadsheet(self):
        """Launch spreadsheet"""
        sheet_path = Path(__file__).parent / 'apps' / 'editors' / 'spreadsheet_editor.py'
        self.launch_app("Spreadsheet", str(sheet_path))

    def launch_document_editor(self):
        """Launch document editor"""
        doc_path = Path(__file__).parent / 'apps' / 'editors' / 'document_editor.py'
        self.launch_app("Document Editor", str(doc_path))

    def launch_focus_mode(self):
        """Launch focus mode"""
        focus_path = Path(__file__).parent / 'apps' / 'wellness' / 'focus_mode.py'
        self.launch_app("Focus Mode", str(focus_path))

    def launch_body_doubling(self):
        """Launch body doubling"""
        bd_path = Path(__file__).parent / 'apps' / 'wellness' / 'body_doubling.py'
        self.launch_app("Body Doubling", str(bd_path))

    def launch_break_timer(self):
        """Launch break timer"""
        # Create inline break timer
        self.show_break_reminder()

    def launch_music_player(self):
        """Launch music player"""
        music_path = Path(__file__).parent / 'apps' / 'music_player.py'
        self.launch_app("Music Player", str(music_path))

    def launch_video_player(self):
        """Launch video player"""
        video_path = Path(__file__).parent / 'apps' / 'video_player.py'
        self.launch_app("Video Player", str(video_path))

    def launch_image_viewer(self):
        """Launch image viewer"""
        img_path = Path(__file__).parent / 'apps' / 'image_viewer.py'
        self.launch_app("Image Viewer", str(img_path))

    def launch_emulator_hub(self):
        """Launch emulator hub"""
        emu_path = Path(__file__).parent / 'apps' / 'emulator_hub.py'
        self.launch_app("Emulator Hub", str(emu_path))

    def launch_wellness_hub(self):
        """Launch wellness hub"""
        wellness_path = Path(__file__).parent / 'apps' / 'wellness' / 'wellness_hub.py'
        self.launch_app("Wellness Hub", str(wellness_path))

    def launch_pdf_viewer(self):
        """Launch PDF viewer"""
        pdf_path = Path(__file__).parent / 'apps' / 'editors' / 'pdf_viewer.py'
        self.launch_app("PDF Viewer", str(pdf_path))

    def launch_image_editor(self):
        """Launch image editor"""
        edit_path = Path(__file__).parent / 'apps' / 'editors' / 'image_editor.py'
        self.launch_app("Image Editor", str(edit_path))

    def launch_browser(self):
        """Launch web browser"""
        try:
            subprocess.Popen(['firefox'])
        except:
            try:
                subprocess.Popen(['chromium'])
            except:
                messagebox.showinfo("Browser", "No web browser found. Please install Firefox or Chromium.")

    def launch_casual_games(self):
        """Launch casual games"""
        messagebox.showinfo("Games", "Casual games collection coming soon!\nCheck Emulator Hub for classic games.")

    # NEW: Roadmap feature launchers
    def launch_voice_assistant(self):
        """Launch voice assistant"""
        va_path = Path(__file__).parent / 'accessibility' / 'voice_assistant.py'
        self.launch_app("Voice Assistant", str(va_path))

    def launch_security_hub(self):
        """Launch security hub"""
        sec_path = Path(__file__).parent / 'security' / 'security_hub.py'
        self.launch_app("Security Hub", str(sec_path))

    def launch_hardware_optimizer(self):
        """Launch hardware optimizer"""
        hw_path = Path(__file__).parent / 'system' / 'hardware_optimizer.py'
        self.launch_app("Hardware Optimizer", str(hw_path))

    def launch_biometric_auth(self):
        """Launch biometric authentication"""
        bio_path = Path(__file__).parent / 'security' / 'biometric_auth.py'
        self.launch_app("Biometric Auth", str(bio_path))

    def launch_cloud_sync(self):
        """Launch cloud sync"""
        cloud_path = Path(__file__).parent / 'system' / 'cloud_sync.py'
        self.launch_app("Cloud Sync", str(cloud_path))

    def launch_gamification(self):
        """Launch wellbeing gamification"""
        game_path = Path(__file__).parent / 'wellbeing' / 'wellbeing_gamification.py'
        self.launch_app("Wellbeing Gamification", str(game_path))

    def launch_mindfulness_journal(self):
        """Launch mindfulness journal"""
        journal_path = Path(__file__).parent / 'wellness' / 'mindfulness_journal.py'
        self.launch_app("Mindfulness Journal", str(journal_path))

    def launch_chronos_ai(self):
        """Launch Chronos AI agent"""
        chronos_path = Path(__file__).parent / 'ai' / 'chronos_ai.py'
        self.launch_app("Chronos AI Agent", str(chronos_path))

    def launch_meditation(self):
        """Launch meditation (same as mindfulness journal)"""
        self.launch_mindfulness_journal()

    # Wellbeing features
    def start_wellbeing_monitor(self):
        """Start the wellbeing monitoring system"""
        def monitor():
            while True:
                import time
                time.sleep(1200)  # Check every 20 minutes
                if self.wellbeing_enabled:
                    self.root.after(0, self.show_break_reminder)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def show_break_reminder(self):
        """Show a break reminder"""
        reminder = tk.Toplevel(self.root)
        reminder.title("Take a Break 🧘")
        reminder.geometry("500x300")
        reminder.configure(bg='#2a2e47')

        # Center on screen
        reminder.transient(self.root)
        reminder.grab_set()

        msg = tk.Label(
            reminder,
            text="🧘 Time for a Break!\n\nYou've been working for a while.\nTake a moment to:\n\n• Stretch your body\n• Rest your eyes\n• Take deep breaths\n• Hydrate",
            font=('Arial', 16),
            bg='#2a2e47',
            fg='white',
            justify=tk.CENTER
        )
        msg.pack(expand=True, pady=20)

        btn_frame = tk.Frame(reminder, bg='#2a2e47')
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Thanks! 👍",
            font=('Arial', 14),
            bg='#50c878',
            fg='white',
            command=reminder.destroy,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Remind me in 10 min",
            font=('Arial', 14),
            bg='#4a90e2',
            fg='white',
            command=lambda: [reminder.destroy(), self.snooze_break()],
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

    def snooze_break(self):
        """Snooze break reminder"""
        self.root.after(600000, self.show_break_reminder)  # 10 minutes

    def show_settings(self):
        """Show settings dialog"""
        settings = tk.Toplevel(self.root)
        settings.title("OS Hub Settings")
        settings.geometry("600x400")
        settings.configure(bg='#1a1e3a')
        settings.transient(self.root)

        title = tk.Label(
            settings,
            text="⚙️ OS Hub Settings",
            font=('Arial', 24, 'bold'),
            bg='#1a1e3a',
            fg='#00ffff'
        )
        title.pack(pady=20)

        # Wellbeing toggle
        wellbeing_frame = tk.Frame(settings, bg='#1a1e3a')
        wellbeing_frame.pack(pady=20, padx=40, fill=tk.X)

        tk.Label(
            wellbeing_frame,
            text="Wellbeing Reminders:",
            font=('Arial', 14),
            bg='#1a1e3a',
            fg='white'
        ).pack(side=tk.LEFT)

        wellbeing_var = tk.BooleanVar(value=self.wellbeing_enabled)
        tk.Checkbutton(
            wellbeing_frame,
            variable=wellbeing_var,
            bg='#1a1e3a',
            fg='white',
            selectcolor='#2a2e4a',
            font=('Arial', 12),
            command=lambda: setattr(self, 'wellbeing_enabled', wellbeing_var.get())
        ).pack(side=tk.RIGHT)

        # Save button
        tk.Button(
            settings,
            text="Save Settings",
            font=('Arial', 14),
            bg='#50c878',
            fg='white',
            command=lambda: [self.save_config(), settings.destroy()],
            padx=30,
            pady=10
        ).pack(pady=30)

    def show_help(self):
        """Show help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("OS Hub Help")
        help_window.geometry("700x500")
        help_window.configure(bg='#1a1e3a')
        help_window.transient(self.root)

        title = tk.Label(
            help_window,
            text="❓ OS Hub Help",
            font=('Arial', 24, 'bold'),
            bg='#1a1e3a',
            fg='#00ffff'
        )
        title.pack(pady=20)

        help_text = """
TL OS Hub - Keyboard Shortcuts

Alt+H       - Return to home
Alt+D       - Desktop portal
Alt+W       - Workspace portal
Alt+E       - Entertainment portal
Ctrl+Q      - Quit hub
Esc or F11  - Toggle fullscreen

About TL OS Hub

This is your portable operating system hub designed for:
• Accessibility and ease of use
• Mental and physical wellbeing
• ADHD and autism support
• Secure portable operation from USB

The hub provides three main portals:

🖥️  Desktop - Full desktop environment with all system tools
💼 Workspace - Productivity tools with focus and wellbeing features
🎮 Entertainment - Media, games, and relaxation

For more information, visit the TL Linux documentation.
        """

        text_widget = tk.Text(
            help_window,
            font=('Courier', 12),
            bg='#2a2e47',
            fg='white',
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)

        tk.Button(
            help_window,
            text="Close",
            font=('Arial', 12),
            bg='#4a90e2',
            fg='white',
            command=help_window.destroy,
            padx=20,
            pady=8
        ).pack(pady=20)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)

    def quit_hub(self):
        """Quit the hub"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit the OS Hub?"):
            self.save_config()
            self.root.quit()

    def run(self):
        """Run the hub"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("Starting TL OS Hub...")
    hub = TLOSHub()
    hub.run()


if __name__ == '__main__':
    main()
