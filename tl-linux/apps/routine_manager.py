#!/usr/bin/env python3
"""
TL Linux - Routine Manager
Visual routine scheduler for autism/ADHD support
Helps maintain structure and predictability
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import os
import json
from datetime import datetime, time, timedelta
import threading

class RoutineManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Routine Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # Config
        self.config_dir = os.path.expanduser('~/.tl-linux/routines')
        self.routines_file = os.path.join(self.config_dir, 'routines.json')
        os.makedirs(self.config_dir, exist_ok=True)

        # Load routines
        self.routines = self.load_routines()

        # Current routine tracking
        self.current_routine = None
        self.current_step_index = 0
        self.routine_active = False

        # Notification thread
        self.notification_thread = None
        self.running = True

        self.setup_ui()
        self.load_routine_list()
        self.start_notification_checker()

    def load_routines(self):
        """Load saved routines"""
        default_routines = {
            "Morning Routine": {
                "steps": [
                    {"name": "Wake up", "duration": 5, "time": "07:00", "color": "#ffb86c"},
                    {"name": "Shower", "duration": 15, "time": "07:05", "color": "#8be9fd"},
                    {"name": "Get dressed", "duration": 10, "time": "07:20", "color": "#bd93f9"},
                    {"name": "Breakfast", "duration": 20, "time": "07:30", "color": "#50fa7b"},
                    {"name": "Medications", "duration": 5, "time": "07:50", "color": "#ff5555"},
                    {"name": "Leave for work", "duration": 5, "time": "07:55", "color": "#f1fa8c"}
                ],
                "enabled": True,
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "Evening Routine": {
                "steps": [
                    {"name": "Dinner", "duration": 30, "time": "18:00", "color": "#50fa7b"},
                    {"name": "Clean up", "duration": 15, "time": "18:30", "color": "#8be9fd"},
                    {"name": "Free time", "duration": 120, "time": "18:45", "color": "#bd93f9"},
                    {"name": "Wind down", "duration": 30, "time": "20:45", "color": "#ffb86c"},
                    {"name": "Bedtime prep", "duration": 20, "time": "21:15", "color": "#ff79c6"},
                    {"name": "Sleep", "duration": 480, "time": "21:35", "color": "#6272a4"}
                ],
                "enabled": True,
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            }
        }

        try:
            if os.path.exists(self.routines_file):
                with open(self.routines_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default routines
                self.save_routines(default_routines)
                return default_routines
        except:
            return default_routines

    def save_routines(self, routines=None):
        """Save routines to file"""
        if routines is None:
            routines = self.routines

        try:
            with open(self.routines_file, 'w') as f:
                json.dump(routines, f, indent=2)
        except Exception as e:
            print(f"Error saving routines: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📅 Routine Manager",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Add routine button
        tk.Button(
            header,
            text="➕ New Routine",
            command=self.create_routine,
            bg='#50fa7b',
            fg='#000000',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=20)

        # Main content - split into list and detail
        content = tk.Frame(self.root, bg='#1a1a1a')
        content.pack(fill=tk.BOTH, expand=True)

        # Left panel - routine list
        list_panel = tk.Frame(content, bg='#1a1a1a', width=300)
        list_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 5), pady=10)
        list_panel.pack_propagate(False)

        tk.Label(
            list_panel,
            text="Your Routines",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(0, 10))

        # Routine listbox
        list_frame = tk.Frame(list_panel, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.routine_listbox = tk.Listbox(
            list_frame,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 11),
            selectbackground='#4a9eff',
            selectforeground='white',
            bd=0,
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.routine_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.routine_listbox.yview)

        self.routine_listbox.bind('<<ListboxSelect>>', self.on_routine_select)

        # List buttons
        list_btns = tk.Frame(list_panel, bg='#1a1a1a')
        list_btns.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            list_btns,
            text="✏️ Edit",
            command=self.edit_routine,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            list_btns,
            text="🗑️ Delete",
            command=self.delete_routine,
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        # Right panel - routine details
        self.detail_panel = tk.Frame(content, bg='#1a1a1a')
        self.detail_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # Create detail view (initially empty)
        self.create_detail_view()

    def create_detail_view(self):
        """Create the routine detail view"""
        # Clear existing
        for widget in self.detail_panel.winfo_children():
            widget.destroy()

        if not self.current_routine:
            tk.Label(
                self.detail_panel,
                text="Select a routine to view details",
                font=('Arial', 12),
                bg='#1a1a1a',
                fg='#888888'
            ).pack(expand=True)
            return

        # Routine header
        header = tk.Frame(self.detail_panel, bg='#1a1a1a')
        header.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            header,
            text=self.current_routine,
            font=('Arial', 16, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(side=tk.LEFT)

        # Start/Stop button
        routine_data = self.routines[self.current_routine]

        if self.routine_active and self.current_routine == self.current_routine:
            btn_text = "⏸ Stop Routine"
            btn_cmd = self.stop_routine
            btn_color = '#ff5555'
        else:
            btn_text = "▶ Start Routine"
            btn_cmd = self.start_routine
            btn_color = '#50fa7b'

        tk.Button(
            header,
            text=btn_text,
            command=btn_cmd,
            bg=btn_color,
            fg='white' if btn_color == '#ff5555' else '#000000',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)

        # Days active
        days_frame = tk.Frame(self.detail_panel, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        days_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            days_frame,
            text="Active on: " + ", ".join(routine_data.get('days', [])),
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white'
        ).pack(padx=15, pady=10)

        # Visual timeline
        timeline_frame = tk.Frame(self.detail_panel, bg='#1a1a1a')
        timeline_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for timeline
        canvas = tk.Canvas(
            timeline_frame,
            bg='#1a1a1a',
            highlightthickness=0
        )
        canvas.pack(fill=tk.BOTH, expand=True)

        # Draw timeline
        self.draw_timeline(canvas, routine_data['steps'])

    def draw_timeline(self, canvas, steps):
        """Draw visual timeline of routine steps"""
        canvas.update()
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 10:
            width = 600
        if height < 10:
            height = 400

        # Calculate total duration
        total_duration = sum(step['duration'] for step in steps)

        # Starting y position
        y = 50
        step_height = 60
        bar_height = 40

        for i, step in enumerate(steps):
            # Calculate bar width based on duration
            bar_width = (step['duration'] / total_duration) * (width - 200) if total_duration > 0 else 100

            # Draw colored bar
            x1 = 150
            y1 = y
            x2 = x1 + bar_width
            y2 = y1 + bar_height

            color = step.get('color', '#4a9eff')

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=color,
                width=2
            )

            # Draw time
            canvas.create_text(
                100, y + bar_height // 2,
                text=step.get('time', ''),
                fill='white',
                font=('Arial', 10, 'bold'),
                anchor='e'
            )

            # Draw step name
            canvas.create_text(
                x1 + 10, y + 10,
                text=step['name'],
                fill='#000000',
                font=('Arial', 10, 'bold'),
                anchor='w'
            )

            # Draw duration
            canvas.create_text(
                x1 + 10, y + 28,
                text=f"{step['duration']} min",
                fill='#000000',
                font=('Arial', 8),
                anchor='w'
            )

            # Highlight current step if routine is active
            if self.routine_active and i == self.current_step_index:
                canvas.create_rectangle(
                    x1 - 5, y1 - 5, x2 + 5, y2 + 5,
                    outline='#f1fa8c',
                    width=3
                )

                # Add "Current" label
                canvas.create_text(
                    x2 + 50, y + bar_height // 2,
                    text="← Current",
                    fill='#f1fa8c',
                    font=('Arial', 10, 'bold'),
                    anchor='w'
                )

            y += step_height + 10

    def load_routine_list(self):
        """Load routines into listbox"""
        self.routine_listbox.delete(0, tk.END)

        for routine_name in self.routines.keys():
            self.routine_listbox.insert(tk.END, routine_name)

    def on_routine_select(self, event):
        """Handle routine selection"""
        selection = self.routine_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_routine = self.routine_listbox.get(index)
            self.create_detail_view()

    def create_routine(self):
        """Create new routine"""
        name = simpledialog.askstring("New Routine", "Enter routine name:")
        if not name:
            return

        if name in self.routines:
            messagebox.showerror("Error", "A routine with this name already exists")
            return

        # Create empty routine
        self.routines[name] = {
            "steps": [],
            "enabled": True,
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        }

        self.save_routines()
        self.load_routine_list()
        messagebox.showinfo("Success", f"Routine '{name}' created!\n\nNow add steps to your routine.")

    def edit_routine(self):
        """Edit selected routine"""
        if not self.current_routine:
            messagebox.showwarning("No Selection", "Please select a routine to edit")
            return

        editor = tk.Toplevel(self.root)
        editor.title(f"Edit Routine - {self.current_routine}")
        editor.geometry("700x600")
        editor.configure(bg='#2b2b2b')
        editor.transient(self.root)
        editor.grab_set()

        routine_data = self.routines[self.current_routine]

        tk.Label(
            editor,
            text=f"Editing: {self.current_routine}",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)

        # Steps list
        steps_frame = tk.LabelFrame(
            editor,
            text="Routine Steps",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Treeview for steps
        tree = ttk.Treeview(
            steps_frame,
            columns=('Time', 'Duration', 'Color'),
            height=10
        )
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree.heading('#0', text='Step Name')
        tree.heading('Time', text='Time')
        tree.heading('Duration', text='Duration')
        tree.heading('Color', text='Color')

        # Load steps
        def load_steps():
            tree.delete(*tree.get_children())
            for step in routine_data['steps']:
                tree.insert('', tk.END,
                           text=step['name'],
                           values=(step.get('time', ''),
                                  f"{step['duration']} min",
                                  step.get('color', '#4a9eff')))

        load_steps()

        # Buttons
        btn_frame = tk.Frame(steps_frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def add_step():
            # Simple add step dialog
            step_name = simpledialog.askstring("Add Step", "Step name:")
            if not step_name:
                return

            step_time = simpledialog.askstring("Add Step", "Time (HH:MM):", initialvalue="09:00")
            step_duration = simpledialog.askinteger("Add Step", "Duration (minutes):", initialvalue=15)

            if step_duration:
                routine_data['steps'].append({
                    'name': step_name,
                    'time': step_time or "09:00",
                    'duration': step_duration,
                    'color': '#4a9eff'
                })
                load_steps()

        def delete_step():
            selection = tree.selection()
            if selection:
                index = tree.index(selection[0])
                routine_data['steps'].pop(index)
                load_steps()

        tk.Button(btn_frame, text="➕ Add Step", command=add_step,
                 bg='#50fa7b', fg='#000000', bd=0, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Delete", command=delete_step,
                 bg='#ff5555', fg='white', bd=0, padx=15, pady=5).pack(side=tk.LEFT)

        # Save button
        def save():
            self.save_routines()
            self.create_detail_view()
            editor.destroy()
            messagebox.showinfo("Success", "Routine updated!")

        tk.Button(
            editor,
            text="Save Changes",
            command=save,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=10
        ).pack(pady=20)

    def delete_routine(self):
        """Delete selected routine"""
        if not self.current_routine:
            messagebox.showwarning("No Selection", "Please select a routine to delete")
            return

        if messagebox.askyesno("Delete Routine", f"Delete routine '{self.current_routine}'?"):
            del self.routines[self.current_routine]
            self.save_routines()
            self.current_routine = None
            self.load_routine_list()
            self.create_detail_view()

    def start_routine(self):
        """Start the selected routine"""
        if not self.current_routine:
            return

        self.routine_active = True
        self.current_step_index = 0

        self.create_detail_view()

        messagebox.showinfo(
            "Routine Started",
            f"Started routine: {self.current_routine}\n\n"
            f"You'll receive notifications for each step!"
        )

    def stop_routine(self):
        """Stop the active routine"""
        self.routine_active = False
        self.create_detail_view()

    def start_notification_checker(self):
        """Start background thread to check for notifications"""
        def checker():
            while self.running:
                try:
                    if self.routine_active and self.current_routine:
                        self.check_routine_notifications()
                except Exception as e:
                    print(f"Notification error: {e}")

                import time
                time.sleep(30)  # Check every 30 seconds

        self.notification_thread = threading.Thread(target=checker, daemon=True)
        self.notification_thread.start()

    def check_routine_notifications(self):
        """Check if it's time to notify about next step"""
        routine_data = self.routines.get(self.current_routine)
        if not routine_data:
            return

        steps = routine_data['steps']
        if self.current_step_index >= len(steps):
            return

        current_step = steps[self.current_step_index]
        step_time_str = current_step.get('time')

        if not step_time_str:
            return

        # Parse step time
        try:
            step_time_parts = step_time_str.split(':')
            step_hour = int(step_time_parts[0])
            step_minute = int(step_time_parts[1])

            now = datetime.now()
            current_time = now.time()

            # Check if it's time for this step (within 1 minute window)
            if (current_time.hour == step_hour and
                abs(current_time.minute - step_minute) <= 1):

                # Send notification
                self.send_step_notification(current_step)

                # Move to next step
                self.current_step_index += 1
                self.root.after(0, self.create_detail_view)

        except:
            pass

    def send_step_notification(self, step):
        """Send notification for routine step"""
        try:
            import subprocess
            subprocess.run([
                'notify-send',
                f"Routine: {self.current_routine}",
                f"Time for: {step['name']}\n({step['duration']} minutes)",
                '-i', 'appointment-soon',
                '-u', 'normal'
            ])
        except:
            pass

    def run(self):
        """Run the routine manager"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        self.running = False
        self.root.destroy()

def main():
    manager = RoutineManager()
    manager.run()

if __name__ == '__main__':
    main()
