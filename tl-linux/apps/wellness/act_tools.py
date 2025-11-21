#!/usr/bin/env python3
"""
TL Linux - ACT Tools
Acceptance and Commitment Therapy tools for mindfulness and values-based living
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from datetime import datetime
import time

class ACTTools:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌱 ACT Tools - Acceptance & Commitment Therapy")
        self.root.geometry("1000x700")

        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellness'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.config_dir / 'act_data.json'

        self.data = self.load_data()
        self.setup_ui()

    def load_data(self):
        """Load ACT data"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'values': {},
            'committed_actions': [],
            'mindfulness_sessions': [],
            'defusion_exercises': []
        }

    def save_data(self):
        """Save ACT data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg='#66BB6A', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🌱 ACT Tools - Acceptance & Commitment Therapy",
            font=('Arial', 18, 'bold'),
            bg='#66BB6A',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Live mindfully, aligned with your values",
            font=('Arial', 10),
            bg='#66BB6A',
            fg='white'
        ).pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg='#2c3e50', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tools = [
            ('🌟 Values Clarification', self.show_values),
            ('🎯 Committed Action', self.show_committed_action),
            ('🧘 Mindfulness Exercises', self.show_mindfulness),
            ('🎈 Cognitive Defusion', self.show_defusion),
            ('🤲 Acceptance Practice', self.show_acceptance),
            ('🧭 Present Moment', self.show_present_moment),
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

        self.show_values()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_values(self):
        """Show values clarification"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🌟 Values Clarification",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Identify what truly matters to you in different life domains",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        domains = [
            ("👨‍👩‍👧‍👦 Family & Relationships", "How do you want to be in your relationships?"),
            ("💼 Work & Career", "What kind of worker/colleague do you want to be?"),
            ("🎓 Personal Growth", "How do you want to develop as a person?"),
            ("💪 Health & Wellness", "How do you want to care for your body and mind?"),
            ("🎨 Leisure & Recreation", "How do you want to spend your free time?"),
            ("🤝 Community & Citizenship", "How do you want to contribute to the world?")
        ]

        # Canvas for scrolling
        canvas = tk.Canvas(self.content_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        entries = {}

        for domain, question in domains:
            frame = tk.LabelFrame(
                scrollable_frame,
                text=domain,
                font=('Arial', 11, 'bold'),
                bg='white',
                padx=10,
                pady=10
            )
            frame.pack(fill=tk.X, pady=10, padx=10)

            tk.Label(
                frame,
                text=question,
                font=('Arial', 9, 'italic'),
                bg='white',
                fg='#666'
            ).pack(anchor='w', pady=(0, 5))

            text = scrolledtext.ScrolledText(
                frame,
                height=3,
                font=('Arial', 10),
                wrap=tk.WORD
            )
            text.pack(fill=tk.X)

            # Load existing value
            if domain in self.data.get('values', {}):
                text.insert('1.0', self.data['values'][domain])

            entries[domain] = text

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def save_values():
            for domain, text_widget in entries.items():
                self.data['values'][domain] = text_widget.get('1.0', tk.END).strip()

            self.save_data()
            messagebox.showinfo("Saved", "Your values have been saved!")

        tk.Button(
            self.content_frame,
            text="💾 Save Values",
            command=save_values,
            bg='#66BB6A',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.BOTTOM, pady=10)

    def show_committed_action(self):
        """Show committed action planning"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎯 Committed Action",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Take action aligned with your values",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Value selection
        tk.Label(
            self.content_frame,
            text="Which value does this action serve?",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        value_var = tk.StringVar()
        value_combo = ttk.Combobox(
            self.content_frame,
            textvariable=value_var,
            values=['Family', 'Work', 'Growth', 'Health', 'Leisure', 'Community'],
            state='readonly',
            font=('Arial', 10)
        )
        value_combo.pack(fill=tk.X, pady=(0, 10))

        # Action description
        tk.Label(
            self.content_frame,
            text="What action will you take?",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        action_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=3,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        action_text.pack(fill=tk.X, pady=(0, 10))

        # Barriers
        tk.Label(
            self.content_frame,
            text="What barriers might you face?",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        barriers_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=2,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        barriers_text.pack(fill=tk.X, pady=(0, 10))

        # How to overcome
        tk.Label(
            self.content_frame,
            text="How will you overcome these barriers?",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        overcome_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=2,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        overcome_text.pack(fill=tk.X, pady=(0, 10))

        # Deadline
        tk.Label(
            self.content_frame,
            text="When will you do this?",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        deadline_entry = tk.Entry(self.content_frame, font=('Arial', 10))
        deadline_entry.pack(fill=tk.X, pady=(0, 10))

        def save_action():
            action = {
                'timestamp': datetime.now().isoformat(),
                'value': value_var.get(),
                'action': action_text.get('1.0', tk.END).strip(),
                'barriers': barriers_text.get('1.0', tk.END).strip(),
                'overcome': overcome_text.get('1.0', tk.END).strip(),
                'deadline': deadline_entry.get()
            }

            self.data['committed_actions'].append(action)
            self.save_data()

            messagebox.showinfo("Saved", "Committed action saved!")

            # Clear fields
            action_text.delete('1.0', tk.END)
            barriers_text.delete('1.0', tk.END)
            overcome_text.delete('1.0', tk.END)
            deadline_entry.delete(0, tk.END)

        tk.Button(
            self.content_frame,
            text="💾 Save Action",
            command=save_action,
            bg='#66BB6A',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=20)

    def show_mindfulness(self):
        """Show mindfulness exercises"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🧘 Mindfulness Exercises",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Practice being present in the moment",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        exercises = [
            ("5-4-3-2-1 Grounding", self.exercise_54321),
            ("Body Scan", self.exercise_body_scan),
            ("Mindful Breathing", self.exercise_breathing),
            ("Observer Self", self.exercise_observer)
        ]

        for exercise_name, command in exercises:
            btn = tk.Button(
                self.content_frame,
                text=f"▶ {exercise_name}",
                command=command,
                bg='#E8F5E9',
                fg='#2c3e50',
                font=('Arial', 12),
                relief=tk.FLAT,
                anchor='w',
                padx=20,
                pady=15,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, pady=5)

    def exercise_54321(self):
        """5-4-3-2-1 grounding exercise"""
        window = tk.Toplevel(self.root)
        window.title("5-4-3-2-1 Grounding Exercise")
        window.geometry("600x500")
        window.configure(bg='#E8F5E9')

        tk.Label(
            window,
            text="🌿 5-4-3-2-1 Grounding Exercise",
            font=('Arial', 16, 'bold'),
            bg='#E8F5E9',
            fg='#2c3e50'
        ).pack(pady=20)

        steps = [
            ("5 things you can SEE", "👀"),
            ("4 things you can TOUCH", "✋"),
            ("3 things you can HEAR", "👂"),
            ("2 things you can SMELL", "👃"),
            ("1 thing you can TASTE", "👅")
        ]

        for step, emoji in steps:
            frame = tk.Frame(window, bg='white', relief=tk.SOLID, borderwidth=1)
            frame.pack(fill=tk.X, padx=20, pady=10)

            tk.Label(
                frame,
                text=f"{emoji} {step}",
                font=('Arial', 12, 'bold'),
                bg='white'
            ).pack(anchor='w', padx=15, pady=10)

        tk.Label(
            window,
            text="Take your time with each sense.\nNotice the details.",
            font=('Arial', 10, 'italic'),
            bg='#E8F5E9',
            fg='#666'
        ).pack(pady=20)

    def exercise_body_scan(self):
        """Body scan exercise"""
        window = tk.Toplevel(self.root)
        window.title("Body Scan Meditation")
        window.geometry("600x500")
        window.configure(bg='#E8F5E9')

        tk.Label(
            window,
            text="🧘 Body Scan Meditation",
            font=('Arial', 16, 'bold'),
            bg='#E8F5E9',
            fg='#2c3e50'
        ).pack(pady=20)

        instructions = """
        1. Find a comfortable position, sitting or lying down

        2. Close your eyes or soften your gaze

        3. Bring attention to your feet
           Notice any sensations - warmth, coolness, tingling

        4. Slowly move attention up through:
           • Legs
           • Hips
           • Stomach
           • Chest
           • Arms
           • Shoulders
           • Neck
           • Head

        5. Notice each area without judgment
           Simply observe what's there

        6. If your mind wanders, gently bring it back
           to the body part you're focusing on

        7. Take 10-15 minutes for the full scan
        """

        tk.Label(
            window,
            text=instructions,
            font=('Arial', 10),
            bg='#E8F5E9',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=30, pady=20)

    def exercise_breathing(self):
        """Mindful breathing exercise"""
        window = tk.Toplevel(self.root)
        window.title("Mindful Breathing")
        window.geometry("600x500")
        window.configure(bg='#E8F5E9')

        tk.Label(
            window,
            text="🌬️ Mindful Breathing",
            font=('Arial', 16, 'bold'),
            bg='#E8F5E9',
            fg='#2c3e50'
        ).pack(pady=20)

        instructions = """
        Follow your breath:

        1. Notice the breath entering your nose

        2. Feel your chest and belly expand

        3. Notice the brief pause at the top

        4. Feel the breath leaving your body

        5. Notice the pause at the bottom

        Continue for a few minutes.

        When your mind wanders (and it will),
        gently bring attention back to the breath.

        No need to change your breathing,
        just notice it as it is.
        """

        tk.Label(
            window,
            text=instructions,
            font=('Arial', 11),
            bg='#E8F5E9',
            fg='#2c3e50',
            justify=tk.CENTER
        ).pack(padx=30, pady=20)

    def exercise_observer(self):
        """Observer self exercise"""
        window = tk.Toplevel(self.root)
        window.title("Observer Self")
        window.geometry("600x500")
        window.configure(bg='#E8F5E9')

        tk.Label(
            window,
            text="👁️ Observer Self Exercise",
            font=('Arial', 16, 'bold'),
            bg='#E8F5E9',
            fg='#2c3e50'
        ).pack(pady=20)

        instructions = """
        Notice your thoughts and feelings from a distance:

        1. Imagine you're sitting by a stream
           Leaves are floating by on the water

        2. Notice each thought or feeling that arises

        3. Place each thought/feeling on a leaf
           Watch it float by

        4. Don't try to push thoughts away
           Don't hold onto them
           Just observe them passing

        5. You are not your thoughts
           You are the one noticing them

        Practice this for 5-10 minutes.

        This helps create space between you
        and your thoughts/feelings.
        """

        tk.Label(
            window,
            text=instructions,
            font=('Arial', 10),
            bg='#E8F5E9',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=30, pady=20)

    def show_defusion(self):
        """Show cognitive defusion techniques"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎈 Cognitive Defusion",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Change your relationship with difficult thoughts",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        techniques = [
            ("🔤 'I'm having the thought that...'",
             "Add this phrase before your thought to create distance\n"
             "Example: Instead of 'I'm worthless', say 'I'm having the thought that I'm worthless'"),

            ("🎵 Sing It",
             "Sing your difficult thought to a silly tune (like Happy Birthday)\n"
             "This reduces the thought's power"),

            ("🗣️ Say It in Different Voices",
             "Say the thought in a cartoon voice, robot voice, or sing-song voice\n"
             "This helps you see it's just words"),

            ("📺 Thank Your Mind",
             "When an unhelpful thought appears, say 'Thanks mind, interesting point'\n"
             "Acknowledge it without buying into it"),

            ("🎬 Imagine It on a Screen",
             "Picture the thought displayed on a movie screen or computer monitor\n"
             "You're watching it, not living in it"),

            ("⏱️ Watch It Pass",
             "Notice the thought arise, peak, and fade away\n"
             "All thoughts are temporary")
        ]

        for title, description in techniques:
            frame = tk.Frame(self.content_frame, bg='#FFF9C4', relief=tk.SOLID, borderwidth=1)
            frame.pack(fill=tk.X, pady=10)

            tk.Label(
                frame,
                text=title,
                font=('Arial', 12, 'bold'),
                bg='#FFF9C4',
                anchor='w'
            ).pack(anchor='w', padx=15, pady=(10, 5))

            tk.Label(
                frame,
                text=description,
                font=('Arial', 9),
                bg='#FFF9C4',
                anchor='w',
                justify=tk.LEFT,
                wraplength=700
            ).pack(anchor='w', padx=15, pady=(0, 10))

    def show_acceptance(self):
        """Show acceptance practices"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🤲 Acceptance Practice",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Make room for difficult experiences",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        content = """
        Acceptance doesn't mean:
        • Liking what's happening
        • Giving up
        • Being passive
        • Tolerating abuse

        Acceptance means:
        • Acknowledging what's present
        • Not struggling against reality
        • Making room for discomfort
        • Choosing your response

        Practice:

        1. Notice what you're struggling against
           What are you trying to avoid or control?

        2. Notice the cost of this struggle
           What does fighting reality cost you?

        3. Imagine opening up to make room
           Like opening your hands instead of clenching fists

        4. Be willing to feel what you feel
           Without trying to change it

        5. Choose your action based on values
           Not on avoiding discomfort

        Remember: "What you resist, persists"
        Acceptance often reduces suffering.
        """

        tk.Label(
            self.content_frame,
            text=content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def show_present_moment(self):
        """Show present moment awareness"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🧭 Present Moment Awareness",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Connect with the here and now",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        content = """
        The present moment is the only time
        where life actually happens.

        Past and future exist only as thoughts.

        Quick practices to return to now:

        🌟 Notice 3 things you can see right now
           Really look at them

        👂 Notice 3 sounds you can hear
           Near, far, very faint

        ✋ Feel your feet on the floor
           Notice the sensations

        🌬️ Take 3 conscious breaths
           Feel each inhale and exhale

        💭 Name what you're doing
           "I am sitting. I am reading. I am breathing."

        🎯 Engage fully in one activity
           Put down your phone. Be here.

        When you notice you're lost in thought about
        the past or future, gently return to sensing
        what's happening right now.

        This moment is enough.
        You are enough.
        """

        tk.Label(
            self.content_frame,
            text=content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == '__main__':
    app = ACTTools()
    app.run()
