#!/usr/bin/env python3
"""
TL Linux Wellbeing Monitor
Comprehensive physical and mental wellbeing monitoring

Features:
- Break reminders (20-20-20 rule for eyes)
- Posture alerts
- Hydration reminders
- Movement tracking
- Screen time monitoring
- Stress management tools
- Accessibility support
"""

import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
import threading

class WellbeingMonitor:
    """Comprehensive wellbeing monitoring system"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Wellbeing Monitor 🧘")
        self.root.geometry("400x600")
        self.root.configure(bg='#1a2332')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellbeing'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'wellbeing_config.json'
        self.stats_file = self.config_dir / 'wellbeing_stats.json'

        # State
        self.session_start = datetime.now()
        self.last_break = datetime.now()
        self.last_eye_break = datetime.now()
        self.last_hydration = datetime.now()
        self.last_posture_alert = datetime.now()

        # Statistics
        self.stats = {
            'total_screen_time': 0,
            'breaks_taken': 0,
            'breaks_skipped': 0,
            'water_consumed': 0,
            'posture_alerts': 0
        }

        # Load configuration and stats
        self.load_config()
        self.load_stats()

        # Setup UI
        self.setup_ui()

        # Start monitoring
        self.monitoring = True
        self.start_monitoring()

        # Minimize to system tray by default
        self.root.withdraw()
        self.root.after(2000, self.check_wellbeing)

    def load_config(self):
        """Load wellbeing configuration"""
        self.config = {
            'break_interval': 30,  # minutes
            'break_duration': 5,  # minutes
            'eye_break_interval': 20,  # minutes (20-20-20 rule)
            'hydration_interval': 60,  # minutes
            'posture_alert_interval': 45,  # minutes
            'enabled': True,
            'eye_care_enabled': True,
            'hydration_enabled': True,
            'posture_enabled': True,
            'movement_enabled': True
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        """Save wellbeing configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def load_stats(self):
        """Load wellbeing statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats.update(json.load(f))
            except:
                pass

    def save_stats(self):
        """Save wellbeing statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def setup_ui(self):
        """Setup the UI"""
        # Title
        title_frame = tk.Frame(self.root, bg='#243447', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="🧘 Wellbeing Monitor",
            font=('Arial', 24, 'bold'),
            bg='#243447',
            fg='#7ed7c1'
        ).pack(pady=20)

        # Main content
        content = tk.Frame(self.root, bg='#1a2332')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Session info
        session_frame = tk.LabelFrame(
            content,
            text="Current Session",
            font=('Arial', 12, 'bold'),
            bg='#1a2332',
            fg='white',
            padx=15,
            pady=15
        )
        session_frame.pack(fill=tk.X, pady=10)

        self.session_time_label = tk.Label(
            session_frame,
            text="Session Time: 0:00",
            font=('Arial', 11),
            bg='#1a2332',
            fg='white'
        )
        self.session_time_label.pack(anchor=tk.W)

        self.next_break_label = tk.Label(
            session_frame,
            text="Next Break: 30:00",
            font=('Arial', 11),
            bg='#1a2332',
            fg='white'
        )
        self.next_break_label.pack(anchor=tk.W)

        # Quick actions
        actions_frame = tk.LabelFrame(
            content,
            text="Quick Actions",
            font=('Arial', 12, 'bold'),
            bg='#1a2332',
            fg='white',
            padx=15,
            pady=15
        )
        actions_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            actions_frame,
            text="☕ Take Break Now",
            font=('Arial', 11),
            bg='#5f9ea0',
            fg='white',
            command=self.take_break_now,
            width=20
        ).pack(pady=5)

        tk.Button(
            actions_frame,
            text="💧 Log Water Intake",
            font=('Arial', 11),
            bg='#5f9ea0',
            fg='white',
            command=self.log_water,
            width=20
        ).pack(pady=5)

        tk.Button(
            actions_frame,
            text="🧘 Quick Stretch",
            font=('Arial', 11),
            bg='#5f9ea0',
            fg='white',
            command=self.quick_stretch,
            width=20
        ).pack(pady=5)

        tk.Button(
            actions_frame,
            text="📊 View Statistics",
            font=('Arial', 11),
            bg='#5f9ea0',
            fg='white',
            command=self.show_statistics,
            width=20
        ).pack(pady=5)

        # Settings
        settings_frame = tk.LabelFrame(
            content,
            text="Settings",
            font=('Arial', 12, 'bold'),
            bg='#1a2332',
            fg='white',
            padx=15,
            pady=15
        )
        settings_frame.pack(fill=tk.X, pady=10)

        self.enabled_var = tk.BooleanVar(value=self.config['enabled'])
        tk.Checkbutton(
            settings_frame,
            text="Enable Monitoring",
            variable=self.enabled_var,
            font=('Arial', 10),
            bg='#1a2332',
            fg='white',
            selectcolor='#243447',
            command=self.toggle_monitoring
        ).pack(anchor=tk.W)

        self.eye_care_var = tk.BooleanVar(value=self.config['eye_care_enabled'])
        tk.Checkbutton(
            settings_frame,
            text="Eye Care Reminders",
            variable=self.eye_care_var,
            font=('Arial', 10),
            bg='#1a2332',
            fg='white',
            selectcolor='#243447',
            command=self.save_config
        ).pack(anchor=tk.W)

        self.hydration_var = tk.BooleanVar(value=self.config['hydration_enabled'])
        tk.Checkbutton(
            settings_frame,
            text="Hydration Reminders",
            variable=self.hydration_var,
            font=('Arial', 10),
            bg='#1a2332',
            fg='white',
            selectcolor='#243447',
            command=self.save_config
        ).pack(anchor=tk.W)

        self.posture_var = tk.BooleanVar(value=self.config['posture_enabled'])
        tk.Checkbutton(
            settings_frame,
            text="Posture Alerts",
            variable=self.posture_var,
            font=('Arial', 10),
            bg='#1a2332',
            fg='white',
            selectcolor='#243447',
            command=self.save_config
        ).pack(anchor=tk.W)

        # Control buttons
        control_frame = tk.Frame(content, bg='#1a2332')
        control_frame.pack(pady=20)

        tk.Button(
            control_frame,
            text="Show Monitor",
            font=('Arial', 10),
            bg='#4a90e2',
            fg='white',
            command=self.show_window,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            control_frame,
            text="Hide Monitor",
            font=('Arial', 10),
            bg='#4a90e2',
            fg='white',
            command=self.hide_window,
            width=12
        ).pack(side=tk.LEFT, padx=5)

    def start_monitoring(self):
        """Start wellbeing monitoring"""
        def monitor_loop():
            while self.monitoring:
                time.sleep(60)  # Check every minute
                self.root.after(0, self.check_wellbeing)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()

        # Update UI every second
        self.update_ui()

    def check_wellbeing(self):
        """Check wellbeing status and trigger alerts"""
        if not self.config['enabled']:
            return

        now = datetime.now()

        # Regular break reminder
        minutes_since_break = (now - self.last_break).seconds // 60
        if minutes_since_break >= self.config['break_interval']:
            self.show_break_reminder()

        # Eye care (20-20-20 rule)
        if self.config['eye_care_enabled']:
            minutes_since_eye_break = (now - self.last_eye_break).seconds // 60
            if minutes_since_eye_break >= self.config['eye_break_interval']:
                self.show_eye_care_reminder()

        # Hydration reminder
        if self.config['hydration_enabled']:
            minutes_since_hydration = (now - self.last_hydration).seconds // 60
            if minutes_since_hydration >= self.config['hydration_interval']:
                self.show_hydration_reminder()

        # Posture alert
        if self.config['posture_enabled']:
            minutes_since_posture = (now - self.last_posture_alert).seconds // 60
            if minutes_since_posture >= self.config['posture_alert_interval']:
                self.show_posture_alert()

    def update_ui(self):
        """Update UI labels"""
        # Session time
        session_duration = datetime.now() - self.session_start
        hours = session_duration.seconds // 3600
        minutes = (session_duration.seconds % 3600) // 60
        self.session_time_label.config(text=f"Session Time: {hours}:{minutes:02d}")

        # Next break
        time_since_break = (datetime.now() - self.last_break).seconds // 60
        time_to_break = max(0, self.config['break_interval'] - time_since_break)
        self.next_break_label.config(text=f"Next Break: {time_to_break} min")

        # Update screen time stats
        self.stats['total_screen_time'] = session_duration.seconds // 60

        # Schedule next update
        self.root.after(1000, self.update_ui)

    def show_break_reminder(self):
        """Show break reminder"""
        self.create_reminder_window(
            "☕ Time for a Break!",
            f"You've been working for {self.config['break_interval']} minutes.\n\n"
            "Take a {}-minute break to:\n"
            "• Stand up and stretch\n"
            "• Walk around\n"
            "• Rest your eyes\n"
            "• Hydrate".format(self.config['break_duration']),
            self.on_break_taken,
            self.on_break_skipped
        )

    def show_eye_care_reminder(self):
        """Show eye care reminder (20-20-20 rule)"""
        self.create_reminder_window(
            "👁️ Eye Care Reminder",
            "20-20-20 Rule:\n\n"
            "Look at something 20 feet away\n"
            "for 20 seconds\n"
            "every 20 minutes\n\n"
            "This helps reduce eye strain!",
            self.on_eye_break_taken,
            lambda: setattr(self, 'last_eye_break', datetime.now())
        )

    def show_hydration_reminder(self):
        """Show hydration reminder"""
        self.create_reminder_window(
            "💧 Hydration Reminder",
            "Stay hydrated!\n\n"
            "Time to drink some water.\n"
            "Proper hydration improves:\n"
            "• Focus and concentration\n"
            "• Energy levels\n"
            "• Overall health",
            self.on_hydration_logged,
            lambda: setattr(self, 'last_hydration', datetime.now())
        )

    def show_posture_alert(self):
        """Show posture alert"""
        self.create_reminder_window(
            "🪑 Posture Check",
            "Check your posture!\n\n"
            "Make sure:\n"
            "• Back is straight\n"
            "• Shoulders relaxed\n"
            "• Feet flat on floor\n"
            "• Screen at eye level\n"
            "• Arms at 90° angle",
            lambda: setattr(self, 'last_posture_alert', datetime.now()),
            lambda: setattr(self, 'last_posture_alert', datetime.now())
        )
        self.stats['posture_alerts'] += 1

    def create_reminder_window(self, title, message, on_accept, on_dismiss):
        """Create a reminder notification window"""
        reminder = tk.Toplevel(self.root)
        reminder.title(title)
        reminder.geometry("450x350")
        reminder.configure(bg='#243447')
        reminder.attributes('-topmost', True)

        # Center on screen
        reminder.update_idletasks()
        x = (reminder.winfo_screenwidth() // 2) - (reminder.winfo_width() // 2)
        y = (reminder.winfo_screenheight() // 2) - (reminder.winfo_height() // 2)
        reminder.geometry(f"+{x}+{y}")

        tk.Label(
            reminder,
            text=title,
            font=('Arial', 18, 'bold'),
            bg='#243447',
            fg='#7ed7c1'
        ).pack(pady=20)

        tk.Label(
            reminder,
            text=message,
            font=('Arial', 12),
            bg='#243447',
            fg='white',
            justify=tk.LEFT
        ).pack(pady=20, padx=30)

        btn_frame = tk.Frame(reminder, bg='#243447')
        btn_frame.pack(pady=30)

        tk.Button(
            btn_frame,
            text="✓ Done",
            font=('Arial', 12),
            bg='#5f9ea0',
            fg='white',
            command=lambda: [on_accept(), reminder.destroy()],
            padx=30,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="⏰ Remind Later",
            font=('Arial', 12),
            bg='#4a90e2',
            fg='white',
            command=lambda: [on_dismiss(), reminder.destroy()],
            padx=30,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

    def on_break_taken(self):
        """Handle break taken"""
        self.last_break = datetime.now()
        self.stats['breaks_taken'] += 1
        self.save_stats()

    def on_break_skipped(self):
        """Handle break skipped"""
        self.last_break = datetime.now()
        self.stats['breaks_skipped'] += 1
        self.save_stats()

    def on_eye_break_taken(self):
        """Handle eye break taken"""
        self.last_eye_break = datetime.now()
        self.save_stats()

    def on_hydration_logged(self):
        """Handle hydration logged"""
        self.last_hydration = datetime.now()
        self.stats['water_consumed'] += 1
        self.save_stats()

    def take_break_now(self):
        """Take a break immediately"""
        self.show_break_reminder()

    def log_water(self):
        """Log water intake"""
        self.on_hydration_logged()
        tk.messagebox.showinfo("Water Logged", "Water intake logged! 💧\nKeep staying hydrated!")

    def quick_stretch(self):
        """Show quick stretch guide"""
        stretch_window = tk.Toplevel(self.root)
        stretch_window.title("Quick Stretch Guide 🧘")
        stretch_window.geometry("500x600")
        stretch_window.configure(bg='#243447')

        tk.Label(
            stretch_window,
            text="🧘 Quick Stretch Routine",
            font=('Arial', 20, 'bold'),
            bg='#243447',
            fg='#7ed7c1'
        ).pack(pady=20)

        stretches = [
            "1. Neck Rolls (10 seconds each direction)",
            "2. Shoulder Shrugs (10 repetitions)",
            "3. Wrist Circles (10 seconds each direction)",
            "4. Back Stretch - Reach for the sky! (15 seconds)",
            "5. Side Bends (10 seconds each side)",
            "6. Seated Twist (10 seconds each side)",
            "7. Ankle Rolls (10 seconds each foot)",
            "8. Deep Breathing (5 deep breaths)"
        ]

        text_widget = tk.Text(
            stretch_window,
            font=('Arial', 12),
            bg='#1a2332',
            fg='white',
            wrap=tk.WORD,
            padx=20,
            pady=20,
            height=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for stretch in stretches:
            text_widget.insert(tk.END, stretch + "\n\n")

        text_widget.config(state=tk.DISABLED)

        tk.Button(
            stretch_window,
            text="Done Stretching ✓",
            font=('Arial', 12),
            bg='#5f9ea0',
            fg='white',
            command=stretch_window.destroy,
            padx=30,
            pady=10
        ).pack(pady=20)

    def show_statistics(self):
        """Show wellbeing statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Wellbeing Statistics 📊")
        stats_window.geometry("500x400")
        stats_window.configure(bg='#243447')

        tk.Label(
            stats_window,
            text="📊 Your Wellbeing Stats",
            font=('Arial', 20, 'bold'),
            bg='#243447',
            fg='#7ed7c1'
        ).pack(pady=20)

        stats_text = f"""
Screen Time Today: {self.stats['total_screen_time']} minutes

Breaks Taken: {self.stats['breaks_taken']}
Breaks Skipped: {self.stats['breaks_skipped']}

Water Consumed: {self.stats['water_consumed']} glasses

Posture Alerts: {self.stats['posture_alerts']}

Keep up the great work! Remember:
• Take regular breaks
• Stay hydrated
• Maintain good posture
• Rest your eyes frequently
        """

        tk.Label(
            stats_window,
            text=stats_text,
            font=('Arial', 12),
            bg='#243447',
            fg='white',
            justify=tk.LEFT
        ).pack(pady=20, padx=30)

        tk.Button(
            stats_window,
            text="Close",
            font=('Arial', 12),
            bg='#5f9ea0',
            fg='white',
            command=stats_window.destroy,
            padx=30,
            pady=10
        ).pack(pady=20)

    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        self.config['enabled'] = self.enabled_var.get()
        self.save_config()

    def show_window(self):
        """Show the monitor window"""
        self.root.deiconify()

    def hide_window(self):
        """Hide the monitor window"""
        self.root.withdraw()

    def run(self):
        """Run the wellbeing monitor"""
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.mainloop()


def main():
    """Main entry point"""
    monitor = WellbeingMonitor()
    monitor.run()


if __name__ == '__main__':
    main()
