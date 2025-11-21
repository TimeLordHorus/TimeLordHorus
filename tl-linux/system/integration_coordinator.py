#!/usr/bin/env python3
"""
TL Linux Integration Coordinator
Coordinates between different TL Linux subsystems

This module acts as a central coordinator that:
- Connects wellbeing monitor with gamification
- Syncs achievement progress across systems
- Coordinates voice assistant with system actions
- Manages cross-component communication
"""

import json
from pathlib import Path
from datetime import datetime

class IntegrationCoordinator:
    """Central coordinator for TL Linux subsystems"""

    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'tl-linux'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Subsystem config paths
        self.wellbeing_dir = self.config_dir / 'wellbeing'
        self.gamification_dir = self.config_dir / 'wellbeing'
        self.journal_dir = self.config_dir / 'mindfulness'

    def sync_wellbeing_to_gamification(self):
        """Sync wellbeing stats to gamification system"""
        try:
            # Load wellbeing stats
            wellbeing_stats_file = self.wellbeing_dir / 'wellbeing_stats.json'
            if not wellbeing_stats_file.exists():
                return

            with open(wellbeing_stats_file, 'r') as f:
                wellbeing_stats = json.load(f)

            # Load gamification progress
            gamification_file = self.gamification_dir / 'gamification_progress.json'
            if not gamification_file.exists():
                gamification_progress = self._create_default_gamification_progress()
            else:
                with open(gamification_file, 'r') as f:
                    gamification_progress = json.load(f)

            # Sync counters
            gamification_progress['counters']['total_breaks'] = wellbeing_stats.get('breaks_taken', 0)
            gamification_progress['counters']['total_water'] = wellbeing_stats.get('water_consumed', 0)
            gamification_progress['counters']['total_posture_checks'] = wellbeing_stats.get('posture_alerts', 0)

            # Check and award achievements
            self._check_and_award_achievements(wellbeing_stats, gamification_progress)

            # Save updated progress
            with open(gamification_file, 'w') as f:
                json.dump(gamification_progress, f, indent=2)

            return True

        except Exception as e:
            print(f"Error syncing wellbeing to gamification: {e}")
            return False

    def _create_default_gamification_progress(self):
        """Create default gamification progress"""
        return {
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

    def _check_and_award_achievements(self, wellbeing_stats, gamification_progress):
        """Check wellbeing stats and award appropriate achievements"""
        unlocked = gamification_progress['unlocked_achievements']

        # First break achievement
        if wellbeing_stats.get('breaks_taken', 0) >= 1 and 'first_break' not in unlocked:
            self._award_achievement(gamification_progress, 'first_break', 10)

        # Break milestones
        if wellbeing_stats.get('breaks_taken', 0) >= 100 and 'break_100' not in unlocked:
            self._award_achievement(gamification_progress, 'break_100', 200)

        # First water achievement
        if wellbeing_stats.get('water_consumed', 0) >= 1 and 'first_water' not in unlocked:
            self._award_achievement(gamification_progress, 'first_water', 10)

        # Posture awareness
        if wellbeing_stats.get('posture_alerts', 0) >= 1 and 'posture_aware' not in unlocked:
            self._award_achievement(gamification_progress, 'posture_aware', 10)

    def _award_achievement(self, progress, achievement_id, points):
        """Award an achievement"""
        if achievement_id not in progress['unlocked_achievements']:
            progress['unlocked_achievements'].append(achievement_id)
            progress['total_points'] += points

            # Check for level up
            self._check_level_up(progress)

    def _check_level_up(self, progress):
        """Check and handle level ups"""
        import math
        current_level = progress['level']
        total_xp = progress['total_points']

        # Calculate XP for next level (XP = 100 * level^1.5)
        while total_xp >= self._calculate_xp_for_level(current_level + 1):
            current_level += 1
            progress['level'] = current_level

    def _calculate_xp_for_level(self, level):
        """Calculate total XP required for a level"""
        import math
        return int(100 * math.pow(level, 1.5))

    def get_achievement_summary(self):
        """Get a summary of current achievements"""
        try:
            gamification_file = self.gamification_dir / 'gamification_progress.json'
            if not gamification_file.exists():
                return None

            with open(gamification_file, 'r') as f:
                progress = json.load(f)

            return {
                'level': progress.get('level', 1),
                'total_xp': progress.get('total_points', 0),
                'achievements': len(progress.get('unlocked_achievements', [])),
                'breaks': progress.get('counters', {}).get('total_breaks', 0),
                'water': progress.get('counters', {}).get('total_water', 0)
            }

        except:
            return None

    def log_voice_command(self, command, success=True):
        """Log voice assistant command"""
        try:
            va_log_file = self.config_dir / 'voice-assistant' / 'command_log.json'
            va_log_file.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'success': success
            }

            if va_log_file.exists():
                with open(va_log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            # Keep only last 100 entries
            logs = logs[-100:]

            with open(va_log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"Error logging voice command: {e}")

    def get_system_health_status(self):
        """Get overall system health status"""
        status = {
            'wellbeing': self._check_wellbeing_status(),
            'achievements': self._check_achievements_status(),
            'security': self._check_security_status(),
            'sync': self._check_sync_status()
        }
        return status

    def _check_wellbeing_status(self):
        """Check wellbeing system status"""
        stats_file = self.wellbeing_dir / 'wellbeing_stats.json'
        if stats_file.exists():
            return {'status': 'active', 'color': 'green'}
        return {'status': 'inactive', 'color': 'gray'}

    def _check_achievements_status(self):
        """Check achievements status"""
        summary = self.get_achievement_summary()
        if summary:
            return {'status': f"Level {summary['level']}", 'color': 'blue'}
        return {'status': 'not started', 'color': 'gray'}

    def _check_security_status(self):
        """Check security status"""
        sec_config = self.config_dir / 'security' / 'security_config.json'
        if sec_config.exists():
            try:
                with open(sec_config, 'r') as f:
                    config = json.load(f)
                if config.get('firewall_enabled'):
                    return {'status': 'protected', 'color': 'green'}
            except:
                pass
        return {'status': 'check settings', 'color': 'yellow'}

    def _check_sync_status(self):
        """Check cloud sync status"""
        sync_config = self.config_dir / 'cloud-sync' / 'sync_config.json'
        if sync_config.exists():
            try:
                with open(sync_config, 'r') as f:
                    config = json.load(f)
                if config.get('enabled'):
                    provider = config.get('provider', 'unknown')
                    return {'status': f"{provider} active", 'color': 'blue'}
            except:
                pass
        return {'status': 'offline (OK)', 'color': 'gray'}

    def trigger_full_sync(self):
        """Trigger a full sync across all systems"""
        results = []

        # 1. Sync wellbeing to gamification
        results.append(('Wellbeing → Gamification', self.sync_wellbeing_to_gamification()))

        # 2. Could add more sync operations here
        # - Journal entries to mood tracking
        # - Voice commands to usage stats
        # etc.

        return results


# Convenience functions for external use
def sync_wellbeing_achievements():
    """Quick sync function for wellbeing to achievements"""
    coordinator = IntegrationCoordinator()
    return coordinator.sync_wellbeing_to_gamification()

def get_achievement_summary():
    """Quick function to get achievement summary"""
    coordinator = IntegrationCoordinator()
    return coordinator.get_achievement_summary()

def get_system_status():
    """Quick function to get system status"""
    coordinator = IntegrationCoordinator()
    return coordinator.get_system_health_status()


def main():
    """Main function for testing"""
    coordinator = IntegrationCoordinator()

    print("=== TL Linux Integration Coordinator ===")
    print()

    # Sync wellbeing to gamification
    print("Syncing wellbeing to gamification...")
    result = coordinator.sync_wellbeing_to_gamification()
    print(f"  Result: {'Success' if result else 'Failed'}")
    print()

    # Get achievement summary
    print("Achievement Summary:")
    summary = coordinator.get_achievement_summary()
    if summary:
        print(f"  Level: {summary['level']}")
        print(f"  Total XP: {summary['total_xp']}")
        print(f"  Achievements: {summary['achievements']}")
        print(f"  Breaks taken: {summary['breaks']}")
        print(f"  Water logged: {summary['water']}")
    else:
        print("  No data yet")
    print()

    # System health
    print("System Health Status:")
    status = coordinator.get_system_health_status()
    for component, info in status.items():
        print(f"  {component.capitalize()}: {info['status']}")
    print()


if __name__ == '__main__':
    main()
