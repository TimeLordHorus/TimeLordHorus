#!/usr/bin/env python3
"""
TL Linux - Screenshot & Annotation Tool
Capture screenshots and annotate with drawing tools
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageGrab, ImageTk
import subprocess
import os
from datetime import datetime

class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Screenshot Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')

        # Screenshot
        self.screenshot = None
        self.screenshot_tk = None

        # Drawing state
        self.drawing = False
        self.draw_mode = 'none'  # none, pen, rectangle, circle, arrow, text
        self.draw_color = '#ff0000'
        self.draw_width = 3
        self.start_x = 0
        self.start_y = 0
        self.temp_item = None

        # Annotation layer (for drawing)
        self.annotation_layer = None

        # Save directory
        self.save_dir = os.path.expanduser('~/Pictures/Screenshots')
        os.makedirs(self.save_dir, exist_ok=True)

        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📸 Screenshot Tool",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Capture toolbar
        capture_toolbar = tk.Frame(self.root, bg='#1a1a1a')
        capture_toolbar.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            capture_toolbar,
            text="Capture:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            capture_toolbar,
            text="🖵 Full Screen",
            command=self.capture_fullscreen,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            capture_toolbar,
            text="✂️ Select Region",
            command=self.capture_region,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            capture_toolbar,
            text="🪟 Window",
            command=self.capture_window,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        # Delay option
        tk.Label(
            capture_toolbar,
            text="Delay:",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.delay_var = tk.IntVar(value=0)
        delay_spin = tk.Spinbox(
            capture_toolbar,
            from_=0,
            to=10,
            textvariable=self.delay_var,
            width=5,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 9)
        )
        delay_spin.pack(side=tk.LEFT, padx=5)

        tk.Label(
            capture_toolbar,
            text="seconds",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 8)
        ).pack(side=tk.LEFT)

        # Annotation toolbar
        annotation_toolbar = tk.Frame(self.root, bg='#2b2b2b')
        annotation_toolbar.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            annotation_toolbar,
            text="Annotate:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(10, 10))

        # Drawing tools
        self.tool_var = tk.StringVar(value='none')

        tools = [
            ('🖱️', 'none', 'Select'),
            ('✏️', 'pen', 'Pen'),
            ('▭', 'rectangle', 'Rectangle'),
            ('○', 'circle', 'Circle'),
            ('➡️', 'arrow', 'Arrow'),
            ('T', 'text', 'Text')
        ]

        for icon, mode, tooltip in tools:
            btn = tk.Radiobutton(
                annotation_toolbar,
                text=icon,
                variable=self.tool_var,
                value=mode,
                command=lambda m=mode: self.set_draw_mode(m),
                bg='#2b2b2b',
                fg='white',
                selectcolor='#4a9eff',
                font=('Arial', 12),
                indicatoron=False,
                width=3,
                bd=0,
                padx=5,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Color picker
        tk.Label(
            annotation_toolbar,
            text="Color:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.color_button = tk.Button(
            annotation_toolbar,
            bg=self.draw_color,
            width=3,
            command=self.choose_color,
            bd=1,
            relief=tk.SOLID
        )
        self.color_button.pack(side=tk.LEFT, padx=5)

        # Width slider
        tk.Label(
            annotation_toolbar,
            text="Width:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.width_var = tk.IntVar(value=3)
        width_scale = tk.Scale(
            annotation_toolbar,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.width_var,
            command=lambda v: setattr(self, 'draw_width', int(v)),
            bg='#2b2b2b',
            fg='white',
            highlightthickness=0,
            length=100
        )
        width_scale.pack(side=tk.LEFT, padx=5)

        # Save/Export toolbar
        save_toolbar = tk.Frame(self.root, bg='#1a1a1a')
        save_toolbar.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(
            save_toolbar,
            text="💾 Save",
            command=self.save_screenshot,
            bg='#50fa7b',
            fg='#000000',
            bd=0,
            padx=20,
            pady=8,
            font=('Arial', 9, 'bold')
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            save_toolbar,
            text="📋 Copy to Clipboard",
            command=self.copy_to_clipboard,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            save_toolbar,
            text="🗑️ Clear",
            command=self.clear_canvas,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        # Canvas
        canvas_frame = tk.Frame(self.root, bg='#000000', bd=2, relief=tk.SOLID)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Canvas bindings
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)

        # Status bar
        status_bar = tk.Frame(self.root, bg='#2b2b2b', height=25)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="Take a screenshot to begin",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

    def capture_fullscreen(self):
        """Capture entire screen"""
        delay = self.delay_var.get()
        if delay > 0:
            self.status_label.config(text=f"Capturing in {delay} seconds...")
            self.root.after(delay * 1000, self._do_fullscreen_capture)
        else:
            self._do_fullscreen_capture()

    def _do_fullscreen_capture(self):
        """Perform fullscreen capture"""
        self.root.withdraw()  # Hide window
        self.root.after(200, self._grab_fullscreen)

    def _grab_fullscreen(self):
        """Grab fullscreen after brief delay"""
        try:
            self.screenshot = ImageGrab.grab()
            self.display_screenshot()
            self.status_label.config(text="Screenshot captured")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot:\n{str(e)}")
        finally:
            self.root.deiconify()

    def capture_region(self):
        """Capture selected region"""
        self.status_label.config(text="Click and drag to select region...")

        # Create selection window
        selector = tk.Toplevel(self.root)
        selector.attributes('-fullscreen', True)
        selector.attributes('-alpha', 0.3)
        selector.configure(bg='black')

        canvas = tk.Canvas(selector, highlightthickness=0, bg='black')
        canvas.pack(fill=tk.BOTH, expand=True)

        selection = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0, 'rect': None}

        def on_press(event):
            selection['x1'] = event.x
            selection['y1'] = event.y

        def on_drag(event):
            selection['x2'] = event.x
            selection['y2'] = event.y

            if selection['rect']:
                canvas.delete(selection['rect'])

            selection['rect'] = canvas.create_rectangle(
                selection['x1'], selection['y1'],
                selection['x2'], selection['y2'],
                outline='red',
                width=2
            )

        def on_release(event):
            selector.destroy()

            x1 = min(selection['x1'], selection['x2'])
            y1 = min(selection['y1'], selection['y2'])
            x2 = max(selection['x1'], selection['x2'])
            y2 = max(selection['y1'], selection['y2'])

            if x2 - x1 > 10 and y2 - y1 > 10:
                self.screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                self.display_screenshot()
                self.status_label.config(text="Region captured")

        canvas.bind('<Button-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)
        canvas.bind('<Escape>', lambda e: selector.destroy())

    def capture_window(self):
        """Capture active window"""
        self.status_label.config(text="Capturing active window in 2 seconds...")
        self.root.after(2000, self._do_window_capture)

    def _do_window_capture(self):
        """Perform window capture using scrot or import"""
        try:
            # Try using scrot for window capture
            output_file = f"/tmp/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            result = subprocess.run(
                ['scrot', '-u', output_file],
                capture_output=True
            )

            if result.returncode == 0 and os.path.exists(output_file):
                self.screenshot = Image.open(output_file)
                os.remove(output_file)
                self.display_screenshot()
                self.status_label.config(text="Window captured")
            else:
                # Fallback to fullscreen
                self._do_fullscreen_capture()

        except FileNotFoundError:
            # scrot not available, use fullscreen
            messagebox.showinfo("Info", "Window capture not available, using fullscreen instead.")
            self._do_fullscreen_capture()

    def display_screenshot(self):
        """Display screenshot on canvas"""
        if not self.screenshot:
            return

        # Clear canvas
        self.canvas.delete('all')

        # Resize to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 100:
            canvas_width = 800
        if canvas_height < 100:
            canvas_height = 500

        # Calculate scaled size
        img_ratio = self.screenshot.width / self.screenshot.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)

        # Create resized image
        resized = self.screenshot.resize((new_width, new_height), Image.LANCZOS)
        self.screenshot_tk = ImageTk.PhotoImage(resized)

        # Display on canvas
        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=self.screenshot_tk,
            anchor=tk.CENTER,
            tags='screenshot'
        )

        # Create annotation layer
        self.annotation_layer = Image.new('RGBA', self.screenshot.size, (0, 0, 0, 0))

    def set_draw_mode(self, mode):
        """Set drawing mode"""
        self.draw_mode = mode
        if mode == 'none':
            self.canvas.config(cursor='')
        else:
            self.canvas.config(cursor='crosshair')

    def choose_color(self):
        """Choose drawing color"""
        color = colorchooser.askcolor(title="Choose Color", initialcolor=self.draw_color)
        if color[1]:
            self.draw_color = color[1]
            self.color_button.config(bg=self.draw_color)

    def on_canvas_click(self, event):
        """Handle canvas click"""
        if self.draw_mode == 'none' or not self.screenshot:
            return

        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y

        if self.draw_mode == 'text':
            self.add_text(event.x, event.y)
            self.drawing = False

    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if not self.drawing or self.draw_mode == 'none':
            return

        # Remove temporary item
        if self.temp_item:
            self.canvas.delete(self.temp_item)

        # Draw temporary shape
        if self.draw_mode == 'pen':
            self.temp_item = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                fill=self.draw_color,
                width=self.draw_width,
                capstyle=tk.ROUND
            )
            self.start_x = event.x
            self.start_y = event.y

        elif self.draw_mode == 'rectangle':
            self.temp_item = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.draw_color,
                width=self.draw_width
            )

        elif self.draw_mode == 'circle':
            self.temp_item = self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.draw_color,
                width=self.draw_width
            )

        elif self.draw_mode == 'arrow':
            self.temp_item = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                fill=self.draw_color,
                width=self.draw_width,
                arrow=tk.LAST,
                arrowshape=(16, 20, 6)
            )

    def on_canvas_release(self, event):
        """Handle canvas release"""
        if not self.drawing:
            return

        self.drawing = False
        self.temp_item = None

        # Draw on annotation layer (for saving)
        if self.annotation_layer:
            self.draw_on_annotation_layer(self.start_x, self.start_y, event.x, event.y)

    def draw_on_annotation_layer(self, x1, y1, x2, y2):
        """Draw annotation on the image layer"""
        # This is simplified - in production would properly scale coordinates
        # and draw on the actual image layer
        pass

    def add_text(self, x, y):
        """Add text annotation"""
        text = tk.simpledialog.askstring("Add Text", "Enter text:")
        if text:
            self.canvas.create_text(
                x, y,
                text=text,
                fill=self.draw_color,
                font=('Arial', 16, 'bold'),
                anchor=tk.NW
            )

    def clear_canvas(self):
        """Clear screenshot and annotations"""
        self.canvas.delete('all')
        self.screenshot = None
        self.screenshot_tk = None
        self.annotation_layer = None
        self.status_label.config(text="Canvas cleared")

    def save_screenshot(self):
        """Save screenshot to file"""
        if not self.screenshot:
            messagebox.showwarning("No Screenshot", "Take a screenshot first.")
            return

        # Generate filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        default_filename = f"screenshot_{timestamp}.png"

        file_path = filedialog.asksaveasfilename(
            initialdir=self.save_dir,
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*")
            ]
        )

        if file_path:
            try:
                # Save (would merge with annotations in production)
                self.screenshot.save(file_path)
                self.status_label.config(text=f"Saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Screenshot saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save screenshot:\n{str(e)}")

    def copy_to_clipboard(self):
        """Copy screenshot to clipboard"""
        if not self.screenshot:
            messagebox.showwarning("No Screenshot", "Take a screenshot first.")
            return

        try:
            # Save to temp file and use xclip
            temp_file = "/tmp/screenshot_clipboard.png"
            self.screenshot.save(temp_file)

            subprocess.run([
                'xclip',
                '-selection', 'clipboard',
                '-t', 'image/png',
                '-i', temp_file
            ])

            os.remove(temp_file)
            self.status_label.config(text="Copied to clipboard")
            messagebox.showinfo("Success", "Screenshot copied to clipboard!")

        except FileNotFoundError:
            messagebox.showwarning(
                "xclip Not Available",
                "xclip is required for clipboard support.\nInstall with: sudo apt install xclip"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")

    def run(self):
        """Run the screenshot tool"""
        self.root.mainloop()

def main():
    try:
        from PIL import Image, ImageGrab, ImageTk
    except ImportError:
        print("Error: PIL/Pillow required for screenshot tool")
        print("Install with: pip3 install pillow")
        return

    tool = ScreenshotTool()
    tool.run()

if __name__ == '__main__':
    main()
