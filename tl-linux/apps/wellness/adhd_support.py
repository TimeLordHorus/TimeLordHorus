#!/usr/bin/env python3
"""
TL Linux - ADHD Support Tools
Tools specifically designed to help with ADHD challenges
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from datetime import datetime
import time

class ADHDSupport:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 ADHD Support Tools")
        self.root.geometry("1000x700")

        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellness'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.config_dir / 'adhd_data.json'

        self.data = self.load_data()
        self.timer_running = False
        self.timer_seconds = 0
        self.setup_ui()

    def load_data(self):
        """Load ADHD data"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'routines': [],
            'tasks': [],
            'focus_sessions': [],
            'rewards': []
        }

    def save_data(self):
        """Save ADHD data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg='#FF9800', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🎯 ADHD Support Tools",
            font=('Arial', 18, 'bold'),
            bg='#FF9800',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Executive function support and focus tools",
            font=('Arial', 10),
            bg='#FF9800',
            fg='white'
        ).pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg='#2c3e50', width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tools = [
            ('⏱️ Focus Timer', self.show_focus_timer),
            ('📋 Task Breakdown', self.show_task_breakdown),
            ('🔄 Routine Builder', self.show_routine_builder),
            ('🧩 Body Doubling', self.show_body_doubling),
            ('🎁 Reward System', self.show_rewards),
            ('💡 ADHD Tips', self.show_tips),
        ]

        for tool_name, command in tools:
            btn = tk.Button(
                sidebar,
                text=tool_name,
                command=command,
                bg='#34495e',
                fg='white',
                font=('Arial', 11),
                relief=tk.FLAT,
                anchor='w',
                padx=20,
                pady=12,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=5, pady=3)

        # Content area
        self.content_frame = tk.Frame(main_container, bg='white')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_focus_timer()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_focus_timer(self):
        """Show Pomodoro-style focus timer"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="⏱️ Focus Timer (Pomodoro)",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Work in focused bursts with regular breaks",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Timer display
        self.timer_label = tk.Label(
            self.content_frame,
            text="25:00",
            font=('Arial', 72, 'bold'),
            bg='white',
            fg='#FF9800'
        )
        self.timer_label.pack(pady=30)

        # Timer type
        timer_frame = tk.Frame(self.content_frame, bg='white')
        timer_frame.pack(pady=20)

        timer_types = [
            ("🎯 Focus (25 min)", 25 * 60),
            ("☕ Short Break (5 min)", 5 * 60),
            ("🌴 Long Break (15 min)", 15 * 60),
        ]

        for label, seconds in timer_types:
            btn = tk.Button(
                timer_frame,
                text=label,
                command=lambda s=seconds: self.set_timer(s),
                bg='#FFF3E0',
                fg='#2c3e50',
                font=('Arial', 11),
                relief=tk.FLAT,
                padx=15,
                pady=10,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Control buttons
        control_frame = tk.Frame(self.content_frame, bg='white')
        control_frame.pack(pady=20)

        self.start_btn = tk.Button(
            control_frame,
            text="▶ Start",
            command=self.start_timer,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 14, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=15,
            cursor='hand2'
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            control_frame,
            text="⏸ Pause",
            command=self.stop_timer,
            bg='#F44336',
            fg='white',
            font=('Arial', 14, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=15,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Task entry
        tk.Label(
            self.content_frame,
            text="What are you working on?",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(20, 5))

        self.task_entry = tk.Entry(
            self.content_frame,
            font=('Arial', 12)
        )
        self.task_entry.pack(fill=tk.X, pady=(0, 10))

        # Tips
        tips_frame = tk.Frame(self.content_frame, bg='#FFF9C4', relief=tk.SOLID, borderwidth=1)
        tips_frame.pack(fill=tk.X, pady=20)

        tips_text = """
        💡 Pomodoro Tips:
        • Remove distractions before starting
        • Focus on ONE task during timer
        • Take breaks seriously - move, stretch, hydrate
        • After 4 focus sessions, take a longer break
        • If you get distracted, note it and return to task
        """

        tk.Label(
            tips_frame,
            text=tips_text,
            font=('Arial', 9),
            bg='#FFF9C4',
            fg='#666',
            justify=tk.LEFT
        ).pack(padx=15, pady=10, anchor='w')

    def set_timer(self, seconds):
        """Set timer duration"""
        self.timer_seconds = seconds
        minutes = seconds // 60
        secs = seconds % 60
        self.timer_label.config(text=f"{minutes:02d}:{secs:02d}")

    def start_timer(self):
        """Start the focus timer"""
        self.timer_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.update_timer()

    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def update_timer(self):
        """Update timer countdown"""
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            minutes = self.timer_seconds // 60
            secs = self.timer_seconds % 60
            self.timer_label.config(text=f"{minutes:02d}:{secs:02d}")
            self.root.after(1000, self.update_timer)
        elif self.timer_seconds == 0 and self.timer_running:
            self.timer_complete()

    def timer_complete(self):
        """Handle timer completion"""
        self.timer_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.timer_label.config(text="00:00")

        # Save session
        if self.task_entry.get():
            session = {
                'timestamp': datetime.now().isoformat(),
                'task': self.task_entry.get()
            }
            self.data['focus_sessions'].append(session)
            self.save_data()

        messagebox.showinfo("Timer Complete", "Great work! Time for a break! 🎉")

    def show_task_breakdown(self):
        """Show task breakdown tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="📋 Task Breakdown",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Break big tasks into tiny, manageable steps",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Big task
        tk.Label(
            self.content_frame,
            text="Big Task (What seems overwhelming?):",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        big_task_entry = tk.Entry(
            self.content_frame,
            font=('Arial', 12)
        )
        big_task_entry.pack(fill=tk.X, pady=(0, 20))

        # Small steps
        tk.Label(
            self.content_frame,
            text="Break it down into TINY steps (each 5-10 minutes):",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        steps_frame = tk.Frame(self.content_frame, bg='white')
        steps_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable steps
        canvas = tk.Canvas(steps_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(steps_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Step entries
        step_entries = []
        for i in range(10):
            step_frame = tk.Frame(scrollable_frame, bg='white')
            step_frame.pack(fill=tk.X, pady=3)

            tk.Label(
                step_frame,
                text=f"{i+1}.",
                font=('Arial', 10),
                bg='white',
                width=3
            ).pack(side=tk.LEFT)

            entry = tk.Entry(
                step_frame,
                font=('Arial', 10)
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            step_entries.append(entry)

            check_var = tk.BooleanVar()
            check = tk.Checkbutton(
                step_frame,
                text="Done",
                variable=check_var,
                bg='white'
            )
            check.pack(side=tk.LEFT)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tips
        tips_frame = tk.Frame(self.content_frame, bg='#E3F2FD', relief=tk.SOLID, borderwidth=1)
        tips_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)

        tips = """
        💡 Breakdown Tips:
        • Make steps RIDICULOUSLY small
        • Each step should take 5-10 minutes max
        • Start with the absolute tiniest first step
        • Example bad: "Clean room" → Example good: "Pick up 5 items"
        • Celebrate completing each tiny step!
        """

        tk.Label(
            tips_frame,
            text=tips,
            font=('Arial', 9),
            bg='#E3F2FD',
            fg='#666',
            justify=tk.LEFT
        ).pack(padx=15, pady=10, anchor='w')

    def show_routine_builder(self):
        """Show routine building tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🔄 Routine Builder",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Create visual routines with time estimates",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Routine templates
        templates = [
            ("🌅 Morning Routine", [
                "Wake up & stretch (2 min)",
                "Drink water (1 min)",
                "Take medication (2 min)",
                "Shower (10 min)",
                "Get dressed (5 min)",
                "Eat breakfast (15 min)",
                "Brush teeth (3 min)"
            ]),
            ("🌙 Evening Routine", [
                "Set out tomorrow's clothes (5 min)",
                "Prepare tomorrow's lunch (10 min)",
                "Shower (10 min)",
                "Skincare routine (5 min)",
                "Lay out everything needed (5 min)",
                "Set alarms (2 min)",
                "Read/relax (20 min)"
            ]),
            ("💼 Work Start Routine", [
                "Clear desk (3 min)",
                "Check calendar (2 min)",
                "Review task list (3 min)",
                "Pick top 3 priorities (2 min)",
                "Start timer for first task"
            ])
        ]

        for routine_name, steps in templates:
            frame = tk.LabelFrame(
                self.content_frame,
                text=routine_name,
                font=('Arial', 12, 'bold'),
                bg='white',
                padx=15,
                pady=10
            )
            frame.pack(fill=tk.X, pady=10)

            for step in steps:
                step_frame = tk.Frame(frame, bg='white')
                step_frame.pack(fill=tk.X, pady=2)

                check_var = tk.BooleanVar()
                check = tk.Checkbutton(
                    step_frame,
                    text=step,
                    variable=check_var,
                    bg='white',
                    font=('Arial', 10)
                )
                check.pack(side=tk.LEFT)

        # Tips
        tips_frame = tk.Frame(self.content_frame, bg='#FFF9C4', relief=tk.SOLID, borderwidth=1)
        tips_frame.pack(fill=tk.X, pady=10)

        tips = """
        🔄 Routine Tips:
        • Keep routines visible (print them out!)
        • Include time estimates for each step
        • Use visual reminders (photos, icons)
        • Build in buffer time
        • Start with just 3-4 essential steps
        • Use alarms/timers as reminders
        """

        tk.Label(
            tips_frame,
            text=tips,
            font=('Arial', 9),
            bg='#FFF9C4',
            fg='#666',
            justify=tk.LEFT
        ).pack(padx=15, pady=10, anchor='w')

    def show_body_doubling(self):
        """Show body doubling explanation"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🧩 Body Doubling",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Work alongside others for motivation and accountability",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        content = """
        🧩 What is Body Doubling?

        Body doubling is working on tasks while someone else is present,
        either in-person or virtually. Their presence helps you:

        ✓ Get started on tasks (hardest part for ADHD)
        ✓ Stay focused and on track
        ✓ Feel accountable
        ✓ Reduce anxiety about boring tasks
        ✓ Combat loneliness while working

        How to Use Body Doubling:

        In-Person:
        • Work at a coffee shop or library
        • Study with friends (parallel working)
        • Ask family member to sit nearby while you work
        • Join a co-working space

        Virtual:
        • Join online body doubling sessions
        • Video call a friend while both work
        • Use Discord/Zoom study rooms
        • Live streams of people working

        Body Doubling Rules:
        1. Both people work on their own tasks
        2. Minimal talking - just presence
        3. Set specific work time (like Pomodoro)
        4. Optional: quick check-ins at start/end
        5. No judgment - just support

        Why It Works:
        ADHD brains often need external structure and
        accountability. Another person's presence provides
        this naturally, making it easier to focus.

        Try It:
        • Start with just 25 minutes
        • Find a body doubling buddy or online community
        • Notice how much easier it is to start and focus!
        """

        tk.Label(
            self.content_frame,
            text=content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def show_rewards(self):
        """Show reward system"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎁 Reward System",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Motivate yourself with immediate rewards",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        content = """
        🎁 ADHD-Friendly Reward System

        ADHD brains need immediate rewards to stay motivated!

        Small Task Rewards (5-10 min task):
        ☕ Favorite beverage
        🎵 One song break
        📱 5 min phone time
        🍫 Small snack
        🎮 5 min game
        📺 One short video

        Medium Task Rewards (30-60 min task):
        🎬 Watch one episode
        📖 Read for pleasure
        🎨 Creative hobby time
        🚶 Walk outside
        📞 Call a friend
        🛁 Relaxing bath

        Big Task Rewards (completed project):
        🎁 Buy something you want
        🍕 Favorite restaurant
        🎮 New game
        📚 New book
        🎉 Plan fun activity
        💆 Spa/self-care treat

        Rules for Success:
        1. Pick reward BEFORE starting task
        2. Make it proportional to task difficulty
        3. Actually take the reward (don't skip it!)
        4. No earning rewards without doing task
        5. Make rewards immediate
        6. Vary rewards to keep them interesting

        Reward Ideas List:
        □ _______________________
        □ _______________________
        □ _______________________
        □ _______________________
        □ _______________________

        Write your personal rewards above!
        """

        tk.Label(
            self.content_frame,
            text=content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def show_tips(self):
        """Show ADHD tips and strategies"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="💡 ADHD Tips & Strategies",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Practical strategies for daily challenges",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Create notebook
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Time Management
        time_frame = tk.Frame(notebook, bg='white')
        notebook.add(time_frame, text='Time Management')

        time_tips = """
        ⏰ Time Management with ADHD

        • Use visual timers (see time passing)
        • Set multiple alarms with labels
        • Time blindness is real - track everything
        • Add 50% buffer time to estimates
        • Use "time boxing" - set limits on tasks
        • Schedule breaks or you'll forget them
        • Use calendar for EVERYTHING
        • Set "preparing to leave" alarms
        • Keep clocks visible everywhere
        • Use Pomodoro technique (25 min work, 5 min break)
        """

        tk.Label(
            time_frame,
            text=time_tips,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Organization
        org_frame = tk.Frame(notebook, bg='white')
        notebook.add(org_frame, text='Organization')

        org_tips = """
        📦 Organization Strategies

        • Everything needs a HOME
        • Label EVERYTHING
        • Clear containers (see what's inside)
        • Minimize steps to put things away
        • Use color coding
        • Keep important items in same spot ALWAYS
        • Put things where you naturally drop them
        • "Don't put it down, put it away"
        • Declutter regularly - less stuff = less lost
        • Take photos of organization systems
        • Use hooks instead of hangers
        • Duplicate important items (keys, chargers)
        """

        tk.Label(
            org_frame,
            text=org_tips,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Focus
        focus_frame = tk.Frame(notebook, bg='white')
        notebook.add(focus_frame, text='Focus')

        focus_tips = """
        🎯 Improving Focus

        • Remove distractions BEFORE starting
        • Use website blockers during focus time
        • Noise-cancelling headphones
        • White noise or focus music
        • Work in short bursts (25 min)
        • Change locations to reset focus
        • Stand/walk while working
        • Fidget tools (spinners, putty)
        • Work during your peak energy time
        • Eat protein before focus work
        • Stay hydrated
        • Exercise before difficult tasks
        • "Everything shower" to reset
        """

        tk.Label(
            focus_frame,
            text=focus_tips,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Motivation
        motivation_frame = tk.Frame(notebook, bg='white')
        notebook.add(motivation_frame, text='Motivation')

        motivation_tips = """
        🚀 Staying Motivated

        • Make tasks more interesting/challenging
        • Work with others (body doubling)
        • Create urgency with deadlines
        • Break tasks into tiny pieces
        • Start with the easiest part
        • Use rewards liberally
        • Make tasks visible (sticky notes)
        • Tell someone your plan (accountability)
        • Connect tasks to your values
        • Focus on progress, not perfection
        • Celebrate small wins
        • Use momentum (do multiple tasks in a row)
        • "10-minute rule" - just start for 10 min
        """

        tk.Label(
            motivation_frame,
            text=motivation_tips,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == '__main__':
    app = ADHDSupport()
    app.run()
