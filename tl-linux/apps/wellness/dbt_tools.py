#!/usr/bin/env python3
"""
TL Linux - DBT Tools
Dialectical Behavior Therapy skills training
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from datetime import datetime

class DBTTools:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚖️ DBT Tools - Dialectical Behavior Therapy")
        self.root.geometry("1000x700")

        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellness'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.config_dir / 'dbt_data.json'

        self.data = self.load_data()
        self.setup_ui()

    def load_data(self):
        """Load DBT data"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'emotion_regulation': [],
            'distress_tolerance': [],
            'interpersonal': [],
            'mindfulness': []
        }

    def save_data(self):
        """Save DBT data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg='#9C27B0', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="⚖️ DBT Tools - Dialectical Behavior Therapy",
            font=('Arial', 18, 'bold'),
            bg='#9C27B0',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Four core skills for emotional wellbeing",
            font=('Arial', 10),
            bg='#9C27B0',
            fg='white'
        ).pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg='#2c3e50', width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        modules = [
            ('🎭 Emotion Regulation', self.show_emotion_regulation),
            ('🛡️ Distress Tolerance', self.show_distress_tolerance),
            ('🤝 Interpersonal Effectiveness', self.show_interpersonal),
            ('🧘 Mindfulness', self.show_mindfulness),
        ]

        for module_name, command in modules:
            btn = tk.Button(
                sidebar,
                text=module_name,
                command=command,
                bg='#34495e',
                fg='white',
                font=('Arial', 11),
                relief=tk.FLAT,
                anchor='w',
                padx=20,
                pady=15,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=5, pady=3)

        # Content area
        self.content_frame = tk.Frame(main_container, bg='white')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_emotion_regulation()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_emotion_regulation(self):
        """Show emotion regulation skills"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🎭 Emotion Regulation",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Skills to understand and manage emotions",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Create notebook for sub-skills
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # ABC PLEASE tab
        abc_frame = tk.Frame(notebook, bg='white')
        notebook.add(abc_frame, text='ABC PLEASE')

        abc_content = """
        🏥 ABC PLEASE - Building Emotional Resilience

        Accumulate positive experiences:
        • Do one pleasant thing each day
        • Work toward long-term goals
        • Build mastery and competence

        Build relationships:
        • Reconnect with people
        • Repair damaged relationships
        • Spend time with positive people

        Cope ahead:
        • Imagine difficult situations
        • Plan how you'll handle them
        • Rehearse your response

        Physical health (PLEASE):
        • PL: Treat Physical iLlness
        • E: Balance Eating
        • A: Avoid mood-altering drugs
        • S: Balance Sleep
        • E: Get Exercise

        Taking care of your body helps regulate emotions!
        """

        tk.Label(
            abc_frame,
            text=abc_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Opposite Action tab
        opposite_frame = tk.Frame(notebook, bg='white')
        notebook.add(opposite_frame, text='Opposite Action')

        opposite_content = """
        🔄 Opposite Action

        When your emotion doesn't fit the facts,
        or when acting on it makes things worse:

        If you feel FEAR (that doesn't fit):
        → Approach what you're afraid of
        → Do what you're avoiding

        If you feel ANGER (unjustified):
        → Gently avoid the person
        → Be kind instead of aggressive
        → Take time to cool down

        If you feel SADNESS (that doesn't fit):
        → Get active
        → Approach, don't avoid
        → Do opposite of urge to withdraw

        If you feel SHAME (unjustified):
        → Do the thing anyway
        → Share your "secret"
        → Validate yourself

        Important: Only use when emotion doesn't fit the facts!
        If emotion is justified, opposite action might not help.
        """

        tk.Label(
            opposite_frame,
            text=opposite_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Check the Facts tab
        facts_frame = tk.Frame(notebook, bg='white')
        notebook.add(facts_frame, text='Check the Facts')

        tk.Label(
            facts_frame,
            text="📋 Check the Facts",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=20, pady=(20, 10))

        questions = [
            "1. What is the emotion I'm feeling?",
            "2. What is the prompting event? What happened?",
            "3. What are my interpretations, thoughts, and assumptions?",
            "4. Am I assuming a threat? What's the threat?",
            "5. What's the catastrophe? (Worst case scenario)",
            "6. Does my emotion fit the actual facts?",
            "7. What's the probability of the catastrophe?",
            "8. Is this emotion helpful for me right now?"
        ]

        for q in questions:
            tk.Label(
                facts_frame,
                text=q,
                font=('Arial', 10),
                bg='white',
                fg='#2c3e50',
                anchor='w'
            ).pack(anchor='w', padx=30, pady=5)

    def show_distress_tolerance(self):
        """Show distress tolerance skills"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🛡️ Distress Tolerance",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Skills for surviving crisis situations",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Create notebook
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # STOP Skill
        stop_frame = tk.Frame(notebook, bg='white')
        notebook.add(stop_frame, text='STOP')

        stop_content = """
        🛑 STOP Skill - When Crisis Hits

        S - Stop
        • Don't react immediately
        • Freeze! Don't move a muscle
        • Your emotions are trying to make you act

        T - Take a step back
        • Get unstuck from the situation
        • Take a break
        • Let go (mentally or physically)

        O - Observe
        • Notice what's happening inside and outside you
        • What are you thinking? Feeling? Wanting to do?
        • What's the situation actually like?

        P - Proceed mindfully
        • Act with awareness
        • Consider your goals
        • Ask: Will this make things better or worse?

        Use STOP when you feel like you're going to do
        something impulsive that you'll regret later.
        """

        tk.Label(
            stop_frame,
            text=stop_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # TIP Skills
        tip_frame = tk.Frame(notebook, bg='white')
        notebook.add(tip_frame, text='TIP')

        tip_content = """
        🌡️ TIP Skills - Change Body Chemistry

        T - Temperature
        • Hold ice cubes in your hands
        • Splash cold water on face
        • Take a cold shower
        • Cold changes body chemistry quickly

        I - Intense Exercise
        • Run, jump, dance
        • Do jumping jacks
        • Physical exertion uses up stress hormones
        • Even 10 minutes helps

        P - Paced Breathing
        • Breathe in for 4 counts
        • Hold for 4 counts (or skip)
        • Breathe out for 6-8 counts
        • Slower exhale than inhale calms you

        Alternative P - Paired Muscle Relaxation
        • Tense muscle groups
        • Then release and relax
        • Work through body systematically

        Use TIP when emotions are extremely intense
        and you need to calm down quickly.
        """

        tk.Label(
            tip_frame,
            text=tip_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # ACCEPTS
        accepts_frame = tk.Frame(notebook, bg='white')
        notebook.add(accepts_frame, text='ACCEPTS')

        accepts_content = """
        🎯 ACCEPTS - Distract Yourself

        A - Activities
        • Do something engaging
        • Exercise, hobbies, chores

        C - Contributing
        • Help someone else
        • Volunteer, be kind

        C - Comparisons
        • Compare to times you coped well
        • Compare to those less fortunate

        E - Emotions (opposite)
        • Read something funny
        • Watch a comedy
        • Listen to upbeat music

        P - Push away
        • Push situation out of mind temporarily
        • Put it in a mental box
        • Revisit when calmer

        T - Thoughts (other)
        • Count things around you
        • Do puzzles, read
        • Occupy your mind

        S - Sensations (other)
        • Hold ice, take a hot shower
        • Listen to loud music
        • Eat something strong-tasting

        Distraction gives you time to calm down.
        It's not avoidance - it's strategic!
        """

        tk.Label(
            accepts_frame,
            text=accepts_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # Self-Soothe
        soothe_frame = tk.Frame(notebook, bg='white')
        notebook.add(soothe_frame, text='Self-Soothe')

        soothe_content = """
        💆 Self-Soothe with the Five Senses

        👁️ Vision
        • Look at beautiful things
        • Nature, art, photos
        • Notice colors and details

        👂 Sound
        • Listen to soothing music
        • Nature sounds, white noise
        • Notice sounds around you

        👃 Smell
        • Scented candles, lotions
        • Fresh air, flowers
        • Bake something fragrant

        👅 Taste
        • Enjoy a favorite food slowly
        • Sip tea or hot chocolate
        • Savor each bite

        ✋ Touch
        • Soft blanket, warm bath
        • Pet an animal
        • Feel textures mindfully

        Be kind to yourself through your senses.
        You deserve soothing and comfort!
        """

        tk.Label(
            soothe_frame,
            text=soothe_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def show_interpersonal(self):
        """Show interpersonal effectiveness skills"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🤝 Interpersonal Effectiveness",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Skills for healthy relationships and communication",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        # Create notebook
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # DEAR MAN
        dear_frame = tk.Frame(notebook, bg='white')
        notebook.add(dear_frame, text='DEAR MAN')

        dear_content = """
        💬 DEAR MAN - Asking for What You Need

        Use this to make requests and set boundaries:

        D - Describe the situation
        • Stick to facts
        • No judgments or opinions
        • "When you..."

        E - Express feelings and opinions
        • Use "I feel..." statements
        • Be clear about your experience

        A - Assert what you want
        • Ask clearly for what you need
        • Say no if necessary

        R - Reinforce
        • Explain positive results
        • "This would help me because..."

        M - Mindful
        • Stay focused on your goal
        • Don't get distracted
        • Ignore attacks

        A - Appear confident
        • Eye contact, tone of voice
        • Firm but friendly

        N - Negotiate
        • Be willing to give to get
        • Offer alternatives
        • Ask what would work for them

        Example: "When you borrow my things without asking (D),
        I feel disrespected (E). I need you to ask first (A).
        This will help us trust each other more (R)."
        """

        tk.Label(
            dear_frame,
            text=dear_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # GIVE
        give_frame = tk.Frame(notebook, bg='white')
        notebook.add(give_frame, text='GIVE')

        give_content = """
        💝 GIVE - Maintaining Relationships

        Use this to keep relationships healthy:

        G - Gentle
        • Be courteous and nice
        • No attacks, threats, or judgments
        • Be respectful

        I - Interested
        • Listen to the other person
        • Don't interrupt
        • Be curious about their perspective

        V - Validate
        • Acknowledge their feelings
        • Show you understand
        • Find the grain of truth

        E - Easy manner
        • Smile, use humor
        • Be lighthearted when appropriate
        • Don't be a martyr

        Example: "I can see this is really frustrating for you (V).
        Tell me more about what happened (I).
        Maybe we can figure this out together (E)."

        GIVE skills show you care about the relationship,
        not just getting your way.
        """

        tk.Label(
            give_frame,
            text=give_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

        # FAST
        fast_frame = tk.Frame(notebook, bg='white')
        notebook.add(fast_frame, text='FAST')

        fast_content = """
        ⭐ FAST - Keeping Self-Respect

        Use this to maintain your self-respect:

        F - Fair
        • Be fair to yourself AND others
        • Don't sacrifice yourself
        • Don't be unfairly demanding

        A - Apologies (no excessive)
        • Don't over-apologize
        • No apologizing for existing
        • Only apologize when appropriate

        S - Stick to values
        • Act according to your values
        • Don't compromise your integrity
        • Be true to yourself

        T - Truthful
        • Don't lie or exaggerate
        • Don't make excuses
        • Be honest (but not brutal)

        Example of FAST violation:
        "I'm so sorry for bothering you, I know I'm
        being ridiculous, but could you possibly..." ❌

        Example using FAST:
        "I'd like to discuss something with you.
        When would be a good time?" ✓

        Your self-respect matters!
        """

        tk.Label(
            fast_frame,
            text=fast_content,
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=20, anchor='w')

    def show_mindfulness(self):
        """Show mindfulness skills"""
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="🧘 Mindfulness",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Core DBT mindfulness skills",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))

        content = """
        🧘 Mindfulness - The Foundation

        Three "WHAT" Skills (What you do):

        1. OBSERVE
           • Notice without words
           • Just observe sensations, thoughts, emotions
           • Watch them come and go

        2. DESCRIBE
           • Put words on what you observe
           • Stick to the facts
           • Separate thoughts from facts

        3. PARTICIPATE
           • Become one with your activity
           • Throw yourself into the moment
           • Go with the flow

        Three "HOW" Skills (How you do it):

        1. NON-JUDGMENTALLY
           • See but don't evaluate
           • No good or bad
           • Just notice "angry thoughts" not "bad thoughts"

        2. ONE-MINDFULLY
           • Do one thing at a time
           • Focus on now
           • When mind wanders, bring it back

        3. EFFECTIVELY
           • Do what works
           • Act skillfully
           • Let go of "right" and "wrong"

        Practice:
        • Observe your breath
        • Describe: "breathing in, breathing out"
        • Participate: become the breath
        • Non-judgmentally: don't judge the thoughts
        • One-mindfully: just the breath
        • Effectively: keep returning when mind wanders

        Mindfulness is the foundation of all DBT skills.
        It helps you respond rather than react.
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
    app = DBTTools()
    app.run()
