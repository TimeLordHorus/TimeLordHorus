#!/usr/bin/env python3
"""
TL Linux - Notification Center
View notification history and manage notification settings
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
from datetime import datetime
import sys

# Add system path to import notification daemon
sys.path.insert(0, os.path.expanduser('~/tl-linux/system'))
from notification_daemon import get_daemon

class NotificationCenter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Notification Center")
        self.root.geometry("600x700")
        self.root.configure(bg='#2b2b2b')

        self.daemon = get_daemon()

        self.setup_ui()
        self.refresh_notifications()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔔 Notifications",
            font=('Arial', 18, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # DND toggle
        self.dnd_var = tk.BooleanVar(value=self.daemon.config.get('do_not_disturb', False))
        tk.Checkbutton(
            header,
            text="🌙 Do Not Disturb",
            variable=self.dnd_var,
            command=self.toggle_dnd,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            selectcolor='#2b2b2b'
        ).pack(side=tk.RIGHT, padx=20)

        # Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notifications tab
        notif_frame = self.create_notifications_tab()
        notebook.add(notif_frame, text="  History  ")

        # Settings tab
        settings_frame = self.create_settings_tab()
        notebook.add(settings_frame, text="  Settings  ")

    def create_notifications_tab(self):
        """Create notifications history tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        # Controls
        controls = tk.Frame(frame, bg='#2b2b2b')
        controls.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            controls,
            text="🔄 Refresh",
            command=self.refresh_notifications,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT)

        tk.Button(
            controls,
            text="🗑️ Clear All",
            command=self.clear_all,
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=10)

        self.count_label = tk.Label(
            controls,
            text="0 notifications",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.count_label.pack(side=tk.RIGHT)

        # Notifications list
        self.notif_container = tk.Frame(frame, bg='#2b2b2b')
        self.notif_container.pack(fill=tk.BOTH, expand=True, padx=20)

        # Scrollbar
        canvas = tk.Canvas(self.notif_container, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.notif_container, orient="vertical", command=canvas.yview)

        self.notif_frame = tk.Frame(canvas, bg='#2b2b2b')

        self.notif_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.notif_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return frame

    def create_settings_tab(self):
        """Create settings tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="Notification Settings",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        # Settings container
        settings = tk.Frame(frame, bg='#2b2b2b')
        settings.pack(fill=tk.BOTH, expand=True, padx=40)

        # Enabled
        self.enabled_var = tk.BooleanVar(value=self.daemon.config.get('enabled', True))
        tk.Checkbutton(
            settings,
            text="Enable notifications",
            variable=self.enabled_var,
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            command=self.save_settings
        ).pack(anchor='w', pady=10)

        # Sound
        self.sound_var = tk.BooleanVar(value=self.daemon.config.get('sound_enabled', True))
        tk.Checkbutton(
            settings,
            text="Play notification sounds",
            variable=self.sound_var,
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            command=self.save_settings
        ).pack(anchor='w', pady=10)

        # Lock screen
        self.lockscreen_var = tk.BooleanVar(value=self.daemon.config.get('show_on_lock_screen', False))
        tk.Checkbutton(
            settings,
            text="Show notifications on lock screen",
            variable=self.lockscreen_var,
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            command=self.save_settings
        ).pack(anchor='w', pady=10)

        # Max visible
        tk.Label(
            settings,
            text="Maximum visible notifications:",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(20, 5))

        self.max_visible_var = tk.IntVar(value=self.daemon.config.get('max_visible_notifications', 3))
        max_scale = tk.Scale(
            settings,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.max_visible_var,
            bg='#2b2b2b',
            fg='white',
            highlightthickness=0,
            command=lambda v: self.save_settings()
        )
        max_scale.pack(fill=tk.X, pady=5)

        # Do Not Disturb schedule
        tk.Label(
            settings,
            text="Do Not Disturb Schedule:",
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(20, 10))

        dnd_frame = tk.Frame(settings, bg='#2b2b2b')
        dnd_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            dnd_frame,
            text="From:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(side=tk.LEFT)

        self.dnd_start_var = tk.StringVar(value=self.daemon.config.get('dnd_start', '22:00'))
        tk.Entry(
            dnd_frame,
            textvariable=self.dnd_start_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='white',
            width=8
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            dnd_frame,
            text="To:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(side=tk.LEFT, padx=(20, 0))

        self.dnd_end_var = tk.StringVar(value=self.daemon.config.get('dnd_end', '08:00'))
        tk.Entry(
            dnd_frame,
            textvariable=self.dnd_end_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='white',
            width=8
        ).pack(side=tk.LEFT, padx=10)

        # Save button
        tk.Button(
            frame,
            text="💾 Save Settings",
            command=self.save_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0
        ).pack(pady=20)

        # Test notification
        tk.Button(
            frame,
            text="🔔 Send Test Notification",
            command=self.send_test_notification,
            font=('Arial', 10),
            bg='#6a6a6a',
            fg='white',
            padx=20,
            pady=8,
            bd=0
        ).pack(pady=10)

        return frame

    def refresh_notifications(self):
        """Refresh notifications list"""
        # Clear existing
        for widget in self.notif_frame.winfo_children():
            widget.destroy()

        # Get notifications (reverse chronological)
        notifications = list(reversed(self.daemon.history))

        if not notifications:
            tk.Label(
                self.notif_frame,
                text="No notifications",
                font=('Arial', 12),
                bg='#2b2b2b',
                fg='#888888'
            ).pack(pady=50)
            self.count_label.config(text="0 notifications")
            return

        # Display notifications
        for notif in notifications:
            self.create_notification_card(notif)

        self.count_label.config(text=f"{len(notifications)} notifications")

    def create_notification_card(self, notification):
        """Create a notification card"""
        card = tk.Frame(self.notif_frame, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        card.pack(fill=tk.X, pady=5)

        # Header
        header = tk.Frame(card, bg='#1a1a1a')
        header.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Icon
        icon = notification.get('icon', '🔔')
        tk.Label(
            header,
            text=icon,
            font=('Arial', 16),
            bg='#1a1a1a'
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Title and app
        info_frame = tk.Frame(header, bg='#1a1a1a')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            info_frame,
            text=notification.get('title', 'Notification'),
            font=('Arial', 11, 'bold'),
            bg='#1a1a1a',
            fg='white',
            anchor='w'
        ).pack(fill=tk.X)

        app_time = f"{notification.get('app_name', 'System')} • {self.format_timestamp(notification.get('timestamp'))}"
        tk.Label(
            info_frame,
            text=app_time,
            font=('Arial', 8),
            bg='#1a1a1a',
            fg='#888888',
            anchor='w'
        ).pack(fill=tk.X)

        # Message
        tk.Label(
            card,
            text=notification.get('message', ''),
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            wraplength=520,
            justify=tk.LEFT,
            anchor='w'
        ).pack(fill=tk.X, padx=15, pady=(0, 10))

    def format_timestamp(self, timestamp_str):
        """Format timestamp for display"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now()

            diff = now - timestamp

            if diff.total_seconds() < 60:
                return "Just now"
            elif diff.total_seconds() < 3600:
                mins = int(diff.total_seconds() / 60)
                return f"{mins}m ago"
            elif diff.total_seconds() < 86400:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours}h ago"
            else:
                return timestamp.strftime("%b %d, %H:%M")
        except:
            return "Unknown"

    def clear_all(self):
        """Clear all notifications"""
        from tkinter import messagebox
        if messagebox.askyesno("Clear All", "Clear all notification history?"):
            self.daemon.history = []
            self.daemon.save_history()
            self.refresh_notifications()

    def toggle_dnd(self):
        """Toggle Do Not Disturb"""
        self.daemon.toggle_do_not_disturb()
        self.save_settings()

    def save_settings(self):
        """Save settings to daemon"""
        self.daemon.config['enabled'] = self.enabled_var.get()
        self.daemon.config['sound_enabled'] = self.sound_var.get()
        self.daemon.config['show_on_lock_screen'] = self.lockscreen_var.get()
        self.daemon.config['max_visible_notifications'] = self.max_visible_var.get()
        self.daemon.config['do_not_disturb'] = self.dnd_var.get()
        self.daemon.config['dnd_start'] = self.dnd_start_var.get()
        self.daemon.config['dnd_end'] = self.dnd_end_var.get()

        self.daemon.save_config()

    def send_test_notification(self):
        """Send a test notification"""
        self.daemon.notify(
            "Test Notification",
            "This is a test notification from TL Linux Notification Center!",
            app_name="Notification Center",
            category="info",
            icon="🔔"
        )

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = NotificationCenter()
    app.run()

if __name__ == '__main__':
    main()
