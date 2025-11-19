#!/usr/bin/env python3
"""
TL Linux - Mouse Keys
Control mouse cursor with keyboard (accessibility feature for motor impairments)
"""

import os
import json
import time
import threading
from pynput import keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Key, KeyCode

class MouseKeys:
    def __init__(self):
        self.config_dir = os.path.expanduser('~/.tl-linux/mouse_keys')
        self.config_file = os.path.join(self.config_dir, 'config.json')

        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

        # Mouse controller
        self.mouse = MouseController()

        # State
        self.enabled = False
        self.running = False
        self.listener = None

        # Movement state
        self.moving = False
        self.movement_thread = None
        self.active_directions = set()

        # Settings
        self.speed = self.config.get('speed', 10)  # pixels per step
        self.acceleration = self.config.get('acceleration', True)
        self.max_speed = self.config.get('max_speed', 50)
        self.acceleration_time = self.config.get('acceleration_time', 2.0)  # seconds

        # Movement start time for acceleration
        self.movement_start_time = None

        # Key bindings (numpad by default)
        self.key_bindings = self.config.get('key_bindings', {
            # Movement (numpad)
            'up': 'num_8',
            'down': 'num_2',
            'left': 'num_4',
            'right': 'num_6',
            'up_left': 'num_7',
            'up_right': 'num_9',
            'down_left': 'num_1',
            'down_right': 'num_3',

            # Clicks
            'left_click': 'num_5',
            'right_click': 'num_minus',
            'middle_click': 'num_asterisk',
            'double_click': 'num_plus',

            # Drag
            'drag_lock': 'num_0',

            # Speed
            'speed_up': 'num_divide',
            'speed_down': 'num_multiply'
        })

        # Drag state
        self.drag_locked = False

    def load_config(self):
        """Load configuration"""
        default_config = {
            'enabled': False,
            'speed': 10,
            'acceleration': True,
            'max_speed': 50,
            'acceleration_time': 2.0,
            'key_bindings': {}  # Will be filled with defaults
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
        """Start Mouse Keys"""
        if self.running:
            return

        self.enabled = True
        self.running = True

        # Start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()

        print("🖱️ Mouse Keys enabled")
        print(f"  Speed: {self.speed} pixels/step")
        print(f"  Acceleration: {'On' if self.acceleration else 'Off'}")
        print("\nNumpad Controls:")
        print("  7 8 9    ↖ ↑ ↗")
        print("  4   6    ← + →")
        print("  1 2 3    ↙ ↓ ↘")
        print("  5 = Left Click")
        print("  0 = Drag Lock")
        print("  + = Double Click")
        print("  - = Right Click")

    def stop(self):
        """Stop Mouse Keys"""
        if not self.running:
            return

        self.enabled = False
        self.running = False

        if self.listener:
            self.listener.stop()

        if self.movement_thread and self.movement_thread.is_alive():
            self.moving = False

        print("🖱️ Mouse Keys disabled")

    def on_key_press(self, key):
        """Handle key press"""
        if not self.enabled:
            return

        try:
            key_name = self.get_key_name(key)

            # Movement keys
            if key_name in ['num_8', 'num_2', 'num_4', 'num_6',
                           'num_7', 'num_9', 'num_1', 'num_3']:
                direction = self.get_direction_from_key(key_name)
                if direction:
                    self.active_directions.add(direction)
                    self.start_movement()
                return False  # Suppress the event

            # Click keys
            elif key_name == 'num_5':
                self.perform_click(Button.left)
                return False

            elif key_name == 'num_minus':
                self.perform_click(Button.right)
                return False

            elif key_name == 'num_asterisk':
                self.perform_click(Button.middle)
                return False

            elif key_name == 'num_plus':
                self.perform_double_click()
                return False

            # Drag lock
            elif key_name == 'num_0':
                self.toggle_drag_lock()
                return False

            # Speed control
            elif key_name == 'num_divide':
                self.adjust_speed(increase=True)
                return False

            elif key_name == 'num_multiply':
                self.adjust_speed(increase=False)
                return False

        except Exception as e:
            print(f"Error in on_key_press: {e}")

    def on_key_release(self, key):
        """Handle key release"""
        if not self.enabled:
            return

        try:
            key_name = self.get_key_name(key)

            # Stop movement when key released
            if key_name in ['num_8', 'num_2', 'num_4', 'num_6',
                           'num_7', 'num_9', 'num_1', 'num_3']:
                direction = self.get_direction_from_key(key_name)
                if direction in self.active_directions:
                    self.active_directions.remove(direction)

                if not self.active_directions:
                    self.stop_movement()

        except Exception as e:
            print(f"Error in on_key_release: {e}")

    def get_key_name(self, key):
        """Get string name of key"""
        if isinstance(key, KeyCode):
            if hasattr(key, 'char'):
                return key.char
            elif hasattr(key, 'vk'):
                # Numpad keys
                numpad_map = {
                    96: 'num_0', 97: 'num_1', 98: 'num_2', 99: 'num_3',
                    100: 'num_4', 101: 'num_5', 102: 'num_6', 103: 'num_7',
                    104: 'num_8', 105: 'num_9',
                    106: 'num_asterisk', 107: 'num_plus',
                    109: 'num_minus', 111: 'num_divide'
                }
                return numpad_map.get(key.vk, str(key))
        return str(key).replace('Key.', '').replace('<', '').replace('>', '')

    def get_direction_from_key(self, key_name):
        """Get movement direction from key name"""
        directions = {
            'num_8': 'up',
            'num_2': 'down',
            'num_4': 'left',
            'num_6': 'right',
            'num_7': 'up_left',
            'num_9': 'up_right',
            'num_1': 'down_left',
            'num_3': 'down_right'
        }
        return directions.get(key_name)

    def start_movement(self):
        """Start continuous mouse movement"""
        if self.moving:
            return

        self.moving = True
        self.movement_start_time = time.time()

        def move_loop():
            while self.moving and self.active_directions:
                # Calculate movement vector
                dx, dy = 0, 0

                if 'up' in self.active_directions or 'up_left' in self.active_directions or 'up_right' in self.active_directions:
                    dy -= 1
                if 'down' in self.active_directions or 'down_left' in self.active_directions or 'down_right' in self.active_directions:
                    dy += 1
                if 'left' in self.active_directions or 'up_left' in self.active_directions or 'down_left' in self.active_directions:
                    dx -= 1
                if 'right' in self.active_directions or 'up_right' in self.active_directions or 'down_right' in self.active_directions:
                    dx += 1

                # Normalize diagonal movement
                if dx != 0 and dy != 0:
                    dx *= 0.707  # 1/√2
                    dy *= 0.707

                # Calculate speed with acceleration
                current_speed = self.calculate_speed()

                # Apply movement
                if dx != 0 or dy != 0:
                    move_x = int(dx * current_speed)
                    move_y = int(dy * current_speed)

                    current_pos = self.mouse.position
                    self.mouse.position = (current_pos[0] + move_x, current_pos[1] + move_y)

                time.sleep(0.05)  # 20Hz update rate

        self.movement_thread = threading.Thread(target=move_loop, daemon=True)
        self.movement_thread.start()

    def stop_movement(self):
        """Stop mouse movement"""
        self.moving = False
        self.movement_start_time = None

    def calculate_speed(self):
        """Calculate current speed with acceleration"""
        if not self.acceleration or self.movement_start_time is None:
            return self.speed

        # Linear acceleration from speed to max_speed over acceleration_time
        elapsed = time.time() - self.movement_start_time
        if elapsed >= self.acceleration_time:
            return self.max_speed

        progress = elapsed / self.acceleration_time
        return self.speed + (self.max_speed - self.speed) * progress

    def perform_click(self, button):
        """Perform mouse click"""
        if self.drag_locked and button == Button.left:
            # Release drag lock
            self.mouse.release(Button.left)
            self.drag_locked = False
            print("  🖱️ Drag released")
        else:
            self.mouse.click(button)
            print(f"  🖱️ {button} click")

    def perform_double_click(self):
        """Perform double click"""
        self.mouse.click(Button.left, 2)
        print("  🖱️ Double click")

    def toggle_drag_lock(self):
        """Toggle drag lock (hold left button)"""
        if self.drag_locked:
            self.mouse.release(Button.left)
            self.drag_locked = False
            print("  🖱️ Drag lock OFF")
        else:
            self.mouse.press(Button.left)
            self.drag_locked = True
            print("  🖱️ Drag lock ON")

    def adjust_speed(self, increase=True):
        """Adjust movement speed"""
        if increase:
            self.speed = min(self.max_speed, self.speed + 5)
            print(f"  🖱️ Speed increased to {self.speed}")
        else:
            self.speed = max(1, self.speed - 5)
            print(f"  🖱️ Speed decreased to {self.speed}")

        self.config['speed'] = self.speed
        self.save_config()

    def set_speed(self, speed):
        """Set movement speed"""
        self.speed = max(1, min(self.max_speed, speed))
        self.config['speed'] = self.speed
        self.save_config()

    def set_acceleration(self, enabled):
        """Enable/disable acceleration"""
        self.acceleration = enabled
        self.config['acceleration'] = enabled
        self.save_config()

    def get_status(self):
        """Get current status"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'speed': self.speed,
            'max_speed': self.max_speed,
            'acceleration': self.acceleration,
            'drag_locked': self.drag_locked,
            'moving': self.moving,
            'active_directions': list(self.active_directions)
        }


# Global instance
_mouse_keys = None

def get_mouse_keys():
    """Get or create mouse keys instance"""
    global _mouse_keys
    if _mouse_keys is None:
        _mouse_keys = MouseKeys()
    return _mouse_keys

def start_mouse_keys():
    """Start Mouse Keys"""
    manager = get_mouse_keys()
    manager.start()
    return manager

def stop_mouse_keys():
    """Stop Mouse Keys"""
    manager = get_mouse_keys()
    manager.stop()

if __name__ == '__main__':
    # Test/demo
    mouse_keys = MouseKeys()
    mouse_keys.start()

    print("\nMouse Keys Test Mode")
    print("Use numpad to control mouse")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        mouse_keys.stop()
