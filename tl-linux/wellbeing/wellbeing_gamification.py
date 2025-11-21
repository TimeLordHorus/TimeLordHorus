#!/usr/bin/env python3
"""
TL Wellbeing Gamification System
Make wellbeing fun and engaging through game mechanics

Features:
- Achievement system with badges
- Daily/weekly challenges
- Experience points and leveling
- Streaks and consistency tracking
- Leaderboards (optional, local only)
- Rewards and unlockables
- Progress visualization
"""

import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from datetime import datetime, timedelta
import math

class WellbeingGamification:
    """Gamification system for wellbeing features"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Wellbeing Achievements 🏆")
            self.root.geometry("800x900")
        else:
            self.root = root

        self.root.configure(bg='#0d1117')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'wellbeing'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.achievements_file = self.config_dir / 'achievements.json'
        self.progress_file = self.config_dir / 'gamification_progress.json'

        # Load data
        self.load_achievements()
        self.load_progress()

        # Setup UI
        self.setup_ui()

        # Update displays
        self.update_displays()

    def load_achievements(self):
        """Load achievement definitions"""
        self.achievements = {
            # Break-taking achievements
            'first_break': {
                'name': 'First Break',
                'description': 'Take your first break',
                'icon': '☕',
                'points': 10,
                'category': 'breaks'
            },
            'break_streak_3': {
                'name': 'Consistency Champion',
                'description': 'Take breaks for 3 days in a row',
                'icon': '🔥',
                'points': 50,
                'category': 'breaks'
            },
            'break_streak_7': {
                'name': 'Week Warrior',
                'description': 'Take breaks for 7 days in a row',
                'icon': '⚡',
                'points': 100,
                'category': 'breaks'
            },
            'break_streak_30': {
                'name': 'Monthly Master',
                'description': 'Take breaks for 30 days in a row',
                'icon': '👑',
                'points': 500,
                'category': 'breaks'
            },
            'break_100': {
                'name': 'Century Club',
                'description': 'Take 100 breaks total',
                'icon': '💯',
                'points': 200,
                'category': 'breaks'
            },

            # Hydration achievements
            'first_water': {
                'name': 'Hydration Station',
                'description': 'Log your first water intake',
                'icon': '💧',
                'points': 10,
                'category': 'hydration'
            },
            'water_day_8': {
                'name': 'Well Hydrated',
                'description': 'Drink 8 glasses in one day',
                'icon': '🌊',
                'points': 50,
                'category': 'hydration'
            },
            'water_streak_7': {
                'name': 'Aqua Athlete',
                'description': 'Stay hydrated for 7 days',
                'icon': '🏊',
                'points': 100,
                'category': 'hydration'
            },

            # Eye care achievements
            'eye_care_first': {
                'name': 'Eye Opener',
                'description': 'Complete first eye care exercise',
                'icon': '👁️',
                'points': 10,
                'category': 'eye_care'
            },
            'eye_care_50': {
                'name': 'Vision Protector',
                'description': 'Complete 50 eye care exercises',
                'icon': '👓',
                'points': 150,
                'category': 'eye_care'
            },

            # Posture achievements
            'posture_aware': {
                'name': 'Posture Aware',
                'description': 'Respond to first posture alert',
                'icon': '🪑',
                'points': 10,
                'category': 'posture'
            },
            'posture_perfect': {
                'name': 'Perfect Posture',
                'description': 'Maintain good posture for 7 days',
                'icon': '🧘',
                'points': 100,
                'category': 'posture'
            },

            # Screen time achievements
            'mindful_user': {
                'name': 'Mindful User',
                'description': 'Keep screen time under 6 hours',
                'icon': '⏰',
                'points': 50,
                'category': 'screen_time'
            },
            'balanced_day': {
                'name': 'Balanced Day',
                'description': 'Perfect balance of work and breaks',
                'icon': '⚖️',
                'points': 75,
                'category': 'balance'
            },

            # Special achievements
            'early_bird': {
                'name': 'Early Bird',
                'description': 'Start work session before 8 AM',
                'icon': '🌅',
                'points': 25,
                'category': 'special'
            },
            'night_owl': {
                'name': 'Night Owl',
                'description': 'Work session after 8 PM',
                'icon': '🦉',
                'points': 25,
                'category': 'special'
            },
            'weekend_warrior': {
                'name': 'Weekend Warrior',
                'description': 'Maintain wellbeing on weekends',
                'icon': '🏖️',
                'points': 50,
                'category': 'special'
            },
            'wellness_guru': {
                'name': 'Wellness Guru',
                'description': 'Unlock all basic achievements',
                'icon': '🌟',
                'points': 1000,
                'category': 'master'
            }
        }

    def load_progress(self):
        """Load user progress"""
        default_progress = {
            'total_points': 0,
            'level': 1,
            'unlocked_achievements': [],
            'current_streaks': {
                'breaks': 0,
                'hydration': 0,
                'eye_care': 0,
                'posture': 0
            },
            'counters': {
                'total_breaks': 0,
                'total_water': 0,
                'total_eye_exercises': 0,
                'total_posture_checks': 0,
                'days_active': 0
            },
            'daily_stats': {},
            'last_activity_date': None
        }

        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    self.progress = json.load(f)
                    # Merge with defaults
                    for key, value in default_progress.items():
                        if key not in self.progress:
                            self.progress[key] = value
            except:
                self.progress = default_progress
        else:
            self.progress = default_progress

    def save_progress(self):
        """Save user progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def setup_ui(self):
        """Setup the UI"""
        # Header with level and XP
        header = tk.Frame(self.root, bg='#161b22', height=120)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Title
        tk.Label(
            header,
            text="🏆 Wellbeing Achievements",
            font=('Arial', 28, 'bold'),
            bg='#161b22',
            fg='#58a6ff'
        ).pack(pady=10)

        # Level and XP bar
        level_frame = tk.Frame(header, bg='#161b22')
        level_frame.pack(pady=5)

        self.level_label = tk.Label(
            level_frame,
            text=f"Level {self.progress['level']}",
            font=('Arial', 18, 'bold'),
            bg='#161b22',
            fg='#ffa657'
        )
        self.level_label.pack()

        # XP Progress bar
        xp_frame = tk.Frame(header, bg='#161b22')
        xp_frame.pack(pady=5)

        self.xp_bar = tk.Canvas(
            xp_frame,
            width=400,
            height=25,
            bg='#0d1117',
            highlightthickness=0
        )
        self.xp_bar.pack()

        self.xp_label = tk.Label(
            xp_frame,
            text="",
            font=('Arial', 10),
            bg='#161b22',
            fg='#8b949e'
        )
        self.xp_label.pack()

        # Tabs for different sections
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.configure('TNotebook', background='#0d1117')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))

        # Create tabs
        self.achievements_tab = tk.Frame(tab_container, bg='#0d1117')
        self.stats_tab = tk.Frame(tab_container, bg='#0d1117')
        self.challenges_tab = tk.Frame(tab_container, bg='#0d1117')

        tab_container.add(self.achievements_tab, text='🏅 Achievements')
        tab_container.add(self.stats_tab, text='📊 Statistics')
        tab_container.add(self.challenges_tab, text='🎯 Daily Challenges')

        # Setup each tab
        self.setup_achievements_tab()
        self.setup_stats_tab()
        self.setup_challenges_tab()

    def setup_achievements_tab(self):
        """Setup achievements display"""
        # Scrollable frame
        canvas = tk.Canvas(self.achievements_tab, bg='#0d1117', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.achievements_tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0d1117')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Group achievements by category
        categories = {}
        for ach_id, ach in self.achievements.items():
            cat = ach['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((ach_id, ach))

        # Display by category
        for cat_name, cat_achievements in categories.items():
            cat_frame = tk.LabelFrame(
                scrollable_frame,
                text=cat_name.replace('_', ' ').title(),
                font=('Arial', 14, 'bold'),
                bg='#0d1117',
                fg='#58a6ff',
                padx=15,
                pady=15
            )
            cat_frame.pack(fill=tk.X, padx=10, pady=10)

            for ach_id, ach in cat_achievements:
                self.create_achievement_card(cat_frame, ach_id, ach)

    def create_achievement_card(self, parent, ach_id, ach):
        """Create an achievement card"""
        unlocked = ach_id in self.progress['unlocked_achievements']

        card = tk.Frame(
            parent,
            bg='#21262d' if unlocked else'#161b22',
            relief=tk.RAISED if unlocked else tk.FLAT,
            borderwidth=2 if unlocked else 1
        )
        card.pack(fill=tk.X, pady=5)

        # Icon
        icon_label = tk.Label(
            card,
            text=ach['icon'] if unlocked else '🔒',
            font=('Arial', 32),
            bg='#21262d' if unlocked else '#161b22'
        )
        icon_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Info
        info_frame = tk.Frame(card, bg='#21262d' if unlocked else '#161b22')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        tk.Label(
            info_frame,
            text=ach['name'],
            font=('Arial', 14, 'bold'),
            bg='#21262d' if unlocked else '#161b22',
            fg='#7ee787' if unlocked else '#8b949e',
            anchor=tk.W
        ).pack(fill=tk.X)

        tk.Label(
            info_frame,
            text=ach['description'],
            font=('Arial', 10),
            bg='#21262d' if unlocked else '#161b22',
            fg='#c9d1d9' if unlocked else '#6e7681',
            anchor=tk.W
        ).pack(fill=tk.X)

        # Points
        points_label = tk.Label(
            card,
            text=f"+{ach['points']} XP",
            font=('Arial', 12, 'bold'),
            bg='#21262d' if unlocked else '#161b22',
            fg='#ffa657' if unlocked else '#6e7681'
        )
        points_label.pack(side=tk.RIGHT, padx=15)

    def setup_stats_tab(self):
        """Setup statistics display"""
        stats_container = tk.Frame(self.stats_tab, bg='#0d1117')
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Summary stats
        summary_frame = tk.LabelFrame(
            stats_container,
            text="Summary",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='#58a6ff',
            padx=20,
            pady=20
        )
        summary_frame.pack(fill=tk.X, pady=10)

        self.stats_text = tk.Text(
            summary_frame,
            font=('Courier', 11),
            bg='#161b22',
            fg='#c9d1d9',
            height=15,
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # Streaks
        streaks_frame = tk.LabelFrame(
            stats_container,
            text="Current Streaks 🔥",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='#58a6ff',
            padx=20,
            pady=20
        )
        streaks_frame.pack(fill=tk.X, pady=10)

        self.streaks_container = tk.Frame(streaks_frame, bg='#161b22')
        self.streaks_container.pack(fill=tk.X)

    def setup_challenges_tab(self):
        """Setup daily challenges"""
        challenges_container = tk.Frame(self.challenges_tab, bg='#0d1117')
        challenges_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            challenges_container,
            text="🎯 Daily Challenges",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # Generate daily challenges
        challenges = [
            {
                'name': 'Break Champion',
                'description': 'Take 5 breaks today',
                'reward': 50,
                'progress': min(self.get_today_breaks(), 5),
                'goal': 5
            },
            {
                'name': 'Hydration Hero',
                'description': 'Drink 8 glasses of water',
                'reward': 40,
                'progress': min(self.get_today_water(), 8),
                'goal': 8
            },
            {
                'name': 'Eye Care Expert',
                'description': 'Complete 3 eye exercises',
                'reward': 30,
                'progress': min(self.get_today_eye_care(), 3),
                'goal': 3
            }
        ]

        for challenge in challenges:
            self.create_challenge_card(challenges_container, challenge)

    def create_challenge_card(self, parent, challenge):
        """Create a challenge card"""
        card = tk.Frame(parent, bg='#161b22', relief=tk.RAISED, borderwidth=2)
        card.pack(fill=tk.X, pady=10)

        # Header
        header = tk.Frame(card, bg='#161b22')
        header.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            header,
            text=challenge['name'],
            font=('Arial', 14, 'bold'),
            bg='#161b22',
            fg='#7ee787',
            anchor=tk.W
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            header,
            text=f"+{challenge['reward']} XP",
            font=('Arial', 12, 'bold'),
            bg='#161b22',
            fg='#ffa657'
        ).pack(side=tk.RIGHT)

        # Description
        tk.Label(
            card,
            text=challenge['description'],
            font=('Arial', 10),
            bg='#161b22',
            fg='#8b949e',
            anchor=tk.W
        ).pack(fill=tk.X, padx=15, pady=(0, 10))

        # Progress bar
        progress_frame = tk.Frame(card, bg='#161b22')
        progress_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        progress_canvas = tk.Canvas(
            progress_frame,
            width=400,
            height=20,
            bg='#0d1117',
            highlightthickness=0
        )
        progress_canvas.pack(side=tk.LEFT)

        # Draw progress
        progress_pct = challenge['progress'] / challenge['goal']
        progress_width = 400 * progress_pct
        progress_canvas.create_rectangle(
            0, 0, progress_width, 20,
            fill='#238636',
            outline=''
        )

        tk.Label(
            progress_frame,
            text=f"{challenge['progress']}/{challenge['goal']}",
            font=('Arial', 10),
            bg='#161b22',
            fg='#c9d1d9'
        ).pack(side=tk.LEFT, padx=10)

    def update_displays(self):
        """Update all displays"""
        self.update_level_display()
        self.update_stats_display()
        self.update_streaks_display()

    def update_level_display(self):
        """Update level and XP bar"""
        level = self.progress['level']
        total_xp = self.progress['total_points']

        # Calculate XP for current level
        xp_for_level = self.calculate_xp_for_level(level)
        xp_for_next_level = self.calculate_xp_for_level(level + 1)
        current_level_xp = total_xp - xp_for_level
        xp_needed = xp_for_next_level - xp_for_level

        # Update label
        self.level_label.config(text=f"Level {level}")

        # Update XP bar
        self.xp_bar.delete('all')
        self.xp_bar.create_rectangle(
            0, 0, 400, 25,
            fill='#21262d',
            outline='#30363d'
        )

        if xp_needed > 0:
            progress_width = (current_level_xp / xp_needed) * 400
            self.xp_bar.create_rectangle(
                0, 0, progress_width, 25,
                fill='#58a6ff',
                outline=''
            )

        self.xp_label.config(
            text=f"{current_level_xp} / {xp_needed} XP to next level"
        )

    def calculate_xp_for_level(self, level):
        """Calculate total XP required for a level"""
        # XP required = 100 * level^1.5
        return int(100 * math.pow(level, 1.5))

    def update_stats_display(self):
        """Update statistics display"""
        stats_text = f"""
╔════════════════════════════════════════════════════════╗
║                   WELLBEING STATISTICS                 ║
╚════════════════════════════════════════════════════════╝

🏆 ACHIEVEMENTS
   Unlocked: {len(self.progress['unlocked_achievements'])} / {len(self.achievements)}
   Total XP: {self.progress['total_points']}
   Current Level: {self.progress['level']}

☕ BREAKS
   Total Breaks Taken: {self.progress['counters']['total_breaks']}
   Current Streak: {self.progress['current_streaks']['breaks']} days

💧 HYDRATION
   Total Water Logged: {self.progress['counters']['total_water']} glasses
   Current Streak: {self.progress['current_streaks']['hydration']} days

👁️  EYE CARE
   Total Exercises: {self.progress['counters']['total_eye_exercises']}
   Current Streak: {self.progress['current_streaks']['eye_care']} days

🪑 POSTURE
   Total Checks: {self.progress['counters']['total_posture_checks']}
   Current Streak: {self.progress['current_streaks']['posture']} days

📅 ACTIVITY
   Days Active: {self.progress['counters']['days_active']}
   Last Activity: {self.progress['last_activity_date'] or 'Never'}
        """

        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert('1.0', stats_text)
        self.stats_text.config(state=tk.DISABLED)

    def update_streaks_display(self):
        """Update streaks display"""
        for widget in self.streaks_container.winfo_children():
            widget.destroy()

        streaks = [
            ('☕ Breaks', self.progress['current_streaks']['breaks']),
            ('💧 Hydration', self.progress['current_streaks']['hydration']),
            ('👁️ Eye Care', self.progress['current_streaks']['eye_care']),
            ('🪑 Posture', self.progress['current_streaks']['posture'])
        ]

        for name, streak_days in streaks:
            streak_frame = tk.Frame(self.streaks_container, bg='#161b22')
            streak_frame.pack(side=tk.LEFT, padx=10, expand=True)

            tk.Label(
                streak_frame,
                text=name,
                font=('Arial', 11),
                bg='#161b22',
                fg='#8b949e'
            ).pack()

            tk.Label(
                streak_frame,
                text=f"🔥 {streak_days}",
                font=('Arial', 20, 'bold'),
                bg='#161b22',
                fg='#ffa657' if streak_days > 0 else '#6e7681'
            ).pack()

    def get_today_breaks(self):
        """Get today's break count"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.progress['daily_stats'].get(today, {}).get('breaks', 0)

    def get_today_water(self):
        """Get today's water count"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.progress['daily_stats'].get(today, {}).get('water', 0)

    def get_today_eye_care(self):
        """Get today's eye care count"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.progress['daily_stats'].get(today, {}).get('eye_care', 0)

    def award_achievement(self, achievement_id):
        """Award an achievement to the user"""
        if achievement_id in self.progress['unlocked_achievements']:
            return  # Already unlocked

        if achievement_id not in self.achievements:
            return  # Invalid achievement

        # Unlock achievement
        self.progress['unlocked_achievements'].append(achievement_id)

        # Award points
        points = self.achievements[achievement_id]['points']
        self.progress['total_points'] += points

        # Check for level up
        self.check_level_up()

        # Save progress
        self.save_progress()

        # Show notification
        self.show_achievement_notification(achievement_id)

        # Refresh displays
        self.update_displays()

    def check_level_up(self):
        """Check if user leveled up"""
        current_level = self.progress['level']
        total_xp = self.progress['total_points']

        while total_xp >= self.calculate_xp_for_level(current_level + 1):
            current_level += 1
            self.progress['level'] = current_level
            self.show_level_up_notification(current_level)

    def show_achievement_notification(self, achievement_id):
        """Show achievement unlock notification"""
        ach = self.achievements[achievement_id]

        notification = tk.Toplevel(self.root)
        notification.title("Achievement Unlocked!")
        notification.geometry("400x200")
        notification.configure(bg='#21262d')
        notification.attributes('-topmost', True)

        tk.Label(
            notification,
            text="🏆 Achievement Unlocked!",
            font=('Arial', 18, 'bold'),
            bg='#21262d',
            fg='#7ee787'
        ).pack(pady=20)

        tk.Label(
            notification,
            text=f"{ach['icon']} {ach['name']}",
            font=('Arial', 16),
            bg='#21262d',
            fg='#58a6ff'
        ).pack()

        tk.Label(
            notification,
            text=ach['description'],
            font=('Arial', 11),
            bg='#21262d',
            fg='#8b949e'
        ).pack(pady=10)

        tk.Label(
            notification,
            text=f"+{ach['points']} XP",
            font=('Arial', 14, 'bold'),
            bg='#21262d',
            fg='#ffa657'
        ).pack()

        tk.Button(
            notification,
            text="Awesome!",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=notification.destroy,
            padx=30,
            pady=10
        ).pack(pady=20)

        # Auto-close after 5 seconds
        notification.after(5000, notification.destroy)

    def show_level_up_notification(self, new_level):
        """Show level up notification"""
        notification = tk.Toplevel(self.root)
        notification.title("Level Up!")
        notification.geometry("400x200")
        notification.configure(bg='#21262d')
        notification.attributes('-topmost', True)

        tk.Label(
            notification,
            text="⬆️ LEVEL UP!",
            font=('Arial', 24, 'bold'),
            bg='#21262d',
            fg='#ffa657'
        ).pack(pady=30)

        tk.Label(
            notification,
            text=f"You are now Level {new_level}!",
            font=('Arial', 16),
            bg='#21262d',
            fg='#58a6ff'
        ).pack()

        tk.Button(
            notification,
            text="Continue",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=notification.destroy,
            padx=30,
            pady=10
        ).pack(pady=30)

        # Auto-close after 5 seconds
        notification.after(5000, notification.destroy)

    def run(self):
        """Run the gamification UI"""
        self.root.mainloop()


def main():
    """Main entry point"""
    game = WellbeingGamification()
    game.run()


if __name__ == '__main__':
    main()
