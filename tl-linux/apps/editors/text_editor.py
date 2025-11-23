#!/usr/bin/env python3
"""
TL Linux - Advanced Text & Markdown Editor
Multi-format text editing with preview and syntax support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import os
from pathlib import Path
import re

class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📝 TL Text Editor")
        self.root.geometry("1200x800")

        self.current_file = None
        self.file_changed = False
        self.current_mode = 'text'  # text, markdown, code

        self.setup_ui()
        self.new_file()

    def setup_ui(self):
        """Setup editor UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export to HTML", command=self.export_html)
        file_menu.add_command(label="Export to PDF", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_editor)

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
        edit_menu.add_command(label="Find", command=self.find, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")

        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=lambda: self.insert_markdown('**'), accelerator="Ctrl+B")
        format_menu.add_command(label="Italic", command=lambda: self.insert_markdown('*'), accelerator="Ctrl+I")
        format_menu.add_command(label="Code", command=lambda: self.insert_markdown('`'))
        format_menu.add_separator()
        format_menu.add_command(label="Heading 1", command=lambda: self.insert_heading(1))
        format_menu.add_command(label="Heading 2", command=lambda: self.insert_heading(2))
        format_menu.add_command(label="Heading 3", command=lambda: self.insert_heading(3))
        format_menu.add_separator()
        format_menu.add_command(label="Bullet List", command=self.insert_bullet)
        format_menu.add_command(label="Numbered List", command=self.insert_numbered)
        format_menu.add_command(label="Quote", command=self.insert_quote)
        format_menu.add_command(label="Code Block", command=self.insert_code_block)
        format_menu.add_separator()
        format_menu.add_command(label="Link", command=self.insert_link)
        format_menu.add_command(label="Image", command=self.insert_image)
        format_menu.add_command(label="Table", command=self.insert_table)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Preview", command=self.toggle_preview, accelerator="Ctrl+P")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Word Wrap", command=self.toggle_wrap)
        view_menu.add_checkbutton(label="Line Numbers", command=self.toggle_line_numbers)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#f0f0f0', pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # File operations
        tk.Button(toolbar, text="📄 New", command=self.new_file, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📁 Open", command=self.open_file, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="💾 Save", command=self.save_file, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Formatting
        tk.Button(toolbar, text="B", command=lambda: self.insert_markdown('**'), relief=tk.FLAT, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="I", command=lambda: self.insert_markdown('*'), relief=tk.FLAT, font=('Arial', 10, 'italic')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="`code`", command=lambda: self.insert_markdown('`'), relief=tk.FLAT, font=('Courier', 9)).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Lists
        tk.Button(toolbar, text="• List", command=self.insert_bullet, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="1. List", command=self.insert_numbered, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='" Quote', command=self.insert_quote, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Insert
        tk.Button(toolbar, text="🔗 Link", command=self.insert_link, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🖼️ Image", command=self.insert_image, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📊 Table", command=self.insert_table, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Preview
        tk.Button(toolbar, text="👁️ Preview", command=self.toggle_preview, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        # Font size
        tk.Label(toolbar, text="Size:", bg='#f0f0f0').pack(side=tk.RIGHT, padx=5)
        self.font_size_var = tk.IntVar(value=11)
        font_spinner = tk.Spinbox(toolbar, from_=8, to=24, textvariable=self.font_size_var, width=5, command=self.change_font_size)
        font_spinner.pack(side=tk.RIGHT, padx=2)

        # Main editor area
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Editor frame (left side)
        editor_frame = tk.Frame(self.paned_window)
        self.paned_window.add(editor_frame)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=5,
            takefocus=0,
            border=0,
            background='#f0f0f0',
            state='disabled'
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text editor with scrollbar
        text_scroll = tk.Scrollbar(editor_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_editor = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            undo=True,
            maxundo=-1,
            yscrollcommand=text_scroll.set,
            font=('Courier New', 11),
            padx=10,
            pady=10
        )
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.text_editor.yview)

        # Bind events
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        self.text_editor.bind('<<Modified>>', self.on_modified)

        # Preview frame (initially hidden)
        self.preview_frame = tk.Frame(self.paned_window, bg='white')
        self.preview_text = tk.Text(
            self.preview_frame,
            wrap=tk.WORD,
            padx=20,
            pady=20,
            font=('Arial', 11),
            state='disabled',
            bg='white'
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Keybindings
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-p>', lambda e: self.toggle_preview())
        self.root.bind('<Control-f>', lambda e: self.find())
        self.root.bind('<Control-h>', lambda e: self.replace())
        self.root.bind('<Control-b>', lambda e: self.insert_markdown('**'))
        self.root.bind('<Control-i>', lambda e: self.insert_markdown('*'))

        self.update_line_numbers()

    def new_file(self):
        """Create new file"""
        if self.file_changed:
            if not messagebox.askyesno("Unsaved Changes", "Discard changes?"):
                return

        self.text_editor.delete('1.0', tk.END)
        self.current_file = None
        self.file_changed = False
        self.update_title()
        self.update_status()

    def open_file(self):
        """Open file"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("Python Files", "*.py"),
                ("JSON Files", "*.json"),
                ("XML Files", "*.xml")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.text_editor.delete('1.0', tk.END)
                self.text_editor.insert('1.0', content)
                self.current_file = Path(file_path)
                self.file_changed = False

                # Detect file type
                if file_path.endswith('.md'):
                    self.current_mode = 'markdown'
                elif file_path.endswith(('.py', '.json', '.xml', '.js', '.html', '.css')):
                    self.current_mode = 'code'
                else:
                    self.current_mode = 'text'

                self.update_title()
                self.update_status()

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        """Save file"""
        if self.current_file:
            self.write_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save as new file"""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.write_file(Path(file_path))

    def write_file(self, file_path):
        """Write content to file"""
        try:
            content = self.text_editor.get('1.0', tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.current_file = file_path
            self.file_changed = False
            self.update_title()
            self.update_status()
            messagebox.showinfo("Saved", f"File saved: {file_path.name}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def export_html(self):
        """Export to HTML"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please save file first")
            return

        html_path = self.current_file.with_suffix('.html')
        content = self.text_editor.get('1.0', tk.END)

        # Simple markdown to HTML conversion
        html = self.markdown_to_html(content)

        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            messagebox.showinfo("Exported", f"Exported to:\n{html_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def export_pdf(self):
        """Export to PDF placeholder"""
        messagebox.showinfo("PDF Export", "PDF export requires additional libraries.\nExport to HTML first, then use a browser to save as PDF.")

    def markdown_to_html(self, markdown_text):
        """Simple markdown to HTML conversion"""
        html = "<html><head><style>body{font-family:Arial;padding:20px;max-width:800px;margin:auto;}</style></head><body>"

        lines = markdown_text.split('\n')
        for line in lines:
            # Headers
            if line.startswith('# '):
                html += f"<h1>{line[2:]}</h1>"
            elif line.startswith('## '):
                html += f"<h2>{line[3:]}</h2>"
            elif line.startswith('### '):
                html += f"<h3>{line[4:]}</h3>"
            # Bold and italic
            elif '**' in line or '*' in line or '`' in line:
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
                line = re.sub(r'`(.*?)`', r'<code>\1</code>', line)
                html += f"<p>{line}</p>"
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                html += f"<li>{line[2:]}</li>"
            elif line.strip().startswith(tuple(f"{i}." for i in range(10))):
                html += f"<li>{line.split('.', 1)[1].strip()}</li>"
            # Quote
            elif line.startswith('> '):
                html += f"<blockquote>{line[2:]}</blockquote>"
            # Regular paragraph
            elif line.strip():
                html += f"<p>{line}</p>"
            else:
                html += "<br>"

        html += "</body></html>"
        return html

    def insert_markdown(self, marker):
        """Insert markdown formatting"""
        try:
            selection = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.insert(tk.INSERT, f"{marker}{selection}{marker}")
        except:
            # No selection, just insert markers
            self.text_editor.insert(tk.INSERT, f"{marker}{marker}")
            self.text_editor.mark_set(tk.INSERT, f"{tk.INSERT}-{len(marker)}c")

    def insert_heading(self, level):
        """Insert heading"""
        self.text_editor.insert(tk.INSERT, f"{'#' * level} ")

    def insert_bullet(self):
        """Insert bullet list"""
        self.text_editor.insert(tk.INSERT, "- ")

    def insert_numbered(self):
        """Insert numbered list"""
        self.text_editor.insert(tk.INSERT, "1. ")

    def insert_quote(self):
        """Insert quote"""
        self.text_editor.insert(tk.INSERT, "> ")

    def insert_code_block(self):
        """Insert code block"""
        self.text_editor.insert(tk.INSERT, "```\n\n```")
        self.text_editor.mark_set(tk.INSERT, f"{tk.INSERT}-4c")

    def insert_link(self):
        """Insert link"""
        self.text_editor.insert(tk.INSERT, "[text](url)")

    def insert_image(self):
        """Insert image"""
        self.text_editor.insert(tk.INSERT, "![alt text](image-url)")

    def insert_table(self):
        """Insert table"""
        table = "| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n"
        self.text_editor.insert(tk.INSERT, table)

    def toggle_preview(self):
        """Toggle markdown preview"""
        if self.preview_frame.winfo_ismapped():
            self.paned_window.forget(self.preview_frame)
        else:
            self.paned_window.add(self.preview_frame)
            self.update_preview()

    def update_preview(self):
        """Update markdown preview"""
        content = self.text_editor.get('1.0', tk.END)
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', tk.END)

        # Simple markdown rendering
        for line in content.split('\n'):
            if line.startswith('# '):
                self.preview_text.insert(tk.END, line[2:] + '\n', 'h1')
            elif line.startswith('## '):
                self.preview_text.insert(tk.END, line[3:] + '\n', 'h2')
            elif line.startswith('### '):
                self.preview_text.insert(tk.END, line[4:] + '\n', 'h3')
            else:
                self.preview_text.insert(tk.END, line + '\n')

        # Configure tags
        self.preview_text.tag_config('h1', font=('Arial', 20, 'bold'))
        self.preview_text.tag_config('h2', font=('Arial', 16, 'bold'))
        self.preview_text.tag_config('h3', font=('Arial', 14, 'bold'))

        self.preview_text.config(state='disabled')

    def toggle_wrap(self):
        """Toggle word wrap"""
        current_wrap = self.text_editor.cget('wrap')
        new_wrap = tk.NONE if current_wrap == tk.WORD else tk.WORD
        self.text_editor.config(wrap=new_wrap)

    def toggle_line_numbers(self):
        """Toggle line numbers"""
        if self.line_numbers.winfo_ismapped():
            self.line_numbers.pack_forget()
        else:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    def update_line_numbers(self):
        """Update line numbers"""
        line_count = int(self.text_editor.index('end-1c').split('.')[0])
        line_numbers_string = '\n'.join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')

    def change_font_size(self):
        """Change font size"""
        size = self.font_size_var.get()
        self.text_editor.config(font=('Courier New', size))
        self.preview_text.config(font=('Arial', size))

    def on_text_change(self, event=None):
        """Handle text change"""
        self.update_line_numbers()
        if self.preview_frame.winfo_ismapped():
            self.update_preview()

    def on_modified(self, event=None):
        """Handle modification"""
        if self.text_editor.edit_modified():
            self.file_changed = True
            self.update_title()
            self.update_status()
            self.text_editor.edit_modified(False)

    def update_title(self):
        """Update window title"""
        file_name = self.current_file.name if self.current_file else "Untitled"
        changed = "*" if self.file_changed else ""
        self.root.title(f"📝 TL Text Editor - {file_name}{changed}")

    def update_status(self):
        """Update status bar"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        char_count = len(self.text_editor.get('1.0', tk.END)) - 1
        word_count = len(self.text_editor.get('1.0', tk.END).split())

        file_name = self.current_file.name if self.current_file else "Untitled"
        self.status_bar.config(text=f"{file_name} | Line {line}, Col {col} | {char_count} chars, {word_count} words | {self.current_mode.upper()} mode")

    def find(self):
        """Find text"""
        search_window = tk.Toplevel(self.root)
        search_window.title("Find")
        search_window.geometry("400x100")

        tk.Label(search_window, text="Find:").pack(pady=5)
        search_entry = tk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()

        def do_find():
            query = search_entry.get()
            self.text_editor.tag_remove('found', '1.0', tk.END)

            if query:
                idx = '1.0'
                while True:
                    idx = self.text_editor.search(query, idx, nocase=True, stopindex=tk.END)
                    if not idx:
                        break
                    lastidx = f"{idx}+{len(query)}c"
                    self.text_editor.tag_add('found', idx, lastidx)
                    idx = lastidx

                self.text_editor.tag_config('found', background='yellow', foreground='black')

        tk.Button(search_window, text="Find All", command=do_find).pack(pady=5)
        search_entry.bind('<Return>', lambda e: do_find())

    def replace(self):
        """Replace text"""
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace")
        replace_window.geometry("400x150")

        tk.Label(replace_window, text="Find:").pack(pady=5)
        find_entry = tk.Entry(replace_window, width=40)
        find_entry.pack(pady=5)

        tk.Label(replace_window, text="Replace with:").pack(pady=5)
        replace_entry = tk.Entry(replace_window, width=40)
        replace_entry.pack(pady=5)

        def do_replace_all():
            find_text = find_entry.get()
            replace_text = replace_entry.get()

            if find_text:
                content = self.text_editor.get('1.0', tk.END)
                new_content = content.replace(find_text, replace_text)
                self.text_editor.delete('1.0', tk.END)
                self.text_editor.insert('1.0', new_content)
                messagebox.showinfo("Replace", "Replacement complete!")

        tk.Button(replace_window, text="Replace All", command=do_replace_all).pack(pady=5)

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
        self.text_editor.event_generate("<<Cut>>")

    def copy(self):
        """Copy"""
        self.text_editor.event_generate("<<Copy>>")

    def paste(self):
        """Paste"""
        self.text_editor.event_generate("<<Paste>>")

    def select_all(self):
        """Select all"""
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)

    def exit_editor(self):
        """Exit editor"""
        if self.file_changed:
            if not messagebox.askyesno("Unsaved Changes", "Exit without saving?"):
                return
        self.root.destroy()

    def run(self):
        """Run editor"""
        self.root.mainloop()

if __name__ == '__main__':
    editor = TextEditor()
    editor.run()
