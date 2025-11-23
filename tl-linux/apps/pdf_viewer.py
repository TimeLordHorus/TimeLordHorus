#!/usr/bin/env python3
"""
TL Linux - PDF Viewer
PDF document viewer with navigation and search
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
from pathlib import Path
import json
import tempfile
import shutil

class PDFViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - PDF Viewer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')

        # Configuration
        self.config_dir = Path.home() / '.tl-linux'
        self.config_file = self.config_dir / 'pdf_viewer_config.json'
        self.config_dir.mkdir(exist_ok=True)

        # PDF state
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.page_images = {}
        self.temp_dir = None

        # Recent files
        self.recent_files = []

        # Check for required tools
        self.has_poppler = self.check_command('pdftoppm')
        self.has_pdfinfo = self.check_command('pdfinfo')

        self.load_config()
        self.setup_ui()

        # Keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.previous_page())
        self.root.bind('<Right>', lambda e: self.next_page())
        self.root.bind('<Home>', lambda e: self.first_page())
        self.root.bind('<End>', lambda e: self.last_page())
        self.root.bind('<plus>', lambda e: self.zoom_in())
        self.root.bind('<minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-f>', lambda e: self.show_search())

    def check_command(self, command):
        """Check if a command is available"""
        try:
            subprocess.run(
                ['which', command],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📄 PDF Viewer",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(header, bg='#2b2b2b')
        toolbar.pack(side=tk.RIGHT, padx=20)

        tk.Button(
            toolbar,
            text="📂 Open PDF",
            command=self.open_pdf,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text="🔍 Search",
            command=self.show_search,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text="🖨 Print",
            command=self.print_pdf,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel - Page thumbnails
        left_panel = tk.Frame(main_container, bg='#1a1a1a', width=180)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="Pages",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(0, 10))

        # Page list
        pages_frame = tk.Frame(left_panel, bg='#1a1a1a')
        pages_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(pages_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.pages_listbox = tk.Listbox(
            pages_frame,
            bg='#2b2b2b',
            fg='white',
            selectbackground='#4a9eff',
            selectforeground='white',
            font=('Arial', 9),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.pages_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pages_listbox.yview)

        self.pages_listbox.bind('<<ListboxSelect>>', self.on_page_select)

        # Recent files
        tk.Label(
            left_panel,
            text="Recent",
            font=('Arial', 11, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(15, 5))

        recent_frame = tk.Frame(left_panel, bg='#1a1a1a')
        recent_frame.pack(fill=tk.BOTH)

        self.recent_listbox = tk.Listbox(
            recent_frame,
            bg='#2b2b2b',
            fg='#888888',
            selectbackground='#4a9eff',
            selectforeground='white',
            font=('Arial', 8),
            bd=0,
            highlightthickness=0,
            height=5
        )
        self.recent_listbox.pack(fill=tk.BOTH)

        self.recent_listbox.bind('<Double-Button-1>', lambda e: self.open_recent())

        # Update recent display
        self.update_recent_display()

        # Right panel - PDF display
        right_panel = tk.Frame(main_container, bg='#1a1a1a')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # PDF info
        info_frame = tk.Frame(right_panel, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.pdf_title_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white',
            anchor='w'
        )
        self.pdf_title_label.pack(fill=tk.X)

        self.pdf_info_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888',
            anchor='w'
        )
        self.pdf_info_label.pack(fill=tk.X)

        # PDF canvas
        canvas_frame = tk.Frame(right_panel, bg='#1a1a1a')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#2b2b2b',
            highlightthickness=0,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)

        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW)

        # Placeholder
        self.placeholder_text = self.canvas.create_text(
            400, 300,
            text="No PDF loaded\n\nClick 'Open PDF' to select a document",
            font=('Arial', 14),
            fill='#888888',
            justify=tk.CENTER
        )

        # Navigation controls
        nav_frame = tk.Frame(right_panel, bg='#1a1a1a')
        nav_frame.pack(pady=10)

        tk.Button(
            nav_frame,
            text="⏮ First",
            command=self.first_page,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=12,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav_frame,
            text="◀ Previous",
            command=self.previous_page,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=12,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        # Page input
        page_input_frame = tk.Frame(nav_frame, bg='#1a1a1a')
        page_input_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(
            page_input_frame,
            text="Page:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.page_var = tk.StringVar(value="0")
        page_entry = tk.Entry(
            page_input_frame,
            textvariable=self.page_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            bd=0,
            width=5,
            justify=tk.CENTER
        )
        page_entry.pack(side=tk.LEFT, ipady=3)
        page_entry.bind('<Return>', lambda e: self.go_to_page())

        self.page_count_label = tk.Label(
            page_input_frame,
            text="/ 0",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        )
        self.page_count_label.pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(
            nav_frame,
            text="Next ▶",
            command=self.next_page,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=12,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav_frame,
            text="Last ⏭",
            command=self.last_page,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=12,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        # Zoom controls
        zoom_frame = tk.Frame(right_panel, bg='#1a1a1a')
        zoom_frame.pack()

        tk.Button(
            zoom_frame,
            text="🔍+ Zoom In",
            command=self.zoom_in,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            zoom_frame,
            text="🔍- Zoom Out",
            command=self.zoom_out,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            zoom_frame,
            text="⛶ Fit Width",
            command=self.fit_width,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            zoom_frame,
            text="⛶ Fit Page",
            command=self.fit_page,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

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

    def open_pdf(self):
        """Open a PDF file"""
        filetypes = [
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=filetypes
        )

        if filename:
            self.load_pdf(filename)

    def load_pdf(self, filepath):
        """Load a PDF file"""
        if not self.has_poppler:
            messagebox.showerror(
                "Missing Dependency",
                "Poppler utilities are not installed.\n\n"
                "Install with:\nsudo apt install poppler-utils"
            )
            return

        try:
            # Clean up previous temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

            # Create new temp directory
            self.temp_dir = tempfile.mkdtemp(prefix='tl-pdf-')

            # Get PDF info
            if self.has_pdfinfo:
                result = subprocess.run(
                    ['pdfinfo', filepath],
                    capture_output=True,
                    text=True
                )

                # Parse page count
                for line in result.stdout.split('\n'):
                    if 'Pages:' in line:
                        self.total_pages = int(line.split(':')[1].strip())
                        break

            if self.total_pages == 0:
                # Fallback: try to render pages until we fail
                self.total_pages = 1

            # Update UI
            self.current_pdf = filepath
            self.current_page = 1
            self.page_images.clear()

            self.pdf_title_label.config(text=Path(filepath).name)

            file_size = os.path.getsize(filepath) / 1024  # KB
            if file_size > 1024:
                size_str = f"{file_size / 1024:.1f} MB"
            else:
                size_str = f"{file_size:.1f} KB"

            self.pdf_info_label.config(
                text=f"{self.total_pages} pages | {size_str}"
            )

            # Update pages list
            self.pages_listbox.delete(0, tk.END)
            for i in range(1, self.total_pages + 1):
                self.pages_listbox.insert(tk.END, f"Page {i}")

            # Update page counter
            self.page_count_label.config(text=f"/ {self.total_pages}")

            # Add to recent
            self.add_to_recent(filepath)

            # Display first page
            self.display_page()

            # Hide placeholder
            self.canvas.itemconfig(self.placeholder_text, state='hidden')

            self.status_label.config(text=f"Loaded: {Path(filepath).name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF:\n{str(e)}")

    def display_page(self):
        """Display the current page"""
        if not self.current_pdf or self.current_page < 1:
            return

        try:
            # Check if page is already rendered
            page_key = f"{self.current_page}_{int(self.zoom_level * 100)}"

            if page_key not in self.page_images:
                # Render page to image
                dpi = int(72 * self.zoom_level)

                output_file = os.path.join(self.temp_dir, f"page_{self.current_page}")

                result = subprocess.run(
                    [
                        'pdftoppm',
                        '-f', str(self.current_page),
                        '-l', str(self.current_page),
                        '-r', str(dpi),
                        '-png',
                        self.current_pdf,
                        output_file
                    ],
                    capture_output=True,
                    timeout=30
                )

                # Find generated image
                image_path = f"{output_file}-{self.current_page}.png"

                if not os.path.exists(image_path):
                    # Try alternative naming
                    image_path = f"{output_file}-1.png"

                if os.path.exists(image_path):
                    # Load image
                    img = Image.open(image_path)
                    self.page_images[page_key] = ImageTk.PhotoImage(img)
                else:
                    raise Exception("Failed to render page")

            # Display image
            photo = self.page_images[page_key]
            self.canvas.itemconfig(self.canvas_image, image=photo)

            # Update canvas scroll region
            self.canvas.config(scrollregion=self.canvas.bbox(self.canvas_image))

            # Update UI
            self.page_var.set(str(self.current_page))

            self.pages_listbox.selection_clear(0, tk.END)
            self.pages_listbox.selection_set(self.current_page - 1)
            self.pages_listbox.see(self.current_page - 1)

            self.zoom_label.config(text=f"Zoom: {int(self.zoom_level * 100)}%")

            self.status_label.config(text=f"Page {self.current_page} of {self.total_pages}")

        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Page rendering timed out")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page:\n{str(e)}")

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_page()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()

    def first_page(self):
        """Go to first page"""
        if self.current_page != 1:
            self.current_page = 1
            self.display_page()

    def last_page(self):
        """Go to last page"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.display_page()

    def go_to_page(self):
        """Go to specific page"""
        try:
            page = int(self.page_var.get())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self.display_page()
            else:
                messagebox.showwarning("Invalid Page", f"Page must be between 1 and {self.total_pages}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")

    def on_page_select(self, event):
        """Handle page selection from list"""
        selection = self.pages_listbox.curselection()
        if selection:
            self.current_page = selection[0] + 1
            self.display_page()

    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.25, 5.0)
        self.page_images.clear()  # Clear cache
        self.display_page()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.25, 0.25)
        self.page_images.clear()  # Clear cache
        self.display_page()

    def fit_width(self):
        """Fit page to canvas width"""
        # This is a simplified version
        self.zoom_level = 1.5
        self.page_images.clear()
        self.display_page()

    def fit_page(self):
        """Fit entire page in canvas"""
        self.zoom_level = 1.0
        self.page_images.clear()
        self.display_page()

    def show_search(self):
        """Show search dialog"""
        if not self.current_pdf:
            messagebox.showwarning("No PDF", "Load a PDF first")
            return

        # Simple search dialog
        search_window = tk.Toplevel(self.root)
        search_window.title("Search PDF")
        search_window.geometry("400x150")
        search_window.configure(bg='#1a1a1a')

        tk.Label(
            search_window,
            text="Search text:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11)
        ).pack(pady=(20, 5))

        search_var = tk.StringVar()
        tk.Entry(
            search_window,
            textvariable=search_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            font=('Arial', 11),
            bd=0
        ).pack(pady=5, padx=20, fill=tk.X, ipady=5)

        def do_search():
            search_term = search_var.get()
            if search_term:
                messagebox.showinfo(
                    "Search",
                    "Text search requires pdfgrep.\n\n"
                    "Install with:\nsudo apt install pdfgrep\n\n"
                    "Then use: pdfgrep '" + search_term + "' in terminal"
                )
                search_window.destroy()

        tk.Button(
            search_window,
            text="Search",
            command=do_search,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10)
        ).pack(pady=20)

    def print_pdf(self):
        """Print the PDF"""
        if not self.current_pdf:
            messagebox.showwarning("No PDF", "Load a PDF first")
            return

        try:
            # Use lpr command
            subprocess.run(['lpr', self.current_pdf])
            self.status_label.config(text="Sent to printer")
        except FileNotFoundError:
            messagebox.showerror(
                "Print Error",
                "Print command not found.\n\n"
                "Install CUPS:\nsudo apt install cups"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print:\n{str(e)}")

    def open_recent(self):
        """Open recent PDF"""
        selection = self.recent_listbox.curselection()
        if selection:
            pdf_path = self.recent_files[selection[0]]
            if os.path.exists(pdf_path):
                self.load_pdf(pdf_path)
            else:
                messagebox.showwarning("File Not Found", "PDF file no longer exists")
                self.recent_files.pop(selection[0])
                self.update_recent_display()

    def add_to_recent(self, filepath):
        """Add PDF to recent list"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)

        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:10]  # Keep last 10

        self.update_recent_display()
        self.save_config()

    def update_recent_display(self):
        """Update recent files display"""
        self.recent_listbox.delete(0, tk.END)

        for pdf_path in self.recent_files:
            self.recent_listbox.insert(tk.END, Path(pdf_path).name)

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.recent_files = config.get('recent_files', [])
            except:
                pass

    def save_config(self):
        """Save configuration"""
        config = {
            'recent_files': self.recent_files
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def run(self):
        """Run the PDF viewer"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        # Clean up temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

        self.save_config()
        self.root.destroy()

def main():
    viewer = PDFViewer()
    viewer.run()

if __name__ == '__main__':
    main()
