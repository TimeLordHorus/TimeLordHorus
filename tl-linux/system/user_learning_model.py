#!/usr/bin/env python3
"""
TL Linux - Personalized User Learning Model
AI system that learns user patterns, preferences, and behaviors
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import hashlib

class UserLearningModel:
    """
    Intelligent learning system that builds a personalized profile
    of each user to enhance system interactions
    """

    def __init__(self, user_id=None):
        self.user_id = user_id or self.get_system_user()
        self.profile_dir = Path.home() / '.config' / 'tl-linux' / 'user_profiles'
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        self.profile_file = self.profile_dir / f'{self.user_id}_profile.json'

        # User profile data
        self.profile = self.load_profile()

    def get_system_user(self):
        """Get current system user ID"""
        import os
        import pwd
        return pwd.getpwuid(os.getuid()).pw_name

    def load_profile(self):
        """Load user profile"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Default profile structure
        return {
            'user_id': self.user_id,
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),

            # Voice and speech patterns
            'voice_patterns': {
                'common_phrases': {},  # phrase -> frequency
                'pronunciation_variants': {},  # standard -> user's variants
                'speaking_pace': 'medium',  # slow, medium, fast
                'accent_indicators': [],
                'background_noise_level': 'medium',
                'preferred_voice_commands': []
            },

            # Application usage
            'app_usage': {
                'frequently_used': {},  # app_name -> usage_count
                'usage_by_time': {},  # hour -> {app_name -> count}
                'app_sequences': [],  # common app opening sequences
                'launch_methods': {}  # app_name -> preferred_method
            },

            # Work patterns
            'work_patterns': {
                'active_hours': [],  # hours when user is most active
                'break_patterns': [],  # typical break times
                'task_categories': {},  # productivity, creative, entertainment
                'multitasking_tendency': 0.5,  # 0-1 scale
                'session_duration_avg': 120  # minutes
            },

            # Theme and UI preferences
            'ui_preferences': {
                'preferred_themes': {},  # theme_name -> selection_count
                'theme_by_time': {},  # hour -> preferred_theme
                'brightness_preference': 0.8,
                'font_size_preference': 12,
                'animation_preference': True,
                'layout_customizations': {}
            },

            # Accessibility needs
            'accessibility': {
                'uses_screen_reader': False,
                'uses_voice_control': False,
                'uses_dictation': False,
                'keyboard_shortcuts_used': {},
                'assistance_level': 'standard',  # minimal, standard, maximum
                'cognitive_assistance': False
            },

            # Learning preferences
            'learning': {
                'shows_tips': True,
                'tip_interactions': {},  # tip_id -> dismissed/helpful
                'onboarding_completed': False,
                'help_topics_accessed': {},
                'error_recovery_patterns': {}
            },

            # Personalization
            'personality': {
                'formality_level': 'professional',  # casual, professional, formal
                'verbosity': 'normal',  # brief, normal, verbose
                'tone': 'friendly',  # friendly, neutral, technical
                'humor': True
            },

            # Privacy settings
            'privacy': {
                'data_collection_consent': True,
                'anonymize_data': False,
                'share_usage_stats': False
            },

            # Performance data
            'performance': {
                'command_recognition_accuracy': {},  # command -> success_rate
                'error_frequency': {},  # error_type -> count
                'response_satisfaction': {},  # interaction -> rating
                'feature_adoption': {}  # feature -> usage_count
            }
        }

    def save_profile(self):
        """Save user profile"""
        self.profile['last_updated'] = datetime.now().isoformat()

        try:
            with open(self.profile_file, 'w') as f:
                json.dump(self.profile, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    # Voice Pattern Learning
    def record_voice_command(self, command, recognized_as, confidence, success):
        """Record voice command for learning"""
        # Normalize command
        command_lower = command.lower().strip()

        # Update common phrases
        phrases = self.profile['voice_patterns']['common_phrases']
        phrases[command_lower] = phrases.get(command_lower, 0) + 1

        # Track pronunciation variants
        if command_lower != recognized_as.lower():
            variants = self.profile['voice_patterns']['pronunciation_variants']
            if command_lower not in variants:
                variants[command_lower] = []
            if recognized_as not in variants[command_lower]:
                variants[command_lower].append(recognized_as)

        # Update command recognition accuracy
        accuracy = self.profile['performance']['command_recognition_accuracy']
        if command_lower not in accuracy:
            accuracy[command_lower] = {'attempts': 0, 'successes': 0}

        accuracy[command_lower]['attempts'] += 1
        if success:
            accuracy[command_lower]['successes'] += 1

        # Update preferred commands (successful ones)
        if success:
            preferred = self.profile['voice_patterns']['preferred_voice_commands']
            if command_lower not in preferred:
                preferred.append(command_lower)

        self.save_profile()

    def get_voice_suggestions(self, partial_command):
        """Get command suggestions based on user's history"""
        partial_lower = partial_command.lower()

        # Get common phrases that match
        suggestions = []
        for phrase, freq in sorted(
            self.profile['voice_patterns']['common_phrases'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if phrase.startswith(partial_lower):
                suggestions.append({
                    'command': phrase,
                    'frequency': freq,
                    'confidence': self.get_command_confidence(phrase)
                })

        return suggestions[:5]  # Top 5

    def get_command_confidence(self, command):
        """Get confidence level for a command"""
        accuracy = self.profile['performance']['command_recognition_accuracy']

        if command in accuracy:
            data = accuracy[command]
            if data['attempts'] > 0:
                return data['successes'] / data['attempts']

        return 0.5  # Default confidence

    def adapt_voice_recognition(self):
        """Generate adapted recognition parameters"""
        return {
            'speaking_pace': self.profile['voice_patterns']['speaking_pace'],
            'noise_tolerance': self.profile['voice_patterns']['background_noise_level'],
            'pronunciation_variants': self.profile['voice_patterns']['pronunciation_variants'],
            'priority_commands': self.profile['voice_patterns']['preferred_voice_commands'][:10]
        }

    # Application Usage Learning
    def record_app_launch(self, app_name, method='click'):
        """Record application launch"""
        hour = datetime.now().hour

        # Update frequency
        usage = self.profile['app_usage']['frequently_used']
        usage[app_name] = usage.get(app_name, 0) + 1

        # Update time-based usage
        by_time = self.profile['app_usage']['usage_by_time']
        if str(hour) not in by_time:
            by_time[str(hour)] = {}
        by_time[str(hour)][app_name] = by_time[str(hour)].get(app_name, 0) + 1

        # Track launch method
        methods = self.profile['app_usage']['launch_methods']
        if app_name not in methods:
            methods[app_name] = {}
        methods[app_name][method] = methods[app_name].get(method, 0) + 1

        self.save_profile()

    def get_app_suggestions(self, context='general'):
        """Get app suggestions based on usage patterns"""
        hour = datetime.now().hour

        # Time-based suggestions
        by_time = self.profile['app_usage']['usage_by_time']
        time_suggestions = []

        if str(hour) in by_time:
            time_apps = sorted(
                by_time[str(hour)].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            time_suggestions = [app for app, _ in time_apps]

        # Overall frequency suggestions
        freq_apps = sorted(
            self.profile['app_usage']['frequently_used'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'time_based': time_suggestions,
            'frequently_used': [app for app, _ in freq_apps],
            'recommended': self.get_smart_recommendations()
        }

    def get_smart_recommendations(self):
        """Get AI-powered app recommendations"""
        # Analyze usage patterns and suggest complementary apps
        recommendations = []

        # Example: If user uses GIMP, suggest Inkscape
        usage = self.profile['app_usage']['frequently_used']

        if 'gimp' in usage and usage['gimp'] > 5:
            recommendations.append({
                'app': 'inkscape',
                'reason': 'Complements GIMP for vector graphics'
            })

        if 'vscode' in usage and usage['vscode'] > 10:
            recommendations.append({
                'app': 'git',
                'reason': 'Essential for version control in development'
            })

        return recommendations

    # Work Pattern Learning
    def record_activity(self, activity_type, duration_minutes):
        """Record user activity"""
        hour = datetime.now().hour

        # Update active hours
        active_hours = self.profile['work_patterns']['active_hours']
        if hour not in active_hours:
            active_hours.append(hour)

        # Update task categories
        categories = self.profile['work_patterns']['task_categories']
        categories[activity_type] = categories.get(activity_type, 0) + duration_minutes

        # Update average session duration
        avg = self.profile['work_patterns']['session_duration_avg']
        # Moving average
        self.profile['work_patterns']['session_duration_avg'] = (avg * 0.9 + duration_minutes * 0.1)

        self.save_profile()

    def predict_activity_intent(self):
        """Predict what user is likely to do next"""
        hour = datetime.now().hour

        # Check active hours
        active_hours = self.profile['work_patterns']['active_hours']
        is_active_time = hour in active_hours

        # Get time-based app preferences
        by_time = self.profile['app_usage']['usage_by_time']
        likely_apps = []

        if str(hour) in by_time:
            likely_apps = sorted(
                by_time[str(hour)].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

        return {
            'is_active_time': is_active_time,
            'likely_apps': [app for app, _ in likely_apps],
            'suggested_theme': self.get_suggested_theme(),
            'energy_level': self.estimate_energy_level()
        }

    def estimate_energy_level(self):
        """Estimate user's energy level based on patterns"""
        hour = datetime.now().hour

        # Morning: 6-12 = high
        # Afternoon: 12-18 = medium
        # Evening: 18-22 = low
        # Night: 22-6 = very low

        if 6 <= hour < 12:
            return 'high'
        elif 12 <= hour < 18:
            return 'medium'
        elif 18 <= hour < 22:
            return 'low'
        else:
            return 'very_low'

    # Theme and UI Learning
    def record_theme_selection(self, theme_name):
        """Record theme selection"""
        hour = datetime.now().hour

        # Update overall preferences
        themes = self.profile['ui_preferences']['preferred_themes']
        themes[theme_name] = themes.get(theme_name, 0) + 1

        # Update time-based preferences
        by_time = self.profile['ui_preferences']['theme_by_time']
        by_time[str(hour)] = theme_name

        self.save_profile()

    def get_suggested_theme(self):
        """Get suggested theme based on time and preferences"""
        hour = datetime.now().hour

        # Check time-based preference
        by_time = self.profile['ui_preferences']['theme_by_time']

        if str(hour) in by_time:
            return by_time[str(hour)]

        # Fall back to most used
        themes = self.profile['ui_preferences']['preferred_themes']
        if themes:
            return max(themes, key=themes.get)

        # Default based on time
        if 6 <= hour < 18:
            return 'splash'  # Light theme for day
        else:
            return 'neon'  # Dark theme for evening

    # Accessibility Learning
    def record_accessibility_usage(self, feature, duration_minutes):
        """Record accessibility feature usage"""
        accessibility = self.profile['accessibility']

        if feature == 'screen_reader':
            accessibility['uses_screen_reader'] = True
        elif feature == 'voice_control':
            accessibility['uses_voice_control'] = True
        elif feature == 'dictation':
            accessibility['uses_dictation'] = True

        # Adjust assistance level based on usage
        total_accessibility_time = duration_minutes

        if total_accessibility_time > 60:  # More than 1 hour
            accessibility['assistance_level'] = 'maximum'
        elif total_accessibility_time > 20:
            accessibility['assistance_level'] = 'standard'

        self.save_profile()

    def get_accessibility_recommendations(self):
        """Get personalized accessibility recommendations"""
        accessibility = self.profile['accessibility']
        recommendations = []

        # If user struggles with typing, suggest voice control
        if self.get_typing_error_rate() > 0.3:
            if not accessibility['uses_voice_control']:
                recommendations.append({
                    'feature': 'voice_control',
                    'reason': 'Voice control may help reduce typing errors'
                })

        # If user uses voice control heavily, suggest dictation
        if accessibility['uses_voice_control']:
            if not accessibility['uses_dictation']:
                recommendations.append({
                    'feature': 'dictation',
                    'reason': 'AI dictation can help with longer text input'
                })

        return recommendations

    def get_typing_error_rate(self):
        """Estimate typing error rate"""
        # Placeholder - would need actual typing data
        return 0.15  # 15% error rate

    # Learning and Help
    def record_help_interaction(self, topic, helpful=True):
        """Record help topic interaction"""
        topics = self.profile['learning']['help_topics_accessed']
        if topic not in topics:
            topics[topic] = {'views': 0, 'helpful': 0}

        topics[topic]['views'] += 1
        if helpful:
            topics[topic]['helpful'] += 1

        self.save_profile()

    def get_personalized_tips(self):
        """Get personalized tips based on user's usage"""
        tips = []

        # Analyze usage to suggest tips
        usage = self.profile['app_usage']['frequently_used']
        accessibility = self.profile['accessibility']

        # Tip: Keyboard shortcuts
        if not self.profile['accessibility']['keyboard_shortcuts_used']:
            tips.append({
                'id': 'keyboard_shortcuts',
                'title': 'Speed up your workflow',
                'message': 'Learn keyboard shortcuts for frequently used features',
                'priority': 'high'
            })

        # Tip: Voice control
        if not accessibility['uses_voice_control'] and self.estimate_energy_level() == 'low':
            tips.append({
                'id': 'voice_control',
                'title': 'Try hands-free control',
                'message': 'Voice control can reduce fatigue during long sessions',
                'priority': 'medium'
            })

        # Tip: Theme optimization
        suggested_theme = self.get_suggested_theme()
        current_themes = self.profile['ui_preferences']['preferred_themes']

        if suggested_theme not in current_themes or current_themes.get(suggested_theme, 0) < 5:
            tips.append({
                'id': f'theme_{suggested_theme}',
                'title': 'Try a new theme',
                'message': f'The {suggested_theme} theme might work well for this time of day',
                'priority': 'low'
            })

        return tips

    # Performance and Feedback
    def record_feedback(self, interaction_id, rating, comment=''):
        """Record user feedback"""
        satisfaction = self.profile['performance']['response_satisfaction']

        if interaction_id not in satisfaction:
            satisfaction[interaction_id] = []

        satisfaction[interaction_id].append({
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        })

        self.save_profile()

    def get_user_satisfaction_score(self):
        """Calculate overall user satisfaction"""
        satisfaction = self.profile['performance']['response_satisfaction']

        if not satisfaction:
            return 0.5  # Neutral

        all_ratings = []
        for interactions in satisfaction.values():
            all_ratings.extend([i['rating'] for i in interactions])

        if all_ratings:
            return sum(all_ratings) / len(all_ratings) / 5.0  # Normalize to 0-1

        return 0.5

    # Privacy and Data
    def export_profile(self, anonymize=False):
        """Export user profile (for backup or analysis)"""
        profile_copy = self.profile.copy()

        if anonymize:
            profile_copy['user_id'] = hashlib.sha256(self.user_id.encode()).hexdigest()[:16]

        return json.dumps(profile_copy, indent=2)

    def clear_learning_data(self, category=None):
        """Clear learning data (for privacy)"""
        if category:
            if category in self.profile:
                # Reset specific category to defaults
                default_profile = self.load_profile()
                self.profile[category] = default_profile[category]
        else:
            # Clear all learning data
            self.profile = self.load_profile()

        self.save_profile()

    # Integration Helpers
    def get_adaptive_settings(self):
        """Get all adaptive settings for system integration"""
        return {
            'voice_recognition': self.adapt_voice_recognition(),
            'theme': self.get_suggested_theme(),
            'app_suggestions': self.get_app_suggestions(),
            'intent_prediction': self.predict_activity_intent(),
            'accessibility_recs': self.get_accessibility_recommendations(),
            'tips': self.get_personalized_tips(),
            'satisfaction_score': self.get_user_satisfaction_score()
        }


# Global instance
_global_model = None

def get_user_model():
    """Get or create global user model"""
    global _global_model
    if _global_model is None:
        _global_model = UserLearningModel()
    return _global_model
