#!/usr/bin/env python3
"""
TL Linux - Notes Application
Rich text notes with organization and search
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font, colorchooser
import json
import os
from pathlib import Path
from datetime import datetime
import uuid

class NotesApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Notes")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')

        # Configuration
        self.notes_dir = Path.home() / '.tl-linux' / 'notes'
        self.notes_dir.mkdir(parents=True, exist_ok=True)

        # Notes data
        self.notes = {}
        self.current_note_id = None
        self.categories = set(['General', 'Work', 'Personal', 'Ideas', 'Todo'])
        self.search_results = []

        # Auto-save
        self.auto_save_job = None
        self.content_modified = False

        self.load_notes()
        self.setup_ui()
        self.start_auto_save()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📝 Notes",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(header, bg='#2b2b2b')
        toolbar.pack(side=tk.RIGHT, padx=20)

        tk.Button(
            toolbar,
            text="+ New Note",
            command=self.new_note,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="💾 Save",
            command=self.save_current_note,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🗑 Delete",
            command=self.delete_note,
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel - Notes list
        left_panel = tk.Frame(main_container, bg='#1a1a1a', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        left_panel.pack_propagate(False)

        # Search
        search_frame = tk.Frame(left_panel, bg='#1a1a1a')
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="🔍", bg='#1a1a1a', fg='white').pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_notes())

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            bd=0,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        # Category filter
        filter_frame = tk.Frame(left_panel, bg='#1a1a1a')
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            filter_frame,
            text="Category:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.category_filter_var = tk.StringVar(value="All")
        category_filter = ttk.Combobox(
            filter_frame,
            textvariable=self.category_filter_var,
            values=["All"] + sorted(list(self.categories)),
            width=15,
            state='readonly'
        )
        category_filter.pack(side=tk.LEFT)
        category_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_notes())

        # Notes list
        tk.Label(
            left_panel,
            text="All Notes",
            font=('Arial', 11, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(0, 5))

        notes_frame = tk.Frame(left_panel, bg='#1a1a1a')
        notes_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(notes_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notes_listbox = tk.Listbox(
            notes_frame,
            bg='#2b2b2b',
            fg='white',
            selectbackground='#4a9eff',
            selectforeground='white',
            font=('Arial', 10),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.notes_listbox.yview)

        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)

        # Right panel - Note editor
        right_panel = tk.Frame(main_container, bg='#1a1a1a')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Note title
        title_frame = tk.Frame(right_panel, bg='#1a1a1a')
        title_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            title_frame,
            text="Title:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.title_var = tk.StringVar()
        self.title_var.trace('w', lambda *args: self.mark_modified())

        tk.Entry(
            title_frame,
            textvariable=self.title_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            bd=0,
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        # Note category
        category_frame = tk.Frame(right_panel, bg='#1a1a1a')
        category_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            category_frame,
            text="Category:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.note_category_var = tk.StringVar(value="General")

        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.note_category_var,
            values=sorted(list(self.categories)),
            width=15
        )
        self.category_combo.pack(side=tk.LEFT)
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.mark_modified())
        self.category_combo.bind('<Return>', self.add_new_category)

        tk.Label(
            category_frame,
            text="(Type to add new)",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Formatting toolbar
        format_toolbar = tk.Frame(right_panel, bg='#2b2b2b', height=50)
        format_toolbar.pack(fill=tk.X, pady=(0, 5))
        format_toolbar.pack_propagate(False)

        # Font controls
        tk.Button(
            format_toolbar,
            text="B",
            command=lambda: self.apply_format('bold'),
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            format_toolbar,
            text="I",
            command=lambda: self.apply_format('italic'),
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 10, 'italic')
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            format_toolbar,
            text="U",
            command=lambda: self.apply_format('underline'),
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 10, 'underline')
        ).pack(side=tk.LEFT, padx=2)

        # Font size
        tk.Label(
            format_toolbar,
            text="Size:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(10, 5))

        self.font_size_var = tk.StringVar(value="11")
        font_size_combo = ttk.Combobox(
            format_toolbar,
            textvariable=self.font_size_var,
            values=['8', '10', '11', '12', '14', '16', '18', '20', '24'],
            width=5,
            state='readonly'
        )
        font_size_combo.pack(side=tk.LEFT, padx=2)
        font_size_combo.bind('<<ComboboxSelected>>', self.change_font_size)

        # Text color
        tk.Button(
            format_toolbar,
            text="🎨 Color",
            command=self.choose_text_color,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(10, 2))

        # Highlight
        tk.Button(
            format_toolbar,
            text="🖍 Highlight",
            command=self.choose_highlight_color,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        # Clear formatting
        tk.Button(
            format_toolbar,
            text="✖ Clear Format",
            command=self.clear_formatting,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=2)

        # Export
        tk.Button(
            format_toolbar,
            text="📤 Export",
            command=self.export_note,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.RIGHT, padx=2)

        # Text editor
        editor_frame = tk.Frame(right_panel, bg='#1a1a1a')
        editor_frame.pack(fill=tk.BOTH, expand=True)

        text_scrollbar = tk.Scrollbar(editor_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_editor = tk.Text(
            editor_frame,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            font=('Arial', 11),
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10,
            yscrollcommand=text_scrollbar.set,
            undo=True,
            maxundo=-1
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.text_editor.yview)

        self.text_editor.bind('<KeyRelease>', lambda e: self.mark_modified())

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

        self.word_count_label = tk.Label(
            status_bar,
            text="Words: 0 | Characters: 0",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='e'
        )
        self.word_count_label.pack(side=tk.RIGHT, padx=10)

        # Bind word count update
        self.text_editor.bind('<KeyRelease>', self.update_word_count, add='+')

        # Update notes list
        self.update_notes_list()

    def new_note(self):
        """Create a new note"""
        # Save current note if modified
        if self.content_modified and self.current_note_id:
            self.save_current_note()

        # Generate new note ID
        note_id = str(uuid.uuid4())

        # Create note
        note = {
            'id': note_id,
            'title': 'Untitled Note',
            'category': 'General',
            'content': '',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat()
        }

        self.notes[note_id] = note
        self.current_note_id = note_id

        # Clear editor
        self.title_var.set('Untitled Note')
        self.note_category_var.set('General')
        self.text_editor.delete('1.0', tk.END)

        # Update list
        self.update_notes_list()
        self.content_modified = False

        # Focus on title
        self.root.after(100, lambda: self.root.focus_force())

    def save_current_note(self):
        """Save the current note"""
        if not self.current_note_id:
            return

        note = self.notes.get(self.current_note_id)
        if not note:
            return

        # Update note data
        note['title'] = self.title_var.get() or 'Untitled Note'
        note['category'] = self.note_category_var.get()
        note['content'] = self.text_editor.get('1.0', tk.END).strip()
        note['modified'] = datetime.now().isoformat()

        # Save to file
        note_file = self.notes_dir / f"{note['id']}.json"
        try:
            with open(note_file, 'w') as f:
                json.dump(note, f, indent=2)

            self.content_modified = False
            self.status_label.config(text=f"Saved: {note['title']}")
            self.update_notes_list()

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save note:\n{str(e)}")

    def delete_note(self):
        """Delete the current note"""
        if not self.current_note_id:
            messagebox.showwarning("No Note", "No note selected")
            return

        note = self.notes.get(self.current_note_id)
        if not note:
            return

        if messagebox.askyesno("Delete Note", f"Delete '{note['title']}'?"):
            # Delete file
            note_file = self.notes_dir / f"{note['id']}.json"
            try:
                if note_file.exists():
                    note_file.unlink()

                # Remove from memory
                del self.notes[self.current_note_id]
                self.current_note_id = None

                # Clear editor
                self.title_var.set('')
                self.text_editor.delete('1.0', tk.END)

                # Update list
                self.update_notes_list()
                self.status_label.config(text="Note deleted")

            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete note:\n{str(e)}")

    def on_note_select(self, event):
        """Handle note selection"""
        selection = self.notes_listbox.curselection()
        if not selection:
            return

        # Save current note if modified
        if self.content_modified and self.current_note_id:
            self.save_current_note()

        # Get selected note
        index = selection[0]
        note_id = list(self.get_filtered_notes().keys())[index]
        note = self.notes[note_id]

        # Load note
        self.current_note_id = note_id
        self.title_var.set(note['title'])
        self.note_category_var.set(note.get('category', 'General'))

        self.text_editor.delete('1.0', tk.END)
        self.text_editor.insert('1.0', note.get('content', ''))

        self.content_modified = False
        self.status_label.config(text=f"Loaded: {note['title']}")

    def mark_modified(self):
        """Mark current note as modified"""
        self.content_modified = True

    def update_notes_list(self):
        """Update the notes list"""
        self.notes_listbox.delete(0, tk.END)

        filtered_notes = self.get_filtered_notes()

        for note_id, note in filtered_notes.items():
            title = note['title']
            category = note.get('category', 'General')
            modified = datetime.fromisoformat(note['modified']).strftime('%m/%d %H:%M')

            display_text = f"[{category}] {title} - {modified}"
            self.notes_listbox.insert(tk.END, display_text)

            # Highlight current note
            if note_id == self.current_note_id:
                self.notes_listbox.selection_clear(0, tk.END)
                self.notes_listbox.selection_set(tk.END)

    def get_filtered_notes(self):
        """Get filtered notes based on search and category"""
        filtered = {}

        search_term = self.search_var.get().lower()
        category_filter = self.category_filter_var.get()

        for note_id, note in self.notes.items():
            # Category filter
            if category_filter != "All" and note.get('category') != category_filter:
                continue

            # Search filter
            if search_term:
                if search_term not in note['title'].lower() and \
                   search_term not in note.get('content', '').lower():
                    continue

            filtered[note_id] = note

        # Sort by modified date
        sorted_notes = dict(sorted(
            filtered.items(),
            key=lambda x: x[1]['modified'],
            reverse=True
        ))

        return sorted_notes

    def search_notes(self):
        """Search notes"""
        self.update_notes_list()

    def filter_notes(self):
        """Filter notes by category"""
        self.update_notes_list()

    def add_new_category(self, event):
        """Add a new category"""
        new_category = self.note_category_var.get().strip()
        if new_category and new_category not in self.categories:
            self.categories.add(new_category)

            # Update comboboxes
            categories_list = sorted(list(self.categories))
            self.category_combo.config(values=categories_list)

            # Update filter
            filter_values = ["All"] + categories_list
            filter_combo = self.root.nametowidget(str(self.category_filter_var))
            if hasattr(filter_combo, 'config'):
                filter_combo.config(values=filter_values)

            self.mark_modified()

    def apply_format(self, format_type):
        """Apply text formatting"""
        try:
            # Get selected text range
            sel_range = self.text_editor.tag_ranges(tk.SEL)
            if not sel_range:
                return

            start, end = sel_range[0], sel_range[1]

            # Create unique tag
            tag_name = f"{format_type}_{start}_{end}"

            # Apply tag
            self.text_editor.tag_add(tag_name, start, end)

            # Configure tag based on format type
            current_font = font.Font(font=self.text_editor['font'])

            if format_type == 'bold':
                self.text_editor.tag_config(tag_name, font=(current_font.actual()['family'], current_font.actual()['size'], 'bold'))
            elif format_type == 'italic':
                self.text_editor.tag_config(tag_name, font=(current_font.actual()['family'], current_font.actual()['size'], 'italic'))
            elif format_type == 'underline':
                self.text_editor.tag_config(tag_name, underline=True)

            self.mark_modified()

        except Exception as e:
            print(f"Format error: {e}")

    def change_font_size(self, event=None):
        """Change font size of selected text"""
        try:
            size = int(self.font_size_var.get())

            sel_range = self.text_editor.tag_ranges(tk.SEL)
            if sel_range:
                start, end = sel_range[0], sel_range[1]
                tag_name = f"size_{size}_{start}_{end}"

                self.text_editor.tag_add(tag_name, start, end)
                self.text_editor.tag_config(tag_name, font=('Arial', size))

                self.mark_modified()
            else:
                # Change default font size
                self.text_editor.config(font=('Arial', size))

        except ValueError:
            pass

    def choose_text_color(self):
        """Choose text color"""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:
            try:
                sel_range = self.text_editor.tag_ranges(tk.SEL)
                if sel_range:
                    start, end = sel_range[0], sel_range[1]
                    tag_name = f"color_{color[1]}_{start}_{end}"

                    self.text_editor.tag_add(tag_name, start, end)
                    self.text_editor.tag_config(tag_name, foreground=color[1])

                    self.mark_modified()
            except:
                pass

    def choose_highlight_color(self):
        """Choose highlight color"""
        color = colorchooser.askcolor(title="Choose Highlight Color")
        if color[1]:
            try:
                sel_range = self.text_editor.tag_ranges(tk.SEL)
                if sel_range:
                    start, end = sel_range[0], sel_range[1]
                    tag_name = f"highlight_{color[1]}_{start}_{end}"

                    self.text_editor.tag_add(tag_name, start, end)
                    self.text_editor.tag_config(tag_name, background=color[1])

                    self.mark_modified()
            except:
                pass

    def clear_formatting(self):
        """Clear formatting from selected text"""
        try:
            sel_range = self.text_editor.tag_ranges(tk.SEL)
            if sel_range:
                start, end = sel_range[0], sel_range[1]

                # Remove all tags from selection
                for tag in self.text_editor.tag_names(start):
                    if tag != tk.SEL:
                        self.text_editor.tag_remove(tag, start, end)

                self.mark_modified()
        except:
            pass

    def export_note(self):
        """Export current note"""
        if not self.current_note_id:
            messagebox.showwarning("No Note", "No note to export")
            return

        note = self.notes.get(self.current_note_id)
        if not note:
            return

        # Ask for file
        filetypes = [
            ("Text files", "*.txt"),
            ("Markdown files", "*.md"),
            ("All files", "*.*")
        ]

        filename = filedialog.asksaveasfilename(
            title="Export Note",
            defaultextension=".txt",
            initialfile=f"{note['title']}.txt",
            filetypes=filetypes
        )

        if filename:
            try:
                content = self.text_editor.get('1.0', tk.END)

                with open(filename, 'w') as f:
                    f.write(f"Title: {note['title']}\n")
                    f.write(f"Category: {note.get('category', 'General')}\n")
                    f.write(f"Created: {note['created']}\n")
                    f.write(f"Modified: {note['modified']}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    f.write(content)

                self.status_label.config(text=f"Exported to {filename}")

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")

    def update_word_count(self, event=None):
        """Update word and character count"""
        content = self.text_editor.get('1.0', tk.END).strip()

        words = len(content.split()) if content else 0
        chars = len(content)

        self.word_count_label.config(text=f"Words: {words} | Characters: {chars}")

    def load_notes(self):
        """Load all notes from disk"""
        self.notes.clear()

        for note_file in self.notes_dir.glob('*.json'):
            try:
                with open(note_file, 'r') as f:
                    note = json.load(f)
                    self.notes[note['id']] = note

                    # Add category
                    if 'category' in note:
                        self.categories.add(note['category'])

            except Exception as e:
                print(f"Error loading {note_file}: {e}")

    def start_auto_save(self):
        """Start auto-save timer"""
        def auto_save():
            if self.content_modified and self.current_note_id:
                self.save_current_note()

            # Schedule next auto-save
            self.auto_save_job = self.root.after(30000, auto_save)  # 30 seconds

        self.auto_save_job = self.root.after(30000, auto_save)

    def run(self):
        """Run the notes application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        # Save current note
        if self.content_modified and self.current_note_id:
            self.save_current_note()

        # Cancel auto-save
        if self.auto_save_job:
            self.root.after_cancel(self.auto_save_job)

        self.root.destroy()

def main():
    app = NotesApp()
    app.run()

if __name__ == '__main__':
    main()
