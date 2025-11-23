#!/usr/bin/env python3
"""
TL Linux - Text Editor
Multi-tab text editor with syntax highlighting, find/replace, and more
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
import os
import re
from datetime import datetime

class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Text Editor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # Tabs (file paths)
        self.tabs = {}  # notebook_tab_id -> {'path': path, 'widget': text_widget, 'modified': bool}
        self.current_tab = None

        # Syntax highlighting patterns
        self.syntax_patterns = {
            'python': {
                'keyword': (r'\b(def|class|import|from|if|elif|else|for|while|return|try|except|with|as|pass|break|continue|and|or|not|in|is|None|True|False|self)\b', '#ff79c6'),
                'string': (r'"[^"]*"|\'[^\']*\'', '#f1fa8c'),
                'comment': (r'#.*$', '#6272a4'),
                'function': (r'\bdef\s+(\w+)', '#50fa7b'),
                'number': (r'\b\d+\b', '#bd93f9'),
            },
            'javascript': {
                'keyword': (r'\b(function|var|let|const|if|else|for|while|return|class|extends|import|export|async|await|try|catch|new|this)\b', '#ff79c6'),
                'string': (r'"[^"]*"|\'[^\']*\'|`[^`]*`', '#f1fa8c'),
                'comment': (r'//.*$|/\*.*?\*/', '#6272a4'),
                'function': (r'\bfunction\s+(\w+)', '#50fa7b'),
                'number': (r'\b\d+\b', '#bd93f9'),
            },
            'html': {
                'tag': (r'</?[a-zA-Z][^>]*>', '#ff79c6'),
                'attribute': (r'\b\w+="[^"]*"', '#50fa7b'),
                'comment': (r'<!--.*?-->', '#6272a4'),
            }
        }

        # Find/Replace state
        self.find_window = None
        self.last_search = ""

        self.setup_ui()
        self.new_file()

    def setup_ui(self):
        """Create the UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")

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
        edit_menu.add_command(label="Find...", command=self.show_find, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.show_replace, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Line Numbers", command=self.toggle_line_numbers)
        view_menu.add_checkbutton(label="Word Wrap", command=self.toggle_word_wrap)

        # Syntax menu
        syntax_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Syntax", menu=syntax_menu)
        syntax_menu.add_command(label="Plain Text", command=lambda: self.set_syntax('none'))
        syntax_menu.add_command(label="Python", command=lambda: self.set_syntax('python'))
        syntax_menu.add_command(label="JavaScript", command=lambda: self.set_syntax('javascript'))
        syntax_menu.add_command(label="HTML", command=lambda: self.set_syntax('html'))

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2b2b2b', height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        # Toolbar buttons
        tk.Button(
            toolbar,
            text="📄 New",
            command=self.new_file,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="📁 Open",
            command=self.open_file,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="💾 Save",
            command=self.save_file,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🔍 Find",
            command=self.show_find,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=20)

        # Font size
        tk.Label(
            toolbar,
            text="Font Size:",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8)
        ).pack(side=tk.RIGHT, padx=(20, 5))

        self.font_size_var = tk.IntVar(value=11)
        tk.Spinbox(
            toolbar,
            from_=8,
            to=24,
            textvariable=self.font_size_var,
            command=self.update_font_size,
            bg='#1a1a1a',
            fg='white',
            width=5
        ).pack(side=tk.RIGHT)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[15, 5])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Bind tab switch
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

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
        self.status_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.cursor_pos_label = tk.Label(
            status_bar,
            text="Line 1, Col 1",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8)
        )
        self.cursor_pos_label.pack(side=tk.RIGHT, padx=10)

        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-q>', lambda e: self.quit())
        self.root.bind('<Control-f>', lambda e: self.show_find())
        self.root.bind('<Control-h>', lambda e: self.show_replace())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())

    def create_text_widget(self):
        """Create a new text widget for a tab"""
        frame = tk.Frame(self.notebook, bg='#1a1a1a')

        # Line numbers (optional)
        line_numbers = tk.Text(
            frame,
            width=5,
            bg='#2b2b2b',
            fg='#888888',
            font=('Courier', self.font_size_var.get()),
            state=tk.DISABLED,
            bd=0,
            highlightthickness=0,
            takefocus=0
        )
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text widget
        text = tk.Text(
            frame,
            bg='#1a1a1a',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            font=('Courier', self.font_size_var.get()),
            wrap=tk.NONE,
            undo=True,
            maxundo=-1,
            bd=0,
            highlightthickness=0,
            selectbackground='#44475a',
            selectforeground='#f8f8f2'
        )
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        y_scroll = tk.Scrollbar(frame, command=text.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=y_scroll.set)

        x_scroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        text.config(xscrollcommand=x_scroll.set)

        # Bind events
        text.bind('<KeyRelease>', lambda e: self.on_text_change())
        text.bind('<Button-1>', lambda e: self.update_cursor_position())
        text.bind('<KeyPress>', lambda e: self.update_cursor_position())

        return frame, text, line_numbers

    def new_file(self):
        """Create a new file tab"""
        frame, text, line_nums = self.create_text_widget()

        tab_name = f"Untitled {len(self.tabs) + 1}"
        self.notebook.add(frame, text=tab_name)

        tab_id = str(frame)
        self.tabs[tab_id] = {
            'path': None,
            'widget': text,
            'line_numbers': line_nums,
            'modified': False,
            'syntax': 'none'
        }

        self.notebook.select(frame)
        self.current_tab = tab_id

        self.update_line_numbers()
        text.focus_set()

    def open_file(self):
        """Open a file"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Create new tab
                frame, text, line_nums = self.create_text_widget()

                tab_name = os.path.basename(file_path)
                self.notebook.add(frame, text=tab_name)

                tab_id = str(frame)

                # Detect syntax from extension
                ext = os.path.splitext(file_path)[1].lower()
                syntax_map = {'.py': 'python', '.js': 'javascript', '.html': 'html'}
                syntax = syntax_map.get(ext, 'none')

                self.tabs[tab_id] = {
                    'path': file_path,
                    'widget': text,
                    'line_numbers': line_nums,
                    'modified': False,
                    'syntax': syntax
                }

                text.insert('1.0', content)
                text.edit_reset()  # Clear undo history

                self.notebook.select(frame)
                self.current_tab = tab_id

                self.apply_syntax_highlighting()
                self.update_line_numbers()

                self.status_label.config(text=f"Opened: {file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save current file"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]

        if tab_data['path']:
            self.save_to_path(tab_data['path'])
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save file with new name"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        file_path = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.save_to_path(file_path)

            # Update tab
            tab_data = self.tabs[self.current_tab]
            tab_data['path'] = file_path

            tab_name = os.path.basename(file_path)
            current_index = self.notebook.index(self.notebook.select())
            self.notebook.tab(current_index, text=tab_name)

    def save_to_path(self, path):
        """Save content to path"""
        try:
            tab_data = self.tabs[self.current_tab]
            text = tab_data['widget']

            content = text.get('1.0', tk.END)

            with open(path, 'w') as f:
                f.write(content)

            tab_data['modified'] = False
            self.update_tab_title()

            self.status_label.config(text=f"Saved: {path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def close_tab(self):
        """Close current tab"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]

        if tab_data['modified']:
            result = messagebox.askyesnocancel(
                "Save Changes?",
                "Do you want to save changes before closing?"
            )

            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()

        # Get current tab index
        current_index = self.notebook.index(self.notebook.select())

        # Remove tab
        self.notebook.forget(current_index)
        del self.tabs[self.current_tab]

        # If no tabs left, create new one
        if not self.tabs:
            self.new_file()
        else:
            # Select another tab
            if current_index > 0:
                self.notebook.select(current_index - 1)
            else:
                self.notebook.select(0)

    def on_tab_change(self, event):
        """Handle tab change"""
        try:
            current_tab_widget = self.notebook.select()
            if current_tab_widget:
                self.current_tab = str(current_tab_widget)
                self.update_cursor_position()
        except:
            pass

    def on_text_change(self):
        """Handle text change"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]
        tab_data['modified'] = True

        self.update_tab_title()
        self.update_line_numbers()
        self.apply_syntax_highlighting()
        self.update_cursor_position()

    def update_tab_title(self):
        """Update tab title with modified indicator"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]
        current_index = self.notebook.index(self.notebook.select())

        if tab_data['path']:
            title = os.path.basename(tab_data['path'])
        else:
            title = self.notebook.tab(current_index, 'text').replace(' *', '')

        if tab_data['modified']:
            title += ' *'

        self.notebook.tab(current_index, text=title)

    def update_line_numbers(self):
        """Update line numbers"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]
        text = tab_data['widget']
        line_nums = tab_data['line_numbers']

        # Get number of lines
        num_lines = int(text.index('end-1c').split('.')[0])

        # Update line numbers
        line_nums.config(state=tk.NORMAL)
        line_nums.delete('1.0', tk.END)

        for i in range(1, num_lines + 1):
            line_nums.insert(tk.END, f"{i:>4}\n")

        line_nums.config(state=tk.DISABLED)

    def update_cursor_position(self):
        """Update cursor position in status bar"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]
        text = tab_data['widget']

        try:
            cursor_pos = text.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_pos_label.config(text=f"Line {line}, Col {int(col) + 1}")
        except:
            pass

    def apply_syntax_highlighting(self):
        """Apply syntax highlighting to current text"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]
        text = tab_data['widget']
        syntax = tab_data['syntax']

        if syntax == 'none' or syntax not in self.syntax_patterns:
            return

        # Remove old tags
        for tag in text.tag_names():
            if tag not in ('sel',):
                text.tag_remove(tag, '1.0', tk.END)

        # Apply new highlighting
        content = text.get('1.0', tk.END)
        patterns = self.syntax_patterns[syntax]

        for tag_name, (pattern, color) in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                start_index = f"1.0+{match.start()}c"
                end_index = f"1.0+{match.end()}c"

                text.tag_add(tag_name, start_index, end_index)
                text.tag_config(tag_name, foreground=color)

    def set_syntax(self, syntax):
        """Set syntax highlighting mode"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        self.tabs[self.current_tab]['syntax'] = syntax
        self.apply_syntax_highlighting()
        self.status_label.config(text=f"Syntax: {syntax.title()}")

    def show_find(self):
        """Show find dialog"""
        if self.find_window:
            self.find_window.lift()
            return

        self.find_window = tk.Toplevel(self.root)
        self.find_window.title("Find")
        self.find_window.geometry("400x150")
        self.find_window.configure(bg='#2b2b2b')
        self.find_window.transient(self.root)

        tk.Label(
            self.find_window,
            text="Find:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(pady=(20, 5))

        find_entry = tk.Entry(
            self.find_window,
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            font=('Arial', 11)
        )
        find_entry.pack(fill=tk.X, padx=20, pady=5)
        find_entry.focus_set()

        btn_frame = tk.Frame(self.find_window, bg='#2b2b2b')
        btn_frame.pack(pady=15)

        def do_find():
            search_text = find_entry.get()
            if search_text:
                self.find_text(search_text)

        tk.Button(
            btn_frame,
            text="Find Next",
            command=do_find,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        find_entry.bind('<Return>', lambda e: do_find())

        self.find_window.protocol("WM_DELETE_WINDOW", lambda: self.close_find_window())

    def close_find_window(self):
        """Close find window"""
        if self.find_window:
            self.find_window.destroy()
            self.find_window = None

    def find_text(self, search_text):
        """Find text in current document"""
        if not self.current_tab or self.current_tab not in self.tabs:
            return

        tab_data = self.tabs[self.current_tab]
        text = tab_data['widget']

        # Remove old highlights
        text.tag_remove('found', '1.0', tk.END)

        if not search_text:
            return

        # Start search from current position
        start_pos = text.index(tk.INSERT)
        pos = text.search(search_text, start_pos, tk.END)

        if pos:
            end_pos = f"{pos}+{len(search_text)}c"
            text.tag_add('found', pos, end_pos)
            text.tag_config('found', background='#f1fa8c', foreground='#000000')
            text.mark_set(tk.INSERT, end_pos)
            text.see(pos)
            self.last_search = search_text
        else:
            # Try from beginning
            pos = text.search(search_text, '1.0', tk.END)
            if pos:
                end_pos = f"{pos}+{len(search_text)}c"
                text.tag_add('found', pos, end_pos)
                text.tag_config('found', background='#f1fa8c', foreground='#000000')
                text.mark_set(tk.INSERT, end_pos)
                text.see(pos)
                self.last_search = search_text
            else:
                messagebox.showinfo("Not Found", f"'{search_text}' not found")

    def show_replace(self):
        """Show find and replace dialog"""
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Find and Replace")
        replace_window.geometry("450x200")
        replace_window.configure(bg='#2b2b2b')
        replace_window.transient(self.root)
        replace_window.grab_set()

        # Find entry
        tk.Label(replace_window, text="Find:", bg='#2b2b2b', fg='white').pack(pady=(20, 5))
        find_entry = tk.Entry(replace_window, bg='#1a1a1a', fg='white', insertbackground='white')
        find_entry.pack(fill=tk.X, padx=20)

        # Replace entry
        tk.Label(replace_window, text="Replace with:", bg='#2b2b2b', fg='white').pack(pady=(10, 5))
        replace_entry = tk.Entry(replace_window, bg='#1a1a1a', fg='white', insertbackground='white')
        replace_entry.pack(fill=tk.X, padx=20)

        # Buttons
        btn_frame = tk.Frame(replace_window, bg='#2b2b2b')
        btn_frame.pack(pady=15)

        def do_replace():
            if not self.current_tab or self.current_tab not in self.tabs:
                return

            find_text = find_entry.get()
            replace_text = replace_entry.get()

            if find_text:
                tab_data = self.tabs[self.current_tab]
                text = tab_data['widget']

                content = text.get('1.0', tk.END)
                new_content = content.replace(find_text, replace_text)

                text.delete('1.0', tk.END)
                text.insert('1.0', new_content)

                replace_window.destroy()
                messagebox.showinfo("Success", "Replacement complete")

        tk.Button(btn_frame, text="Replace All", command=do_replace,
                 bg='#4a9eff', fg='white', bd=0, padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=replace_window.destroy,
                 bg='#ff5555', fg='white', bd=0, padx=20, pady=8).pack(side=tk.LEFT)

    # Edit operations
    def undo(self):
        """Undo last change"""
        if self.current_tab and self.current_tab in self.tabs:
            try:
                self.tabs[self.current_tab]['widget'].edit_undo()
            except:
                pass

    def redo(self):
        """Redo last undone change"""
        if self.current_tab and self.current_tab in self.tabs:
            try:
                self.tabs[self.current_tab]['widget'].edit_redo()
            except:
                pass

    def cut(self):
        """Cut selected text"""
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab]['widget'].event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text"""
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab]['widget'].event_generate("<<Copy>>")

    def paste(self):
        """Paste text"""
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab]['widget'].event_generate("<<Paste>>")

    def select_all(self):
        """Select all text"""
        if self.current_tab and self.current_tab in self.tabs:
            text = self.tabs[self.current_tab]['widget']
            text.tag_add(tk.SEL, '1.0', tk.END)

    # View operations
    def zoom_in(self):
        """Increase font size"""
        self.font_size_var.set(min(24, self.font_size_var.get() + 1))
        self.update_font_size()

    def zoom_out(self):
        """Decrease font size"""
        self.font_size_var.set(max(8, self.font_size_var.get() - 1))
        self.update_font_size()

    def reset_zoom(self):
        """Reset font size to default"""
        self.font_size_var.set(11)
        self.update_font_size()

    def update_font_size(self):
        """Update font size for all text widgets"""
        size = self.font_size_var.get()

        for tab_data in self.tabs.values():
            tab_data['widget'].config(font=('Courier', size))
            tab_data['line_numbers'].config(font=('Courier', size))

    def toggle_line_numbers(self):
        """Toggle line numbers visibility"""
        # Would implement showing/hiding line numbers
        pass

    def toggle_word_wrap(self):
        """Toggle word wrap"""
        if self.current_tab and self.current_tab in self.tabs:
            text = self.tabs[self.current_tab]['widget']
            current_wrap = text.cget('wrap')
            new_wrap = tk.NONE if current_wrap == tk.WORD else tk.WORD
            text.config(wrap=new_wrap)

    def quit(self):
        """Quit application"""
        # Check for unsaved changes
        has_unsaved = any(tab['modified'] for tab in self.tabs.values())

        if has_unsaved:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before quitting?"
            )

            if result is None:  # Cancel
                return
            elif result:  # Yes - save all
                for tab_id, tab_data in self.tabs.items():
                    if tab_data['modified'] and tab_data['path']:
                        self.current_tab = tab_id
                        self.save_file()

        self.root.destroy()

    def run(self):
        """Run the text editor"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

def main():
    editor = TextEditor()
    editor.run()

if __name__ == '__main__':
    main()
