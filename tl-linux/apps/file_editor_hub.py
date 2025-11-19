#!/usr/bin/env python3
"""
TL Linux - File Editor Hub
Central launcher for all file editing tools
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
from pathlib import Path

class FileEditorHub:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📂 TL File Editor Hub")
        self.root.geometry("900x600")
        self.root.configure(bg='#2c3e50')

        # Determine base path for editors
        self.base_path = Path(__file__).parent / "editors"

        self.editors = [
            {
                'name': 'Text & Markdown Editor',
                'icon': '📝',
                'description': 'Advanced text and markdown editor with live preview',
                'script': 'text_editor.py',
                'color': '#3498db',
                'file_types': '.txt .md .markdown'
            },
            {
                'name': 'Data Format Editor',
                'icon': '🗂️',
                'description': 'Edit JSON, XML, CSV, and YAML files',
                'script': 'data_editor.py',
                'color': '#2ecc71',
                'file_types': '.json .xml .csv .yaml .yml'
            },
            {
                'name': 'Spreadsheet Editor',
                'icon': '📊',
                'description': 'Spreadsheet with formulas and CSV support',
                'script': 'spreadsheet_editor.py',
                'color': '#27ae60',
                'file_types': '.csv'
            },
            {
                'name': 'Image Editor',
                'icon': '🖼️',
                'description': 'Basic image editing with filters and transforms',
                'script': 'image_editor.py',
                'color': '#9b59b6',
                'file_types': '.png .jpg .jpeg .gif .bmp'
            },
            {
                'name': 'Document Editor',
                'icon': '📄',
                'description': 'Rich text word processor with formatting',
                'script': 'document_editor.py',
                'color': '#e74c3c',
                'file_types': '.tldoc .txt'
            },
            {
                'name': 'PDF Viewer',
                'icon': '📕',
                'description': 'View and annotate PDF documents',
                'script': 'pdf_viewer.py',
                'color': '#c0392b',
                'file_types': '.pdf'
            }
        ]

        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#34495e', pady=20)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="📂 TL File Editor Hub",
            font=('Arial', 24, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Choose an editor to launch or open a file",
            font=('Arial', 11),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(5, 0))

        # Quick actions
        actions_frame = tk.Frame(self.root, bg='#2c3e50', pady=15)
        actions_frame.pack(fill=tk.X)

        tk.Button(
            actions_frame,
            text="📁 Open File...",
            command=self.open_file,
            bg='#3498db',
            fg='white',
            font=('Arial', 12),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            actions_frame,
            text="or select an editor below",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack(side=tk.LEFT, padx=10)

        # Editors grid
        editors_frame = tk.Frame(self.root, bg='#2c3e50')
        editors_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create cards in grid layout (2 columns)
        for idx, editor in enumerate(self.editors):
            row = idx // 2
            col = idx % 2

            card = self.create_editor_card(editors_frame, editor)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Configure grid weights for responsiveness
        editors_frame.grid_columnconfigure(0, weight=1)
        editors_frame.grid_columnconfigure(1, weight=1)
        for i in range((len(self.editors) + 1) // 2):
            editors_frame.grid_rowconfigure(i, weight=1)

        # Footer
        footer = tk.Frame(self.root, bg='#34495e', pady=10)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(
            footer,
            text="TL Linux File Editor Hub • All editors are free and open source",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6'
        ).pack()

    def create_editor_card(self, parent, editor):
        """Create editor card"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        card.configure(highlightbackground='#bdc3c7', highlightthickness=1)

        # Header with icon and color
        card_header = tk.Frame(card, bg=editor['color'], height=60)
        card_header.pack(fill=tk.X)
        card_header.pack_propagate(False)

        tk.Label(
            card_header,
            text=editor['icon'],
            font=('Arial', 32),
            bg=editor['color'],
            fg='white'
        ).pack(expand=True)

        # Content
        content = tk.Frame(card, bg='white', padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            content,
            text=editor['name'],
            font=('Arial', 13, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w')

        tk.Label(
            content,
            text=editor['description'],
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d',
            wraplength=250,
            justify='left'
        ).pack(anchor='w', pady=(5, 10))

        tk.Label(
            content,
            text=f"File types: {editor['file_types']}",
            font=('Arial', 8),
            bg='white',
            fg='#95a5a6'
        ).pack(anchor='w', pady=(0, 10))

        # Launch button
        btn = tk.Button(
            content,
            text="Launch",
            command=lambda e=editor: self.launch_editor(e),
            bg=editor['color'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        btn.pack(fill=tk.X)

        # Hover effects
        def on_enter(e):
            card.configure(highlightbackground=editor['color'], highlightthickness=2)
            btn.configure(bg=self.darken_color(editor['color']))

        def on_leave(e):
            card.configure(highlightbackground='#bdc3c7', highlightthickness=1)
            btn.configure(bg=editor['color'])

        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        for child in card.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)

        return card

    def darken_color(self, hex_color):
        """Darken a hex color"""
        # Simple darkening by reducing RGB values
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'

    def launch_editor(self, editor):
        """Launch an editor"""
        script_path = self.base_path / editor['script']

        if not script_path.exists():
            messagebox.showerror(
                "Editor Not Found",
                f"Could not find editor script:\n{script_path}\n\n"
                "Please ensure all editor files are properly installed."
            )
            return

        try:
            # Launch editor in new process
            subprocess.Popen([sys.executable, str(script_path)])
            self.update_status(f"Launched {editor['name']}")

        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch editor:\n{e}")

    def open_file(self):
        """Open file with appropriate editor"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt *.md"),
                ("Data files", "*.json *.xml *.csv *.yaml"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.tldoc"),
                ("PDF files", "*.pdf")
            ]
        )

        if file_path:
            file_ext = Path(file_path).suffix.lower()

            # Find appropriate editor
            editor_found = False
            for editor in self.editors:
                if file_ext in editor['file_types']:
                    script_path = self.base_path / editor['script']

                    if script_path.exists():
                        try:
                            # Launch editor with file
                            # Note: Current editors don't support command-line args,
                            # so we just launch them. User will need to open file manually.
                            subprocess.Popen([sys.executable, str(script_path)])
                            messagebox.showinfo(
                                "Editor Launched",
                                f"Launched {editor['name']}\n\n"
                                f"Please open the file from within the editor:\n{file_path}"
                            )
                            editor_found = True
                            break
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not launch editor:\n{e}")
                            return

            if not editor_found:
                messagebox.showwarning(
                    "No Editor Found",
                    f"No suitable editor found for file type: {file_ext}\n\n"
                    "You can still launch an editor manually from the hub."
                )

    def update_status(self, message):
        """Update status (could be shown in status bar if added)"""
        # For now, just print to console
        print(f"Status: {message}")

    def run(self):
        """Run hub"""
        self.root.mainloop()

def main():
    """Main entry point"""
    hub = FileEditorHub()
    hub.run()

if __name__ == '__main__':
    main()
