#!/usr/bin/env python3
"""
TL Linux - CBT Tools
Cognitive Behavioral Therapy tools for managing thoughts and emotions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from datetime import datetime

class CBTTools:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 CBT Tools - Cognitive Behavioral Therapy")
        self.root.geometry("1000x700")

        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellness'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.config_dir / 'cbt_data.json'

        self.data = self.load_data()
        self.setup_ui()

    def load_data(self):
        """Load CBT data"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'thought_records': [],
            'mood_log': [],
            'cognitive_distortions': [],
            'achievements': []
        }

    def save_data(self):
        """Save CBT data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg='#4A90E2', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🧠 CBT Tools - Cognitive Behavioral Therapy",
            font=('Arial', 18, 'bold'),
            bg='#4A90E2',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Tools to help identify and restructure unhelpful thoughts",
            font=('Arial', 10),
            bg='#4A90E2',
            fg='white'
        ).pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar with tool buttons
        sidebar = tk.Frame(main_container, bg='#2c3e50', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tools = [
            ('📝 Thought Record', self.show_thought_record),
            ('😊 Mood Tracker', self.show_mood_tracker),
            ('🔍 Identify Distortions', self.show_distortions),
            ('💪 Behavioral Activation', self.show_behavioral_activation),
            ('🎯 Goal Setting', self.show_goal_setting),
            ('📊 Progress Report', self.show_progress),
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

        # Show initial tool
        self.show_thought_record()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_thought_record(self):
        """Show thought record tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="📝 Thought Record",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Record and examine your automatic thoughts",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Situation
        tk.Label(
            self.content_frame,
            text="1. Situation (What happened?):",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        situation_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=3,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        situation_text.pack(fill=tk.X, pady=(0, 10))

        # Emotions
        tk.Label(
            self.content_frame,
            text="2. Emotions (What did you feel?):",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        emotions_frame = tk.Frame(self.content_frame, bg='white')
        emotions_frame.pack(fill=tk.X, pady=(0, 10))

        emotion_text = tk.Entry(emotions_frame, font=('Arial', 10))
        emotion_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        tk.Label(
            emotions_frame,
            text="Intensity (0-100):",
            bg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        intensity_scale = tk.Scale(
            emotions_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=150
        )
        intensity_scale.pack(side=tk.LEFT)

        # Automatic Thoughts
        tk.Label(
            self.content_frame,
            text="3. Automatic Thoughts (What went through your mind?):",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        thoughts_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=3,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        thoughts_text.pack(fill=tk.X, pady=(0, 10))

        # Evidence For
        tk.Label(
            self.content_frame,
            text="4. Evidence Supporting the Thought:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        evidence_for_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=2,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        evidence_for_text.pack(fill=tk.X, pady=(0, 10))

        # Evidence Against
        tk.Label(
            self.content_frame,
            text="5. Evidence Against the Thought:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        evidence_against_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=2,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        evidence_against_text.pack(fill=tk.X, pady=(0, 10))

        # Alternative Thought
        tk.Label(
            self.content_frame,
            text="6. Alternative, Balanced Thought:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        alternative_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=2,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        alternative_text.pack(fill=tk.X, pady=(0, 10))

        # Save button
        def save_thought_record():
            record = {
                'timestamp': datetime.now().isoformat(),
                'situation': situation_text.get('1.0', tk.END).strip(),
                'emotion': emotion_text.get(),
                'intensity': intensity_scale.get(),
                'automatic_thoughts': thoughts_text.get('1.0', tk.END).strip(),
                'evidence_for': evidence_for_text.get('1.0', tk.END).strip(),
                'evidence_against': evidence_against_text.get('1.0', tk.END).strip(),
                'alternative_thought': alternative_text.get('1.0', tk.END).strip()
            }

            self.data['thought_records'].append(record)
            self.save_data()

            messagebox.showinfo("Saved", "Thought record saved successfully!")

            # Clear fields
            situation_text.delete('1.0', tk.END)
            emotion_text.delete(0, tk.END)
            intensity_scale.set(50)
            thoughts_text.delete('1.0', tk.END)
            evidence_for_text.delete('1.0', tk.END)
            evidence_against_text.delete('1.0', tk.END)
            alternative_text.delete('1.0', tk.END)

        tk.Button(
            self.content_frame,
            text="💾 Save Thought Record",
            command=save_thought_record,
            bg='#4A90E2',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=20)

    def show_mood_tracker(self):
        """Show mood tracking tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="😊 Mood Tracker",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Track your mood throughout the day",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Mood selection
        tk.Label(
            self.content_frame,
            text="How are you feeling right now?",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=(10, 10))

        mood_frame = tk.Frame(self.content_frame, bg='white')
        mood_frame.pack(pady=20)

        moods = [
            ('😊', 'Happy', '#4CAF50'),
            ('😌', 'Calm', '#8BC34A'),
            ('😐', 'Neutral', '#FFC107'),
            ('😔', 'Sad', '#FF9800'),
            ('😰', 'Anxious', '#FF5722'),
            ('😠', 'Angry', '#F44336')
        ]

        selected_mood = tk.StringVar(value='Neutral')

        for emoji, mood_name, color in moods:
            btn = tk.Button(
                mood_frame,
                text=f"{emoji}\n{mood_name}",
                command=lambda m=mood_name: selected_mood.set(m),
                bg=color,
                fg='white',
                font=('Arial', 12),
                width=8,
                height=3,
                relief=tk.FLAT,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Energy level
        tk.Label(
            self.content_frame,
            text="Energy Level:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(20, 5))

        energy_scale = tk.Scale(
            self.content_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=400,
            label="0 = Very Low, 100 = Very High"
        )
        energy_scale.set(50)
        energy_scale.pack(pady=10)

        # Notes
        tk.Label(
            self.content_frame,
            text="Notes (optional):",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        notes_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=4,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        notes_text.pack(fill=tk.X, pady=(0, 10))

        def save_mood():
            mood_entry = {
                'timestamp': datetime.now().isoformat(),
                'mood': selected_mood.get(),
                'energy': energy_scale.get(),
                'notes': notes_text.get('1.0', tk.END).strip()
            }

            self.data['mood_log'].append(mood_entry)
            self.save_data()

            messagebox.showinfo("Saved", "Mood entry saved!")
            notes_text.delete('1.0', tk.END)

        tk.Button(
            self.content_frame,
            text="💾 Save Mood Entry",
            command=save_mood,
            bg='#4A90E2',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=20)

    def show_distortions(self):
        """Show cognitive distortions guide"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🔍 Cognitive Distortions",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Common thinking patterns that can affect mood",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        distortions = [
            ("All-or-Nothing Thinking", "Seeing things as black or white, no middle ground\nExample: 'If I'm not perfect, I'm a failure'"),
            ("Overgeneralization", "Drawing broad conclusions from single events\nExample: 'Nothing ever works out for me'"),
            ("Mental Filter", "Focusing only on negatives, filtering out positives\nExample: Dwelling on one criticism despite many compliments"),
            ("Catastrophizing", "Expecting the worst-case scenario\nExample: 'This will be a disaster'"),
            ("Emotional Reasoning", "Believing feelings reflect reality\nExample: 'I feel stupid, so I must be stupid'"),
            ("Should Statements", "Rigid rules about how things 'should' be\nExample: 'I should never make mistakes'"),
            ("Labeling", "Attaching negative labels to yourself or others\nExample: 'I'm a loser'"),
            ("Personalization", "Blaming yourself for things outside your control\nExample: 'It's all my fault'"),
            ("Mind Reading", "Assuming you know what others are thinking\nExample: 'They think I'm boring'"),
            ("Fortune Telling", "Predicting negative outcomes without evidence\nExample: 'I know I'll fail the test'")
        ]

        # Scrollable frame
        canvas = tk.Canvas(self.content_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for distortion, description in distortions:
            frame = tk.Frame(scrollable_frame, bg='#f0f0f0', relief=tk.SOLID, borderwidth=1)
            frame.pack(fill=tk.X, pady=5, padx=10)

            tk.Label(
                frame,
                text=distortion,
                font=('Arial', 11, 'bold'),
                bg='#f0f0f0',
                anchor='w'
            ).pack(anchor='w', padx=10, pady=(10, 5))

            tk.Label(
                frame,
                text=description,
                font=('Arial', 9),
                bg='#f0f0f0',
                anchor='w',
                justify=tk.LEFT
            ).pack(anchor='w', padx=10, pady=(0, 10))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_behavioral_activation(self):
        """Show behavioral activation tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="💪 Behavioral Activation",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Plan enjoyable and meaningful activities",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        categories = [
            ("🎯 Achievement Activities", "Activities that give a sense of accomplishment"),
            ("😊 Pleasure Activities", "Activities that bring joy and relaxation"),
            ("👥 Social Activities", "Connecting with others"),
            ("🧘 Self-Care Activities", "Taking care of your physical and mental health")
        ]

        for emoji_title, description in categories:
            frame = tk.LabelFrame(
                self.content_frame,
                text=emoji_title,
                font=('Arial', 11, 'bold'),
                bg='white',
                padx=10,
                pady=10
            )
            frame.pack(fill=tk.X, pady=10)

            tk.Label(
                frame,
                text=description,
                font=('Arial', 9, 'italic'),
                bg='white',
                fg='#666'
            ).pack(anchor='w')

        tk.Label(
            self.content_frame,
            text="💡 Tip: Schedule at least one activity from each category daily",
            font=('Arial', 10, 'italic'),
            bg='#FFF9C4',
            fg='#666',
            pady=10,
            padx=10
        ).pack(fill=tk.X, pady=20)

    def show_goal_setting(self):
        """Show goal setting tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎯 SMART Goal Setting",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Set Specific, Measurable, Achievable, Relevant, Time-bound goals",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        fields = [
            ("Specific", "What exactly do you want to accomplish?"),
            ("Measurable", "How will you know you've achieved it?"),
            ("Achievable", "Is this realistic given your resources?"),
            ("Relevant", "Why is this important to you?"),
            ("Time-bound", "When will you achieve this by?")
        ]

        entries = {}

        for field_name, prompt in fields:
            tk.Label(
                self.content_frame,
                text=f"{field_name}: {prompt}",
                font=('Arial', 10, 'bold'),
                bg='white'
            ).pack(anchor='w', pady=(10, 5))

            entry = tk.Entry(self.content_frame, font=('Arial', 10))
            entry.pack(fill=tk.X, pady=(0, 5))
            entries[field_name] = entry

        def save_goal():
            goal = {
                'timestamp': datetime.now().isoformat(),
                'specific': entries['Specific'].get(),
                'measurable': entries['Measurable'].get(),
                'achievable': entries['Achievable'].get(),
                'relevant': entries['Relevant'].get(),
                'timebound': entries['Time-bound'].get()
            }

            if not self.data.get('goals'):
                self.data['goals'] = []

            self.data['goals'].append(goal)
            self.save_data()

            messagebox.showinfo("Saved", "Goal saved successfully!")

            for entry in entries.values():
                entry.delete(0, tk.END)

        tk.Button(
            self.content_frame,
            text="💾 Save Goal",
            command=save_goal,
            bg='#4A90E2',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=20)

    def show_progress(self):
        """Show progress report"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="📊 Your Progress",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 20))

        stats = [
            ("📝 Thought Records", len(self.data.get('thought_records', []))),
            ("😊 Mood Entries", len(self.data.get('mood_log', []))),
            ("🎯 Goals Set", len(self.data.get('goals', [])))
        ]

        for stat_name, count in stats:
            frame = tk.Frame(self.content_frame, bg='#E3F2FD', relief=tk.SOLID, borderwidth=1)
            frame.pack(fill=tk.X, pady=5)

            tk.Label(
                frame,
                text=stat_name,
                font=('Arial', 12),
                bg='#E3F2FD'
            ).pack(side=tk.LEFT, padx=20, pady=15)

            tk.Label(
                frame,
                text=str(count),
                font=('Arial', 20, 'bold'),
                bg='#E3F2FD',
                fg='#4A90E2'
            ).pack(side=tk.RIGHT, padx=20, pady=15)

        tk.Label(
            self.content_frame,
            text="🌟 Keep up the great work!",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#4CAF50'
        ).pack(pady=30)

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == '__main__':
    app = CBTTools()
    app.run()
