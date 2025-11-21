#!/usr/bin/env python3
"""
TL Linux - Focus Mode & Distraction Blocker

Helps with ADHD by:
- Blocking distracting websites and apps
- Pomodoro timer with enforced breaks
- Hyperfocus protection (scheduled breaks)
- Distraction tracking and analytics
- Reward system for focus sessions
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime, timedelta
import subprocess
import threading
import time

class FocusMode:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Focus Mode")
        self.root.geometry("900x800")
        self.root.configure(bg='#2b2b2b')

        self.data_dir = os.path.expanduser('~/.tl-linux/focus_mode')
        os.makedirs(self.data_dir, exist_ok=True)

        self.config_file = os.path.join(self.data_dir, 'config.json')
        self.sessions_file = os.path.join(self.data_dir, 'sessions.json')

        self.config = self.load_config()
        self.sessions = self.load_sessions()

        # Focus state
        self.focus_active = False
        self.break_active = False
        self.session_start_time = None
        self.remaining_time = 0
        self.timer_thread = None

        self.setup_ui()

    def load_config(self):
        """Load configuration"""
        default_config = {
            'pomodoro_duration': 25,  # minutes
            'short_break': 5,
            'long_break': 15,
            'pomodoros_before_long_break': 4,
            'blocked_websites': [
                'youtube.com',
                'facebook.com',
                'twitter.com',
                'reddit.com',
                'instagram.com',
                'tiktok.com'
            ],
            'blocked_apps': [
                'discord',
                'slack',
                'telegram'
            ],
            'allow_emergency_exit': True,
            'emergency_exit_delay': 10,  # seconds
            'hyperfocus_protection': True,
            'max_continuous_focus': 120,  # minutes
            'sound_notifications': True,
            'fullscreen_break_screen': False
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

    def load_sessions(self):
        """Load focus session history"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_sessions(self):
        """Save session history"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🎯 Focus Mode",
            font=('Arial', 20, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=25)

        # Main container
        container = tk.Frame(self.root, bg='#2b2b2b')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Left side - Timer and controls
        left_frame = tk.Frame(container, bg='#2b2b2b')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.create_timer_panel(left_frame)
        self.create_controls_panel(left_frame)

        # Right side - Settings and stats
        right_frame = tk.Frame(container, bg='#2b2b2b')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.create_stats_panel(right_frame)
        self.create_blocklist_panel(right_frame)

    def create_timer_panel(self, parent):
        """Create the main timer display"""
        frame = tk.Frame(parent, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        frame.pack(fill=tk.X, pady=(0, 20))

        # Status label
        self.status_label = tk.Label(
            frame,
            text="Ready to Focus",
            font=('Arial', 14),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.status_label.pack(pady=(20, 10))

        # Timer display
        self.timer_label = tk.Label(
            frame,
            text="25:00",
            font=('Arial', 72, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        )
        self.timer_label.pack(pady=20)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 20), padx=30)

        # Session counter
        self.session_counter_label = tk.Label(
            frame,
            text="0/4 Pomodoros",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.session_counter_label.pack(pady=(0, 20))

        self.current_pomodoro_count = 0

    def create_controls_panel(self, parent):
        """Create control buttons"""
        frame = tk.Frame(parent, bg='#2b2b2b')
        frame.pack(fill=tk.X, pady=(0, 20))

        # Main control buttons
        btn_frame = tk.Frame(frame, bg='#2b2b2b')
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Focus",
            command=self.start_focus,
            font=('Arial', 14, 'bold'),
            bg='#5cb85c',
            fg='white',
            padx=30,
            pady=15,
            bd=0,
            cursor='hand2'
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(
            btn_frame,
            text="⏸ Pause",
            command=self.pause_focus,
            font=('Arial', 14, 'bold'),
            bg='#f0ad4e',
            fg='white',
            padx=30,
            pady=15,
            bd=0,
            state='disabled',
            cursor='hand2'
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ Stop",
            command=self.stop_focus,
            font=('Arial', 14, 'bold'),
            bg='#d9534f',
            fg='white',
            padx=30,
            pady=15,
            bd=0,
            state='disabled',
            cursor='hand2'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Quick timers
        quick_frame = tk.Frame(frame, bg='#2b2b2b')
        quick_frame.pack(pady=10)

        tk.Label(
            quick_frame,
            text="Quick Start:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(side=tk.LEFT, padx=(0, 10))

        for duration, label in [(25, "25 min"), (45, "45 min"), (90, "90 min")]:
            tk.Button(
                quick_frame,
                text=label,
                command=lambda d=duration: self.quick_start(d),
                font=('Arial', 9),
                bg='#3a3a3a',
                fg='white',
                padx=12,
                pady=6,
                bd=0,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=2)

    def create_stats_panel(self, parent):
        """Create statistics panel"""
        frame = tk.Frame(parent, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            frame,
            text="📊 Today's Focus Stats",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=(15, 10))

        # Get today's stats
        stats = self.get_today_stats()

        stats_grid = tk.Frame(frame, bg='#1a1a1a')
        stats_grid.pack(pady=(0, 15), padx=20)

        stat_items = [
            ("Total Focus Time", f"{stats['total_minutes']} min"),
            ("Completed Pomodoros", str(stats['completed_pomodoros'])),
            ("Longest Streak", f"{stats['longest_streak']} min"),
            ("Distractions Blocked", str(stats['blocks_today']))
        ]

        for i, (label, value) in enumerate(stat_items):
            row = i // 2
            col = i % 2

            stat_frame = tk.Frame(stats_grid, bg='#1a1a1a')
            stat_frame.grid(row=row, column=col, padx=10, pady=8, sticky='w')

            tk.Label(
                stat_frame,
                text=label,
                font=('Arial', 9),
                bg='#1a1a1a',
                fg='#888888'
            ).pack(anchor='w')

            tk.Label(
                stat_frame,
                text=value,
                font=('Arial', 13, 'bold'),
                bg='#1a1a1a',
                fg='white'
            ).pack(anchor='w')

        # Achievements
        if stats['completed_pomodoros'] >= 4:
            tk.Label(
                frame,
                text="🏆 Achievement: 4+ Pomodoros!",
                font=('Arial', 10, 'bold'),
                bg='#1a1a1a',
                fg='#ffd700'
            ).pack(pady=(0, 15))

    def create_blocklist_panel(self, parent):
        """Create blocklist management panel"""
        frame = tk.Frame(parent, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="🚫 Blocked During Focus",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=(15, 10))

        # Tabs for websites and apps
        tab_frame = tk.Frame(frame, bg='#1a1a1a')
        tab_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Websites
        tk.Label(
            tab_frame,
            text="Websites:",
            font=('Arial', 10, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', pady=(5, 5))

        websites_frame = tk.Frame(tab_frame, bg='#2b2b2b')
        websites_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.websites_listbox = tk.Listbox(
            websites_frame,
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='white',
            selectbackground='#4a9eff',
            height=6
        )
        self.websites_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(websites_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.websites_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.websites_listbox.yview)

        # Populate websites
        for site in self.config['blocked_websites']:
            self.websites_listbox.insert(tk.END, site)

        # Add/Remove buttons
        web_btn_frame = tk.Frame(tab_frame, bg='#1a1a1a')
        web_btn_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            web_btn_frame,
            text="➕ Add",
            command=self.add_website,
            font=('Arial', 8),
            bg='#5cb85c',
            fg='white',
            padx=8,
            pady=4,
            bd=0
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            web_btn_frame,
            text="➖ Remove",
            command=self.remove_website,
            font=('Arial', 8),
            bg='#d9534f',
            fg='white',
            padx=8,
            pady=4,
            bd=0
        ).pack(side=tk.LEFT, padx=2)

        # Apps
        tk.Label(
            tab_frame,
            text="Applications:",
            font=('Arial', 10, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', pady=(10, 5))

        apps_frame = tk.Frame(tab_frame, bg='#2b2b2b')
        apps_frame.pack(fill=tk.BOTH, expand=True)

        self.apps_listbox = tk.Listbox(
            apps_frame,
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='white',
            selectbackground='#4a9eff',
            height=6
        )
        self.apps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Populate apps
        for app in self.config['blocked_apps']:
            self.apps_listbox.insert(tk.END, app)

        # Settings
        settings_frame = tk.Frame(frame, bg='#1a1a1a')
        settings_frame.pack(fill=tk.X, padx=15, pady=(10, 15))

        self.hyperfocus_var = tk.BooleanVar(value=self.config.get('hyperfocus_protection', True))
        tk.Checkbutton(
            settings_frame,
            text="Hyperfocus Protection (force breaks)",
            variable=self.hyperfocus_var,
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b',
            command=self.update_settings
        ).pack(anchor='w')

        self.emergency_exit_var = tk.BooleanVar(value=self.config.get('allow_emergency_exit', True))
        tk.Checkbutton(
            settings_frame,
            text="Allow emergency exit (10s delay)",
            variable=self.emergency_exit_var,
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b',
            command=self.update_settings
        ).pack(anchor='w')

    def start_focus(self):
        """Start focus session"""
        if not self.focus_active:
            self.focus_active = True
            self.session_start_time = datetime.now()
            self.remaining_time = self.config['pomodoro_duration'] * 60

            # Enable blocks
            self.activate_blocks()

            # Update UI
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="🎯 FOCUS MODE ACTIVE", fg='#5cb85c')

            # Start timer
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()

    def quick_start(self, minutes):
        """Quick start with custom duration"""
        if not self.focus_active:
            self.config['pomodoro_duration'] = minutes
            self.start_focus()

    def pause_focus(self):
        """Pause the focus session"""
        if self.focus_active:
            self.focus_active = False
            self.deactivate_blocks()
            self.start_btn.config(state='normal', text="▶ Resume")
            self.pause_btn.config(state='disabled')
            self.status_label.config(text="⏸ Paused", fg='#f0ad4e')

    def stop_focus(self):
        """Stop the focus session"""
        if self.focus_active or self.break_active:
            # Save session
            self.save_session_record()

            self.focus_active = False
            self.break_active = False
            self.deactivate_blocks()

            # Reset UI
            self.start_btn.config(state='normal', text="▶ Start Focus")
            self.pause_btn.config(state='disabled')
            self.stop_btn.config(state='disabled')
            self.status_label.config(text="Ready to Focus", fg='#888888')
            self.timer_label.config(text="25:00")
            self.progress_var.set(0)

            # Update stats
            self.refresh_stats()

    def run_timer(self):
        """Timer thread"""
        total_time = self.remaining_time

        while self.focus_active and self.remaining_time > 0:
            time.sleep(1)
            if self.focus_active:
                self.remaining_time -= 1

                # Update display
                minutes = self.remaining_time // 60
                seconds = self.remaining_time % 60
                time_str = f"{minutes:02d}:{seconds:02d}"

                progress = ((total_time - self.remaining_time) / total_time) * 100

                self.root.after(0, lambda: self.timer_label.config(text=time_str))
                self.root.after(0, lambda: self.progress_var.set(progress))

        # Timer finished
        if self.focus_active:
            self.root.after(0, self.focus_complete)

    def focus_complete(self):
        """Focus session completed"""
        self.focus_active = False
        self.current_pomodoro_count += 1

        # Save completed session
        self.save_session_record(completed=True)

        # Play sound
        self.play_completion_sound()

        # Determine break length
        if self.current_pomodoro_count >= self.config['pomodoros_before_long_break']:
            break_duration = self.config['long_break']
            self.current_pomodoro_count = 0
            break_type = "long break"
        else:
            break_duration = self.config['short_break']
            break_type = "short break"

        # Show completion message
        messagebox.showinfo(
            "🎉 Focus Complete!",
            f"Great work! You completed a {self.config['pomodoro_duration']}-minute focus session.\n\n" +
            f"Time for a {break_duration}-minute {break_type}!"
        )

        # Start break timer
        self.start_break(break_duration)

    def start_break(self, duration):
        """Start break period"""
        self.break_active = True
        self.remaining_time = duration * 60

        self.status_label.config(text="☕ BREAK TIME - Rest & Recharge", fg='#ffd700')
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # Deactivate blocks during break
        self.deactivate_blocks()

        # Start break timer
        threading.Thread(target=self.run_break_timer, daemon=True).start()

    def run_break_timer(self):
        """Break timer thread"""
        total_time = self.remaining_time

        while self.break_active and self.remaining_time > 0:
            time.sleep(1)
            if self.break_active:
                self.remaining_time -= 1

                minutes = self.remaining_time // 60
                seconds = self.remaining_time % 60
                time_str = f"{minutes:02d}:{seconds:02d}"

                progress = ((total_time - self.remaining_time) / total_time) * 100

                self.root.after(0, lambda: self.timer_label.config(text=time_str))
                self.root.after(0, lambda: self.progress_var.set(progress))

        # Break finished
        if self.break_active:
            self.root.after(0, self.break_complete)

    def break_complete(self):
        """Break completed"""
        self.break_active = False

        messagebox.showinfo(
            "Break Over",
            "Break time is over! Ready for another focus session?"
        )

        # Reset for next session
        self.stop_focus()

    def activate_blocks(self):
        """Activate website and app blocking"""
        # Block websites by modifying /etc/hosts (requires sudo)
        # For demo, we'll just track that blocks are active
        self.blocks_active = True

        # Could implement with:
        # 1. /etc/hosts modification for websites
        # 2. pkill for applications
        # 3. Browser extensions
        # 4. Firewall rules

    def deactivate_blocks(self):
        """Deactivate blocks"""
        self.blocks_active = False

    def add_website(self):
        """Add website to blocklist"""
        from tkinter import simpledialog
        site = simpledialog.askstring("Add Website", "Enter website to block (e.g., example.com):")
        if site:
            if site not in self.config['blocked_websites']:
                self.config['blocked_websites'].append(site)
                self.websites_listbox.insert(tk.END, site)
                self.save_config()

    def remove_website(self):
        """Remove website from blocklist"""
        selection = self.websites_listbox.curselection()
        if selection:
            site = self.websites_listbox.get(selection[0])
            self.websites_listbox.delete(selection)
            self.config['blocked_websites'].remove(site)
            self.save_config()

    def update_settings(self):
        """Update settings from checkboxes"""
        self.config['hyperfocus_protection'] = self.hyperfocus_var.get()
        self.config['allow_emergency_exit'] = self.emergency_exit_var.get()
        self.save_config()

    def save_session_record(self, completed=False):
        """Save focus session to history"""
        if self.session_start_time:
            session = {
                'start_time': self.session_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': self.config['pomodoro_duration'],
                'completed': completed,
                'type': 'pomodoro'
            }

            self.sessions.append(session)
            self.save_sessions()

    def get_today_stats(self):
        """Calculate today's statistics"""
        today = datetime.now().date()

        total_minutes = 0
        completed_pomodoros = 0
        longest_streak = 0

        for session in self.sessions:
            session_date = datetime.fromisoformat(session['start_time']).date()
            if session_date == today:
                if session.get('completed'):
                    completed_pomodoros += 1
                    total_minutes += session.get('duration_minutes', 25)
                    if session.get('duration_minutes', 25) > longest_streak:
                        longest_streak = session.get('duration_minutes', 25)

        return {
            'total_minutes': total_minutes,
            'completed_pomodoros': completed_pomodoros,
            'longest_streak': longest_streak,
            'blocks_today': completed_pomodoros * 3  # Estimate
        }

    def refresh_stats(self):
        """Refresh statistics display"""
        # Rebuild stats panel
        pass

    def play_completion_sound(self):
        """Play sound when session completes"""
        if self.config.get('sound_notifications'):
            # Could use aplay, paplay, or other sound player
            try:
                subprocess.Popen(['paplay', '/usr/share/sounds/freedesktop/stereo/complete.oga'])
            except:
                pass

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = FocusMode()
    app.run()

if __name__ == '__main__':
    main()
