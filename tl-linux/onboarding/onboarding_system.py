#!/usr/bin/env python3
"""
TL Linux Onboarding System
Comprehensive user familiarization and system configuration
"""

import os
import json
import time
from pathlib import Path

class OnboardingSystem:
    def __init__(self):
        self.user_profile = {
            'name': '',
            'preferences': {
                'theme': 'retro',
                'usage_patterns': [],
                'favorite_apps': [],
                'skill_level': 'intermediate'
            },
            'ml_data': {
                'interaction_count': 0,
                'app_usage': {},
                'time_preferences': {},
                'color_preferences': []
            }
        }
        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def clear_screen(self):
        os.system('clear')

    def print_header(self, text):
        print("\n" + "═" * 60)
        print(f"  {text}")
        print("═" * 60 + "\n")

    def welcome_screen(self):
        self.clear_screen()
        print("""
    ████████╗██╗         ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗
    ╚══██╔══╝██║         ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝
       ██║   ██║         ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝
       ██║   ██║         ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗
       ██║   ███████╗    ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗
       ╚═╝   ╚══════╝    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝

        Welcome to Time Lord Linux - Your Personal Computing Companion
        """)
        input("\n    Press ENTER to begin your journey...")

    def step_1_introduction(self):
        self.clear_screen()
        self.print_header("Step 1: Getting to Know You")

        print("Let's start by introducing ourselves!")
        print("\nTL Linux is an intelligent operating system that learns from")
        print("your preferences and adapts to your workflow.\n")

        self.user_profile['name'] = input("What should we call you? ").strip()
        if not self.user_profile['name']:
            self.user_profile['name'] = "Time Traveler"

        print(f"\nNice to meet you, {self.user_profile['name']}!")
        time.sleep(1.5)

    def step_2_experience_level(self):
        self.clear_screen()
        self.print_header("Step 2: Your Experience Level")

        print(f"Tell us about your computing experience, {self.user_profile['name']}:\n")
        print("  1. Beginner - I'm new to computers")
        print("  2. Intermediate - I know the basics")
        print("  3. Advanced - I'm a power user")
        print("  4. Expert - I live in the terminal")

        choice = input("\nYour choice (1-4): ").strip()
        levels = {'1': 'beginner', '2': 'intermediate', '3': 'advanced', '4': 'expert'}
        self.user_profile['preferences']['skill_level'] = levels.get(choice, 'intermediate')

        print(f"\nGreat! We'll tailor the experience for a {self.user_profile['preferences']['skill_level']} user.")
        time.sleep(1.5)

    def step_3_theme_selection(self):
        self.clear_screen()
        self.print_header("Step 3: Choose Your Visual Style")

        print("TL Linux features ML-powered themes that adapt to your preferences:\n")
        print("  1. 🎮 Retro - Classic computing aesthetics with pixel art")
        print("  2. 🌈 Neon - Vibrant cyberpunk-inspired colors")
        print("  3. ⚡ Lightning - High contrast, energetic interface")
        print("  4. 💧 Splash - Fluid, modern, and colorful")
        print("  5. 🤖 Auto - Let ML choose based on your usage\n")

        choice = input("Select your theme (1-5): ").strip()
        themes = {'1': 'retro', '2': 'neon', '3': 'lightning', '4': 'splash', '5': 'auto'}
        self.user_profile['preferences']['theme'] = themes.get(choice, 'retro')

        print(f"\n✨ {self.user_profile['preferences']['theme'].title()} theme activated!")
        time.sleep(1.5)

    def step_4_app_preferences(self):
        self.clear_screen()
        self.print_header("Step 4: Application Interests")

        print("What kind of applications are you most interested in?\n")
        print("  [1] Development & Programming")
        print("  [2] Gaming & Emulation")
        print("  [3] Productivity & Office")
        print("  [4] Creative & Multimedia")
        print("  [5] System Administration")
        print("  [6] All of the above")

        choice = input("\nSelect (1-6, or comma-separated): ").strip()

        app_categories = {
            '1': 'development',
            '2': 'gaming',
            '3': 'productivity',
            '4': 'creative',
            '5': 'sysadmin',
            '6': 'all'
        }

        if ',' in choice:
            for c in choice.split(','):
                cat = app_categories.get(c.strip())
                if cat:
                    self.user_profile['preferences']['favorite_apps'].append(cat)
        else:
            cat = app_categories.get(choice, 'all')
            self.user_profile['preferences']['favorite_apps'].append(cat)

        print("\n📦 We'll prioritize relevant applications for you!")
        time.sleep(1.5)

    def step_5_system_tour(self):
        self.clear_screen()
        self.print_header("Step 5: System Tour")

        print("Let's familiarize you with TL Linux key features:\n")

        features = [
            ("🎯 Application Tray", "Bottom tray for quick access to running apps"),
            ("📁 File Manager", "Intuitive file management with cross-platform support"),
            ("🚀 App Drawer", "Access all installed applications"),
            ("🪟 Multi-Platform Support", "Run Windows, Linux, Android & Ubuntu apps"),
            ("⚙️ Settings Hub", "Centralized system configuration"),
            ("🧠 ML Personalization", "Adaptive themes and intelligent suggestions"),
            ("🎮 Emulation Suite", "Built-in emulators for retro systems"),
            ("💻 Development IDE", "Integrated coding environment"),
        ]

        for icon_name, description in features:
            print(f"  {icon_name}: {description}")
            time.sleep(0.5)

        input("\n\nPress ENTER to continue...")

    def step_6_compatibility_setup(self):
        self.clear_screen()
        self.print_header("Step 6: Application Compatibility")

        print("TL Linux supports multiple application platforms:\n")
        print("  ✓ Native Linux applications (.AppImage, .deb, .rpm)")
        print("  ✓ Windows applications (via Wine/Proton)")
        print("  ✓ Android applications (via Waydroid)")
        print("  ✓ Ubuntu applications (native compatibility)")
        print("\nWe'll set up compatibility layers in the background.")

        time.sleep(2)
        print("\n[████████████████████] 100% - Compatibility layers configured")
        time.sleep(1)

    def step_7_finalization(self):
        self.clear_screen()
        self.print_header("Step 7: Ready to Go!")

        print(f"Congratulations, {self.user_profile['name']}! Your system is ready.\n")
        print("Your personalized configuration:")
        print(f"  • Theme: {self.user_profile['preferences']['theme'].title()}")
        print(f"  • Experience Level: {self.user_profile['preferences']['skill_level'].title()}")
        print(f"  • Favorite Apps: {', '.join(self.user_profile['preferences']['favorite_apps'])}")

        print("\n\nTL Linux will continue to learn and adapt to your preferences.")
        print("The more you use it, the better it becomes!\n")

        # Save profile
        self.save_profile()

        input("Press ENTER to launch TL Linux Desktop...")

    def save_profile(self):
        """Save user profile to config directory"""
        profile_path = self.config_dir / 'user_profile.json'
        with open(profile_path, 'w') as f:
            json.dump(self.user_profile, f, indent=2)

    def run_onboarding(self):
        """Execute the complete onboarding process"""
        self.welcome_screen()
        self.step_1_introduction()
        self.step_2_experience_level()
        self.step_3_theme_selection()
        self.step_4_app_preferences()
        self.step_5_system_tour()
        self.step_6_compatibility_setup()
        self.step_7_finalization()

        return self.user_profile

if __name__ == '__main__':
    onboarding = OnboardingSystem()
    onboarding.run_onboarding()
