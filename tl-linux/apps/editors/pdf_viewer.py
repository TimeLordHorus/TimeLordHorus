#!/usr/bin/env python3
"""
TL Linux - PDF Viewer and Annotator
View and annotate PDF files with PyMuPDF
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
import io

try:
    import fitz  # PyMuPDF
    from PIL import Image, ImageTk
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

class PDFViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📕 TL PDF Viewer")
        self.root.geometry("1000x700")

        if not HAS_PYMUPDF:
            messagebox.showerror(
                "Missing Dependency",
                "PyMuPDF (fitz) is required for PDF viewing.\n\n"
                "Install with: pip install PyMuPDF pillow"
            )
            self.show_installation_guide()
            return

        self.current_file = None
        self.pdf_document = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.display_image = None
        self.annotation_mode = None
        self.annotation_color = (1, 1, 0)  # Yellow

        self.setup_ui()

    def show_installation_guide(self):
        """Show installation guide when PyMuPDF is missing"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Installation Required")
        guide_window.geometry("600x400")

        text = tk.Text(guide_window, wrap=tk.WORD, padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)

        guide_text = """PDF Viewer Installation Guide

The TL PDF Viewer requires PyMuPDF (also called 'fitz') to function.

Installation Steps:

1. Open a terminal

2. Install PyMuPDF:
   pip install PyMuPDF pillow

   OR if using system Python:
   sudo apt-get install python3-pip
   pip3 install PyMuPDF pillow

3. Restart the PDF Viewer

Features (once installed):
• View PDF documents
• Navigate pages
• Zoom in/out
• Search text
• Add annotations (highlights, text notes)
• Save annotated PDFs
• Export pages as images

For more information, visit:
https://pymupdf.readthedocs.io/
"""

        text.insert('1.0', guide_text)
        text.config(state=tk.DISABLED)

        tk.Button(guide_window, text="Close", command=guide_window.destroy, padx=20, pady=10).pack(pady=10)

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF", command=self.open_pdf, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Annotated PDF", command=self.save_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Export Page as Image", command=self.export_page_image)
        file_menu.add_separator()
        file_menu.add_command(label="Close PDF", command=self.close_pdf)
        file_menu.add_command(label="Exit", command=self.root.destroy)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Actual Size", command=self.zoom_actual, accelerator="Ctrl+0")
        view_menu.add_command(label="Fit Width", command=self.fit_width)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Search", command=self.show_search, accelerator="Ctrl+F")
        tools_menu.add_separator()
        tools_menu.add_command(label="Highlight Tool", command=lambda: self.set_annotation_mode('highlight'))
        tools_menu.add_command(label="Text Note Tool", command=lambda: self.set_annotation_mode('text'))

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2c3e50', pady=8)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="📁 Open PDF", command=self.open_pdf, bg='#34495e', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 Save", command=self.save_pdf, bg='#34495e', fg='white', relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Navigation
        tk.Button(toolbar, text="⟨ Prev", command=self.prev_page, bg='#34495e', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        self.page_label = tk.Label(toolbar, text="Page 0/0", bg='#2c3e50', fg='white', font=('Arial', 10))
        self.page_label.pack(side=tk.LEFT, padx=10)

        tk.Button(toolbar, text="Next ⟩", command=self.next_page, bg='#34495e', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        tk.Label(toolbar, text="Go to:", bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=5)
        self.page_entry = tk.Entry(toolbar, width=6)
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind('<Return>', lambda e: self.goto_page())

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Zoom controls
        tk.Button(toolbar, text="🔍-", command=self.zoom_out, bg='#34495e', fg='white', relief=tk.FLAT, width=4).pack(side=tk.LEFT, padx=2)

        self.zoom_label = tk.Label(toolbar, text="100%", bg='#2c3e50', fg='white', font=('Arial', 10), width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="🔍+", command=self.zoom_in, bg='#34495e', fg='white', relief=tk.FLAT, width=4).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Search
        tk.Button(toolbar, text="🔎 Search", command=self.show_search, bg='#34495e', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        # Main content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Page thumbnails (simplified)
        pages_frame = tk.Frame(main_frame, bg='#ecf0f1', width=150)
        pages_frame.pack(side=tk.LEFT, fill=tk.Y)
        pages_frame.pack_propagate(False)

        tk.Label(pages_frame, text="Pages", bg='#ecf0f1', font=('Arial', 10, 'bold'), pady=10).pack()

        self.pages_listbox = tk.Listbox(pages_frame, bg='white')
        self.pages_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.pages_listbox.bind('<<ListboxSelect>>', self.on_page_select)

        # Canvas for PDF display
        canvas_frame = tk.Frame(main_frame, bg='#34495e')
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#2c3e50',
            highlightthickness=0,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)

        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-f>', lambda e: self.show_search())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_actual())
        self.root.bind('<Left>', lambda e: self.prev_page())
        self.root.bind('<Right>', lambda e: self.next_page())

        # Status bar
        self.status_bar = tk.Label(self.root, text="No PDF loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_pdf(self):
        """Open PDF file"""
        file_path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Close previous PDF if open
                if self.pdf_document:
                    self.pdf_document.close()

                self.pdf_document = fitz.open(file_path)
                self.current_file = Path(file_path)
                self.current_page = 0

                # Populate pages list
                self.pages_listbox.delete(0, tk.END)
                for i in range(len(self.pdf_document)):
                    self.pages_listbox.insert(tk.END, f"Page {i+1}")

                self.display_page()
                self.status_bar.config(text=f"Opened: {self.current_file.name} ({len(self.pdf_document)} pages)")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF:\n{e}")

    def close_pdf(self):
        """Close current PDF"""
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
            self.current_file = None
            self.canvas.delete('all')
            self.pages_listbox.delete(0, tk.END)
            self.page_label.config(text="Page 0/0")
            self.status_bar.config(text="PDF closed")

    def save_pdf(self):
        """Save annotated PDF"""
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Annotated PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if file_path:
            try:
                self.pdf_document.save(file_path)
                messagebox.showinfo("Saved", "PDF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF:\n{e}")

    def display_page(self):
        """Display current page"""
        if not self.pdf_document:
            return

        try:
            page = self.pdf_document[self.current_page]

            # Render page to image
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert to PhotoImage
            self.display_image = ImageTk.PhotoImage(img)

            # Display on canvas
            self.canvas.delete('all')
            self.canvas.create_image(0, 0, anchor='nw', image=self.display_image)

            # Update scroll region
            self.canvas.config(scrollregion=self.canvas.bbox('all'))

            # Update page label
            self.page_label.config(text=f"Page {self.current_page + 1}/{len(self.pdf_document)}")
            self.pages_listbox.selection_clear(0, tk.END)
            self.pages_listbox.selection_set(self.current_page)
            self.pages_listbox.see(self.current_page)

        except Exception as e:
            messagebox.showerror("Error", f"Could not display page:\n{e}")

    def next_page(self):
        """Go to next page"""
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.display_page()

    def prev_page(self):
        """Go to previous page"""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def goto_page(self):
        """Go to specific page"""
        if not self.pdf_document:
            return

        try:
            page_num = int(self.page_entry.get()) - 1
            if 0 <= page_num < len(self.pdf_document):
                self.current_page = page_num
                self.display_page()
            else:
                messagebox.showerror("Error", f"Page must be between 1 and {len(self.pdf_document)}")
        except ValueError:
            messagebox.showerror("Error", "Invalid page number")

    def on_page_select(self, event):
        """Handle page selection from listbox"""
        selection = self.pages_listbox.curselection()
        if selection:
            self.current_page = selection[0]
            self.display_page()

    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level + 0.25, 5.0)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.display_page()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level - 0.25, 0.25)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.display_page()

    def zoom_actual(self):
        """Zoom to actual size (100%)"""
        self.zoom_level = 1.0
        self.zoom_label.config(text="100%")
        self.display_page()

    def fit_width(self):
        """Fit page width to window"""
        if not self.pdf_document:
            return

        canvas_width = self.canvas.winfo_width()
        page = self.pdf_document[self.current_page]
        page_width = page.rect.width

        self.zoom_level = canvas_width / page_width * 0.95
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.display_page()

    def set_annotation_mode(self, mode):
        """Set annotation mode"""
        self.annotation_mode = mode
        self.status_bar.config(text=f"Annotation mode: {mode}")

    def show_search(self):
        """Show search dialog"""
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Search PDF")
        dialog.geometry("400x100")
        dialog.transient(self.root)

        tk.Label(dialog, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        search_entry = tk.Entry(dialog, width=40)
        search_entry.grid(row=0, column=1, padx=5, pady=5)

        def search():
            query = search_entry.get()
            if query:
                found = False
                for page_num in range(len(self.pdf_document)):
                    page = self.pdf_document[page_num]
                    text_instances = page.search_for(query)
                    if text_instances:
                        self.current_page = page_num
                        self.display_page()
                        found = True
                        self.status_bar.config(text=f"Found '{query}' on page {page_num + 1}")
                        break

                if not found:
                    messagebox.showinfo("Search", f"'{query}' not found")

        tk.Button(dialog, text="Search", command=search, padx=20).grid(row=1, column=0, columnspan=2, pady=10)

    def export_page_image(self):
        """Export current page as image"""
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Page as Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )

        if file_path:
            try:
                page = self.pdf_document[self.current_page]
                mat = fitz.Matrix(2.0, 2.0)  # High resolution
                pix = page.get_pixmap(matrix=mat)
                pix.save(file_path)
                messagebox.showinfo("Exported", f"Page {self.current_page + 1} exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export page:\n{e}")

    def run(self):
        """Run viewer"""
        self.root.mainloop()

if __name__ == '__main__':
    viewer = PDFViewer()
    viewer.run()
