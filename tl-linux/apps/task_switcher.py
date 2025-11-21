#!/usr/bin/env python3
"""
TL Linux - Task Switcher (Alt+Tab)
Visual task switcher for switching between windows
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import json

class TaskSwitcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#1a1a1a')

        self.windows = []
        self.current_index = 0

        # Bind global hotkey (would use xbindkeys or similar in production)
        # For now, can be triggered programmatically

        self.setup_ui()

    def setup_ui(self):
        """Create the task switcher UI"""
        # Main frame
        self.frame = tk.Frame(self.root, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        self.frame.pack(padx=5, pady=5)

        # Title
        self.title_label = tk.Label(
            self.frame,
            text="Switch Window",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        )
        self.title_label.pack(pady=(10, 5))

        # Window list container
        self.list_frame = tk.Frame(self.frame, bg='#1a1a1a')
        self.list_frame.pack(padx=10, pady=(5, 10))

    def show(self):
        """Show task switcher"""
        # Get list of windows
        self.windows = self.get_windows()

        if not self.windows:
            return

        # Clear previous
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Display windows
        for i, window in enumerate(self.windows):
            self.create_window_item(window, i)

        # Position in center of screen
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Show
        self.root.deiconify()

        # Highlight first window
        self.current_index = 0
        self.highlight_window(0)

        # Focus root to capture key events
        self.root.focus_force()

        # Bind keys
        self.root.bind('<Tab>', lambda e: self.next_window())
        self.root.bind('<Shift-Tab>', lambda e: self.prev_window())
        self.root.bind('<Return>', lambda e: self.switch_to_current())
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<Alt_L>', lambda e: self.switch_to_current())  # Release Alt to switch

    def create_window_item(self, window, index):
        """Create a window item in the list"""
        item_frame = tk.Frame(self.list_frame, bg='#2b2b2b', bd=1, relief=tk.SOLID)
        item_frame.pack(fill=tk.X, pady=2)
        item_frame.config(width=400)

        # Store reference
        window['frame'] = item_frame

        # Icon (would show actual window icon if available)
        icon_label = tk.Label(
            item_frame,
            text=self.get_window_icon(window),
            font=('Arial', 24),
            bg='#2b2b2b'
        )
        icon_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Window info
        info_frame = tk.Frame(item_frame, bg='#2b2b2b')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # Window title
        title = window.get('title', 'Untitled')
        if len(title) > 50:
            title = title[:47] + '...'

        tk.Label(
            info_frame,
            text=title,
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='white',
            anchor='w'
        ).pack(fill=tk.X)

        # App name
        tk.Label(
            info_frame,
            text=window.get('app', 'Application'),
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        ).pack(fill=tk.X)

        # Click to select
        item_frame.bind('<Button-1>', lambda e, i=index: self.select_window(i))

    def get_window_icon(self, window):
        """Get emoji icon for window"""
        app = window.get('app', '').lower()

        icons = {
            'firefox': '🌐',
            'chrome': '🌐',
            'terminal': '🖥️',
            'nautilus': '📁',
            'code': '💻',
            'text': '📝',
            'music': '🎵',
            'video': '🎬',
            'image': '🖼️'
        }

        for key, icon in icons.items():
            if key in app:
                return icon

        return '🪟'

    def get_windows(self):
        """Get list of open windows"""
        windows = []

        try:
            # Use wmctrl to get window list
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True
            )

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split(None, 3)
                if len(parts) >= 4:
                    window_id = parts[0]
                    desktop = parts[1]
                    client = parts[2]
                    title = parts[3]

                    # Skip desktop and panels
                    if 'Desktop' in title or 'Panel' in title:
                        continue

                    windows.append({
                        'id': window_id,
                        'title': title,
                        'app': client,
                        'desktop': desktop
                    })

        except FileNotFoundError:
            # wmctrl not available, use demo data
            windows = [
                {'id': '1', 'title': 'Firefox - Mozilla Firefox', 'app': 'firefox', 'desktop': '0'},
                {'id': '2', 'title': 'File Manager - Home', 'app': 'nautilus', 'desktop': '0'},
                {'id': '3', 'title': 'Terminal', 'app': 'gnome-terminal', 'desktop': '0'},
                {'id': '4', 'title': 'Text Editor - document.txt', 'app': 'gedit', 'desktop': '0'}
            ]

        return windows

    def highlight_window(self, index):
        """Highlight window at index"""
        for i, window in enumerate(self.windows):
            frame = window.get('frame')
            if frame:
                if i == index:
                    frame.config(bg='#4a9eff', bd=2)
                    # Update all child widgets
                    for child in frame.winfo_children():
                        child.config(bg='#4a9eff')
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg='#4a9eff')
                else:
                    frame.config(bg='#2b2b2b', bd=1)
                    for child in frame.winfo_children():
                        child.config(bg='#2b2b2b')
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg='#2b2b2b')

    def next_window(self):
        """Select next window"""
        self.current_index = (self.current_index + 1) % len(self.windows)
        self.highlight_window(self.current_index)

    def prev_window(self):
        """Select previous window"""
        self.current_index = (self.current_index - 1) % len(self.windows)
        self.highlight_window(self.current_index)

    def select_window(self, index):
        """Select window by index"""
        self.current_index = index
        self.highlight_window(index)
        self.switch_to_current()

    def switch_to_current(self):
        """Switch to currently selected window"""
        if 0 <= self.current_index < len(self.windows):
            window = self.windows[self.current_index]
            self.activate_window(window['id'])

        self.hide()

    def activate_window(self, window_id):
        """Activate window by ID"""
        try:
            # Use wmctrl to activate window
            subprocess.run(['wmctrl', '-i', '-a', window_id])
        except FileNotFoundError:
            print(f"Would activate window: {window_id}")

    def hide(self):
        """Hide task switcher"""
        self.root.withdraw()

    def run(self):
        """Run the task switcher"""
        self.root.mainloop()


def show_task_switcher():
    """Show the task switcher (callable from hotkey)"""
    switcher = TaskSwitcher()
    switcher.show()
    switcher.run()

if __name__ == '__main__':
    show_task_switcher()
