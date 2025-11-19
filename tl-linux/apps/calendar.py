#!/usr/bin/env python3
"""
TL Linux Calendar
Calendar with event management and reminders
"""

import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime, timedelta
import json
from pathlib import Path

class TLCalendar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Calendar")
        self.root.geometry("800x600")

        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.config_dir / 'calendar_events.json'

        self.current_date = datetime.now()
        self.events = self.load_events()

        self.setup_ui()
        self.update_calendar()

    def load_events(self):
        """Load events from file"""
        if self.events_file.exists():
            with open(self.events_file, 'r') as f:
                return json.load(f)
        return {}

    def save_events(self):
        """Save events to file"""
        with open(self.events_file, 'w') as f:
            json.dump(self.events, f, indent=2)

    def setup_ui(self):
        """Setup calendar UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a1a', pady=10)
        header_frame.pack(fill=tk.X)

        # Navigation
        tk.Button(
            header_frame,
            text="◀",
            command=self.prev_month,
            bg='#333333',
            fg='#00FF00',
            font=('Sans', 12, 'bold'),
            bd=0,
            cursor='hand2',
            padx=10
        ).pack(side=tk.LEFT, padx=10)

        self.month_label = tk.Label(
            header_frame,
            text="",
            font=('Sans', 18, 'bold'),
            bg='#1a1a1a',
            fg='#00FF00'
        )
        self.month_label.pack(side=tk.LEFT, expand=True)

        tk.Button(
            header_frame,
            text="▶",
            command=self.next_month,
            bg='#333333',
            fg='#00FF00',
            font=('Sans', 12, 'bold'),
            bd=0,
            cursor='hand2',
            padx=10
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            header_frame,
            text="Today",
            command=self.go_to_today,
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 10, 'bold'),
            bd=0,
            cursor='hand2',
            padx=15
        ).pack(side=tk.RIGHT, padx=5)

        # Main content area
        content_frame = tk.Frame(self.root, bg='#0a0a0a')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Calendar grid
        self.calendar_frame = tk.Frame(content_frame, bg='#0a0a0a')
        self.calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Events sidebar
        events_frame = tk.Frame(content_frame, bg='#1a1a1a', width=250)
        events_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        events_frame.pack_propagate(False)

        tk.Label(
            events_frame,
            text="Upcoming Events",
            font=('Sans', 14, 'bold'),
            bg='#1a1a1a',
            fg='#00FF00'
        ).pack(pady=10)

        self.events_listbox = tk.Listbox(
            events_frame,
            bg='#0a0a0a',
            fg='#00FF00',
            font=('Monospace', 9),
            selectbackground='#333333',
            bd=0,
            highlightthickness=0
        )
        self.events_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Button(
            events_frame,
            text="+ Add Event",
            command=self.add_event,
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 10, 'bold'),
            bd=0,
            cursor='hand2'
        ).pack(pady=10, padx=10, fill=tk.X)

    def update_calendar(self):
        """Update calendar display"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update month label
        month_name = self.current_date.strftime("%B %Y")
        self.month_label.config(text=month_name)

        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = tk.Label(
                self.calendar_frame,
                text=day,
                font=('Sans', 10, 'bold'),
                bg='#333333',
                fg='#00FFFF',
                width=10,
                height=2
            )
            label.grid(row=0, column=i, padx=1, pady=1, sticky='nsew')

        # Get calendar for current month
        year = self.current_date.year
        month = self.current_date.month
        cal = calendar.monthcalendar(year, month)

        # Create day buttons
        today = datetime.now().date()
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty day
                    frame = tk.Frame(
                        self.calendar_frame,
                        bg='#0a0a0a',
                        width=10,
                        height=8
                    )
                    frame.grid(row=week_num, column=day_num, padx=1, pady=1, sticky='nsew')
                else:
                    # Day button
                    date_obj = datetime(year, month, day).date()
                    is_today = date_obj == today

                    # Check if day has events
                    date_str = date_obj.isoformat()
                    has_event = date_str in self.events

                    bg_color = '#FF00FF' if is_today else ('#333333' if has_event else '#1a1a1a')
                    fg_color = '#000000' if is_today else '#00FF00'

                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        font=('Sans', 12, 'bold' if is_today else 'normal'),
                        bg=bg_color,
                        fg=fg_color,
                        bd=0,
                        cursor='hand2',
                        command=lambda d=date_obj: self.select_day(d)
                    )
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky='nsew')

                    # Event indicator
                    if has_event:
                        indicator = tk.Label(
                            btn,
                            text="●",
                            font=('Sans', 6),
                            bg=bg_color,
                            fg='#FFFF00'
                        )
                        indicator.place(relx=0.9, rely=0.1)

        # Configure grid weights
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame.grid_rowconfigure(i, weight=1)

        self.update_events_list()

    def update_events_list(self):
        """Update upcoming events list"""
        self.events_listbox.delete(0, tk.END)

        # Get upcoming events
        today = datetime.now().date()
        upcoming = []

        for date_str, event_list in self.events.items():
            date_obj = datetime.fromisoformat(date_str).date()
            if date_obj >= today:
                for event in event_list:
                    upcoming.append((date_obj, event))

        # Sort by date
        upcoming.sort(key=lambda x: x[0])

        # Display
        for date_obj, event in upcoming[:10]:  # Show next 10 events
            date_str = date_obj.strftime("%m/%d")
            self.events_listbox.insert(tk.END, f"{date_str} - {event}")

    def prev_month(self):
        """Go to previous month"""
        year = self.current_date.year
        month = self.current_date.month - 1
        if month == 0:
            month = 12
            year -= 1
        self.current_date = datetime(year, month, 1)
        self.update_calendar()

    def next_month(self):
        """Go to next month"""
        year = self.current_date.year
        month = self.current_date.month + 1
        if month == 13:
            month = 1
            year += 1
        self.current_date = datetime(year, month, 1)
        self.update_calendar()

    def go_to_today(self):
        """Go to current month"""
        self.current_date = datetime.now()
        self.update_calendar()

    def select_day(self, date_obj):
        """Handle day selection"""
        date_str = date_obj.isoformat()
        events = self.events.get(date_str, [])

        msg = f"Events on {date_obj.strftime('%B %d, %Y')}:\n\n"
        if events:
            for i, event in enumerate(events, 1):
                msg += f"{i}. {event}\n"
        else:
            msg += "No events"

        messagebox.showinfo("Day Events", msg)

    def add_event(self):
        """Add new event"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Event")
        dialog.geometry("400x250")
        dialog.configure(bg='#1a1a1a')

        tk.Label(
            dialog,
            text="Date (YYYY-MM-DD):",
            bg='#1a1a1a',
            fg='#00FF00',
            font=('Sans', 10)
        ).pack(pady=(20, 5))

        date_entry = tk.Entry(dialog, font=('Sans', 11))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)

        tk.Label(
            dialog,
            text="Event Description:",
            bg='#1a1a1a',
            fg='#00FF00',
            font=('Sans', 10)
        ).pack(pady=(10, 5))

        event_entry = tk.Entry(dialog, font=('Sans', 11), width=40)
        event_entry.pack(pady=5)

        def save_event():
            date_str = date_entry.get()
            event_text = event_entry.get()

            if date_str and event_text:
                if date_str not in self.events:
                    self.events[date_str] = []
                self.events[date_str].append(event_text)
                self.save_events()
                self.update_calendar()
                dialog.destroy()
                messagebox.showinfo("Success", "Event added!")

        tk.Button(
            dialog,
            text="Save Event",
            command=save_event,
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 11, 'bold'),
            bd=0,
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(pady=20)

    def run(self):
        """Run calendar"""
        self.root.mainloop()

if __name__ == '__main__':
    cal = TLCalendar()
    cal.run()
