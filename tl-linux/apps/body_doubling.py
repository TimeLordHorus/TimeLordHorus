#!/usr/bin/env python3
"""
TL Linux - Body Doubling Mode
Virtual co-working companion for ADHD support
Provides presence and accountability to help maintain focus
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import os
import json
from datetime import datetime, timedelta
import threading
import time

class BodyDoublingCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Body Doubling Companion")
        self.root.geometry("400x600")
        self.root.configure(bg='#1a1a1a')

        # Config
        self.config_dir = os.path.expanduser('~/.tl-linux/body-doubling')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

        # Session state
        self.session_active = False
        self.session_start_time = None
        self.session_duration = 0
        self.work_sessions_today = 0
        self.total_focus_time = 0

        # Companion state
        self.companion_name = self.config.get('companion_name', 'Alex')
        self.companion_mood = 'focused'  # focused, encouraging, break, tired
        self.last_check_in = None

        # Check-in timer
        self.check_in_interval = self.config.get('check_in_interval', 15) * 60  # minutes to seconds
        self.check_in_timer = None

        # Activity messages
        self.activities = [
            "working on a project",
            "reviewing code",
            "writing documentation",
            "studying",
            "organizing notes",
            "planning tasks",
            "reading articles",
            "debugging issues"
        ]

        self.setup_ui()
        self.update_display()

    def load_config(self):
        """Load configuration"""
        default_config = {
            'companion_name': 'Alex',
            'check_in_interval': 15,  # minutes
            'enable_sounds': True,
            'enable_notifications': True,
            'work_goal_minutes': 120,  # daily goal
            'sessions_today': 0,
            'total_focus_time': 0,
            'last_session_date': None
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)

                    # Reset daily stats if new day
                    last_date = loaded.get('last_session_date')
                    today = datetime.now().strftime('%Y-%m-%d')

                    if last_date != today:
                        loaded['sessions_today'] = 0
                        loaded['total_focus_time'] = 0

                    default_config.update(loaded)
        except:
            pass

        return default_config

    def save_config(self):
        """Save configuration"""
        self.config['last_session_date'] = datetime.now().strftime('%Y-%m-%d')

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Header with companion avatar
        header = tk.Frame(self.root, bg='#2b2b2b', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Avatar (simple emoji-based)
        avatar_frame = tk.Frame(header, bg='#2b2b2b')
        avatar_frame.pack(expand=True)

        self.avatar_label = tk.Label(
            avatar_frame,
            text="👤",
            font=('Arial', 48),
            bg='#2b2b2b'
        )
        self.avatar_label.pack()

        self.name_label = tk.Label(
            avatar_frame,
            text=self.companion_name,
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        )
        self.name_label.pack()

        # Status section
        status_frame = tk.Frame(self.root, bg='#1a1a1a')
        status_frame.pack(fill=tk.X, padx=20, pady=20)

        self.status_label = tk.Label(
            status_frame,
            text="Ready to work together!",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            wraplength=350,
            justify=tk.CENTER
        )
        self.status_label.pack()

        self.activity_label = tk.Label(
            status_frame,
            text="",
            font=('Arial', 9, 'italic'),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.activity_label.pack(pady=(5, 0))

        # Session controls
        control_frame = tk.Frame(self.root, bg='#1a1a1a')
        control_frame.pack(pady=20)

        self.start_button = tk.Button(
            control_frame,
            text="▶ Start Session",
            command=self.start_session,
            bg='#50fa7b',
            fg='#000000',
            font=('Arial', 12, 'bold'),
            bd=0,
            padx=30,
            pady=15,
            width=15
        )
        self.start_button.pack()

        # Timer display
        timer_frame = tk.Frame(self.root, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        timer_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            timer_frame,
            text="Current Session",
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(pady=(10, 5))

        self.timer_label = tk.Label(
            timer_frame,
            text="00:00:00",
            font=('Courier', 24, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        )
        self.timer_label.pack(pady=(0, 10))

        # Stats
        stats_frame = tk.Frame(self.root, bg='#1a1a1a')
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            stats_frame,
            text="Today's Progress",
            font=('Arial', 11, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', pady=(0, 10))

        # Sessions count
        session_stat = tk.Frame(stats_frame, bg='#2b2b2b')
        session_stat.pack(fill=tk.X, pady=5)

        tk.Label(
            session_stat,
            text="Sessions:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        ).pack(side=tk.LEFT, padx=10, pady=8)

        self.sessions_label = tk.Label(
            session_stat,
            text="0",
            font=('Arial', 10, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        self.sessions_label.pack(side=tk.RIGHT, padx=10, pady=8)

        # Total time
        time_stat = tk.Frame(stats_frame, bg='#2b2b2b')
        time_stat.pack(fill=tk.X, pady=5)

        tk.Label(
            time_stat,
            text="Total Focus Time:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        ).pack(side=tk.LEFT, padx=10, pady=8)

        self.total_time_label = tk.Label(
            time_stat,
            text="0h 0m",
            font=('Arial', 10, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        self.total_time_label.pack(side=tk.RIGHT, padx=10, pady=8)

        # Goal progress
        goal_stat = tk.Frame(stats_frame, bg='#2b2b2b')
        goal_stat.pack(fill=tk.X, pady=5)

        tk.Label(
            goal_stat,
            text="Daily Goal:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        ).pack(side=tk.LEFT, padx=10, pady=8)

        self.goal_label = tk.Label(
            goal_stat,
            text="0%",
            font=('Arial', 10, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        self.goal_label.pack(side=tk.RIGHT, padx=10, pady=8)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            stats_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 10))

        # Settings button
        tk.Button(
            self.root,
            text="⚙ Settings",
            command=self.show_settings,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 9),
            bd=0,
            padx=15,
            pady=5
        ).pack(pady=(0, 10))

        # Load saved stats
        self.work_sessions_today = self.config.get('sessions_today', 0)
        self.total_focus_time = self.config.get('total_focus_time', 0)
        self.update_stats()

    def start_session(self):
        """Start a work session"""
        self.session_active = True
        self.session_start_time = datetime.now()
        self.session_duration = 0

        # Update UI
        self.start_button.config(
            text="⏸ End Session",
            command=self.end_session,
            bg='#ff5555',
            fg='white'
        )

        # Update companion
        self.companion_mood = 'focused'
        activity = random.choice(self.activities)
        self.status_label.config(text=f"Great! Let's focus together.")
        self.activity_label.config(text=f"{self.companion_name} is {activity}...")

        # Start timer
        self.update_timer()

        # Schedule first check-in
        self.schedule_check_in()

    def end_session(self):
        """End work session"""
        if not self.session_active:
            return

        self.session_active = False

        # Calculate session duration
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).total_seconds()
            duration_minutes = int(duration / 60)

            # Update stats
            self.work_sessions_today += 1
            self.total_focus_time += duration_minutes

            self.config['sessions_today'] = self.work_sessions_today
            self.config['total_focus_time'] = self.total_focus_time
            self.save_config()

            # Show completion message
            self.show_session_complete(duration_minutes)

        # Reset UI
        self.start_button.config(
            text="▶ Start Session",
            command=self.start_session,
            bg='#50fa7b',
            fg='#000000'
        )

        self.timer_label.config(text="00:00:00")
        self.status_label.config(text="Good work! Take a break when you need it.")
        self.activity_label.config(text="")

        # Cancel check-in timer
        if self.check_in_timer:
            self.root.after_cancel(self.check_in_timer)
            self.check_in_timer = None

        self.update_stats()

    def update_timer(self):
        """Update session timer"""
        if not self.session_active:
            return

        # Calculate elapsed time
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        # Schedule next update
        self.root.after(1000, self.update_timer)

    def schedule_check_in(self):
        """Schedule periodic check-in"""
        if not self.session_active:
            return

        # Random check-in message
        messages = [
            "Still working on your task? You're doing great!",
            "How's it going? I'm still here with you!",
            "Making good progress? Keep it up!",
            "You're focused and doing well!",
            "Great job staying on task!",
            "You're not alone - we're working together!"
        ]

        def check_in():
            if self.session_active:
                message = random.choice(messages)
                self.status_label.config(text=message)

                # Optionally show notification
                if self.config.get('enable_notifications'):
                    self.show_notification("Body Doubling", message)

                # Schedule next check-in
                self.schedule_check_in()

        # Schedule after interval
        self.check_in_timer = self.root.after(self.check_in_interval * 1000, check_in)

    def show_session_complete(self, duration_minutes):
        """Show session completion message"""
        encouragements = [
            f"Awesome work! You focused for {duration_minutes} minutes!",
            f"Great session! {duration_minutes} minutes of focused work!",
            f"Well done! You stayed focused for {duration_minutes} minutes!",
            f"Excellent! {duration_minutes} minutes completed!",
            f"You did it! {duration_minutes} minutes of productive work!"
        ]

        message = random.choice(encouragements)

        if duration_minutes >= 25:
            message += "\n\nYou deserve a break! 🎉"

        messagebox.showinfo("Session Complete", message)

    def update_stats(self):
        """Update statistics display"""
        # Sessions
        self.sessions_label.config(text=str(self.work_sessions_today))

        # Total time
        hours = self.total_focus_time // 60
        minutes = self.total_focus_time % 60
        self.total_time_label.config(text=f"{hours}h {minutes}m")

        # Goal progress
        goal_minutes = self.config.get('work_goal_minutes', 120)
        progress_pct = min(100, (self.total_focus_time / goal_minutes) * 100)
        self.progress_var.set(progress_pct)
        self.goal_label.config(text=f"{int(progress_pct)}%")

    def update_display(self):
        """Update companion display"""
        # Change avatar based on mood
        avatars = {
            'focused': '👤',
            'encouraging': '😊',
            'break': '☕',
            'tired': '😴'
        }

        self.avatar_label.config(text=avatars.get(self.companion_mood, '👤'))

    def show_notification(self, title, message):
        """Show desktop notification"""
        try:
            subprocess.run([
                'notify-send',
                title,
                message,
                '-i', 'dialog-information'
            ])
        except:
            pass

    def show_settings(self):
        """Show settings dialog"""
        settings = tk.Toplevel(self.root)
        settings.title("Body Doubling Settings")
        settings.geometry("450x400")
        settings.configure(bg='#2b2b2b')
        settings.transient(self.root)
        settings.grab_set()

        tk.Label(
            settings,
            text="Settings",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)

        # Companion name
        name_frame = tk.Frame(settings, bg='#2b2b2b')
        name_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            name_frame,
            text="Companion Name:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        name_var = tk.StringVar(value=self.companion_name)
        name_entry = tk.Entry(
            name_frame,
            textvariable=name_var,
            bg='#1a1a1a',
            fg='white',
            insertbackground='white'
        )
        name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Check-in interval
        checkin_frame = tk.Frame(settings, bg='#2b2b2b')
        checkin_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            checkin_frame,
            text="Check-in Interval (minutes):",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        checkin_var = tk.IntVar(value=self.check_in_interval // 60)
        tk.Spinbox(
            checkin_frame,
            from_=5,
            to=60,
            textvariable=checkin_var,
            bg='#1a1a1a',
            fg='white',
            width=10
        ).pack(side=tk.RIGHT)

        # Daily goal
        goal_frame = tk.Frame(settings, bg='#2b2b2b')
        goal_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            goal_frame,
            text="Daily Goal (minutes):",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        goal_var = tk.IntVar(value=self.config.get('work_goal_minutes', 120))
        tk.Spinbox(
            goal_frame,
            from_=30,
            to=480,
            increment=30,
            textvariable=goal_var,
            bg='#1a1a1a',
            fg='white',
            width=10
        ).pack(side=tk.RIGHT)

        # Notifications
        notif_var = tk.BooleanVar(value=self.config.get('enable_notifications', True))
        tk.Checkbutton(
            settings,
            text="Enable Check-in Notifications",
            variable=notif_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(pady=10)

        # Sounds
        sound_var = tk.BooleanVar(value=self.config.get('enable_sounds', True))
        tk.Checkbutton(
            settings,
            text="Enable Sounds",
            variable=sound_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(pady=10)

        # Save button
        def save_settings():
            self.companion_name = name_var.get()
            self.check_in_interval = checkin_var.get() * 60

            self.config['companion_name'] = self.companion_name
            self.config['check_in_interval'] = checkin_var.get()
            self.config['work_goal_minutes'] = goal_var.get()
            self.config['enable_notifications'] = notif_var.get()
            self.config['enable_sounds'] = sound_var.get()

            self.save_config()

            self.name_label.config(text=self.companion_name)
            self.update_stats()

            settings.destroy()
            messagebox.showinfo("Success", "Settings saved!")

        tk.Button(
            settings,
            text="Save Settings",
            command=save_settings,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=10
        ).pack(pady=20)

    def run(self):
        """Run the body doubling companion"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        if self.session_active:
            if messagebox.askyesno("End Session?", "You have an active session. End it before closing?"):
                self.end_session()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    import subprocess

    companion = BodyDoublingCompanion()
    companion.run()

if __name__ == '__main__':
    main()
