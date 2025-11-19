#!/usr/bin/env python3
"""
TL Linux - Notification Daemon
System-wide notification service with D-Bus interface
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
import time
import threading
import queue
import subprocess

class NotificationBubble:
    def __init__(self, parent_daemon, notification):
        self.daemon = parent_daemon
        self.notification = notification
        self.window = None
        self.visible = False

    def show(self):
        """Show notification bubble"""
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.configure(bg='#2b2b2b')

        # Position in top-right corner
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = screen_width - 420
        y = 50

        # Stack multiple notifications
        y += len([n for n in self.daemon.active_bubbles if n.visible]) * 130

        self.window.geometry(f"400x120+{x}+{y}")

        # Frame with border
        frame = tk.Frame(self.window, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header with icon and title
        header = tk.Frame(frame, bg='#1a1a1a')
        header.pack(fill=tk.X, padx=15, pady=(10, 5))

        # App icon/emoji
        icon = self.get_icon()
        tk.Label(
            header,
            text=icon,
            font=('Arial', 20),
            bg='#1a1a1a',
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Title and app name
        title_frame = tk.Frame(header, bg='#1a1a1a')
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            title_frame,
            text=self.notification['title'],
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white',
            anchor='w'
        ).pack(fill=tk.X)

        tk.Label(
            title_frame,
            text=self.notification.get('app_name', 'System'),
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888',
            anchor='w'
        ).pack(fill=tk.X)

        # Close button
        close_btn = tk.Label(
            header,
            text="✕",
            font=('Arial', 14),
            bg='#1a1a1a',
            fg='#888888',
            cursor='hand2'
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind('<Button-1>', lambda e: self.dismiss())

        # Message body
        message_label = tk.Label(
            frame,
            text=self.notification['message'],
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            wraplength=360,
            justify=tk.LEFT,
            anchor='w'
        )
        message_label.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Action buttons
        if self.notification.get('actions'):
            actions_frame = tk.Frame(frame, bg='#1a1a1a')
            actions_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

            for action in self.notification['actions']:
                tk.Button(
                    actions_frame,
                    text=action['label'],
                    command=lambda a=action: self.action_clicked(a),
                    font=('Arial', 9),
                    bg='#4a9eff',
                    fg='white',
                    bd=0,
                    padx=12,
                    pady=5
                ).pack(side=tk.LEFT, padx=5)

        # Click to open
        frame.bind('<Button-1>', lambda e: self.clicked())

        self.visible = True

        # Auto-dismiss after timeout
        timeout = self.notification.get('timeout', 5000)
        if timeout > 0:
            self.window.after(timeout, self.dismiss)

        # Fade in animation
        self.animate_in()

    def get_icon(self):
        """Get icon for notification"""
        urgency = self.notification.get('urgency', 'normal')
        category = self.notification.get('category', 'general')

        # Priority-based icons
        if urgency == 'critical':
            return '🔴'
        elif urgency == 'low':
            return 'ℹ️'

        # Category-based icons
        icon_map = {
            'email': '📧',
            'message': '💬',
            'update': '🔄',
            'download': '⬇️',
            'upload': '⬆️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'info': 'ℹ️',
            'security': '🔒',
            'calendar': '📅',
            'battery': '🔋',
            'network': '🌐'
        }

        return icon_map.get(category, self.notification.get('icon', '🔔'))

    def animate_in(self):
        """Fade in animation"""
        # Simple show - could add opacity animation
        pass

    def dismiss(self):
        """Dismiss notification"""
        if self.window:
            self.window.destroy()
            self.visible = False
            if self in self.daemon.active_bubbles:
                self.daemon.active_bubbles.remove(self)

    def clicked(self):
        """Handle notification click"""
        if self.notification.get('default_action'):
            callback = self.notification['default_action']
            if callable(callback):
                callback()
        self.dismiss()

    def action_clicked(self, action):
        """Handle action button click"""
        if action.get('callback'):
            action['callback']()
        self.dismiss()


class NotificationDaemon:
    def __init__(self):
        # History storage
        self.history_file = os.path.expanduser('~/.tl-linux/notifications/history.json')
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

        self.history = self.load_history()
        self.active_bubbles = []
        self.notification_queue = queue.Queue()

        # Settings
        self.config_file = os.path.expanduser('~/.tl-linux/notifications/config.json')
        self.config = self.load_config()

        # Start daemon thread
        self.running = True
        self.daemon_thread = threading.Thread(target=self.daemon_loop, daemon=True)
        self.daemon_thread.start()

        # Create hidden root window for Tkinter
        self.root = tk.Tk()
        self.root.withdraw()

    def load_history(self):
        """Load notification history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_history(self):
        """Save notification history"""
        try:
            # Keep only last 100 notifications
            self.history = self.history[-100:]
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving notification history: {e}")

    def load_config(self):
        """Load configuration"""
        default_config = {
            'enabled': True,
            'do_not_disturb': False,
            'dnd_start': '22:00',
            'dnd_end': '08:00',
            'sound_enabled': True,
            'show_on_lock_screen': False,
            'max_visible_notifications': 3
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

    def daemon_loop(self):
        """Main daemon loop"""
        while self.running:
            try:
                # Check for new notifications
                if not self.notification_queue.empty():
                    notification = self.notification_queue.get()
                    self.process_notification(notification)

                time.sleep(0.1)
            except Exception as e:
                print(f"Daemon error: {e}")

    def notify(self, title, message, **kwargs):
        """Send a notification"""
        notification = {
            'id': self.generate_id(),
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'app_name': kwargs.get('app_name', 'System'),
            'icon': kwargs.get('icon', '🔔'),
            'category': kwargs.get('category', 'general'),
            'urgency': kwargs.get('urgency', 'normal'),  # low, normal, critical
            'timeout': kwargs.get('timeout', 5000),  # milliseconds, 0 = no auto-dismiss
            'actions': kwargs.get('actions', []),  # list of {'label': str, 'callback': func}
            'default_action': kwargs.get('default_action', None),  # callback on click
            'sound': kwargs.get('sound', None),
            'persistent': kwargs.get('persistent', False)
        }

        self.notification_queue.put(notification)

    def process_notification(self, notification):
        """Process and display notification"""
        # Check if notifications are enabled
        if not self.config['enabled']:
            return

        # Check Do Not Disturb
        if self.config['do_not_disturb']:
            if notification['urgency'] != 'critical':
                # Still save to history but don't show
                self.add_to_history(notification)
                return

        # Add to history
        self.add_to_history(notification)

        # Check max visible notifications
        if len(self.active_bubbles) >= self.config['max_visible_notifications']:
            # Dismiss oldest non-critical notification
            for bubble in self.active_bubbles:
                if bubble.notification.get('urgency') != 'critical':
                    bubble.dismiss()
                    break

        # Play sound
        if self.config['sound_enabled'] and notification.get('sound'):
            self.play_sound(notification['sound'])

        # Show bubble
        bubble = NotificationBubble(self, notification)
        self.active_bubbles.append(bubble)
        self.root.after(0, bubble.show)

    def add_to_history(self, notification):
        """Add notification to history"""
        # Remove callback functions before saving (not JSON serializable)
        history_entry = notification.copy()
        history_entry.pop('actions', None)
        history_entry.pop('default_action', None)

        self.history.append(history_entry)
        self.save_history()

    def play_sound(self, sound):
        """Play notification sound"""
        try:
            sound_file = f"/usr/share/sounds/freedesktop/stereo/{sound}.oga"
            if os.path.exists(sound_file):
                subprocess.Popen(['paplay', sound_file], stderr=subprocess.DEVNULL)
        except:
            pass

    def generate_id(self):
        """Generate unique notification ID"""
        import random
        return f"notif_{int(time.time())}_{random.randint(1000, 9999)}"

    def dismiss_all(self):
        """Dismiss all active notifications"""
        for bubble in self.active_bubbles[:]:
            bubble.dismiss()

    def toggle_do_not_disturb(self):
        """Toggle Do Not Disturb mode"""
        self.config['do_not_disturb'] = not self.config['do_not_disturb']
        self.save_config()
        return self.config['do_not_disturb']

    def run(self):
        """Start the daemon"""
        self.root.mainloop()

    def stop(self):
        """Stop the daemon"""
        self.running = False
        self.root.quit()


# Global daemon instance
_daemon = None

def get_daemon():
    """Get or create daemon instance"""
    global _daemon
    if _daemon is None:
        _daemon = NotificationDaemon()
    return _daemon

def notify(title, message, **kwargs):
    """Send a notification"""
    daemon = get_daemon()
    daemon.notify(title, message, **kwargs)

def main():
    """Run notification daemon"""
    daemon = get_daemon()

    # Test notifications
    daemon.notify(
        "Welcome to TL Linux",
        "Notification system is running!",
        category='info',
        icon='🎉'
    )

    daemon.run()

if __name__ == '__main__':
    main()
