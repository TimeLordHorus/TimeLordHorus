#!/usr/bin/env python3
"""
TL IDE - Integrated Development Environment
Lightweight coding environment with syntax highlighting and tools
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
from pathlib import Path

class TLIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL IDE")
        self.root.geometry("1200x800")

        self.current_file = None
        self.file_changed = False

        self.setup_ui()
        self.setup_syntax_highlighting()

    def setup_ui(self):
        """Setup IDE interface"""
        # Menu bar
        menubar = tk.Menu(self.root, bg='#1a1a1a', fg='#00FF00')
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#1a1a1a', fg='#00FF00')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_ide)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#1a1a1a', fg='#00FF00')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find, accelerator="Ctrl+F")

        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0, bg='#1a1a1a', fg='#00FF00')
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run File", command=self.run_file, accelerator="F5")
        run_menu.add_command(label="Run Selection", command=self.run_selection, accelerator="F9")

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#1a1a1a', pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        buttons = [
            ("📄", "New", self.new_file),
            ("📁", "Open", self.open_file),
            ("💾", "Save", self.save_file),
            ("▶", "Run", self.run_file),
            ("⚙️", "Settings", self.show_settings),
        ]

        for icon, text, cmd in buttons:
            btn = tk.Button(
                toolbar,
                text=f"{icon} {text}",
                command=cmd,
                bg='#333333',
                fg='#00FF00',
                font=('Sans', 9),
                bd=0,
                padx=10,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Main container
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#0a0a0a')
        main_container.pack(fill=tk.BOTH, expand=True)

        # File explorer
        explorer_frame = tk.Frame(main_container, bg='#1a1a1a', width=200)
        tk.Label(
            explorer_frame,
            text="📁 File Explorer",
            bg='#1a1a1a',
            fg='#00FF00',
            font=('Sans', 10, 'bold'),
            pady=5
        ).pack(fill=tk.X)

        self.file_tree = ttk.Treeview(explorer_frame, selectmode='browse')
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind('<Double-1>', self.tree_double_click)

        scrollbar = ttk.Scrollbar(explorer_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        main_container.add(explorer_frame)

        # Editor container
        editor_container = tk.PanedWindow(main_container, orient=tk.VERTICAL, bg='#0a0a0a')
        main_container.add(editor_container)

        # Editor frame
        editor_frame = tk.Frame(editor_container, bg='#0a0a0a')

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            bg='#1a1a1a',
            fg='#666666',
            font=('Monospace', 11),
            state='disabled',
            bd=0,
            highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            bg='#000000',
            fg='#00FF00',
            font=('Monospace', 11),
            insertbackground='#00FF00',
            selectbackground='#333333',
            bd=0,
            undo=True,
            maxundo=-1
        )
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        self.text_editor.bind('<MouseWheel>', self.on_scroll)

        editor_container.add(editor_frame)

        # Output/Terminal panel
        output_frame = tk.Frame(editor_container, bg='#0a0a0a')
        tk.Label(
            output_frame,
            text="📟 Output",
            bg='#1a1a1a',
            fg='#00FFFF',
            font=('Sans', 9, 'bold'),
            anchor='w'
        ).pack(fill=tk.X)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            bg='#000000',
            fg='#00FFFF',
            font=('Monospace', 9),
            bd=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        editor_container.add(output_frame)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bg='#1a1a1a',
            fg='#00FF00',
            font=('Monospace', 9),
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Keybindings
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_file())

        # Load current directory in file tree
        self.load_directory(Path.cwd())

    def setup_syntax_highlighting(self):
        """Setup basic syntax highlighting"""
        # Python keywords
        self.keywords = [
            'def', 'class', 'import', 'from', 'return', 'if', 'elif', 'else',
            'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass',
            'break', 'continue', 'yield', 'lambda', 'and', 'or', 'not', 'in',
            'is', 'True', 'False', 'None'
        ]

        # Configure tags
        self.text_editor.tag_config('keyword', foreground='#FF00FF')
        self.text_editor.tag_config('string', foreground='#FFFF00')
        self.text_editor.tag_config('comment', foreground='#666666')
        self.text_editor.tag_config('number', foreground='#00FFFF')

    def highlight_syntax(self):
        """Apply syntax highlighting (basic)"""
        content = self.text_editor.get('1.0', tk.END)

        # Clear existing tags
        for tag in ['keyword', 'string', 'comment', 'number']:
            self.text_editor.tag_remove(tag, '1.0', tk.END)

        # Highlight keywords
        for keyword in self.keywords:
            start = '1.0'
            while True:
                pos = self.text_editor.search(r'\m{}\M'.format(keyword), start, tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.text_editor.tag_add('keyword', pos, end)
                start = end

    def update_line_numbers(self):
        """Update line number display"""
        line_count = self.text_editor.get('1.0', tk.END).count('\n')
        line_numbers_string = '\n'.join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')

    def on_text_change(self, event=None):
        """Handle text change"""
        self.file_changed = True
        self.update_line_numbers()
        self.update_status()

    def on_scroll(self, event):
        """Sync line numbers with editor scroll"""
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])

    def update_status(self):
        """Update status bar"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        file_name = self.current_file.name if self.current_file else "Untitled"
        changed = "*" if self.file_changed else ""
        self.status_bar.config(text=f"{file_name}{changed} | Line {line}, Col {col}")

    def load_directory(self, path):
        """Load directory into file tree"""
        self.file_tree.delete(*self.file_tree.get_children())
        self.populate_tree(path, '')

    def populate_tree(self, path, parent):
        """Recursively populate file tree"""
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    node = self.file_tree.insert(parent, 'end', text=f"📁 {item.name}", open=False)
                    self.file_tree.insert(node, 'end')  # Dummy for expand
                else:
                    self.file_tree.insert(parent, 'end', text=f"📄 {item.name}", values=[str(item)])
        except PermissionError:
            pass

    def tree_double_click(self, event):
        """Handle double-click on file tree"""
        item = self.file_tree.selection()[0]
        values = self.file_tree.item(item, 'values')
        if values:
            file_path = Path(values[0])
            if file_path.is_file():
                self.load_file(file_path)

    def new_file(self):
        """Create new file"""
        if self.file_changed:
            if not messagebox.askyesno("Unsaved Changes", "Discard unsaved changes?"):
                return

        self.text_editor.delete('1.0', tk.END)
        self.current_file = None
        self.file_changed = False
        self.update_status()

    def open_file(self):
        """Open file dialog"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("Text Files", "*.txt")]
        )
        if file_path:
            self.load_file(Path(file_path))

    def load_file(self, file_path):
        """Load file into editor"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            self.text_editor.delete('1.0', tk.END)
            self.text_editor.insert('1.0', content)
            self.current_file = file_path
            self.file_changed = False
            self.update_status()
            self.highlight_syntax()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_file(self):
        """Save current file"""
        if self.current_file:
            self.write_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save as new file"""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("Text Files", "*.txt")]
        )
        if file_path:
            self.write_file(Path(file_path))

    def write_file(self, file_path):
        """Write content to file"""
        try:
            content = self.text_editor.get('1.0', tk.END)
            with open(file_path, 'w') as f:
                f.write(content)

            self.current_file = file_path
            self.file_changed = False
            self.update_status()
            self.output_text.insert(tk.END, f"✓ Saved: {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def run_file(self):
        """Run current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please save the file first")
            return

        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, f"Running {self.current_file.name}...\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n")

        try:
            result = subprocess.run(
                ['python3', str(self.current_file)],
                capture_output=True,
                text=True,
                timeout=10
            )

            self.output_text.insert(tk.END, result.stdout)
            if result.stderr:
                self.output_text.insert(tk.END, "\nErrors:\n" + result.stderr)
            self.output_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.output_text.insert(tk.END, f"Exit code: {result.returncode}\n")

        except subprocess.TimeoutExpired:
            self.output_text.insert(tk.END, "\n⚠ Execution timed out\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"\n✗ Error: {e}\n")

    def run_selection(self):
        """Run selected text"""
        try:
            selection = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, "Running selection...\n")
            exec(selection)
        except tk.TclError:
            messagebox.showwarning("No Selection", "Please select code to run")
        except Exception as e:
            self.output_text.insert(tk.END, f"\n✗ Error: {e}\n")

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

    def find(self):
        """Find dialog"""
        search_toplevel = tk.Toplevel(self.root)
        search_toplevel.title("Find")
        search_toplevel.geometry("300x100")

        tk.Label(search_toplevel, text="Find:").pack(pady=5)
        search_entry = tk.Entry(search_toplevel, width=30)
        search_entry.pack(pady=5)

        def find_text():
            query = search_entry.get()
            self.text_editor.tag_remove('found', '1.0', tk.END)

            if query:
                idx = '1.0'
                while True:
                    idx = self.text_editor.search(query, idx, nocase=1, stopindex=tk.END)
                    if not idx:
                        break
                    lastidx = f"{idx}+{len(query)}c"
                    self.text_editor.tag_add('found', idx, lastidx)
                    idx = lastidx

                self.text_editor.tag_config('found', background='yellow', foreground='black')

        tk.Button(search_toplevel, text="Find All", command=find_text).pack(pady=5)

    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings panel coming soon!")

    def exit_ide(self):
        """Exit IDE"""
        if self.file_changed:
            if not messagebox.askyesno("Unsaved Changes", "Exit without saving?"):
                return
        self.root.destroy()

    def run(self):
        """Run IDE"""
        self.root.mainloop()

if __name__ == '__main__':
    ide = TLIDE()
    ide.run()
