#!/usr/bin/env python3
"""
TL Linux - Autism Support Tools
Tools specifically designed to help with autism-related challenges
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from datetime import datetime

class AutismSupport:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧩 Autism Support Tools")
        self.root.geometry("1000x700")

        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellness'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.config_dir / 'autism_data.json'

        self.data = self.load_data()
        self.setup_ui()

    def load_data(self):
        """Load autism support data"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'social_scripts': [],
            'sensory_log': [],
            'routines': [],
            'communication_cards': []
        }

    def save_data(self):
        """Save autism support data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg='#2196F3', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🧩 Autism Support Tools",
            font=('Arial', 18, 'bold'),
            bg='#2196F3',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Social, sensory, and communication support",
            font=('Arial', 10),
            bg='#2196F3',
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
            ('💬 Social Scripts', self.show_social_scripts),
            ('🎨 Sensory Tracker', self.show_sensory_tracker),
            ('📅 Visual Schedules', self.show_visual_schedules),
            ('🗣️ Communication Cards', self.show_communication_cards),
            ('🔊 Sensory Accommodations', self.show_accommodations),
            ('💡 Autism Tips', self.show_tips),
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

        self.show_social_scripts()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_social_scripts(self):
        """Show social scripts library"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="💬 Social Scripts",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Pre-written scripts for common social situations",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Script categories
        scripts = {
            "Phone Calls": [
                ("Making an appointment",
                 "Hi, I'd like to make an appointment.\n"
                 "My name is [NAME].\n"
                 "I'm available on [DAYS/TIMES].\n"
                 "Thank you!"),

                ("Ordering food",
                 "Hi, I'd like to place an order for pickup.\n"
                 "[Order your items]\n"
                 "What time will it be ready?\n"
                 "Thank you!"),

                ("Calling in sick",
                 "Hi, this is [NAME].\n"
                 "I'm not feeling well and won't be able to come in today.\n"
                 "I expect to be back [tomorrow/date].\n"
                 "Thank you for understanding.")
            ],

            "Shopping": [
                ("Asking for help",
                 "Excuse me, could you help me find [ITEM]?\n"
                 "[If they show you] Thank you!\n"
                 "[If they don't know] That's okay, thank you anyway."),

                ("Returning an item",
                 "Hi, I'd like to return this.\n"
                 "[Show receipt]\n"
                 "It [didn't fit/wasn't what I expected].\n"
                 "Thank you for your help."),

                ("Asking about prices",
                 "Excuse me, could you tell me the price of this?\n"
                 "Thank you!")
            ],

            "Social Situations": [
                ("Polite exit from conversation",
                 "It was nice talking to you, but I need to [go/get back to work].\n"
                 "Have a good day!"),

                ("Declining an invitation",
                 "Thank you for inviting me, but I can't make it [this time/that day].\n"
                 "I appreciate you thinking of me!"),

                ("Small talk responses",
                 "How are you? → I'm doing well, thank you. How about you?\n"
                 "Nice weather → Yes, it's [nice/pleasant/sunny] today.\n"
                 "What did you do this weekend? → I [activity]. It was [adjective]. How about you?")
            ],

            "Workplace": [
                ("Asking for clarification",
                 "Could you please explain that again?\n"
                 "I want to make sure I understand correctly."),

                ("Asking for accommodation",
                 "I work better when [accommodation].\n"
                 "Would it be possible to [request]?\n"
                 "This would help me be more productive."),

                ("Declining extra work",
                 "I'd like to help, but I'm at capacity right now.\n"
                 "I want to make sure I can do quality work on my current tasks.")
            ]
        }

        # Create notebook
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        for category, script_list in scripts.items():
            category_frame = tk.Frame(notebook, bg='white')
            notebook.add(category_frame, text=category)

            # Scrollable frame
            canvas = tk.Canvas(category_frame, bg='white', highlightthickness=0)
            scrollbar = tk.Scrollbar(category_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            for script_name, script_text in script_list:
                script_frame = tk.LabelFrame(
                    scrollable_frame,
                    text=script_name,
                    font=('Arial', 11, 'bold'),
                    bg='white',
                    padx=10,
                    pady=10
                )
                script_frame.pack(fill=tk.X, pady=10, padx=10)

                text = scrolledtext.ScrolledText(
                    script_frame,
                    height=4,
                    font=('Arial', 10),
                    wrap=tk.WORD
                )
                text.insert('1.0', script_text)
                text.config(state=tk.DISABLED)
                text.pack(fill=tk.X)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_sensory_tracker(self):
        """Show sensory tracking tool"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎨 Sensory Tracker",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Track sensory experiences and triggers",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Current sensory state
        tk.Label(
            self.content_frame,
            text="How are your senses right now?",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 10))

        sensory_categories = [
            ("👁️ Visual", "Lights, colors, movement, clutter"),
            ("👂 Auditory", "Noise level, specific sounds"),
            ("👃 Smell", "Strong scents, food smells"),
            ("👅 Taste", "Food textures, flavors"),
            ("✋ Touch", "Clothing, temperature, textures"),
            ("🏃 Proprioception", "Body awareness, movement"),
            ("🎢 Vestibular", "Balance, motion"),
            ("🔥 Interoception", "Internal body signals")
        ]

        sensory_vars = {}

        for sense, description in sensory_categories:
            frame = tk.Frame(self.content_frame, bg='white')
            frame.pack(fill=tk.X, pady=5)

            tk.Label(
                frame,
                text=f"{sense}:",
                font=('Arial', 10, 'bold'),
                bg='white',
                width=20,
                anchor='w'
            ).pack(side=tk.LEFT)

            var = tk.StringVar(value="neutral")
            sensory_vars[sense] = var

            for state, color in [("Under", "#4CAF50"), ("OK", "#FFC107"), ("Over", "#F44336")]:
                tk.Radiobutton(
                    frame,
                    text=state,
                    variable=var,
                    value=state.lower(),
                    bg='white',
                    selectcolor=color
                ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                frame,
                text=f"({description})",
                font=('Arial', 8),
                bg='white',
                fg='#666'
            ).pack(side=tk.LEFT, padx=10)

        # Notes
        tk.Label(
            self.content_frame,
            text="Notes about triggers or what helps:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(20, 5))

        notes_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=4,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        notes_text.pack(fill=tk.X, pady=(0, 10))

        def save_sensory_log():
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'sensory_state': {sense: var.get() for sense, var in sensory_vars.items()},
                'notes': notes_text.get('1.0', tk.END).strip()
            }

            self.data['sensory_log'].append(log_entry)
            self.save_data()

            messagebox.showinfo("Saved", "Sensory log saved!")
            notes_text.delete('1.0', tk.END)

        tk.Button(
            self.content_frame,
            text="💾 Save Sensory Log",
            command=save_sensory_log,
            bg='#2196F3',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=20)

    def show_visual_schedules(self):
        """Show visual schedule builder"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="📅 Visual Schedules",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Visual representations of routines and schedules",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Daily schedule template
        schedule_items = [
            ("🌅 Morning", [
                "⏰ Wake up (7:00 AM)",
                "🚿 Shower",
                "👔 Get dressed",
                "🍳 Breakfast",
                "🪥 Brush teeth",
                "🎒 Pack bag"
            ]),
            ("🌞 Daytime", [
                "💼 Work/School (9:00 AM - 5:00 PM)",
                "🍱 Lunch (12:00 PM)",
                "☕ Afternoon break (3:00 PM)"
            ]),
            ("🌙 Evening", [
                "🍽️ Dinner (6:00 PM)",
                "🧺 Chores",
                "😊 Free time",
                "🛁 Evening routine",
                "📖 Bedtime prep (9:00 PM)",
                "😴 Sleep (10:00 PM)"
            ])
        ]

        for period, items in schedule_items:
            frame = tk.LabelFrame(
                self.content_frame,
                text=period,
                font=('Arial', 12, 'bold'),
                bg='white',
                padx=15,
                pady=10
            )
            frame.pack(fill=tk.X, pady=10)

            for item in items:
                item_frame = tk.Frame(frame, bg='white')
                item_frame.pack(fill=tk.X, pady=3)

                check_var = tk.BooleanVar()
                check = tk.Checkbutton(
                    item_frame,
                    text=item,
                    variable=check_var,
                    bg='white',
                    font=('Arial', 11)
                )
                check.pack(side=tk.LEFT)

        # Tips
        tips_frame = tk.Frame(self.content_frame, bg='#E3F2FD', relief=tk.SOLID, borderwidth=1)
        tips_frame.pack(fill=tk.X, pady=10)

        tips = """
        💡 Visual Schedule Tips:
        • Use pictures/icons for each step
        • Keep it in the same place always
        • Check off items as you complete them
        • Include approximate times
        • Build in transition time between activities
        • Print and laminate for reuse
        • Use colors to categorize activities
        """

        tk.Label(
            tips_frame,
            text=tips,
            font=('Arial', 9),
            bg='#E3F2FD',
            fg='#666',
            justify=tk.LEFT
        ).pack(padx=15, pady=10, anchor='w')

    def show_communication_cards(self):
        """Show communication cards"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🗣️ Communication Cards",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Quick cards for common needs and feelings",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Communication cards
        cards = [
            ("🔇 I need quiet", "I'm overwhelmed by noise", "#FFE082"),
            ("⏸️ I need a break", "I need time to recharge", "#90CAF9"),
            ("❓ I don't understand", "Please explain differently", "#CE93D8"),
            ("⏰ I need more time", "I'm processing information", "#A5D6A7"),
            ("🚫 Please stop", "This is too much", "#EF9A9A"),
            ("✋ Don't touch me", "I need personal space", "#FFAB91"),
            ("🤔 I'm thinking", "Give me a moment to respond", "#F48FB1"),
            ("👍 I'm okay", "I'm doing fine", "#81C784"),
            ("😰 I'm anxious", "I'm feeling worried", "#FFF176"),
            ("😔 I'm sad", "I'm feeling down", "#B0BEC5"),
            ("😠 I'm frustrated", "I'm having a hard time", "#FF8A65"),
            ("🏠 I want to go home", "I've reached my limit", "#BCAAA4")
        ]

        # Grid layout for cards
        card_frame = tk.Frame(self.content_frame, bg='white')
        card_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        row = 0
        col = 0

        for emoji_text, description, color in cards:
            card = tk.Frame(
                card_frame,
                bg=color,
                relief=tk.RAISED,
                borderwidth=2
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

            tk.Label(
                card,
                text=emoji_text,
                font=('Arial', 14, 'bold'),
                bg=color,
                fg='#2c3e50'
            ).pack(pady=5)

            tk.Label(
                card,
                text=description,
                font=('Arial', 9),
                bg=color,
                fg='#2c3e50',
                wraplength=100
            ).pack(pady=5, padx=5)

            col += 1
            if col > 2:
                col = 0
                row += 1

        # Configure grid weights
        for i in range(3):
            card_frame.grid_columnconfigure(i, weight=1)

    def show_accommodations(self):
        """Show sensory accommodation suggestions"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🔊 Sensory Accommodations",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Strategies for sensory comfort",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Create notebook
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Visual
        visual_frame = tk.Frame(notebook, bg='white')
        notebook.add(visual_frame, text='Visual')

        visual_content = """
        👁️ Visual Accommodations

        For Light Sensitivity:
        • Wear sunglasses (even indoors if needed)
        • Use blue light filtering glasses
        • Dim screens and use dark mode
        • Use lamps instead of overhead lights
        • Sit away from windows
        • Use blackout curtains

        For Visual Clutter:
        • Minimize decorations
        • Use organizational systems
        • Label everything clearly
        • Keep workspaces tidy
        • Use neutral colors
        • Remove visual distractions during focus work

        For Movement Sensitivity:
        • Sit where you won't see people walking by
        • Use screen filters to reduce flicker
        • Take breaks from screens
        • Close eyes periodically
        """

        tk.Label(
            visual_frame,
            text=visual_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Auditory
        auditory_frame = tk.Frame(notebook, bg='white')
        notebook.add(auditory_frame, text='Auditory')

        auditory_content = """
        👂 Auditory Accommodations

        For Noise Sensitivity:
        • Noise-cancelling headphones
        • Earplugs or ear defenders
        • White noise or brown noise
        • Music (if helpful)
        • Request quiet workspace
        • Work during quiet hours
        • Use "do not disturb" signs

        For Processing:
        • Ask for written instructions
        • Request one-on-one conversations
        • Take notes during meetings
        • Ask people to speak slower
        • Use visual supports with audio
        • Reduce background noise

        For Specific Sounds:
        • Identify and avoid triggers
        • Communicate your needs
        • Have an exit strategy
        • Practice gradual exposure (if desired)
        """

        tk.Label(
            auditory_frame,
            text=auditory_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Tactile
        tactile_frame = tk.Frame(notebook, bg='white')
        notebook.add(tactile_frame, text='Tactile')

        tactile_content = """
        ✋ Tactile Accommodations

        For Clothing Sensitivity:
        • Remove tags from clothes
        • Wear soft, comfortable fabrics
        • Avoid tight or scratchy materials
        • Wear same style if it works
        • Inside-out if seams bother you
        • Wash new clothes before wearing

        For Touch Sensitivity:
        • Communicate boundaries about touch
        • Use weighted blankets
        • Self-administer deep pressure
        • Carry fidget tools
        • Use gloves if needed
        • Control your environment temperature

        For Texture Seeking:
        • Keep fidget toys handy
        • Use textured materials
        • Chew safe items (gum, chewelry)
        • Access to sensory tools
        """

        tk.Label(
            tactile_frame,
            text=tactile_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # General
        general_frame = tk.Frame(notebook, bg='white')
        notebook.add(general_frame, text='General')

        general_content = """
        🌟 General Strategies

        Sensory Diet:
        • Regular sensory input throughout day
        • Movement breaks
        • Deep pressure activities
        • Proprioceptive input (heavy work)
        • Schedule sensory activities

        Safe Spaces:
        • Create a calm-down area
        • Low lighting, minimal sound
        • Comfortable seating
        • Sensory tools available
        • Escape plan for overwhelm

        Communication:
        • Tell others your needs
        • Use communication cards
        • Set boundaries
        • Explain sensory processing
        • Ask for accommodations

        Self-Regulation:
        • Know your limits
        • Take breaks before meltdown
        • Use calming strategies
        • Monitor sensory input
        • Practice self-advocacy
        """

        tk.Label(
            general_frame,
            text=general_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def show_tips(self):
        """Show autism-specific tips"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="💡 Autism Tips & Strategies",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Practical strategies for daily life",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        content = """
        💡 Daily Life Tips

        Social Interactions:
        • Practice scripts for common situations
        • It's okay to need breaks from socializing
        • Ask for clarification when confused
        • Unmask at home - you don't have to perform
        • Find your people (neurodivergent friends)
        • Body language isn't universal - ask directly
        • Parallel play counts as socializing

        Sensory Management:
        • Know your sensory profile
        • Carry sensory tools (headphones, sunglasses, fidgets)
        • Create a sensory-friendly space at home
        • It's okay to stim - it helps regulate
        • Leave situations when overwhelmed
        • Use sensory accommodations without shame

        Executive Function:
        • Use visual schedules and checklists
        • Set up routines for regular tasks
        • Use timers and alarms liberally
        • Break tasks into tiny steps
        • External organization systems are your friends
        • Ask for help - it's not failure

        Communication:
        • Being direct is not rude - it's efficient
        • Ask for written communication
        • Take time to process before responding
        • Use scripts when helpful
        • Selective mutism is valid
        • AAC is communication

        Special Interests:
        • Your interests are valuable
        • Share them with people who appreciate them
        • Use them for self-regulation
        • They can become careers
        • Stimming related to interests is great
        • You don't have to justify enjoyment

        Self-Care:
        • Masking is exhausting - rest after
        • Meltdowns/shutdowns are not failures
        • Recovery time is necessary
        • Your needs are not "too much"
        • Accommodations are not cheating
        • You are not broken - you're autistic

        Remember: There is no wrong way to be autistic.
        Your experiences are valid.
        You don't need to earn acceptance.
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
    app = AutismSupport()
    app.run()
