#!/usr/bin/env python3
"""
TL Chronos AI Agent
Friendly, learning AI assistant for TL Linux

Features:
- Learns from user interactions and patterns
- Friendly conversational personality
- Context-aware suggestions
- Pattern recognition for habits
- Proactive assistance
- Integration with voice assistant
- Personalized recommendations
- Privacy-focused (all learning local)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import random

# Conditional tkinter import (only for GUI mode)
try:
    import tkinter as tk
    from tkinter import scrolledtext, ttk
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    print("Warning: tkinter not available - GUI mode disabled")

class ChronosAI:
    """Chronos - The friendly TL Linux AI agent"""

    def __init__(self, root=None, headless=False):
        # Force headless mode if tkinter is not available
        if not HAS_TKINTER and not headless:
            print("Warning: Forcing headless mode - tkinter not available")
            headless = True

        self.headless = headless

        if not headless:
            if root is None:
                self.root = tk.Tk()
                self.root.title("Chronos AI Agent 🤖")
                self.root.geometry("700x800")
            else:
                self.root = root

            self.root.configure(bg='#0d1117')
        else:
            self.root = None

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'chronos-ai'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.memory_file = self.config_dir / 'memory.json'
        self.patterns_file = self.config_dir / 'patterns.json'
        self.preferences_file = self.config_dir / 'preferences.json'
        self.conversation_file = self.config_dir / 'conversations.json'

        # Load AI data
        self.load_memory()
        self.load_patterns()
        self.load_preferences()

        # Personality traits
        self.personality = {
            'name': 'Chronos',
            'friendliness': 0.9,  # 0-1
            'helpfulness': 0.95,
            'humor': 0.7,
            'formality': 0.3,  # Lower = more casual
            'enthusiasm': 0.8
        }

        # Current conversation context
        self.conversation_context = []
        self.last_interaction = None

        # Setup UI (only if not headless)
        if not headless:
            self.setup_ui()
            # Greet user
            self.greet_user()

    def load_memory(self):
        """Load AI memory"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                'user_name': None,
                'first_interaction': datetime.now().isoformat(),
                'total_interactions': 0,
                'favorite_apps': {},
                'common_times': {},  # When user typically uses system
                'frequently_asked': {},
                'user_mood_pattern': {},
                'achievements_celebrated': []
            }

    def save_memory(self):
        """Save AI memory"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def load_patterns(self):
        """Load learned patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = {
                'app_usage': {},  # App -> times used
                'time_patterns': {},  # Hour -> activities
                'session_length': [],  # List of session durations
                'break_compliance': [],  # Did user take breaks?
                'productivity_patterns': {},
                'wellbeing_engagement': 0.0
            }

    def save_patterns(self):
        """Save learned patterns"""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)

    def load_preferences(self):
        """Load user preferences"""
        if self.preferences_file.exists():
            with open(self.preferences_file, 'r') as f:
                self.preferences = json.load(f)
        else:
            self.preferences = {
                'communication_style': 'friendly',  # friendly, professional, casual
                'proactive_suggestions': True,
                'learning_enabled': True,
                'celebration_style': 'enthusiastic',  # enthusiastic, subtle, none
                'reminder_style': 'gentle'  # gentle, direct, none
            }

    def save_preferences(self):
        """Save preferences"""
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)

    def setup_ui(self):
        """Setup the UI"""
        # Header with Chronos branding
        header = tk.Frame(self.root, bg='#1a1f35', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🤖 Chronos",
            font=('Arial', 32, 'bold'),
            bg='#1a1f35',
            fg='#00d4ff'
        ).pack(pady=5)

        tk.Label(
            header,
            text="Your Friendly AI Assistant",
            font=('Arial', 12, 'italic'),
            bg='#1a1f35',
            fg='#66b3ff'
        ).pack()

        # Main content area with tabs
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.configure('TNotebook', background='#0d1117')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))

        # Create tabs
        self.chat_tab = tk.Frame(tab_container, bg='#0d1117')
        self.insights_tab = tk.Frame(tab_container, bg='#0d1117')
        self.learning_tab = tk.Frame(tab_container, bg='#0d1117')
        self.settings_tab = tk.Frame(tab_container, bg='#0d1117')

        tab_container.add(self.chat_tab, text='💬 Chat')
        tab_container.add(self.insights_tab, text='💡 Insights')
        tab_container.add(self.learning_tab, text='🧠 Learning')
        tab_container.add(self.settings_tab, text='⚙️ Settings')

        # Setup tabs
        self.setup_chat_tab()
        self.setup_insights_tab()
        self.setup_learning_tab()
        self.setup_settings_tab()

    def setup_chat_tab(self):
        """Setup chat interface"""
        container = tk.Frame(self.chat_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            container,
            font=('Arial', 11),
            bg='#161b22',
            fg='#c9d1d9',
            wrap=tk.WORD,
            padx=15,
            pady=15,
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure tags for styling
        self.chat_display.tag_config('chronos', foreground='#00d4ff', font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('user', foreground='#7ee787', font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('timestamp', foreground='#8b949e', font=('Arial', 9))
        self.chat_display.tag_config('suggestion', foreground='#ffa657', font=('Arial', 10, 'italic'))

        # Input area
        input_frame = tk.Frame(container, bg='#0d1117')
        input_frame.pack(fill=tk.X)

        self.chat_input = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='#161b22',
            fg='#c9d1d9',
            insertbackground='white'
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', lambda e: self.send_message())

        tk.Button(
            input_frame,
            text="Send 📤",
            font=('Arial', 11),
            bg='#238636',
            fg='white',
            command=self.send_message,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)

        # Quick suggestions
        suggestions_frame = tk.Frame(container, bg='#0d1117')
        suggestions_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            suggestions_frame,
            text="Quick actions:",
            font=('Arial', 9),
            bg='#0d1117',
            fg='#8b949e'
        ).pack(side=tk.LEFT, padx=5)

        quick_actions = [
            "How am I doing?",
            "Give me a tip",
            "What should I focus on?",
            "Tell me a joke"
        ]

        for action in quick_actions:
            tk.Button(
                suggestions_frame,
                text=action,
                font=('Arial', 8),
                bg='#21262d',
                fg='#c9d1d9',
                command=lambda a=action: self.quick_action(a),
                relief=tk.FLAT,
                padx=8,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

    def setup_insights_tab(self):
        """Setup insights display"""
        container = tk.Frame(self.insights_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="📊 Your Insights & Patterns",
            font=('Arial', 18, 'bold'),
            bg='#0d1117',
            fg='#00d4ff'
        ).pack(pady=10)

        # Insights display
        self.insights_display = scrolledtext.ScrolledText(
            container,
            font=('Courier', 10),
            bg='#161b22',
            fg='#c9d1d9',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.insights_display.pack(fill=tk.BOTH, expand=True, pady=10)

        # Refresh button
        tk.Button(
            container,
            text="🔄 Refresh Insights",
            font=('Arial', 11),
            bg='#238636',
            fg='white',
            command=self.generate_insights,
            padx=20,
            pady=10
        ).pack()

        # Load initial insights
        self.generate_insights()

    def setup_learning_tab(self):
        """Setup learning progress display"""
        container = tk.Frame(self.learning_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="🧠 What I've Learned About You",
            font=('Arial', 18, 'bold'),
            bg='#0d1117',
            fg='#00d4ff'
        ).pack(pady=10)

        # Learning display
        learning_frame = tk.LabelFrame(
            container,
            text="Knowledge Base",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        learning_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.learning_display = scrolledtext.ScrolledText(
            learning_frame,
            font=('Arial', 11),
            bg='#161b22',
            fg='#c9d1d9',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.learning_display.pack(fill=tk.BOTH, expand=True)

        # Learning controls
        controls = tk.Frame(container, bg='#0d1117')
        controls.pack(fill=tk.X, pady=10)

        tk.Button(
            controls,
            text="📊 Update Learning",
            font=('Arial', 11),
            bg='#238636',
            fg='white',
            command=self.display_learning,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="🗑️ Clear Memory",
            font=('Arial', 11),
            bg='#da3633',
            fg='white',
            command=self.clear_memory,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Initial display
        self.display_learning()

    def setup_settings_tab(self):
        """Setup AI settings"""
        container = tk.Frame(self.settings_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Personality settings
        personality_frame = tk.LabelFrame(
            container,
            text="Personality Settings",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        personality_frame.pack(fill=tk.X, pady=10)

        # Communication style
        style_frame = tk.Frame(personality_frame, bg='#0d1117')
        style_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            style_frame,
            text="Communication Style:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(side=tk.LEFT)

        self.comm_style_var = tk.StringVar(value=self.preferences['communication_style'])
        for style in ['Casual', 'Friendly', 'Professional']:
            tk.Radiobutton(
                style_frame,
                text=style,
                variable=self.comm_style_var,
                value=style.lower(),
                font=('Arial', 10),
                bg='#0d1117',
                fg='white',
                selectcolor='#161b22'
            ).pack(side=tk.LEFT, padx=10)

        # Features
        features_frame = tk.LabelFrame(
            container,
            text="Features",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        features_frame.pack(fill=tk.X, pady=10)

        self.proactive_var = tk.BooleanVar(value=self.preferences['proactive_suggestions'])
        tk.Checkbutton(
            features_frame,
            text="Proactive suggestions (I'll offer help before you ask)",
            variable=self.proactive_var,
            font=('Arial', 10),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

        self.learning_var = tk.BooleanVar(value=self.preferences['learning_enabled'])
        tk.Checkbutton(
            features_frame,
            text="Learning enabled (I'll remember your preferences)",
            variable=self.learning_var,
            font=('Arial', 10),
            bg='#0d1117',
            fg='white',
            selectcolor='#161b22'
        ).pack(anchor=tk.W, pady=5)

        # Save button
        tk.Button(
            container,
            text="💾 Save Settings",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=self.save_settings,
            padx=30,
            pady=12
        ).pack(pady=20)

    def greet_user(self):
        """Greet the user"""
        user_name = self.memory.get('user_name') or "friend"

        greetings = [
            f"Hey {user_name}! 👋 Great to see you!",
            f"Welcome back, {user_name}! How can I help you today?",
            f"Hi {user_name}! Ready to make today awesome? 😊",
            f"Hello {user_name}! I'm here if you need anything!"
        ]

        greeting = random.choice(greetings)
        self.add_to_chat("Chronos", greeting)

        # Add a helpful tip if it's been a while
        if self.memory['total_interactions'] == 0:
            self.add_to_chat("Chronos", "I'm Chronos, your friendly AI assistant! I learn from our interactions to help you better. Try asking me anything!")

    def add_to_chat(self, speaker, message, tag=None):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M")

        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')

        if speaker == "Chronos":
            self.chat_display.insert(tk.END, "🤖 Chronos: ", 'chronos')
        else:
            self.chat_display.insert(tk.END, f"👤 {speaker}: ", 'user')

        self.chat_display.insert(tk.END, f"{message}\n\n", tag or '')
        self.chat_display.see(tk.END)

        # Save to conversation history
        self.conversation_context.append({
            'speaker': speaker,
            'message': message,
            'timestamp': timestamp
        })

    def send_message(self):
        """Send a message to Chronos"""
        message = self.chat_input.get().strip()
        if not message:
            return

        self.chat_input.delete(0, tk.END)

        # Display user message
        self.add_to_chat("You", message)

        # Process message and generate response
        response = self.process_message(message)

        # Display Chronos response
        self.add_to_chat("Chronos", response)

        # Update memory
        self.memory['total_interactions'] += 1
        self.last_interaction = datetime.now()
        self.save_memory()

    def process_message(self, message):
        """Process user message and generate response"""
        message_lower = message.lower()

        # Learn from the message
        if self.preferences['learning_enabled']:
            self.learn_from_message(message_lower)

        # Intent detection and response generation

        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return self.generate_greeting_response()

        # Name learning
        if 'my name is' in message_lower or 'call me' in message_lower:
            return self.learn_name(message)

        # Status check
        if any(phrase in message_lower for phrase in ['how am i doing', 'my progress', 'my status']):
            return self.generate_status_response()

        # Advice/tips
        if any(word in message_lower for word in ['tip', 'advice', 'suggestion', 'recommend']):
            return self.generate_tip()

        # Focus assistance
        if 'focus' in message_lower or 'concentrate' in message_lower:
            return self.generate_focus_advice()

        # Motivation
        if any(word in message_lower for word in ['motivate', 'inspire', 'encourage']):
            return self.generate_motivation()

        # Jokes/humor
        if 'joke' in message_lower or 'funny' in message_lower:
            return self.tell_joke()

        # Help
        if 'help' in message_lower or 'what can you do' in message_lower:
            return self.generate_help_response()

        # Wellbeing check
        if any(word in message_lower for word in ['tired', 'stressed', 'overwhelmed']):
            return self.generate_wellbeing_response(message_lower)

        # Default: conversational response
        return self.generate_conversational_response(message)

    def learn_from_message(self, message):
        """Learn patterns from user message"""
        # Track frequently asked topics
        words = message.split()
        for word in words:
            if len(word) > 3:  # Ignore short words
                self.memory['frequently_asked'][word] = self.memory['frequently_asked'].get(word, 0) + 1

        # Update time patterns
        hour = datetime.now().hour
        self.memory['common_times'][str(hour)] = self.memory['common_times'].get(str(hour), 0) + 1

        self.save_memory()

    def learn_name(self, message):
        """Learn user's name"""
        # Simple name extraction
        if 'my name is' in message.lower():
            name = message.lower().split('my name is')[1].strip().split()[0]
        elif 'call me' in message.lower():
            name = message.lower().split('call me')[1].strip().split()[0]
        else:
            return "I didn't quite catch your name. Could you say 'My name is [name]'?"

        name = name.capitalize()
        self.memory['user_name'] = name
        self.save_memory()

        return f"Nice to meet you, {name}! I'll remember that. 😊"

    def generate_greeting_response(self):
        """Generate a greeting response"""
        responses = [
            "Hey! How's it going? 😊",
            "Hi there! What's on your mind?",
            "Hello! Ready to tackle something today?",
            "Hey! Good to hear from you!"
        ]
        return random.choice(responses)

    def generate_status_response(self):
        """Generate status/progress response"""
        # Check if we have gamification data
        from system.integration_coordinator import get_achievement_summary

        try:
            summary = get_achievement_summary()
            if summary:
                return f"You're doing great! 🌟\n\nYou're at Level {summary['level']} with {summary['total_xp']} XP!\n\nYou've unlocked {summary['achievements']} achievements, taken {summary['breaks']} breaks, and logged {summary['water']} glasses of water.\n\nKeep up the awesome work!"
        except:
            pass

        return "You're making great progress! Keep engaging with the wellbeing features and I'll have more detailed stats for you soon! 💪"

    def generate_tip(self):
        """Generate a helpful tip"""
        tips = [
            "💡 Try the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds. Your eyes will thank you!",
            "🧘 Taking regular breaks actually improves productivity! Your brain needs rest to work at its best.",
            "💧 Staying hydrated boosts focus and energy. Aim for 8 glasses a day!",
            "🎯 Use Focus Mode when you really need to concentrate. It blocks distractions and helps you get in the zone.",
            "📔 Journaling for just 5 minutes a day can significantly improve your mental clarity and mood.",
            "🏆 Check out the Achievements tab - gamifying your wellbeing makes healthy habits more fun!",
            "🎤 Did you know you can control the system with voice commands? Just say 'Hey TL'!",
            "🧘 A quick 2-minute breathing exercise can reduce stress and increase focus instantly."
        ]
        return random.choice(tips)

    def generate_focus_advice(self):
        """Generate focus-related advice"""
        advice = [
            "🎯 Here's my focus formula:\n1. Close unnecessary apps\n2. Use Focus Mode\n3. Set a timer for 25 minutes\n4. Take a 5-minute break\n5. Repeat!\n\nThis is called the Pomodoro Technique and it works wonders!",
            "To help you focus:\n• Turn on Focus Mode\n• Put phone in another room\n• Tell Chronos what you're working on (accountability!)\n• Take breaks to stay fresh\n\nYou've got this! 💪",
            "Focus tip: Your brain works best in 90-minute cycles. Work intensely for 90 min, then take a real break. Quality over quantity! 🧠"
        ]
        return random.choice(advice)

    def generate_motivation(self):
        """Generate motivational message"""
        motivations = [
            "You're doing amazing! Every small step forward is progress. Keep going! 🌟",
            "Remember: You're capable of more than you think. Believe in yourself! 💪",
            "Progress isn't always linear, but you're moving forward. That's what matters! 🚀",
            "You've overcome challenges before, and you'll overcome this one too. I believe in you! ⭐",
            "Small daily improvements lead to stunning results. You're on the right path! 🌈",
            "You're not just using a computer - you're investing in your wellbeing. That's awesome! 🎉"
        ]
        return random.choice(motivations)

    def tell_joke(self):
        """Tell a joke"""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 😄",
            "Why was the computer cold? It left its Windows open! 🪟❄️",
            "What's a computer's favorite snack? Microchips! 🍪",
            "Why did the developer go broke? Because he used up all his cache! 💸",
            "How does a computer get drunk? It takes screenshots! 📸😂",
            "I'd tell you a UDP joke, but you might not get it. 😉"
        ]
        return random.choice(jokes)

    def generate_wellbeing_response(self, message):
        """Generate response to wellbeing concerns"""
        if 'tired' in message:
            return "It sounds like you could use a break! 🧘\n\nWhy not:\n• Step away for 5 minutes\n• Do some light stretches\n• Get some fresh air\n• Have a healthy snack\n\nYour wellbeing matters more than any task! 💙"

        elif 'stressed' in message:
            return "I hear you - stress happens. Let's tackle this together! 😊\n\nTry:\n1. Take 5 deep breaths (in for 4, hold for 4, out for 4)\n2. Write down what's stressing you in the Journal\n3. Break big tasks into tiny steps\n4. Remember: You can only do your best, and that's enough!\n\nI'm here for you! 💚"

        elif 'overwhelmed' in message:
            return "Feeling overwhelmed is totally normal. Let's simplify! 🌟\n\nHere's what helps:\n• List everything (brain dump in Journal)\n• Pick ONE thing to focus on now\n• Ignore the rest temporarily\n• Take breaks\n• Be kind to yourself\n\nYou don't have to do everything at once! 🤗"

        return "I'm here for you! Remember to take care of yourself. Want to try a quick breathing exercise or take a short break? 💙"

    def generate_help_response(self):
        """Generate help response"""
        return """I can help you with lots of things! 🤖

**I can:**
• Give you tips and advice for productivity and wellbeing
• Check your progress and achievements
• Motivate and encourage you
• Help you focus
• Tell jokes to lighten the mood
• Learn your patterns and preferences
• Offer proactive suggestions
• Be a friendly companion!

**Try asking:**
• "How am I doing?"
• "Give me a tip"
• "What should I focus on?"
• "Tell me a joke"
• "I'm feeling stressed"
• "Help me focus"

I learn more about you with each interaction, so I get better at helping over time! 💙"""

    def generate_conversational_response(self, message):
        """Generate a conversational response"""
        responses = [
            "That's interesting! Tell me more.",
            "I see! How can I help with that?",
            "Got it! What would you like to do?",
            "Noted! Anything else on your mind?",
            "Thanks for sharing! I'm learning more about you. 😊",
            "Interesting! I'm here if you need any help with that."
        ]
        return random.choice(responses)

    def quick_action(self, action):
        """Handle quick action button"""
        self.chat_input.delete(0, tk.END)
        self.chat_input.insert(0, action)
        self.send_message()

    def generate_insights(self):
        """Generate insights from learned data"""
        self.insights_display.delete('1.0', tk.END)

        insights = []
        insights.append("═" * 60)
        insights.append("YOUR PERSONAL INSIGHTS")
        insights.append("═" * 60)
        insights.append("")

        # Interaction stats
        insights.append(f"📊 INTERACTION STATS:")
        insights.append(f"   Total conversations: {self.memory['total_interactions']}")

        if self.memory.get('first_interaction'):
            first = datetime.fromisoformat(self.memory['first_interaction'])
            days = (datetime.now() - first).days
            insights.append(f"   Days since first meeting: {days}")
        insights.append("")

        # Time patterns
        if self.memory['common_times']:
            insights.append("🕐 ACTIVITY PATTERNS:")
            sorted_times = sorted(self.memory['common_times'].items(), key=lambda x: int(x[0]))
            peak_hour = max(sorted_times, key=lambda x: x[1])
            insights.append(f"   Most active hour: {peak_hour[0]}:00")
            insights.append(f"   You tend to use the system most around {peak_hour[0]}:00")
            insights.append("")

        # Frequently asked
        if self.memory['frequently_asked']:
            insights.append("💬 COMMON TOPICS:")
            top_topics = sorted(
                self.memory['frequently_asked'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for topic, count in top_topics:
                insights.append(f"   • {topic} (mentioned {count} times)")
            insights.append("")

        # Suggestions
        insights.append("💡 PERSONALIZED SUGGESTIONS:")
        insights.append(self.generate_tip())
        insights.append("")

        insights.append("═" * 60)
        insights.append("These insights help me serve you better! 🤖")

        self.insights_display.insert('1.0', '\n'.join(insights))

    def display_learning(self):
        """Display what AI has learned"""
        self.learning_display.delete('1.0', tk.END)

        learning = []
        learning.append("🧠 WHAT I KNOW ABOUT YOU:\n\n")

        if self.memory.get('user_name'):
            learning.append(f"✓ Your name: {self.memory['user_name']}\n")

        learning.append(f"✓ We've had {self.memory['total_interactions']} conversations\n")

        if self.memory['common_times']:
            peak = max(self.memory['common_times'].items(), key=lambda x: x[1])[0]
            learning.append(f"✓ You're most active around {peak}:00\n")

        learning.append(f"\n📚 LEARNING STATUS:\n\n")
        learning.append(f"Patterns tracked: {len(self.patterns)}\n")
        learning.append(f"Preferences saved: {len(self.preferences)}\n")
        learning.append(f"Memory entries: {len(self.memory)}\n")

        learning.append(f"\n🎯 WHAT I'M LEARNING:\n\n")
        learning.append("• Your common questions and topics\n")
        learning.append("• Your activity patterns and timing\n")
        learning.append("• Your wellbeing engagement\n")
        learning.append("• Your communication preferences\n")

        learning.append("\n💙 All learning is stored locally on your device for privacy!")

        self.learning_display.insert('1.0', ''.join(learning))

    def clear_memory(self):
        """Clear AI memory"""
        import tkinter.messagebox as messagebox

        if messagebox.askyesno("Clear Memory", "Are you sure you want to clear all my memory and learning? This cannot be undone!"):
            self.memory = {
                'user_name': None,
                'first_interaction': datetime.now().isoformat(),
                'total_interactions': 0,
                'favorite_apps': {},
                'common_times': {},
                'frequently_asked': {},
                'user_mood_pattern': {},
                'achievements_celebrated': []
            }
            self.patterns = {
                'app_usage': {},
                'time_patterns': {},
                'session_length': [],
                'break_compliance': [],
                'productivity_patterns': {},
                'wellbeing_engagement': 0.0
            }
            self.save_memory()
            self.save_patterns()

            messagebox.showinfo("Memory Cleared", "My memory has been cleared. We're starting fresh!")
            self.display_learning()

    def save_settings(self):
        """Save AI settings"""
        self.preferences['communication_style'] = self.comm_style_var.get()
        self.preferences['proactive_suggestions'] = self.proactive_var.get()
        self.preferences['learning_enabled'] = self.learning_var.get()
        self.save_preferences()

        import tkinter.messagebox as messagebox
        messagebox.showinfo("Settings Saved", "Chronos settings saved successfully!")

    def run(self):
        """Run the AI agent"""
        self.root.mainloop()


def main():
    """Main entry point"""
    ai = ChronosAI()
    ai.run()


if __name__ == '__main__':
    main()
