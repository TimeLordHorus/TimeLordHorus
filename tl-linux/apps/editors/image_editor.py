#!/usr/bin/env python3
"""
TL Linux - Basic Image Editor
Simple image editing with PIL/Pillow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from pathlib import Path
import io

class ImageEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖼️ TL Image Editor")
        self.root.geometry("1200x700")

        self.current_file = None
        self.original_image = None
        self.current_image = None
        self.display_image = None
        self.history = []
        self.history_index = -1

        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Save As", command=self.save_as_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset to Original", command=self.reset_image)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2c3e50', pady=8)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="📁 Open", command=self.open_image, bg='#34495e', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 Save", command=self.save_image, bg='#34495e', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        tk.Button(toolbar, text="↶ Undo", command=self.undo, bg='#34495e', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="↷ Redo", command=self.redo, bg='#34495e', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        tk.Button(toolbar, text="🔄 Reset", command=self.reset_image, bg='#e74c3c', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)

        # Main content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Tools
        tools_frame = tk.Frame(main_frame, bg='#ecf0f1', width=250, padx=10, pady=10)
        tools_frame.pack(side=tk.LEFT, fill=tk.Y)
        tools_frame.pack_propagate(False)

        # Transform section
        tk.Label(tools_frame, text="Transform", bg='#ecf0f1', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        transform_frame = tk.Frame(tools_frame, bg='#ecf0f1')
        transform_frame.pack(fill=tk.X, pady=5)

        tk.Button(transform_frame, text="⟲ Rotate Left", command=lambda: self.rotate(-90), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(transform_frame, text="⟳ Rotate Right", command=lambda: self.rotate(90), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(transform_frame, text="↔ Flip Horizontal", command=lambda: self.flip('horizontal'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(transform_frame, text="↕ Flip Vertical", command=lambda: self.flip('vertical'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)

        ttk.Separator(tools_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Resize section
        tk.Label(tools_frame, text="Resize", bg='#ecf0f1', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        resize_frame = tk.Frame(tools_frame, bg='#ecf0f1')
        resize_frame.pack(fill=tk.X, pady=5)

        tk.Label(resize_frame, text="Width:", bg='#ecf0f1').grid(row=0, column=0, sticky='w')
        self.width_entry = tk.Entry(resize_frame, width=8)
        self.width_entry.grid(row=0, column=1, padx=5)

        tk.Label(resize_frame, text="Height:", bg='#ecf0f1').grid(row=1, column=0, sticky='w')
        self.height_entry = tk.Entry(resize_frame, width=8)
        self.height_entry.grid(row=1, column=1, padx=5)

        tk.Button(resize_frame, text="Apply Resize", command=self.resize_image, bg='#3498db', fg='white', relief=tk.FLAT).grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

        ttk.Separator(tools_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Filters section
        tk.Label(tools_frame, text="Filters", bg='#ecf0f1', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        filters_frame = tk.Frame(tools_frame, bg='#ecf0f1')
        filters_frame.pack(fill=tk.X, pady=5)

        tk.Button(filters_frame, text="Blur", command=lambda: self.apply_filter('blur'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(filters_frame, text="Sharpen", command=lambda: self.apply_filter('sharpen'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(filters_frame, text="Edge Enhance", command=lambda: self.apply_filter('edge'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(filters_frame, text="Emboss", command=lambda: self.apply_filter('emboss'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(filters_frame, text="Grayscale", command=lambda: self.apply_filter('grayscale'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)
        tk.Button(filters_frame, text="Sepia", command=lambda: self.apply_filter('sepia'), bg='white', relief=tk.GROOVE).pack(fill=tk.X, pady=2)

        ttk.Separator(tools_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Adjustments section
        tk.Label(tools_frame, text="Adjustments", bg='#ecf0f1', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        adjustments_frame = tk.Frame(tools_frame, bg='#ecf0f1')
        adjustments_frame.pack(fill=tk.X, pady=5)

        tk.Label(adjustments_frame, text="Brightness:", bg='#ecf0f1').pack(anchor='w')
        self.brightness_scale = tk.Scale(adjustments_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, bg='#ecf0f1')
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack(fill=tk.X)

        tk.Label(adjustments_frame, text="Contrast:", bg='#ecf0f1').pack(anchor='w')
        self.contrast_scale = tk.Scale(adjustments_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, bg='#ecf0f1')
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(fill=tk.X)

        tk.Button(adjustments_frame, text="Apply Adjustments", command=self.apply_adjustments, bg='#2ecc71', fg='white', relief=tk.FLAT).pack(fill=tk.X, pady=5)

        # Canvas for image display
        canvas_frame = tk.Frame(main_frame, bg='#34495e')
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg='#2c3e50', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Info label
        info_frame = tk.Frame(canvas_frame, bg='#34495e')
        info_frame.pack(fill=tk.X, pady=(5, 0))

        self.info_label = tk.Label(info_frame, text="No image loaded", bg='#34495e', fg='white', font=('Arial', 9))
        self.info_label.pack(side=tk.LEFT, padx=10)

        # Keyboard shortcuts
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_image(self):
        """Open image file"""
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.current_file = Path(file_path)

                # Reset history
                self.history = [self.current_image.copy()]
                self.history_index = 0

                # Update size entries
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.current_image.width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.current_image.height))

                self.display_current_image()
                self.update_info()
                self.status_bar.config(text=f"Opened: {self.current_file.name}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open image:\n{e}")

    def save_image(self):
        """Save current image"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save")
            return

        if self.current_file:
            self.save_to_file(str(self.current_file))
        else:
            self.save_as_image()

    def save_as_image(self):
        """Save image as new file"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Save to specific file path"""
        try:
            self.current_image.save(file_path)
            self.current_file = Path(file_path)
            self.status_bar.config(text=f"Saved: {self.current_file.name}")
            messagebox.showinfo("Saved", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image:\n{e}")

    def add_to_history(self):
        """Add current state to history"""
        if self.current_image:
            # Remove any redo history
            self.history = self.history[:self.history_index + 1]
            # Add new state
            self.history.append(self.current_image.copy())
            self.history_index += 1
            # Limit history size
            if len(self.history) > 20:
                self.history.pop(0)
                self.history_index -= 1

    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_current_image()
            self.update_info()
            self.status_bar.config(text="Undo")

    def redo(self):
        """Redo last undone operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_current_image()
            self.update_info()
            self.status_bar.config(text="Redo")

    def reset_image(self):
        """Reset to original image"""
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.add_to_history()
            self.display_current_image()
            self.update_info()
            self.status_bar.config(text="Reset to original")

    def rotate(self, angle):
        """Rotate image"""
        if self.current_image:
            self.current_image = self.current_image.rotate(angle, expand=True)
            self.add_to_history()
            self.display_current_image()
            self.update_info()
            self.status_bar.config(text=f"Rotated {angle}°")

    def flip(self, direction):
        """Flip image"""
        if self.current_image:
            if direction == 'horizontal':
                self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
                self.status_bar.config(text="Flipped horizontally")
            else:
                self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
                self.status_bar.config(text="Flipped vertically")

            self.add_to_history()
            self.display_current_image()
            self.update_info()

    def resize_image(self):
        """Resize image to specified dimensions"""
        if self.current_image is None:
            return

        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            if width <= 0 or height <= 0:
                messagebox.showerror("Error", "Width and height must be positive")
                return

            self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
            self.add_to_history()
            self.display_current_image()
            self.update_info()
            self.status_bar.config(text=f"Resized to {width}x{height}")

        except ValueError:
            messagebox.showerror("Error", "Invalid width or height")

    def apply_filter(self, filter_type):
        """Apply filter to image"""
        if self.current_image is None:
            return

        if filter_type == 'blur':
            self.current_image = self.current_image.filter(ImageFilter.BLUR)
        elif filter_type == 'sharpen':
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
        elif filter_type == 'edge':
            self.current_image = self.current_image.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == 'emboss':
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
        elif filter_type == 'grayscale':
            self.current_image = self.current_image.convert('L').convert('RGB')
        elif filter_type == 'sepia':
            # Convert to grayscale first
            grayscale = self.current_image.convert('L')
            # Create sepia by tinting
            sepia = Image.new('RGB', grayscale.size)
            pixels = sepia.load()
            gray_pixels = grayscale.load()
            for y in range(sepia.height):
                for x in range(sepia.width):
                    gray = gray_pixels[x, y]
                    # Sepia tone
                    r = min(255, int(gray * 1.0))
                    g = min(255, int(gray * 0.95))
                    b = min(255, int(gray * 0.82))
                    pixels[x, y] = (r, g, b)
            self.current_image = sepia

        self.add_to_history()
        self.display_current_image()
        self.status_bar.config(text=f"Applied {filter_type} filter")

    def apply_adjustments(self):
        """Apply brightness and contrast adjustments"""
        if self.current_image is None:
            return

        brightness_value = self.brightness_scale.get()
        contrast_value = self.contrast_scale.get()

        # Apply brightness
        enhancer = ImageEnhance.Brightness(self.current_image)
        self.current_image = enhancer.enhance(brightness_value)

        # Apply contrast
        enhancer = ImageEnhance.Contrast(self.current_image)
        self.current_image = enhancer.enhance(contrast_value)

        self.add_to_history()
        self.display_current_image()
        self.status_bar.config(text=f"Applied adjustments (B:{brightness_value:.1f}, C:{contrast_value:.1f})")

    def display_current_image(self):
        """Display current image on canvas"""
        if self.current_image is None:
            return

        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized
            self.root.after(100, self.display_current_image)
            return

        # Calculate scaling to fit canvas
        img_width, img_height = self.current_image.size
        scale_width = canvas_width / img_width
        scale_height = canvas_height / img_height
        scale = min(scale_width, scale_height, 1.0)  # Don't scale up

        display_width = int(img_width * scale)
        display_height = int(img_height * scale)

        # Resize for display
        self.display_image = self.current_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.display_image)

        # Clear canvas and display
        self.canvas.delete('all')
        x = (canvas_width - display_width) // 2
        y = (canvas_height - display_height) // 2
        self.canvas.create_image(x, y, anchor='nw', image=self.photo)

    def update_info(self):
        """Update image info display"""
        if self.current_image:
            width, height = self.current_image.size
            mode = self.current_image.mode
            file_name = self.current_file.name if self.current_file else "Untitled"
            self.info_label.config(text=f"{file_name} - {width}x{height} - {mode}")

            # Update size entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(height))

    def run(self):
        """Run editor"""
        self.root.mainloop()

if __name__ == '__main__':
    editor = ImageEditor()
    editor.run()
