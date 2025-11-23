#!/usr/bin/env python3
"""
TL Linux - Screen Magnifier
Accessibility screen magnifier with customizable zoom levels
"""

import tkinter as tk
from tkinter import ttk
import subprocess
from PIL import Image, ImageTk, ImageGrab
import threading
import time

class ScreenMagnifier:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Magnifier")
        self.root.geometry("400x400")
        self.root.configure(bg='#000000')
        self.root.attributes('-topmost', True)

        # Settings
        self.zoom_level = 2.0
        self.follow_mouse = True
        self.show_crosshair = True
        self.running = False

        # Magnifier window
        self.mag_label = None

        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Control panel
        control_panel = tk.Frame(self.root, bg='#1a1a1a')
        control_panel.pack(fill=tk.X)

        # Zoom controls
        zoom_frame = tk.Frame(control_panel, bg='#1a1a1a')
        zoom_frame.pack(side=tk.LEFT, padx=10, pady=5)

        tk.Label(
            zoom_frame,
            text="Zoom:",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='white'
        ).pack(side=tk.LEFT)

        self.zoom_var = tk.DoubleVar(value=2.0)
        zoom_scale = tk.Scale(
            zoom_frame,
            from_=1.5,
            to=16.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            variable=self.zoom_var,
            command=self.update_zoom,
            bg='#1a1a1a',
            fg='white',
            highlightthickness=0,
            length=150
        )
        zoom_scale.pack(side=tk.LEFT, padx=5)

        self.zoom_label = tk.Label(
            zoom_frame,
            text="2.0x",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='white',
            width=5
        )
        self.zoom_label.pack(side=tk.LEFT)

        # Toggle buttons
        toggle_frame = tk.Frame(control_panel, bg='#1a1a1a')
        toggle_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        self.follow_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            toggle_frame,
            text="Follow Mouse",
            variable=self.follow_var,
            command=self.toggle_follow,
            font=('Arial', 8),
            bg='#1a1a1a',
            fg='white',
            selectcolor='#2b2b2b'
        ).pack(side=tk.LEFT, padx=5)

        self.crosshair_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            toggle_frame,
            text="Crosshair",
            variable=self.crosshair_var,
            font=('Arial', 8),
            bg='#1a1a1a',
            fg='white',
            selectcolor='#2b2b2b'
        ).pack(side=tk.LEFT, padx=5)

        # Magnifier display
        mag_frame = tk.Frame(self.root, bg='#000000', bd=2, relief=tk.SOLID)
        mag_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.canvas = tk.Canvas(
            mag_frame,
            bg='#000000',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Start magnifier
        self.running = True
        self.update_thread = threading.Thread(target=self.update_magnifier, daemon=True)
        self.update_thread.start()

    def update_zoom(self, value):
        """Update zoom level"""
        self.zoom_level = float(value)
        self.zoom_label.config(text=f"{self.zoom_level:.1f}x")

    def toggle_follow(self):
        """Toggle follow mouse"""
        self.follow_mouse = self.follow_var.get()

    def update_magnifier(self):
        """Update magnifier display"""
        while self.running:
            try:
                if self.follow_mouse:
                    # Get mouse position
                    mouse_x, mouse_y = self.get_mouse_position()

                    # Capture area around mouse
                    capture_size = 200  # Base capture size
                    x1 = mouse_x - capture_size // 2
                    y1 = mouse_y - capture_size // 2
                    x2 = mouse_x + capture_size // 2
                    y2 = mouse_y + capture_size // 2

                    # Capture screenshot
                    try:
                        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

                        # Resize for zoom
                        canvas_width = self.canvas.winfo_width()
                        canvas_height = self.canvas.winfo_height()

                        if canvas_width > 1 and canvas_height > 1:
                            zoomed = screenshot.resize(
                                (int(canvas_width), int(canvas_height)),
                                Image.NEAREST  # Pixelated zoom for clarity
                            )

                            # Convert to PhotoImage
                            photo = ImageTk.PhotoImage(zoomed)

                            # Update canvas
                            self.root.after(0, lambda: self.update_canvas(photo))

                    except:
                        pass

                time.sleep(0.05)  # ~20 FPS

            except Exception as e:
                print(f"Magnifier error: {e}")
                time.sleep(0.1)

    def update_canvas(self, photo):
        """Update canvas with new image"""
        try:
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # Keep reference

            # Draw crosshair
            if self.crosshair_var.get():
                width = self.canvas.winfo_width()
                height = self.canvas.winfo_height()

                # Horizontal line
                self.canvas.create_line(
                    0, height//2, width, height//2,
                    fill='red',
                    width=2
                )

                # Vertical line
                self.canvas.create_line(
                    width//2, 0, width//2, height,
                    fill='red',
                    width=2
                )

        except:
            pass

    def get_mouse_position(self):
        """Get current mouse position"""
        try:
            # Use xdotool
            result = subprocess.run(
                ['xdotool', 'getmouselocation', '--shell'],
                capture_output=True,
                text=True
            )

            x, y = 0, 0
            for line in result.stdout.split('\n'):
                if line.startswith('X='):
                    x = int(line.split('=')[1])
                elif line.startswith('Y='):
                    y = int(line.split('=')[1])

            return x, y

        except:
            # Fallback
            return self.root.winfo_pointerx(), self.root.winfo_pointery()

    def run(self):
        """Run the magnifier"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        """Handle window close"""
        self.running = False
        self.root.destroy()

def main():
    # Check if PIL is available
    try:
        from PIL import Image, ImageTk, ImageGrab
    except ImportError:
        print("Error: PIL/Pillow required for screen magnifier")
        print("Install with: pip3 install pillow")
        return

    app = ScreenMagnifier()
    app.run()

if __name__ == '__main__':
    main()
