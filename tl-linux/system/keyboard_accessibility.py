#!/usr/bin/env python3
"""
TL Linux - Keyboard Accessibility Manager
Sticky Keys, Slow Keys, Bounce Keys, and other keyboard accessibility features
"""

import os
import json
import time
import threading
from pynput import keyboard
from pynput.keyboard import Key, Controller

class KeyboardAccessibilityManager:
    def __init__(self):
        self.config_dir = os.path.expanduser('~/.tl-linux/keyboard_accessibility')
        self.config_file = os.path.join(self.config_dir, 'config.json')

        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

        # Sticky Keys state
        self.sticky_keys_enabled = self.config.get('sticky_keys_enabled', False)
        self.sticky_modifiers = {}  # modifier -> state (pressed, locked)
        self.modifier_keys = [Key.ctrl_l, Key.ctrl_r, Key.shift_l, Key.shift_r,
                             Key.alt_l, Key.alt_r, Key.cmd]

        # Slow Keys state
        self.slow_keys_enabled = self.config.get('slow_keys_enabled', False)
        self.slow_keys_delay = self.config.get('slow_keys_delay', 0.5)  # seconds
        self.pending_key = None
        self.pending_key_time = None

        # Bounce Keys state
        self.bounce_keys_enabled = self.config.get('bounce_keys_enabled', False)
        self.bounce_keys_delay = self.config.get('bounce_keys_delay', 0.5)  # seconds
        self.last_key = None
        self.last_key_time = None

        # Repeat Keys settings
        self.repeat_keys_enabled = self.config.get('repeat_keys_enabled', True)
        self.repeat_delay = self.config.get('repeat_delay', 0.5)  # seconds
        self.repeat_rate = self.config.get('repeat_rate', 0.05)  # seconds between repeats

        # Toggle Keys (beep on Caps Lock, Num Lock, etc.)
        self.toggle_keys_enabled = self.config.get('toggle_keys_enabled', False)

        # Keyboard controller
        self.controller = Controller()

        # Listener
        self.listener = None
        self.running = False

    def load_config(self):
        """Load configuration"""
        default_config = {
            'sticky_keys_enabled': False,
            'sticky_keys_beep': True,
            'sticky_keys_lock_on_double': True,
            'slow_keys_enabled': False,
            'slow_keys_delay': 0.5,
            'slow_keys_beep': True,
            'bounce_keys_enabled': False,
            'bounce_keys_delay': 0.5,
            'repeat_keys_enabled': True,
            'repeat_delay': 0.5,
            'repeat_rate': 0.05,
            'toggle_keys_enabled': False
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except:
            pass

        return default_config

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def start(self):
        """Start keyboard accessibility features"""
        if self.running:
            return

        self.running = True

        # Start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()

        print("🎹 Keyboard Accessibility Manager started")
        if self.sticky_keys_enabled:
            print("  ✓ Sticky Keys enabled")
        if self.slow_keys_enabled:
            print(f"  ✓ Slow Keys enabled (delay: {self.slow_keys_delay}s)")
        if self.bounce_keys_enabled:
            print(f"  ✓ Bounce Keys enabled (delay: {self.bounce_keys_delay}s)")

    def stop(self):
        """Stop keyboard accessibility features"""
        if not self.running:
            return

        self.running = False

        if self.listener:
            self.listener.stop()

        print("🎹 Keyboard Accessibility Manager stopped")

    def on_key_press(self, key):
        """Handle key press"""
        try:
            # Sticky Keys
            if self.sticky_keys_enabled:
                if key in self.modifier_keys:
                    self.handle_sticky_key(key)
                    return False  # Suppress the event

            # Slow Keys
            if self.slow_keys_enabled:
                if not self.is_modifier(key):
                    self.handle_slow_key_press(key)
                    return False  # Suppress the event

            # Bounce Keys
            if self.bounce_keys_enabled:
                if self.should_bounce(key):
                    return False  # Suppress the event
                else:
                    self.last_key = key
                    self.last_key_time = time.time()

            # Toggle Keys beep
            if self.toggle_keys_enabled:
                if key in [Key.caps_lock, Key.num_lock, Key.scroll_lock]:
                    self.play_toggle_beep()

        except Exception as e:
            print(f"Error in on_key_press: {e}")

    def on_key_release(self, key):
        """Handle key release"""
        try:
            # Clear pending slow key if released before delay
            if self.slow_keys_enabled:
                if self.pending_key == key:
                    self.pending_key = None
                    self.pending_key_time = None
        except Exception as e:
            print(f"Error in on_key_release: {e}")

    # Sticky Keys implementation
    def handle_sticky_key(self, key):
        """Handle sticky modifier key press"""
        current_state = self.sticky_modifiers.get(key, 'off')

        if current_state == 'off':
            # First press - latch the modifier
            self.sticky_modifiers[key] = 'latched'
            if self.config.get('sticky_keys_beep'):
                self.play_sticky_beep('latch')
            print(f"  Sticky: {key} latched")

        elif current_state == 'latched':
            if self.config.get('sticky_keys_lock_on_double'):
                # Second press - lock the modifier
                self.sticky_modifiers[key] = 'locked'
                if self.config.get('sticky_keys_beep'):
                    self.play_sticky_beep('lock')
                print(f"  Sticky: {key} locked")
            else:
                # Release
                self.sticky_modifiers[key] = 'off'
                if self.config.get('sticky_keys_beep'):
                    self.play_sticky_beep('release')
                print(f"  Sticky: {key} released")

        elif current_state == 'locked':
            # Third press - unlock
            self.sticky_modifiers[key] = 'off'
            if self.config.get('sticky_keys_beep'):
                self.play_sticky_beep('release')
            print(f"  Sticky: {key} unlocked")

    def get_active_modifiers(self):
        """Get list of active sticky modifiers"""
        return [key for key, state in self.sticky_modifiers.items()
                if state in ['latched', 'locked']]

    def release_latched_modifiers(self):
        """Release latched (but not locked) modifiers after use"""
        for key, state in list(self.sticky_modifiers.items()):
            if state == 'latched':
                self.sticky_modifiers[key] = 'off'
                print(f"  Sticky: {key} auto-released")

    # Slow Keys implementation
    def handle_slow_key_press(self, key):
        """Handle slow key press (requires hold before accepting)"""
        self.pending_key = key
        self.pending_key_time = time.time()

        # Start timer to check if key is held long enough
        def check_slow_key():
            time.sleep(self.slow_keys_delay)
            if self.pending_key == key:
                # Key was held long enough, accept it
                if self.config.get('slow_keys_beep'):
                    self.play_slow_key_beep()
                self.emit_key(key)
                self.pending_key = None
                self.pending_key_time = None

        threading.Thread(target=check_slow_key, daemon=True).start()

    # Bounce Keys implementation
    def should_bounce(self, key):
        """Check if key press should be bounced (ignored as accidental repeat)"""
        if self.last_key == key:
            time_since_last = time.time() - self.last_key_time
            if time_since_last < self.bounce_keys_delay:
                print(f"  Bounce: Ignoring rapid repeat of {key}")
                return True
        return False

    # Helper methods
    def is_modifier(self, key):
        """Check if key is a modifier"""
        return key in self.modifier_keys

    def emit_key(self, key):
        """Emit a key press (with active sticky modifiers)"""
        # Apply sticky modifiers
        active_modifiers = self.get_active_modifiers()

        # Press modifiers
        for mod in active_modifiers:
            self.controller.press(mod)

        # Press the key
        self.controller.press(key)
        self.controller.release(key)

        # Release modifiers
        for mod in active_modifiers:
            self.controller.release(mod)

        # Release latched modifiers
        self.release_latched_modifiers()

    # Sound feedback
    def play_sticky_beep(self, action):
        """Play beep for sticky key action"""
        # Different tones for latch, lock, release
        tones = {
            'latch': 800,    # Hz
            'lock': 1200,
            'release': 600
        }
        self.play_beep(tones.get(action, 800), 0.1)

    def play_slow_key_beep(self):
        """Play beep when slow key is accepted"""
        self.play_beep(1000, 0.1)

    def play_toggle_beep(self):
        """Play beep for toggle keys"""
        self.play_beep(1500, 0.1)

    def play_beep(self, frequency, duration):
        """Play a beep sound"""
        try:
            # Use paplay with generated tone
            # In production, would generate actual tone
            # For now, just use system beep
            import subprocess
            subprocess.Popen(['paplay', '/usr/share/sounds/freedesktop/stereo/bell.oga'],
                           stderr=subprocess.DEVNULL)
        except:
            # Fallback to print
            print(f"  *BEEP* ({frequency}Hz, {duration}s)")

    # Configuration methods
    def enable_sticky_keys(self, enabled=True):
        """Enable/disable sticky keys"""
        self.sticky_keys_enabled = enabled
        self.config['sticky_keys_enabled'] = enabled
        self.save_config()
        if enabled:
            print("✓ Sticky Keys enabled")
        else:
            print("✗ Sticky Keys disabled")
            self.sticky_modifiers.clear()

    def enable_slow_keys(self, enabled=True, delay=None):
        """Enable/disable slow keys"""
        self.slow_keys_enabled = enabled
        self.config['slow_keys_enabled'] = enabled
        if delay is not None:
            self.slow_keys_delay = delay
            self.config['slow_keys_delay'] = delay
        self.save_config()
        if enabled:
            print(f"✓ Slow Keys enabled (delay: {self.slow_keys_delay}s)")
        else:
            print("✗ Slow Keys disabled")

    def enable_bounce_keys(self, enabled=True, delay=None):
        """Enable/disable bounce keys"""
        self.bounce_keys_enabled = enabled
        self.config['bounce_keys_enabled'] = enabled
        if delay is not None:
            self.bounce_keys_delay = delay
            self.config['bounce_keys_delay'] = delay
        self.save_config()
        if enabled:
            print(f"✓ Bounce Keys enabled (delay: {self.bounce_keys_delay}s)")
        else:
            print("✗ Bounce Keys disabled")

    def enable_toggle_keys(self, enabled=True):
        """Enable/disable toggle keys beep"""
        self.toggle_keys_enabled = enabled
        self.config['toggle_keys_enabled'] = enabled
        self.save_config()
        if enabled:
            print("✓ Toggle Keys beep enabled")
        else:
            print("✗ Toggle Keys beep disabled")

    def get_status(self):
        """Get current status"""
        return {
            'sticky_keys_enabled': self.sticky_keys_enabled,
            'sticky_modifiers': {str(k): v for k, v in self.sticky_modifiers.items()},
            'slow_keys_enabled': self.slow_keys_enabled,
            'slow_keys_delay': self.slow_keys_delay,
            'bounce_keys_enabled': self.bounce_keys_enabled,
            'bounce_keys_delay': self.bounce_keys_delay,
            'toggle_keys_enabled': self.toggle_keys_enabled,
            'running': self.running
        }


# Global instance
_keyboard_manager = None

def get_keyboard_manager():
    """Get or create keyboard accessibility manager"""
    global _keyboard_manager
    if _keyboard_manager is None:
        _keyboard_manager = KeyboardAccessibilityManager()
    return _keyboard_manager

def start_keyboard_accessibility():
    """Start keyboard accessibility features"""
    manager = get_keyboard_manager()
    manager.start()
    return manager

def stop_keyboard_accessibility():
    """Stop keyboard accessibility features"""
    manager = get_keyboard_manager()
    manager.stop()

if __name__ == '__main__':
    # Test/demo
    manager = KeyboardAccessibilityManager()
    manager.enable_sticky_keys(True)
    manager.enable_slow_keys(True, delay=1.0)
    manager.enable_bounce_keys(True, delay=0.5)

    manager.start()

    print("\nKeyboard Accessibility Test Mode")
    print("Press keys to test features...")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        manager.stop()
