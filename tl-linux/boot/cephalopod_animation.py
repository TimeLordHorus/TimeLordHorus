#!/usr/bin/env python3
"""
TL Linux Boot Animation - Pixelated Cephalopod
Displays an animated cephalopod floating in a sea of pixels during boot
"""

import sys
import time
import random
import os

# ANSI color codes for pixel art
COLORS = {
    'reset': '\033[0m',
    'cyan': '\033[96m',
    'blue': '\033[94m',
    'purple': '\033[95m',
    'white': '\033[97m',
    'dark_blue': '\033[34m',
    'aqua': '\033[36m',
}

# Pixelated cephalopod frames for animation
CEPHALOPOD_FRAMES = [
    # Frame 1
    """
        ▓▓▓▓▓▓▓▓
      ▓▓░░░░░░░░▓▓
    ▓▓░░░░░░░░░░░░▓▓
    ▓░░░░◉░░░◉░░░░▓
    ▓▓░░░░░░░░░░░░▓▓
      ▓▓░░░◡░░░░▓▓
        ▓▓▓▓▓▓▓▓
      ▓  ▓  ▓  ▓  ▓
     ▓  ▓  ▓  ▓  ▓  ▓
    ▓  ▓  ▓  ▓  ▓  ▓
    """,
    # Frame 2
    """
        ▓▓▓▓▓▓▓▓
      ▓▓░░░░░░░░▓▓
    ▓▓░░░░░░░░░░░░▓▓
    ▓░░░░◉░░░◉░░░░▓
    ▓▓░░░░░░░░░░░░▓▓
      ▓▓░░░◡░░░░▓▓
        ▓▓▓▓▓▓▓▓
     ▓  ▓  ▓  ▓  ▓
    ▓  ▓  ▓  ▓  ▓  ▓
       ▓  ▓  ▓  ▓
    """,
    # Frame 3
    """
        ▓▓▓▓▓▓▓▓
      ▓▓░░░░░░░░▓▓
    ▓▓░░░░░░░░░░░░▓▓
    ▓░░░░◉░░░◉░░░░▓
    ▓▓░░░░░░░░░░░░▓▓
      ▓▓░░░◡░░░░▓▓
        ▓▓▓▓▓▓▓▓
    ▓  ▓  ▓  ▓  ▓  ▓
     ▓  ▓  ▓  ▓  ▓
      ▓  ▓  ▓  ▓
    """
]

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def generate_pixel_sea(width, height, density=0.15):
    """Generate a sea of random pixels"""
    sea = []
    pixel_chars = ['░', '▒', '▓', '█', '▪', '▫', '·']

    for _ in range(height):
        row = ''
        for _ in range(width):
            if random.random() < density:
                char = random.choice(pixel_chars)
                color = random.choice([COLORS['cyan'], COLORS['blue'], COLORS['aqua'], COLORS['dark_blue']])
                row += f"{color}{char}{COLORS['reset']}"
            else:
                row += ' '
        sea.append(row)
    return sea

def draw_frame(frame_num, terminal_width=80, terminal_height=24):
    """Draw a single animation frame"""
    clear_screen()

    # Generate pixel sea background
    sea = generate_pixel_sea(terminal_width, terminal_height - 15)

    # Draw top portion of sea
    for i in range(3):
        if i < len(sea):
            print(sea[i])

    # Draw cephalopod
    octopus = CEPHALOPOD_FRAMES[frame_num % len(CEPHALOPOD_FRAMES)]
    octopus_lines = octopus.strip().split('\n')

    for line in octopus_lines:
        # Center the cephalopod and apply color
        padding = (terminal_width - len(line)) // 2
        colored_line = f"{COLORS['purple']}{line}{COLORS['reset']}"
        print(' ' * padding + colored_line)

    # Draw bottom portion of sea
    for i in range(3, min(len(sea), terminal_height - len(octopus_lines) - 5)):
        print(sea[i])

    # Draw boot message
    print(f"\n{COLORS['cyan']}{'═' * terminal_width}{COLORS['reset']}")
    print(f"{COLORS['white']}{'TL Linux - Time Lord Computing Experience':^{terminal_width}}{COLORS['reset']}")
    print(f"{COLORS['cyan']}{'═' * terminal_width}{COLORS['reset']}")

    # Loading animation
    loading_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    loading_char = loading_chars[frame_num % len(loading_chars)]
    print(f"{COLORS['aqua']}{loading_char} Initializing TL Linux...{COLORS['reset']}")

def run_boot_animation(duration=5):
    """Run the boot animation for specified duration"""
    start_time = time.time()
    frame = 0

    try:
        while time.time() - start_time < duration:
            draw_frame(frame)
            frame += 1
            time.sleep(0.15)
    except KeyboardInterrupt:
        pass

    clear_screen()
    print(f"\n{COLORS['cyan']}TL Linux boot complete!{COLORS['reset']}\n")

if __name__ == '__main__':
    run_boot_animation()
