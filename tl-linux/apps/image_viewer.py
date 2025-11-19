#!/usr/bin/env python3
"""
TL Linux - Image Viewer
Image viewer with slideshow and navigation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os
from pathlib import Path
import json
import shutil

class ImageViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Image Viewer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')

        # Configuration
        self.config_dir = Path.home() / '.tl-linux'
        self.config_file = self.config_dir / 'image_viewer_config.json'
        self.config_dir.mkdir(exist_ok=True)

        # Image state
        self.image_files = []
        self.current_index = -1
        self.current_image = None
        self.current_photo = None
        self.zoom_level = 1.0
        self.rotation = 0

        # Slideshow
        self.slideshow_active = False
        self.slideshow_interval = 3000  # milliseconds
        self.slideshow_job = None

        # Recent folders
        self.recent_folders = []

        # Supported formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico'}

        self.load_config()
        self.setup_ui()

        # Keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.previous_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<space>', lambda e: self.toggle_slideshow())
        self.root.bind('<plus>', lambda e: self.zoom_in())
        self.root.bind('<minus>', lambda e: self.zoom_out())
        self.root.bind('<r>', lambda e: self.rotate_image())
        self.root.bind('<f>', lambda e: self.fit_to_window())

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🖼 Image Viewer",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(header, bg='#2b2b2b')
        toolbar.pack(side=tk.RIGHT, padx=20)

        tk.Button(
            toolbar,
            text="📂 Open",
            command=self.open_image,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text="📁 Open Folder",
            command=self.open_folder,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text="▶ Slideshow",
            command=self.toggle_slideshow,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel - Thumbnails
        left_panel = tk.Frame(main_container, bg='#1a1a1a', width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="Images",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(0, 10))

        # Thumbnails list
        thumb_frame = tk.Frame(left_panel, bg='#1a1a1a')
        thumb_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(thumb_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.thumbnails_listbox = tk.Listbox(
            thumb_frame,
            bg='#2b2b2b',
            fg='white',
            selectbackground='#4a9eff',
            selectforeground='white',
            font=('Arial', 9),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.thumbnails_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.thumbnails_listbox.yview)

        self.thumbnails_listbox.bind('<<ListboxSelect>>', self.on_thumbnail_select)

        # Image counter
        self.counter_label = tk.Label(
            left_panel,
            text="0 / 0",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.counter_label.pack(pady=10)

        # Right panel - Image display
        right_panel = tk.Frame(main_container, bg='#1a1a1a')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Image canvas
        self.canvas = tk.Canvas(
            right_panel,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW)

        # Placeholder
        self.placeholder_text = self.canvas.create_text(
            400, 300,
            text="No image loaded\n\nPress 'Open' to select an image or folder",
            font=('Arial', 14),
            fill='#888888',
            justify=tk.CENTER
        )

        # Image info
        info_frame = tk.Frame(right_panel, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.image_name_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white',
            anchor='w'
        )
        self.image_name_label.pack(fill=tk.X)

        self.image_info_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888',
            anchor='w'
        )
        self.image_info_label.pack(fill=tk.X)

        # Controls
        controls_frame = tk.Frame(right_panel, bg='#1a1a1a')
        controls_frame.pack(pady=10)

        # Navigation
        tk.Button(
            controls_frame,
            text="⏮ Previous",
            command=self.previous_image,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame,
            text="Next ⏭",
            command=self.next_image,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Zoom controls
        tk.Button(
            controls_frame,
            text="🔍+ Zoom In",
            command=self.zoom_in,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame,
            text="🔍- Zoom Out",
            command=self.zoom_out,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame,
            text="⛶ Fit",
            command=self.fit_to_window,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Rotate
        tk.Button(
            controls_frame,
            text="🔄 Rotate",
            command=self.rotate_image,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Delete
        tk.Button(
            controls_frame,
            text="🗑 Delete",
            command=self.delete_image,
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Slideshow controls
        slideshow_frame = tk.Frame(right_panel, bg='#1a1a1a')
        slideshow_frame.pack(pady=(5, 0))

        tk.Label(
            slideshow_frame,
            text="Slideshow interval:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.interval_var = tk.StringVar(value="3")
        interval_combo = ttk.Combobox(
            slideshow_frame,
            textvariable=self.interval_var,
            values=['1', '2', '3', '5', '10'],
            width=5,
            state='readonly'
        )
        interval_combo.pack(side=tk.LEFT, padx=2)
        interval_combo.bind('<<ComboboxSelected>>', self.change_interval)

        tk.Label(
            slideshow_frame,
            text="seconds",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(2, 0))

        # Status bar
        status_bar = tk.Frame(self.root, bg='#2b2b2b', height=25)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.zoom_label = tk.Label(
            status_bar,
            text="Zoom: 100%",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='e'
        )
        self.zoom_label.pack(side=tk.RIGHT, padx=10)

    def open_image(self):
        """Open a single image"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp *.ico"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Open Image",
            filetypes=filetypes
        )

        if filename:
            folder = str(Path(filename).parent)
            self.load_folder(folder)

            # Find and display the selected image
            for i, img_file in enumerate(self.image_files):
                if img_file == filename:
                    self.current_index = i
                    self.display_image()
                    break

    def open_folder(self):
        """Open a folder of images"""
        folder = filedialog.askdirectory(title="Select Image Folder")

        if folder:
            self.load_folder(folder)
            if self.image_files:
                self.current_index = 0
                self.display_image()

    def load_folder(self, folder):
        """Load all images from a folder"""
        self.image_files.clear()
        self.thumbnails_listbox.delete(0, tk.END)

        # Find all image files
        folder_path = Path(folder)
        for file_path in sorted(folder_path.iterdir()):
            if file_path.suffix.lower() in self.supported_formats:
                self.image_files.append(str(file_path))
                self.thumbnails_listbox.insert(tk.END, file_path.name)

        # Add to recent folders
        self.add_to_recent_folders(folder)

        # Update counter
        self.update_counter()

        self.status_label.config(text=f"Loaded {len(self.image_files)} images from {folder}")

    def display_image(self):
        """Display the current image"""
        if not self.image_files or self.current_index < 0:
            return

        try:
            image_path = self.image_files[self.current_index]

            # Load image
            self.current_image = Image.open(image_path)

            # Apply rotation
            if self.rotation != 0:
                self.current_image = self.current_image.rotate(-self.rotation, expand=True)

            # Update info
            self.image_name_label.config(text=Path(image_path).name)
            width, height = self.current_image.size
            file_size = os.path.getsize(image_path) / 1024  # KB

            self.image_info_label.config(
                text=f"{width} × {height} pixels | {file_size:.1f} KB | {self.current_image.format}"
            )

            # Update thumbnails selection
            self.thumbnails_listbox.selection_clear(0, tk.END)
            self.thumbnails_listbox.selection_set(self.current_index)
            self.thumbnails_listbox.see(self.current_index)

            # Display with current zoom
            self.update_display()

            # Update counter
            self.update_counter()

            # Hide placeholder
            self.canvas.itemconfig(self.placeholder_text, state='hidden')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def update_display(self):
        """Update the display with current zoom"""
        if not self.current_image:
            return

        try:
            # Calculate display size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width < 10 or canvas_height < 10:
                # Canvas not ready yet
                self.root.after(100, self.update_display)
                return

            # Apply zoom
            img_width, img_height = self.current_image.size
            new_width = int(img_width * self.zoom_level)
            new_height = int(img_height * self.zoom_level)

            # Resize image
            resized = self.current_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

            # Convert to PhotoImage
            self.current_photo = ImageTk.PhotoImage(resized)

            # Center on canvas
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2

            self.canvas.coords(self.canvas_image, max(0, x), max(0, y))
            self.canvas.itemconfig(self.canvas_image, image=self.current_photo)

            # Update zoom label
            self.zoom_label.config(text=f"Zoom: {int(self.zoom_level * 100)}%")

        except Exception as e:
            print(f"Display error: {e}")

    def next_image(self):
        """Show next image"""
        if not self.image_files:
            return

        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.rotation = 0
        self.display_image()

    def previous_image(self):
        """Show previous image"""
        if not self.image_files:
            return

        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.rotation = 0
        self.display_image()

    def on_thumbnail_select(self, event):
        """Handle thumbnail selection"""
        selection = self.thumbnails_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.rotation = 0
            self.display_image()

    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 10.0)
        self.update_display()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.update_display()

    def fit_to_window(self):
        """Fit image to window"""
        if not self.current_image:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = self.current_image.size

        # Calculate zoom to fit
        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height

        self.zoom_level = min(width_ratio, height_ratio) * 0.95
        self.update_display()

    def rotate_image(self):
        """Rotate image 90 degrees"""
        if not self.current_image:
            return

        self.rotation = (self.rotation + 90) % 360
        self.display_image()

    def delete_image(self):
        """Delete current image"""
        if not self.image_files or self.current_index < 0:
            return

        image_path = self.image_files[self.current_index]
        filename = Path(image_path).name

        if messagebox.askyesno("Delete Image", f"Move '{filename}' to trash?"):
            try:
                # Move to trash (create trash folder in same directory)
                trash_dir = Path(image_path).parent / '.trash'
                trash_dir.mkdir(exist_ok=True)

                trash_path = trash_dir / filename
                shutil.move(image_path, trash_path)

                # Remove from list
                self.image_files.pop(self.current_index)
                self.thumbnails_listbox.delete(self.current_index)

                # Show next image or previous
                if self.image_files:
                    if self.current_index >= len(self.image_files):
                        self.current_index = len(self.image_files) - 1
                    self.display_image()
                else:
                    self.current_index = -1
                    self.canvas.itemconfig(self.placeholder_text, state='normal')

                self.status_label.config(text=f"Moved to trash: {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete image:\n{str(e)}")

    def toggle_slideshow(self):
        """Toggle slideshow mode"""
        if not self.image_files:
            messagebox.showwarning("No Images", "Load images first")
            return

        self.slideshow_active = not self.slideshow_active

        if self.slideshow_active:
            self.start_slideshow()
            self.status_label.config(text="Slideshow started")
        else:
            self.stop_slideshow()
            self.status_label.config(text="Slideshow stopped")

    def start_slideshow(self):
        """Start slideshow"""
        def advance():
            if self.slideshow_active:
                self.next_image()
                self.slideshow_job = self.root.after(self.slideshow_interval, advance)

        self.slideshow_job = self.root.after(self.slideshow_interval, advance)

    def stop_slideshow(self):
        """Stop slideshow"""
        if self.slideshow_job:
            self.root.after_cancel(self.slideshow_job)
            self.slideshow_job = None

    def change_interval(self, event=None):
        """Change slideshow interval"""
        try:
            interval = int(self.interval_var.get())
            self.slideshow_interval = interval * 1000  # Convert to milliseconds

            # Restart slideshow if active
            if self.slideshow_active:
                self.stop_slideshow()
                self.start_slideshow()

        except ValueError:
            pass

    def update_counter(self):
        """Update image counter"""
        if self.image_files:
            self.counter_label.config(text=f"{self.current_index + 1} / {len(self.image_files)}")
        else:
            self.counter_label.config(text="0 / 0")

    def add_to_recent_folders(self, folder):
        """Add folder to recent list"""
        if folder in self.recent_folders:
            self.recent_folders.remove(folder)

        self.recent_folders.insert(0, folder)
        self.recent_folders = self.recent_folders[:10]  # Keep last 10

        self.save_config()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.recent_folders = config.get('recent_folders', [])
                    self.slideshow_interval = config.get('slideshow_interval', 3000)

                # Update UI
                self.interval_var.set(str(self.slideshow_interval // 1000))

            except:
                pass

    def save_config(self):
        """Save configuration"""
        config = {
            'recent_folders': self.recent_folders,
            'slideshow_interval': self.slideshow_interval
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def run(self):
        """Run the image viewer"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        self.stop_slideshow()
        self.save_config()
        self.root.destroy()

def main():
    viewer = ImageViewer()
    viewer.run()

if __name__ == '__main__':
    main()
