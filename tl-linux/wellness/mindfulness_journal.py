#!/usr/bin/env python3
"""
TL Mindfulness & Journaling Tool
Combined mindfulness exercises and therapeutic journaling

Features:
- Guided meditation sessions
- Breathing exercises
- Mindfulness timer
- Daily journaling with prompts
- Mood tracking
- Gratitude journaling
- CBT thought records
- Progress tracking
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import json
from pathlib import Path
from datetime import datetime
import threading
import time

class MindfulnessJournal:
    """Mindfulness and journaling application"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Mindfulness & Journal 🧘")
            self.root.geometry("900x800")
        else:
            self.root = root

        self.root.configure(bg='#1a1a2e')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'mindfulness'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.journals_dir = self.config_dir / 'journals'
        self.journals_dir.mkdir(parents=True, exist_ok=True)

        # State
        self.meditation_running = False
        self.meditation_time_remaining = 0

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        # Header
        header = tk.Frame(self.root, bg='#16213e', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🧘 Mindfulness & Journal",
            font=('Arial', 28, 'bold'),
            bg='#16213e',
            fg='#a8dadc'
        ).pack(pady=20)

        # Tabs
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.configure('TNotebook', background='#1a1a2e')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))

        # Create tabs
        self.meditation_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.journal_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.mood_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.gratitude_tab = tk.Frame(tab_container, bg='#1a1a2e')

        tab_container.add(self.meditation_tab, text='🧘 Meditation')
        tab_container.add(self.journal_tab, text='📝 Journal')
        tab_container.add(self.mood_tab, text='😊 Mood Tracking')
        tab_container.add(self.gratitude_tab, text='🙏 Gratitude')

        # Setup tabs
        self.setup_meditation_tab()
        self.setup_journal_tab()
        self.setup_mood_tab()
        self.setup_gratitude_tab()

    def setup_meditation_tab(self):
        """Setup meditation exercises"""
        container = tk.Frame(self.meditation_tab, bg='#1a1a2e')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Title
        tk.Label(
            container,
            text="Guided Meditation & Breathing",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        ).pack(pady=20)

        # Quick breathing exercises
        breathing_frame = tk.LabelFrame(
            container,
            text="Quick Breathing Exercises",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        breathing_frame.pack(fill=tk.X, pady=10)

        exercises = [
            ("4-7-8 Breathing", "Breathe in 4s, hold 7s, out 8s", lambda: self.start_breathing_exercise('4-7-8')),
            ("Box Breathing", "Breathe in 4s, hold 4s, out 4s, hold 4s", lambda: self.start_breathing_exercise('box')),
            ("Deep Belly Breathing", "Slow, deep breaths from diaphragm", lambda: self.start_breathing_exercise('belly'))
        ]

        for name, desc, cmd in exercises:
            btn_frame = tk.Frame(breathing_frame, bg='#1a1a2e')
            btn_frame.pack(fill=tk.X, pady=5)

            tk.Button(
                btn_frame,
                text=name,
                font=('Arial', 12, 'bold'),
                bg='#457b9d',
                fg='white',
                command=cmd,
                width=20,
                padx=10,
                pady=8
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                btn_frame,
                text=desc,
                font=('Arial', 10),
                bg='#1a1a2e',
                fg='#8b949e'
            ).pack(side=tk.LEFT, padx=10)

        # Meditation timer
        timer_frame = tk.LabelFrame(
            container,
            text="Meditation Timer",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        timer_frame.pack(fill=tk.X, pady=10)

        # Duration selection
        duration_frame = tk.Frame(timer_frame, bg='#1a1a2e')
        duration_frame.pack(pady=10)

        tk.Label(
            duration_frame,
            text="Duration:",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

        self.meditation_duration = tk.IntVar(value=5)
        for minutes in [1, 3, 5, 10, 15, 20]:
            tk.Radiobutton(
                duration_frame,
                text=f"{minutes} min",
                variable=self.meditation_duration,
                value=minutes,
                font=('Arial', 10),
                bg='#1a1a2e',
                fg='white',
                selectcolor='#16213e'
            ).pack(side=tk.LEFT, padx=5)

        # Timer display
        self.timer_label = tk.Label(
            timer_frame,
            text="00:00",
            font=('Arial', 48, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        )
        self.timer_label.pack(pady=20)

        # Controls
        controls = tk.Frame(timer_frame, bg='#1a1a2e')
        controls.pack(pady=10)

        self.start_med_btn = tk.Button(
            controls,
            text="🧘 Start Meditation",
            font=('Arial', 14),
            bg='#457b9d',
            fg='white',
            command=self.start_meditation,
            padx=30,
            pady=15
        )
        self.start_med_btn.pack(side=tk.LEFT, padx=5)

        self.stop_med_btn = tk.Button(
            controls,
            text="⏹ Stop",
            font=('Arial', 14),
            bg='#e63946',
            fg='white',
            command=self.stop_meditation,
            padx=30,
            pady=15,
            state=tk.DISABLED
        )
        self.stop_med_btn.pack(side=tk.LEFT, padx=5)

    def setup_journal_tab(self):
        """Setup journaling interface"""
        container = tk.Frame(self.journal_tab, bg='#1a1a2e')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Title with date
        title_frame = tk.Frame(container, bg='#1a1a2e')
        title_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            title_frame,
            text="Daily Journal Entry",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        ).pack(side=tk.LEFT)

        self.journal_date_label = tk.Label(
            title_frame,
            text=datetime.now().strftime("%B %d, %Y"),
            font=('Arial', 14),
            bg='#1a1a2e',
            fg='#8b949e'
        )
        self.journal_date_label.pack(side=tk.RIGHT)

        # Journal prompts
        prompts_frame = tk.LabelFrame(
            container,
            text="Journaling Prompts",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=15,
            pady=15
        )
        prompts_frame.pack(fill=tk.X, pady=10)

        prompts = [
            "What went well today?",
            "What challenged me today?",
            "What am I grateful for?",
            "What did I learn today?",
            "How am I feeling right now?",
            "What can I improve tomorrow?"
        ]

        for prompt in prompts:
            tk.Button(
                prompts_frame,
                text=prompt,
                font=('Arial', 9),
                bg='#457b9d',
                fg='white',
                command=lambda p=prompt: self.insert_prompt(p),
                anchor=tk.W,
                padx=10,
                pady=5
            ).pack(fill=tk.X, pady=2)

        # Journal text area
        self.journal_text = scrolledtext.ScrolledText(
            container,
            font=('Georgia', 12),
            bg='#f1faee',
            fg='#1d3557',
            wrap=tk.WORD,
            padx=15,
            pady=15,
            height=15
        )
        self.journal_text.pack(fill=tk.BOTH, expand=True, pady=10)

        # Load today's entry if it exists
        self.load_journal_entry()

        # Save button
        tk.Button(
            container,
            text="💾 Save Journal Entry",
            font=('Arial', 14),
            bg='#457b9d',
            fg='white',
            command=self.save_journal_entry,
            padx=30,
            pady=12
        ).pack(pady=10)

        # View history
        tk.Button(
            container,
            text="📚 View Past Entries",
            font=('Arial', 12),
            bg='#6c757d',
            fg='white',
            command=self.view_journal_history,
            padx=20,
            pady=8
        ).pack()

    def setup_mood_tab(self):
        """Setup mood tracking"""
        container = tk.Frame(self.mood_tab, bg='#1a1a2e')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(
            container,
            text="How are you feeling today?",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        ).pack(pady=30)

        # Mood selection
        moods_frame = tk.Frame(container, bg='#1a1a2e')
        moods_frame.pack(pady=20)

        moods = [
            ("😁", "Great", "#2d6a4f"),
            ("🙂", "Good", "#52b788"),
            ("😐", "Okay", "#95d5b2"),
            ("😔", "Not Great", "#ffb703"),
            ("😢", "Difficult", "#e63946")
        ]

        for emoji, label, color in moods:
            btn = tk.Button(
                moods_frame,
                text=f"{emoji}\n{label}",
                font=('Arial', 16),
                bg=color,
                fg='white',
                command=lambda m=label: self.log_mood(m),
                width=10,
                height=4
            )
            btn.pack(side=tk.LEFT, padx=10)

        # Additional notes
        tk.Label(
            container,
            text="Additional notes (optional):",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=(30, 10))

        self.mood_notes = scrolledtext.ScrolledText(
            container,
            font=('Arial', 11),
            bg='#f1faee',
            fg='#1d3557',
            wrap=tk.WORD,
            height=8,
            padx=10,
            pady=10
        )
        self.mood_notes.pack(fill=tk.BOTH, expand=True, padx=50)

        # View mood history
        tk.Button(
            container,
            text="📊 View Mood History",
            font=('Arial', 12),
            bg='#457b9d',
            fg='white',
            command=self.view_mood_history,
            padx=20,
            pady=10
        ).pack(pady=20)

    def setup_gratitude_tab(self):
        """Setup gratitude journaling"""
        container = tk.Frame(self.gratitude_tab, bg='#1a1a2e')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(
            container,
            text="🙏 Three Good Things",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        ).pack(pady=20)

        tk.Label(
            container,
            text="Write three things you're grateful for today:",
            font=('Arial', 14),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=10)

        # Three text entries
        self.gratitude_entries = []
        for i in range(3):
            frame = tk.Frame(container, bg='#1a1a2e')
            frame.pack(fill=tk.X, pady=10, padx=50)

            tk.Label(
                frame,
                text=f"{i+1}.",
                font=('Arial', 14, 'bold'),
                bg='#1a1a2e',
                fg='#a8dadc'
            ).pack(side=tk.LEFT, padx=10)

            entry = tk.Text(
                frame,
                font=('Georgia', 12),
                bg='#f1faee',
                fg='#1d3557',
                wrap=tk.WORD,
                height=3,
                padx=10,
                pady=10
            )
            entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.gratitude_entries.append(entry)

        # Save button
        tk.Button(
            container,
            text="💾 Save Gratitude Entry",
            font=('Arial', 14),
            bg='#457b9d',
            fg='white',
            command=self.save_gratitude,
            padx=30,
            pady=12
        ).pack(pady=30)

        # Load today's gratitude if exists
        self.load_gratitude()

    # Meditation functions
    def start_breathing_exercise(self, exercise_type):
        """Start a breathing exercise"""
        window = tk.Toplevel(self.root)
        window.title(f"{exercise_type.title()} Breathing")
        window.geometry("500x400")
        window.configure(bg='#1a1a2e')

        instruction_label = tk.Label(
            window,
            text="",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        )
        instruction_label.pack(expand=True)

        count_label = tk.Label(
            window,
            text="",
            font=('Arial', 48, 'bold'),
            bg='#1a1a2e',
            fg='#457b9d'
        )
        count_label.pack()

        def run_exercise():
            if exercise_type == '4-7-8':
                sequence = [
                    ("Breathe In", 4),
                    ("Hold", 7),
                    ("Breathe Out", 8)
                ]
            elif exercise_type == 'box':
                sequence = [
                    ("Breathe In", 4),
                    ("Hold", 4),
                    ("Breathe Out", 4),
                    ("Hold", 4)
                ]
            else:  # belly
                sequence = [
                    ("Deep Breath In", 5),
                    ("Breathe Out Slowly", 5)
                ]

            for _ in range(5):  # 5 cycles
                for instruction, duration in sequence:
                    for i in range(duration, 0, -1):
                        instruction_label.config(text=instruction)
                        count_label.config(text=str(i))
                        window.update()
                        time.sleep(1)

            instruction_label.config(text="Exercise Complete!")
            count_label.config(text="✓")
            window.after(2000, window.destroy)

        threading.Thread(target=run_exercise, daemon=True).start()

    def start_meditation(self):
        """Start meditation timer"""
        self.meditation_running = True
        self.meditation_time_remaining = self.meditation_duration.get() * 60

        self.start_med_btn.config(state=tk.DISABLED)
        self.stop_med_btn.config(state=tk.NORMAL)

        self.update_meditation_timer()

    def update_meditation_timer(self):
        """Update meditation timer display"""
        if not self.meditation_running or self.meditation_time_remaining <= 0:
            self.stop_meditation()
            if self.meditation_time_remaining <= 0:
                self.meditation_complete()
            return

        minutes = self.meditation_time_remaining // 60
        seconds = self.meditation_time_remaining % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

        self.meditation_time_remaining -= 1
        self.root.after(1000, self.update_meditation_timer)

    def stop_meditation(self):
        """Stop meditation"""
        self.meditation_running = False
        self.start_med_btn.config(state=tk.NORMAL)
        self.stop_med_btn.config(state=tk.DISABLED)
        self.timer_label.config(text="00:00")

    def meditation_complete(self):
        """Show meditation complete message"""
        tk.messagebox.showinfo(
            "Meditation Complete",
            "🧘 Wonderful! You completed your meditation session.\n\nTake a moment to notice how you feel."
        )

    # Journal functions
    def insert_prompt(self, prompt):
        """Insert a prompt into the journal"""
        self.journal_text.insert(tk.END, f"\n{prompt}\n")
        self.journal_text.focus()

    def save_journal_entry(self):
        """Save journal entry"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        content = self.journal_text.get('1.0', tk.END).strip()

        if not content:
            tk.messagebox.showwarning("Empty Entry", "Please write something before saving.")
            return

        journal_file = self.journals_dir / f"journal_{date_str}.txt"

        with open(journal_file, 'w') as f:
            f.write(f"Journal Entry - {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n\n")
            f.write(content)

        tk.messagebox.showinfo("Saved", "Journal entry saved successfully!")

    def load_journal_entry(self):
        """Load today's journal entry"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        journal_file = self.journals_dir / f"journal_{date_str}.txt"

        if journal_file.exists():
            with open(journal_file, 'r') as f:
                content = f.read()
                # Skip the header line
                lines = content.split('\n', 2)
                if len(lines) > 2:
                    self.journal_text.insert('1.0', lines[2])

    def view_journal_history(self):
        """View past journal entries"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Journal History")
        history_window.geometry("700x600")
        history_window.configure(bg='#1a1a2e')

        tk.Label(
            history_window,
            text="📚 Past Journal Entries",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        ).pack(pady=20)

        # List entries
        entries_frame = tk.Frame(history_window, bg='#1a1a2e')
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        journal_files = sorted(self.journals_dir.glob("journal_*.txt"), reverse=True)

        if not journal_files:
            tk.Label(
                entries_frame,
                text="No journal entries yet. Start writing today!",
                font=('Arial', 12),
                bg='#1a1a2e',
                fg='#8b949e'
            ).pack(pady=50)
        else:
            for journal_file in journal_files[:10]:  # Show last 10 entries
                date = journal_file.stem.replace('journal_', '')
                formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')

                tk.Button(
                    entries_frame,
                    text=f"📝 {formatted_date}",
                    font=('Arial', 12),
                    bg='#457b9d',
                    fg='white',
                    command=lambda f=journal_file: self.view_entry(f),
                    anchor=tk.W,
                    padx=20,
                    pady=10
                ).pack(fill=tk.X, pady=5)

    def view_entry(self, journal_file):
        """View a specific journal entry"""
        with open(journal_file, 'r') as f:
            content = f.read()

        entry_window = tk.Toplevel(self.root)
        entry_window.title(journal_file.stem)
        entry_window.geometry("600x500")
        entry_window.configure(bg='#1a1a2e')

        text_widget = scrolledtext.ScrolledText(
            entry_window,
            font=('Georgia', 11),
            bg='#f1faee',
            fg='#1d3557',
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert('1.0', content)
        text_widget.config(state=tk.DISABLED)

    # Mood functions
    def log_mood(self, mood):
        """Log mood entry"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        notes = self.mood_notes.get('1.0', tk.END).strip()

        mood_data = {
            'date': date_str,
            'time': datetime.now().strftime('%H:%M:%S'),
            'mood': mood,
            'notes': notes
        }

        mood_file = self.config_dir / 'mood_log.json'
        mood_log = []

        if mood_file.exists():
            with open(mood_file, 'r') as f:
                mood_log = json.load(f)

        mood_log.append(mood_data)

        with open(mood_file, 'w') as f:
            json.dump(mood_log, f, indent=2)

        tk.messagebox.showinfo("Mood Logged", f"Mood '{mood}' logged successfully!")
        self.mood_notes.delete('1.0', tk.END)

    def view_mood_history(self):
        """View mood history"""
        mood_file = self.config_dir / 'mood_log.json'

        if not mood_file.exists():
            tk.messagebox.showinfo("No Data", "No mood data logged yet.")
            return

        with open(mood_file, 'r') as f:
            mood_log = json.load(f)

        history_window = tk.Toplevel(self.root)
        history_window.title("Mood History")
        history_window.geometry("600x500")
        history_window.configure(bg='#1a1a2e')

        tk.Label(
            history_window,
            text="😊 Mood History",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#a8dadc'
        ).pack(pady=20)

        text_widget = scrolledtext.ScrolledText(
            history_window,
            font=('Courier', 10),
            bg='#f1faee',
            fg='#1d3557',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for entry in reversed(mood_log[-30:]):  # Last 30 entries
            text_widget.insert(tk.END, f"{entry['date']} {entry['time']} - {entry['mood']}\n")
            if entry['notes']:
                text_widget.insert(tk.END, f"  Notes: {entry['notes']}\n")
            text_widget.insert(tk.END, "\n")

        text_widget.config(state=tk.DISABLED)

    # Gratitude functions
    def save_gratitude(self):
        """Save gratitude entries"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        gratitude_items = []

        for entry in self.gratitude_entries:
            text = entry.get('1.0', tk.END).strip()
            if text:
                gratitude_items.append(text)

        if not gratitude_items:
            tk.messagebox.showwarning("Empty", "Please write at least one thing you're grateful for.")
            return

        gratitude_file = self.journals_dir / f"gratitude_{date_str}.json"

        with open(gratitude_file, 'w') as f:
            json.dump({
                'date': date_str,
                'items': gratitude_items
            }, f, indent=2)

        tk.messagebox.showinfo("Saved", "Gratitude entry saved! 🙏")

    def load_gratitude(self):
        """Load today's gratitude entry"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        gratitude_file = self.journals_dir / f"gratitude_{date_str}.json"

        if gratitude_file.exists():
            with open(gratitude_file, 'r') as f:
                data = json.load(f)
                items = data.get('items', [])

                for i, item in enumerate(items[:3]):
                    self.gratitude_entries[i].insert('1.0', item)

    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = MindfulnessJournal()
    app.run()


if __name__ == '__main__':
    main()
