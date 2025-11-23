#!/usr/bin/env python3
"""
TL Linux - Document Editor (Word Processor)
Rich text document editing with formatting
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font, colorchooser
from pathlib import Path
import json

class DocumentEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📝 TL Document Editor")
        self.root.geometry("1000x700")

        self.current_file = None
        self.current_font_family = "Arial"
        self.current_font_size = 12
        self.is_bold = False
        self.is_italic = False
        self.is_underline = False

        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_document, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_document, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_document, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_document)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Plain Text", command=self.export_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find & Replace", command=self.show_find_replace, accelerator="Ctrl+F")

        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=self.toggle_bold, accelerator="Ctrl+B")
        format_menu.add_command(label="Italic", command=self.toggle_italic, accelerator="Ctrl+I")
        format_menu.add_command(label="Underline", command=self.toggle_underline, accelerator="Ctrl+U")
        format_menu.add_separator()
        format_menu.add_command(label="Text Color", command=self.change_text_color)
        format_menu.add_command(label="Highlight Color", command=self.change_highlight_color)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Word Count", command=self.show_word_count)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#f0f0f0', pady=5)
        toolbar.pack(fill=tk.X)

        # File operations
        tk.Button(toolbar, text="📄 New", command=self.new_document, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📁 Open", command=self.open_document, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="💾 Save", command=self.save_document, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=8, fill=tk.Y)

        # Font family
        tk.Label(toolbar, text="Font:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.font_family_var = tk.StringVar(value="Arial")
        font_families = list(font.families())
        common_fonts = ["Arial", "Times New Roman", "Courier New", "Georgia", "Verdana", "Comic Sans MS"]
        available_fonts = [f for f in common_fonts if f in font_families] + ["Helvetica", "Times"]

        self.font_combo = ttk.Combobox(toolbar, textvariable=self.font_family_var, values=available_fonts, width=15, state='readonly')
        self.font_combo.pack(side=tk.LEFT, padx=2)
        self.font_combo.bind('<<ComboboxSelected>>', self.change_font)

        # Font size
        tk.Label(toolbar, text="Size:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.font_size_var = tk.StringVar(value="12")
        font_sizes = [str(s) for s in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]]

        self.size_combo = ttk.Combobox(toolbar, textvariable=self.font_size_var, values=font_sizes, width=5, state='readonly')
        self.size_combo.pack(side=tk.LEFT, padx=2)
        self.size_combo.bind('<<ComboboxSelected>>', self.change_font_size)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=8, fill=tk.Y)

        # Format buttons
        self.bold_btn = tk.Button(toolbar, text="B", command=self.toggle_bold, relief=tk.RAISED, font=('Arial', 10, 'bold'), width=3)
        self.bold_btn.pack(side=tk.LEFT, padx=2)

        self.italic_btn = tk.Button(toolbar, text="I", command=self.toggle_italic, relief=tk.RAISED, font=('Arial', 10, 'italic'), width=3)
        self.italic_btn.pack(side=tk.LEFT, padx=2)

        self.underline_btn = tk.Button(toolbar, text="U", command=self.toggle_underline, relief=tk.RAISED, font=('Arial', 10, 'underline'), width=3)
        self.underline_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=8, fill=tk.Y)

        # Color buttons
        tk.Button(toolbar, text="🎨 Color", command=self.change_text_color, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🖍️ Highlight", command=self.change_highlight_color, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=8, fill=tk.Y)

        # Alignment buttons
        tk.Button(toolbar, text="⬅️", command=lambda: self.align_text('left'), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="⬛", command=lambda: self.align_text('center'), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="➡️", command=lambda: self.align_text('right'), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=8, fill=tk.Y)

        # List buttons
        tk.Button(toolbar, text="• List", command=self.insert_bullet, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)

        # Text editor
        editor_frame = tk.Frame(self.root)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = tk.Scrollbar(editor_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        self.text_editor = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=(self.current_font_family, self.current_font_size),
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_editor.yview)

        # Configure tags for formatting
        self.text_editor.tag_configure('bold', font=(self.current_font_family, self.current_font_size, 'bold'))
        self.text_editor.tag_configure('italic', font=(self.current_font_family, self.current_font_size, 'italic'))
        self.text_editor.tag_configure('underline', underline=True)
        self.text_editor.tag_configure('left', justify='left')
        self.text_editor.tag_configure('center', justify='center')
        self.text_editor.tag_configure('right', justify='right')

        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_document())
        self.root.bind('<Control-o>', lambda e: self.open_document())
        self.root.bind('<Control-s>', lambda e: self.save_document())
        self.root.bind('<Control-b>', lambda e: self.toggle_bold())
        self.root.bind('<Control-i>', lambda e: self.toggle_italic())
        self.root.bind('<Control-u>', lambda e: self.toggle_underline())
        self.root.bind('<Control-f>', lambda e: self.show_find_replace())

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready - Words: 0 | Characters: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Update word count on text change
        self.text_editor.bind('<<Modified>>', self.on_text_modified)

    def on_text_modified(self, event=None):
        """Handle text modification"""
        if self.text_editor.edit_modified():
            self.update_word_count()
            self.text_editor.edit_modified(False)

    def update_word_count(self):
        """Update word count in status bar"""
        content = self.text_editor.get('1.0', 'end-1c')
        words = len(content.split())
        chars = len(content)
        file_name = self.current_file.name if self.current_file else "Untitled"
        self.status_bar.config(text=f"{file_name} - Words: {words} | Characters: {chars}")

    def new_document(self):
        """Create new document"""
        if self.text_editor.get('1.0', 'end-1c').strip():
            if messagebox.askyesno("New Document", "Discard current document?"):
                self.text_editor.delete('1.0', tk.END)
                self.current_file = None
                self.update_word_count()
        else:
            self.text_editor.delete('1.0', tk.END)
            self.current_file = None
            self.update_word_count()

    def open_document(self):
        """Open document"""
        file_path = filedialog.askopenfilename(
            title="Open Document",
            filetypes=[
                ("TL Document", "*.tldoc"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.tldoc'):
                        # Load formatted document
                        data = json.load(f)
                        self.text_editor.delete('1.0', tk.END)
                        self.text_editor.insert('1.0', data.get('content', ''))
                        # TODO: Restore formatting from data['formatting']
                    else:
                        # Load plain text
                        content = f.read()
                        self.text_editor.delete('1.0', tk.END)
                        self.text_editor.insert('1.0', content)

                self.current_file = Path(file_path)
                self.update_word_count()

            except Exception as e:
                messagebox.showerror("Error", f"Could not open document:\n{e}")

    def save_document(self):
        """Save document"""
        if self.current_file:
            self.save_to_file(str(self.current_file))
        else:
            self.save_as_document()

    def save_as_document(self):
        """Save document as new file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Document As",
            defaultextension=".tldoc",
            filetypes=[
                ("TL Document", "*.tldoc"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Save to specific file"""
        try:
            content = self.text_editor.get('1.0', 'end-1c')

            if file_path.endswith('.tldoc'):
                # Save with formatting info
                data = {
                    'content': content,
                    'formatting': {},  # TODO: Store tag information
                    'metadata': {
                        'font_family': self.current_font_family,
                        'font_size': self.current_font_size
                    }
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                # Save as plain text
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            self.current_file = Path(file_path)
            self.update_word_count()
            messagebox.showinfo("Saved", "Document saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save document:\n{e}")

    def export_txt(self):
        """Export to plain text"""
        file_path = filedialog.asksaveasfilename(
            title="Export to Plain Text",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )

        if file_path:
            try:
                content = self.text_editor.get('1.0', 'end-1c')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Exported", "Document exported as plain text!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export:\n{e}")

    def undo(self):
        """Undo"""
        try:
            self.text_editor.edit_undo()
        except:
            pass

    def redo(self):
        """Redo"""
        try:
            self.text_editor.edit_redo()
        except:
            pass

    def cut(self):
        """Cut"""
        try:
            self.text_editor.event_generate("<<Cut>>")
        except:
            pass

    def copy(self):
        """Copy"""
        try:
            self.text_editor.event_generate("<<Copy>>")
        except:
            pass

    def paste(self):
        """Paste"""
        try:
            self.text_editor.event_generate("<<Paste>>")
        except:
            pass

    def select_all(self):
        """Select all text"""
        self.text_editor.tag_add('sel', '1.0', 'end')

    def toggle_bold(self):
        """Toggle bold"""
        try:
            current_tags = self.text_editor.tag_names('sel.first')
            if 'bold' in current_tags:
                self.text_editor.tag_remove('bold', 'sel.first', 'sel.last')
                self.bold_btn.config(relief=tk.RAISED, bg='SystemButtonFace')
            else:
                self.text_editor.tag_add('bold', 'sel.first', 'sel.last')
                self.bold_btn.config(relief=tk.SUNKEN, bg='#e0e0e0')
        except:
            pass

    def toggle_italic(self):
        """Toggle italic"""
        try:
            current_tags = self.text_editor.tag_names('sel.first')
            if 'italic' in current_tags:
                self.text_editor.tag_remove('italic', 'sel.first', 'sel.last')
                self.italic_btn.config(relief=tk.RAISED, bg='SystemButtonFace')
            else:
                self.text_editor.tag_add('italic', 'sel.first', 'sel.last')
                self.italic_btn.config(relief=tk.SUNKEN, bg='#e0e0e0')
        except:
            pass

    def toggle_underline(self):
        """Toggle underline"""
        try:
            current_tags = self.text_editor.tag_names('sel.first')
            if 'underline' in current_tags:
                self.text_editor.tag_remove('underline', 'sel.first', 'sel.last')
                self.underline_btn.config(relief=tk.RAISED, bg='SystemButtonFace')
            else:
                self.text_editor.tag_add('underline', 'sel.first', 'sel.last')
                self.underline_btn.config(relief=tk.SUNKEN, bg='#e0e0e0')
        except:
            pass

    def change_font(self, event=None):
        """Change font family"""
        self.current_font_family = self.font_family_var.get()
        self.text_editor.config(font=(self.current_font_family, self.current_font_size))

    def change_font_size(self, event=None):
        """Change font size"""
        self.current_font_size = int(self.font_size_var.get())
        self.text_editor.config(font=(self.current_font_family, self.current_font_size))

    def change_text_color(self):
        """Change text color"""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:
            try:
                tag_name = f"color_{color[1]}"
                self.text_editor.tag_configure(tag_name, foreground=color[1])
                self.text_editor.tag_add(tag_name, 'sel.first', 'sel.last')
            except:
                pass

    def change_highlight_color(self):
        """Change highlight color"""
        color = colorchooser.askcolor(title="Choose Highlight Color")
        if color[1]:
            try:
                tag_name = f"highlight_{color[1]}"
                self.text_editor.tag_configure(tag_name, background=color[1])
                self.text_editor.tag_add(tag_name, 'sel.first', 'sel.last')
            except:
                pass

    def align_text(self, alignment):
        """Align text"""
        try:
            # Remove other alignment tags
            self.text_editor.tag_remove('left', '1.0', 'end')
            self.text_editor.tag_remove('center', '1.0', 'end')
            self.text_editor.tag_remove('right', '1.0', 'end')

            # Add new alignment
            self.text_editor.tag_add(alignment, 'sel.first', 'sel.last')
        except:
            pass

    def insert_bullet(self):
        """Insert bullet point"""
        self.text_editor.insert(tk.INSERT, '• ')

    def show_find_replace(self):
        """Show find and replace dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Find & Replace")
        dialog.geometry("400x150")
        dialog.transient(self.root)

        tk.Label(dialog, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        find_entry = tk.Entry(dialog, width=40)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        replace_entry = tk.Entry(dialog, width=40)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        def find_next():
            search_term = find_entry.get()
            if search_term:
                # Remove previous highlight
                self.text_editor.tag_remove('search', '1.0', tk.END)

                # Search from current position
                pos = self.text_editor.search(search_term, tk.INSERT, tk.END)
                if pos:
                    end_pos = f"{pos}+{len(search_term)}c"
                    self.text_editor.tag_add('search', pos, end_pos)
                    self.text_editor.tag_configure('search', background='yellow')
                    self.text_editor.mark_set(tk.INSERT, end_pos)
                    self.text_editor.see(pos)
                else:
                    messagebox.showinfo("Find", "No more matches found")

        def replace_current():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            try:
                if self.text_editor.tag_ranges('search'):
                    self.text_editor.delete('search.first', 'search.last')
                    self.text_editor.insert(tk.INSERT, replace_term)
                    find_next()
            except:
                pass

        def replace_all():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            if search_term:
                content = self.text_editor.get('1.0', 'end-1c')
                new_content = content.replace(search_term, replace_term)
                self.text_editor.delete('1.0', tk.END)
                self.text_editor.insert('1.0', new_content)
                messagebox.showinfo("Replace All", "All occurrences replaced")

        button_frame = tk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Find Next", command=find_next, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Replace", command=replace_current, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Replace All", command=replace_all, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy, padx=10).pack(side=tk.LEFT, padx=5)

    def show_word_count(self):
        """Show detailed word count"""
        content = self.text_editor.get('1.0', 'end-1c')
        words = len(content.split())
        chars = len(content)
        chars_no_spaces = len(content.replace(' ', '').replace('\n', ''))
        lines = content.count('\n') + 1
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])

        info = f"""Word Count Statistics:

Words: {words}
Characters (with spaces): {chars}
Characters (no spaces): {chars_no_spaces}
Lines: {lines}
Paragraphs: {paragraphs}"""

        messagebox.showinfo("Word Count", info)

    def run(self):
        """Run editor"""
        self.root.mainloop()

if __name__ == '__main__':
    editor = DocumentEditor()
    editor.run()
