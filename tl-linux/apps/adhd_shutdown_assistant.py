#!/usr/bin/env python3
"""
TL Linux - ADHD-Friendly Shutdown Assistant

Helps users transition off the computer by:
- Celebrating accomplishments (dopamine reward)
- Breaking down next tasks (reduce paralysis)
- Providing motivation and structure
- Managing task transitions smoothly
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime, timedelta
import subprocess

class ADHDShutdownAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Transition Assistant")
        self.root.geometry("800x900")
        self.root.configure(bg='#2b2b2b')

        # Load user data
        self.data_dir = os.path.expanduser('~/.tl-linux/adhd_assistant')
        os.makedirs(self.data_dir, exist_ok=True)

        self.session_file = os.path.join(self.data_dir, 'sessions.json')
        self.goals_file = os.path.join(self.data_dir, 'goals.json')

        self.sessions = self.load_json(self.session_file, [])
        self.goals = self.load_json(self.goals_file, {
            'daily_goals': [],
            'weekly_goals': [],
            'accomplishments': []
        })

        # Track current session
        self.current_session = {
            'start_time': datetime.now().isoformat(),
            'accomplishments': [],
            'next_task': '',
            'next_task_steps': [],
            'transition_notes': ''
        }

        # Current page
        self.current_page = 0
        self.pages = []

        self.setup_ui()

    def load_json(self, filepath, default):
        """Load JSON data with fallback"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except:
            pass
        return default

    def save_json(self, filepath, data):
        """Save JSON data"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")

    def setup_ui(self):
        """Create the multi-page wizard UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="🌊 Time to Transition",
            font=('Arial', 24, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        )
        title.pack(pady=20)

        # Content area
        self.content_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30)

        # Navigation
        nav_frame = tk.Frame(self.root, bg='#2b2b2b', height=100)
        nav_frame.pack(fill=tk.X, pady=20, padx=30)
        nav_frame.pack_propagate(False)

        self.prev_btn = tk.Button(
            nav_frame,
            text="← Back",
            command=self.prev_page,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.prev_btn.pack(side=tk.LEFT)

        self.page_label = tk.Label(
            nav_frame,
            text="Step 1 of 6",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.page_label.pack(side=tk.LEFT, padx=20)

        self.next_btn = tk.Button(
            nav_frame,
            text="Next →",
            command=self.next_page,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=10
        )
        self.next_btn.pack(side=tk.RIGHT)

        self.skip_btn = tk.Button(
            nav_frame,
            text="Skip This Step",
            command=self.next_page,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            bd=0,
            padx=10
        )
        self.skip_btn.pack(side=tk.RIGHT, padx=10)

        # Build pages
        self.build_pages()
        self.show_page(0)

    def build_pages(self):
        """Build all wizard pages"""
        self.pages = [
            self.build_celebration_page,
            self.build_session_review_page,
            self.build_next_task_page,
            self.build_task_breakdown_page,
            self.build_motivation_page,
            self.build_final_page
        ]

    def build_celebration_page(self):
        """Page 1: Celebrate what you did!"""
        frame = tk.Frame(self.content_frame, bg='#2b2b2b')

        tk.Label(
            frame,
            text="🎉 Let's Celebrate Your Session!",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text="You showed up and used your computer with intention.\nThat's worth celebrating! What did you accomplish?",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#cccccc',
            justify=tk.CENTER
        ).pack(pady=(0, 30))

        # Accomplishment checklist
        tk.Label(
            frame,
            text="Check off what you did (dopamine boost! ✨):",
            font=('Arial', 13, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(0, 10))

        # Pre-defined accomplishments
        accomplishment_frame = tk.Frame(frame, bg='#2b2b2b')
        accomplishment_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.accomplishment_vars = []
        predefined = [
            "Completed a task I've been putting off",
            "Learned something new",
            "Communicated with someone",
            "Created something",
            "Organized or cleaned up files",
            "Made progress on a project",
            "Solved a problem",
            "Helped someone else"
        ]

        for item in predefined:
            var = tk.BooleanVar()
            self.accomplishment_vars.append((var, item))

            cb = tk.Checkbutton(
                accomplishment_frame,
                text=item,
                variable=var,
                font=('Arial', 11),
                bg='#2b2b2b',
                fg='#cccccc',
                selectcolor='#1a1a1a',
                activebackground='#2b2b2b',
                activeforeground='white',
                command=self.play_check_sound
            )
            cb.pack(anchor='w', pady=5)

        # Custom accomplishment
        tk.Label(
            frame,
            text="Or add your own:",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(anchor='w', pady=(10, 5))

        self.custom_accomplishment = scrolledtext.ScrolledText(
            frame,
            height=3,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.custom_accomplishment.pack(fill=tk.X, pady=(0, 10))

        return frame

    def build_session_review_page(self):
        """Page 2: Review session stats"""
        frame = tk.Frame(self.content_frame, bg='#2b2b2b')

        tk.Label(
            frame,
            text="📊 Your Session Summary",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text="Here's what your session looked like:",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(pady=(0, 30))

        # Stats container
        stats_container = tk.Frame(frame, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Get session stats (simulated for now - would integrate with user learning model)
        stats = self.get_session_stats()

        # Display stats
        for stat_name, stat_value in stats.items():
            stat_frame = tk.Frame(stats_container, bg='#1a1a1a')
            stat_frame.pack(fill=tk.X, padx=20, pady=15)

            tk.Label(
                stat_frame,
                text=stat_name,
                font=('Arial', 11),
                bg='#1a1a1a',
                fg='#888888'
            ).pack(side=tk.LEFT)

            tk.Label(
                stat_frame,
                text=stat_value,
                font=('Arial', 13, 'bold'),
                bg='#1a1a1a',
                fg='#4a9eff'
            ).pack(side=tk.RIGHT)

        # Reflection question
        tk.Label(
            frame,
            text="Quick reflection (optional):",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(20, 5))

        tk.Label(
            frame,
            text="How do you feel about this session? Any insights?",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(anchor='w', pady=(0, 5))

        self.session_reflection = scrolledtext.ScrolledText(
            frame,
            height=4,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.session_reflection.pack(fill=tk.X, pady=(0, 10))

        return frame

    def build_next_task_page(self):
        """Page 3: What's next?"""
        frame = tk.Frame(self.content_frame, bg='#2b2b2b')

        tk.Label(
            frame,
            text="🎯 What Happens Next?",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text="Let's plan your transition off the computer.\nThis helps reduce that 'what now?' paralysis.",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#cccccc',
            justify=tk.CENTER
        ).pack(pady=(0, 30))

        # Next task input
        tk.Label(
            frame,
            text="What's the NEXT THING you need/want to do?",
            font=('Arial', 13, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            frame,
            text="Don't overthink it. Just the immediate next action.",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            justify=tk.LEFT
        ).pack(anchor='w', pady=(0, 10))

        self.next_task_entry = tk.Entry(
            frame,
            font=('Arial', 14),
            bg='#1a1a1a',
            fg='white',
            insertbackground='white'
        )
        self.next_task_entry.pack(fill=tk.X, pady=(0, 30), ipady=10)

        # Quick suggestions
        tk.Label(
            frame,
            text="Common next tasks (click to use):",
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(anchor='w', pady=(0, 10))

        suggestions_frame = tk.Frame(frame, bg='#2b2b2b')
        suggestions_frame.pack(fill=tk.BOTH, expand=True)

        suggestions = [
            ("🍽️", "Eat a meal or snack"),
            ("🚶", "Take a walk or move body"),
            ("💧", "Drink water"),
            ("🛁", "Personal hygiene"),
            ("🧹", "Tidy one area"),
            ("📞", "Call/text someone"),
            ("📚", "Read something"),
            ("😴", "Rest or nap"),
            ("🎮", "Recreational activity"),
            ("📋", "Check to-do list")
        ]

        for i, (emoji, text) in enumerate(suggestions):
            btn = tk.Button(
                suggestions_frame,
                text=f"{emoji} {text}",
                command=lambda t=text: self.set_next_task(t),
                font=('Arial', 10),
                bg='#3a3a3a',
                fg='white',
                padx=10,
                pady=8,
                bd=0,
                anchor='w'
            )
            btn.pack(fill=tk.X, pady=2)

        return frame

    def build_task_breakdown_page(self):
        """Page 4: Break down the task"""
        frame = tk.Frame(self.content_frame, bg='#2b2b2b')

        tk.Label(
            frame,
            text="🔨 Break It Down",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text="Task paralysis happens when tasks feel too big.\nLet's break yours into tiny, doable steps.",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#cccccc',
            justify=tk.CENTER
        ).pack(pady=(0, 20))

        # Show the task
        task_display_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        task_display_frame.pack(fill=tk.X, pady=(0, 20), padx=20)

        tk.Label(
            task_display_frame,
            text="Your next task:",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888'
        ).pack(anchor='w', padx=15, pady=(10, 5))

        self.task_display_label = tk.Label(
            task_display_frame,
            text="",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff',
            wraplength=700,
            justify=tk.LEFT
        )
        self.task_display_label.pack(anchor='w', padx=15, pady=(0, 10))

        # First step (most important!)
        tk.Label(
            frame,
            text="What's the VERY FIRST physical action?",
            font=('Arial', 13, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(10, 5))

        tk.Label(
            frame,
            text="Example: 'Stand up' or 'Pick up phone' - make it stupidly small!",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(anchor='w', pady=(0, 10))

        self.first_step_entry = tk.Entry(
            frame,
            font=('Arial', 13),
            bg='#1a1a1a',
            fg='white',
            insertbackground='white'
        )
        self.first_step_entry.pack(fill=tk.X, ipady=8, pady=(0, 20))

        # Additional steps
        tk.Label(
            frame,
            text="What are 2-3 steps after that? (optional)",
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(anchor='w', pady=(0, 10))

        self.additional_steps = scrolledtext.ScrolledText(
            frame,
            height=4,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.additional_steps.pack(fill=tk.X, pady=(0, 10))
        self.additional_steps.insert('1.0', 'One step per line...')
        self.additional_steps.bind('<FocusIn>', lambda e: self.clear_placeholder(self.additional_steps, 'One step per line...'))

        # Time estimate
        tk.Label(
            frame,
            text="How long will this take? (helps with time blindness)",
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(anchor='w', pady=(10, 10))

        time_frame = tk.Frame(frame, bg='#2b2b2b')
        time_frame.pack(fill=tk.X, pady=(0, 10))

        self.time_estimate_var = tk.StringVar(value="15")

        for minutes in [5, 10, 15, 30, 60]:
            rb = tk.Radiobutton(
                time_frame,
                text=f"{minutes} min",
                variable=self.time_estimate_var,
                value=str(minutes),
                font=('Arial', 10),
                bg='#2b2b2b',
                fg='#cccccc',
                selectcolor='#1a1a1a',
                activebackground='#2b2b2b'
            )
            rb.pack(side=tk.LEFT, padx=10)

        return frame

    def build_motivation_page(self):
        """Page 5: Motivation and encouragement"""
        frame = tk.Frame(self.content_frame, bg='#2b2b2b')

        tk.Label(
            frame,
            text="💪 You've Got This!",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(0, 10))

        # Personalized motivation
        motivation_text = self.get_personalized_motivation()

        tk.Label(
            frame,
            text=motivation_text,
            font=('Arial', 13),
            bg='#2b2b2b',
            fg='#cccccc',
            wraplength=700,
            justify=tk.CENTER
        ).pack(pady=(0, 30))

        # Transition breathing
        breathing_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        breathing_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            breathing_frame,
            text="🫁 Optional: 30-Second Transition Breathing",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=(15, 10))

        tk.Label(
            breathing_frame,
            text="Help your brain switch gears with a quick breathing exercise.\nThis can reduce that 'stuck' feeling.",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            justify=tk.CENTER
        ).pack(pady=(0, 10))

        self.breathing_btn = tk.Button(
            breathing_frame,
            text="▶ Start Breathing Exercise",
            command=self.start_breathing_exercise,
            font=('Arial', 11, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        )
        self.breathing_btn.pack(pady=(0, 15))

        self.breathing_label = tk.Label(
            breathing_frame,
            text="",
            font=('Arial', 16, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        )
        self.breathing_label.pack(pady=(0, 10))

        # Set reminder/alarm
        reminder_frame = tk.Frame(frame, bg='#2b2b2b')
        reminder_frame.pack(fill=tk.X, pady=20)

        tk.Label(
            reminder_frame,
            text="⏰ Want a reminder to get started?",
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', pady=(0, 10))

        self.reminder_var = tk.BooleanVar()
        tk.Checkbutton(
            reminder_frame,
            text="Set a reminder/alarm",
            variable=self.reminder_var,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            selectcolor='#1a1a1a'
        ).pack(anchor='w')

        return frame

    def build_final_page(self):
        """Page 6: Summary and shutdown"""
        frame = tk.Frame(self.content_frame, bg='#2b2b2b')

        tk.Label(
            frame,
            text="✨ Ready for Your Next Adventure!",
            font=('Arial', 20, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text="Here's your transition plan:",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#cccccc'
        ).pack(pady=(0, 30))

        # Summary container
        summary_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.summary_text = scrolledtext.ScrolledText(
            summary_frame,
            height=15,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#cccccc',
            wrap=tk.WORD,
            state='disabled'
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Action buttons
        action_frame = tk.Frame(frame, bg='#2b2b2b')
        action_frame.pack(fill=tk.X, pady=20)

        tk.Button(
            action_frame,
            text="📋 Save Plan & Keep Computer On",
            command=self.save_and_stay,
            font=('Arial', 11),
            bg='#3a3a3a',
            fg='white',
            padx=20,
            pady=12,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            action_frame,
            text="🔒 Save Plan & Lock Screen",
            command=self.save_and_lock,
            font=('Arial', 11),
            bg='#6a6a6a',
            fg='white',
            padx=20,
            pady=12,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            action_frame,
            text="⚡ Save Plan & Shutdown",
            command=self.save_and_shutdown,
            font=('Arial', 11, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=12,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def show_page(self, page_num):
        """Display specific page"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Build and show page
        if 0 <= page_num < len(self.pages):
            page_widget = self.pages[page_num]()
            page_widget.pack(fill=tk.BOTH, expand=True)

            self.current_page = page_num

            # Update navigation
            self.page_label.config(text=f"Step {page_num + 1} of {len(self.pages)}")

            self.prev_btn.config(state='normal' if page_num > 0 else 'disabled')

            if page_num == len(self.pages) - 1:
                self.next_btn.pack_forget()
                self.skip_btn.pack_forget()
            else:
                self.next_btn.config(text="Next →")

            # Special handling for final page
            if page_num == len(self.pages) - 1:
                self.populate_summary()

    def next_page(self):
        """Go to next page"""
        # Save current page data
        self.save_page_data()

        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)

            # Update task display on breakdown page
            if self.current_page == 3:  # Task breakdown page
                task = self.next_task_entry.get() if hasattr(self, 'next_task_entry') else ''
                self.task_display_label.config(text=task or "No task specified")

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def save_page_data(self):
        """Save data from current page"""
        if self.current_page == 0:  # Celebration page
            accomplishments = []
            for var, text in self.accomplishment_vars:
                if var.get():
                    accomplishments.append(text)

            custom = self.custom_accomplishment.get('1.0', 'end-1c').strip()
            if custom:
                accomplishments.append(custom)

            self.current_session['accomplishments'] = accomplishments

        elif self.current_page == 1:  # Session review
            reflection = self.session_reflection.get('1.0', 'end-1c').strip()
            self.current_session['reflection'] = reflection

        elif self.current_page == 2:  # Next task
            self.current_session['next_task'] = self.next_task_entry.get()

        elif self.current_page == 3:  # Task breakdown
            first_step = self.first_step_entry.get()
            additional = self.additional_steps.get('1.0', 'end-1c').strip()

            steps = [first_step] if first_step else []
            if additional and additional != 'One step per line...':
                steps.extend([s.strip() for s in additional.split('\n') if s.strip()])

            self.current_session['next_task_steps'] = steps
            self.current_session['time_estimate'] = int(self.time_estimate_var.get())

        elif self.current_page == 4:  # Motivation
            self.current_session['wants_reminder'] = self.reminder_var.get()

    def populate_summary(self):
        """Fill in the final summary"""
        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', tk.END)

        summary = "🎉 SESSION ACCOMPLISHMENTS\n"
        summary += "=" * 50 + "\n\n"

        if self.current_session.get('accomplishments'):
            for acc in self.current_session['accomplishments']:
                summary += f"✓ {acc}\n"
        else:
            summary += "You showed up - that counts!\n"

        summary += "\n" + "=" * 50 + "\n\n"
        summary += "🎯 YOUR NEXT TASK\n"
        summary += "=" * 50 + "\n\n"

        next_task = self.current_session.get('next_task', 'Take a break')
        summary += f"Task: {next_task}\n\n"

        if self.current_session.get('next_task_steps'):
            summary += "Steps:\n"
            for i, step in enumerate(self.current_session['next_task_steps'], 1):
                summary += f"  {i}. {step}\n"
            summary += "\n"

        time_est = self.current_session.get('time_estimate', 15)
        summary += f"Estimated time: {time_est} minutes\n\n"

        summary += "=" * 50 + "\n\n"
        summary += "💡 REMEMBER\n"
        summary += "=" * 50 + "\n\n"
        summary += "• The first step is the hardest - just do that one thing\n"
        summary += "• It's okay if it takes longer than expected\n"
        summary += "• You can take breaks - this isn't a race\n"
        summary += "• Progress > Perfection\n\n"

        if self.current_session.get('wants_reminder'):
            summary += "⏰ Reminder will be set for you to start!\n\n"

        summary += "You've got this! 💪"

        self.summary_text.insert('1.0', summary)
        self.summary_text.config(state='disabled')

    def set_next_task(self, task):
        """Set the next task from suggestion"""
        self.next_task_entry.delete(0, tk.END)
        self.next_task_entry.insert(0, task)

    def clear_placeholder(self, widget, placeholder):
        """Clear placeholder text on focus"""
        current = widget.get('1.0', 'end-1c')
        if current == placeholder:
            widget.delete('1.0', tk.END)

    def play_check_sound(self):
        """Play satisfying sound when checkbox checked"""
        # Could play a sound here for dopamine boost
        pass

    def get_session_stats(self):
        """Get current session statistics"""
        # Would integrate with user learning model
        # For now, return simulated data
        return {
            "Session Length": "2 hours 15 minutes",
            "Apps Used": "3 applications",
            "Most Used": "Text Editor (45 min)",
            "Breaks Taken": "2 breaks",
            "Focus Score": "8/10 ⭐"
        }

    def get_personalized_motivation(self):
        """Get personalized motivational message"""
        messages = [
            "You've already done the hard part - you engaged with your tasks. Now it's time to refuel and reset. The next task doesn't have to be perfect, it just has to be started.",

            "Remember: Your brain works differently, and that's a strength. You've shown up today. Now give yourself permission to transition at your own pace.",

            "Task initiation is tough with ADHD - but you've already proven you can do hard things today. The first step is always the hardest. Just focus on that one tiny action.",

            "You don't owe anyone productivity. But if this next task matters to YOU, breaking it down makes it doable. One small step at a time.",

            "Your accomplishments today count, no matter how small they feel. Now let's make the transition to what's next just as manageable."
        ]

        import random
        return random.choice(messages)

    def start_breathing_exercise(self):
        """Guided breathing exercise"""
        self.breathing_btn.config(state='disabled')

        sequence = [
            ("Breathe in...", 4000, '#4a9eff'),
            ("Hold...", 4000, '#ffd700'),
            ("Breathe out...", 6000, '#90ee90'),
            ("Almost done...", 2000, '#888888'),
            ("Breathe in...", 4000, '#4a9eff'),
            ("Hold...", 4000, '#ffd700'),
            ("Breathe out...", 6000, '#90ee90'),
            ("Complete! ✓", 2000, '#4a9eff')
        ]

        def show_instruction(index=0):
            if index < len(sequence):
                text, duration, color = sequence[index]
                self.breathing_label.config(text=text, fg=color)
                self.root.after(duration, lambda: show_instruction(index + 1))
            else:
                self.breathing_btn.config(state='normal')
                self.breathing_label.config(text="")

        show_instruction()

    def save_and_stay(self):
        """Save session and stay logged in"""
        self.save_session()
        messagebox.showinfo(
            "Plan Saved!",
            "Your transition plan has been saved.\nYou can access it anytime from the Wellness Hub.\n\nGood luck with your next task! 💪"
        )
        self.root.destroy()

    def save_and_lock(self):
        """Save session and lock screen"""
        self.save_session()
        messagebox.showinfo(
            "Locking Screen",
            "Your plan is saved. Locking screen now...\n\nSee you soon! 🔒"
        )
        # Lock screen command
        try:
            subprocess.Popen(['gnome-screensaver-command', '-l'])
        except:
            try:
                subprocess.Popen(['xdg-screensaver', 'lock'])
            except:
                pass
        self.root.destroy()

    def save_and_shutdown(self):
        """Save session and shutdown"""
        self.save_session()

        response = messagebox.askyesno(
            "Confirm Shutdown",
            "Your plan is saved!\n\nReady to shutdown the computer?\n\nRemember: " +
            (self.current_session.get('next_task_steps', ['Your next step'])[0] if self.current_session.get('next_task_steps') else 'Take care of yourself!')
        )

        if response:
            try:
                subprocess.Popen(['systemctl', 'poweroff'])
            except:
                messagebox.showerror("Error", "Could not initiate shutdown. Please shutdown manually.")

        self.root.destroy()

    def save_session(self):
        """Save session data"""
        self.save_page_data()

        # Add timestamp
        self.current_session['end_time'] = datetime.now().isoformat()

        # Save to history
        self.sessions.append(self.current_session)
        self.save_json(self.session_file, self.sessions)

        # Update goals
        if self.current_session.get('accomplishments'):
            self.goals['accomplishments'].extend(self.current_session['accomplishments'])
            self.save_json(self.goals_file, self.goals)

        # Set reminder if requested
        if self.current_session.get('wants_reminder'):
            self.set_reminder()

    def set_reminder(self):
        """Set a system reminder/notification"""
        time_est = self.current_session.get('time_estimate', 5)
        task = self.current_session.get('next_task', 'your next task')

        # Use notify-send if available
        try:
            subprocess.Popen([
                'notify-send',
                '-u', 'critical',
                '-i', 'appointment-soon',
                'TL Linux - Time to Start!',
                f"Ready to begin: {task}"
            ])
        except:
            pass

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = ADHDShutdownAssistant()
    app.run()

if __name__ == '__main__':
    main()
