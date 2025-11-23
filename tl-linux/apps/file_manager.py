#!/usr/bin/env python3
"""
TL Linux - File Manager
Comprehensive file and folder management with modern features
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import shutil
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import mimetypes

class FileManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - File Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')

        # State
        self.current_path = os.path.expanduser('~')
        self.history = [self.current_path]
        self.history_index = 0
        self.clipboard = []
        self.clipboard_action = None  # 'copy' or 'cut'
        self.view_mode = 'list'  # 'list' or 'grid'
        self.show_hidden = False
        self.sort_by = 'name'
        self.sort_reverse = False

        # Bookmarks
        self.bookmarks_file = os.path.expanduser('~/.tl-linux/file_manager_bookmarks.json')
        self.bookmarks = self.load_bookmarks()

        # Selection
        self.selected_items = []

        self.setup_ui()
        self.navigate_to(self.current_path)

        # Keyboard bindings
        self.root.bind('<Control-c>', lambda e: self.copy_selected())
        self.root.bind('<Control-x>', lambda e: self.cut_selected())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<F2>', lambda e: self.rename_selected())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-f>', lambda e: self.focus_search())
        self.root.bind('<BackSpace>', lambda e: self.go_up())
        self.root.bind('<Alt-Left>', lambda e: self.go_back())
        self.root.bind('<Alt-Right>', lambda e: self.go_forward())

    def load_bookmarks(self):
        """Load saved bookmarks"""
        default_bookmarks = [
            {'name': 'Home', 'path': os.path.expanduser('~')},
            {'name': 'Documents', 'path': os.path.expanduser('~/Documents')},
            {'name': 'Downloads', 'path': os.path.expanduser('~/Downloads')},
            {'name': 'Pictures', 'path': os.path.expanduser('~/Pictures')},
            {'name': 'Music', 'path': os.path.expanduser('~/Music')},
            {'name': 'Videos', 'path': os.path.expanduser('~/Videos')},
            {'name': 'Desktop', 'path': os.path.expanduser('~/Desktop')},
        ]

        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r') as f:
                    return json.load(f)
        except:
            pass

        return default_bookmarks

    def save_bookmarks(self):
        """Save bookmarks to file"""
        try:
            os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)
            with open(self.bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Toolbar
        toolbar = tk.Frame(self.root, bg='#1a1a1a', height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        # Navigation buttons
        nav_frame = tk.Frame(toolbar, bg='#1a1a1a')
        nav_frame.pack(side=tk.LEFT, padx=10)

        self.back_btn = tk.Button(
            nav_frame,
            text="←",
            command=self.go_back,
            font=('Arial', 14),
            bg='#3a3a3a',
            fg='white',
            padx=10,
            pady=5,
            bd=0
        )
        self.back_btn.pack(side=tk.LEFT, padx=2)

        self.forward_btn = tk.Button(
            nav_frame,
            text="→",
            command=self.go_forward,
            font=('Arial', 14),
            bg='#3a3a3a',
            fg='white',
            padx=10,
            pady=5,
            bd=0
        )
        self.forward_btn.pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav_frame,
            text="↑",
            command=self.go_up,
            font=('Arial', 14),
            bg='#3a3a3a',
            fg='white',
            padx=10,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav_frame,
            text="⌂",
            command=lambda: self.navigate_to(os.path.expanduser('~')),
            font=('Arial', 14),
            bg='#3a3a3a',
            fg='white',
            padx=10,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=2)

        # Address bar
        addr_frame = tk.Frame(toolbar, bg='#1a1a1a')
        addr_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(
            addr_frame,
            textvariable=self.address_var,
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white'
        )
        self.address_entry.pack(fill=tk.X, ipady=5)
        self.address_entry.bind('<Return>', lambda e: self.navigate_to(self.address_var.get()))

        # View controls
        view_frame = tk.Frame(toolbar, bg='#1a1a1a')
        view_frame.pack(side=tk.RIGHT, padx=10)

        tk.Button(
            view_frame,
            text="☰",
            command=lambda: self.set_view_mode('list'),
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='white',
            padx=8,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            view_frame,
            text="▦",
            command=lambda: self.set_view_mode('grid'),
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='white',
            padx=8,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=2)

        # Search
        search_frame = tk.Frame(toolbar, bg='#1a1a1a')
        search_frame.pack(side=tk.RIGHT, padx=10)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            width=20
        )
        self.search_entry.pack(side=tk.LEFT)

        # Main container
        main_container = tk.Frame(self.root, bg='#2b2b2b')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar with bookmarks
        sidebar = tk.Frame(main_container, bg='#1a1a1a', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Bookmarks",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=10)

        # Bookmarks list
        self.bookmarks_listbox = tk.Listbox(
            sidebar,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='white',
            selectbackground='#4a9eff',
            selectforeground='white',
            bd=0,
            highlightthickness=0
        )
        self.bookmarks_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.bookmarks_listbox.bind('<<ListboxSelect>>', self.bookmark_selected)

        self.update_bookmarks_list()

        # Add bookmark button
        tk.Button(
            sidebar,
            text="+ Add Bookmark",
            command=self.add_bookmark,
            font=('Arial', 9),
            bg='#4a9eff',
            fg='white',
            bd=0,
            pady=5
        ).pack(fill=tk.X, padx=5, pady=5)

        # File view area
        view_container = tk.Frame(main_container, bg='#2b2b2b')
        view_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # File list/grid
        self.file_frame = tk.Frame(view_container, bg='#2b2b2b')
        self.file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create treeview for list view
        self.setup_list_view()

        # Status bar
        statusbar = tk.Frame(self.root, bg='#1a1a1a', height=30)
        statusbar.pack(fill=tk.X)
        statusbar.pack_propagate(False)

        self.status_label = tk.Label(
            statusbar,
            text="Ready",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.item_count_label = tk.Label(
            statusbar,
            text="0 items",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.item_count_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Context menu
        self.create_context_menu()

    def setup_list_view(self):
        """Setup list view with treeview"""
        # Clear existing
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        # Scrollbars
        vsb = ttk.Scrollbar(self.file_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(self.file_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ('Type', 'Size', 'Modified')
        self.file_tree = ttk.Treeview(
            self.file_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='extended'
        )

        vsb.config(command=self.file_tree.yview)
        hsb.config(command=self.file_tree.xview)

        # Column headings
        self.file_tree.heading('#0', text='Name', command=lambda: self.sort_files('name'))
        self.file_tree.heading('Type', text='Type', command=lambda: self.sort_files('type'))
        self.file_tree.heading('Size', text='Size', command=lambda: self.sort_files('size'))
        self.file_tree.heading('Modified', text='Modified', command=lambda: self.sort_files('modified'))

        # Column widths
        self.file_tree.column('#0', width=400)
        self.file_tree.column('Type', width=150)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=200)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bindings
        self.file_tree.bind('<Double-Button-1>', self.item_double_clicked)
        self.file_tree.bind('<Button-3>', self.show_context_menu)
        self.file_tree.bind('<<TreeviewSelect>>', self.selection_changed)

    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#2b2b2b', fg='white')
        self.context_menu.add_command(label="Open", command=self.open_selected)
        self.context_menu.add_command(label="Open With...", command=self.open_with)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cut", command=self.cut_selected, accelerator="Ctrl+X")
        self.context_menu.add_command(label="Copy", command=self.copy_selected, accelerator="Ctrl+C")
        self.context_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename", command=self.rename_selected, accelerator="F2")
        self.context_menu.add_command(label="Delete", command=self.delete_selected, accelerator="Del")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Properties", command=self.show_properties)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="New Folder", command=self.create_folder)
        self.context_menu.add_command(label="New File", command=self.create_file)

    def navigate_to(self, path):
        """Navigate to a directory"""
        path = os.path.expanduser(path)

        if not os.path.exists(path):
            messagebox.showerror("Error", f"Path does not exist: {path}")
            return

        if not os.path.isdir(path):
            # If it's a file, open it
            self.open_file(path)
            return

        self.current_path = os.path.abspath(path)
        self.address_var.set(self.current_path)

        # Update history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_path)
        self.history_index = len(self.history) - 1

        self.update_navigation_buttons()
        self.refresh_view()

    def refresh_view(self):
        """Refresh the file view"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        try:
            # Get directory contents
            items = []
            for entry in os.scandir(self.current_path):
                if not self.show_hidden and entry.name.startswith('.'):
                    continue

                try:
                    stat = entry.stat()
                    is_dir = entry.is_dir()

                    item = {
                        'name': entry.name,
                        'path': entry.path,
                        'is_dir': is_dir,
                        'type': 'Folder' if is_dir else self.get_file_type(entry.name),
                        'size': 0 if is_dir else stat.st_size,
                        'modified': stat.st_mtime
                    }
                    items.append(item)
                except (PermissionError, OSError):
                    continue

            # Sort items
            items.sort(key=lambda x: (not x['is_dir'], self.get_sort_key(x)))

            if self.sort_reverse:
                items.reverse()

            # Populate tree
            for item in items:
                icon = '📁' if item['is_dir'] else self.get_file_icon(item['name'])

                self.file_tree.insert(
                    '',
                    'end',
                    text=f"{icon}  {item['name']}",
                    values=(
                        item['type'],
                        self.format_size(item['size']) if not item['is_dir'] else '',
                        datetime.fromtimestamp(item['modified']).strftime('%Y-%m-%d %H:%M')
                    ),
                    tags=('directory' if item['is_dir'] else 'file',)
                )

            # Update status
            self.item_count_label.config(text=f"{len(items)} items")
            self.status_label.config(text=f"Showing {self.current_path}")

        except PermissionError:
            messagebox.showerror("Permission Denied", f"Cannot access {self.current_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read directory: {e}")

    def get_sort_key(self, item):
        """Get sort key for an item"""
        if self.sort_by == 'name':
            return item['name'].lower()
        elif self.sort_by == 'type':
            return item['type'].lower()
        elif self.sort_by == 'size':
            return item['size']
        elif self.sort_by == 'modified':
            return item['modified']
        return item['name'].lower()

    def sort_files(self, column):
        """Sort files by column"""
        if self.sort_by == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = column
            self.sort_reverse = False
        self.refresh_view()

    def get_file_type(self, filename):
        """Get file type description"""
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            main_type = mime_type.split('/')[0]
            type_map = {
                'text': 'Text Document',
                'image': 'Image',
                'video': 'Video',
                'audio': 'Audio',
                'application': 'Application'
            }
            return type_map.get(main_type, mime_type)

        ext = os.path.splitext(filename)[1].upper()
        if ext:
            return f"{ext[1:]} File"
        return 'File'

    def get_file_icon(self, filename):
        """Get emoji icon for file type"""
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            main_type = mime_type.split('/')[0]
            icon_map = {
                'text': '📄',
                'image': '🖼️',
                'video': '🎬',
                'audio': '🎵',
                'application': '📦'
            }
            return icon_map.get(main_type, '📄')

        ext = os.path.splitext(filename)[1].lower()
        ext_icons = {
            '.py': '🐍',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.pdf': '📕',
            '.doc': '📘',
            '.docx': '📘',
            '.xls': '📊',
            '.xlsx': '📊'
        }
        return ext_icons.get(ext, '📄')

    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def filter_files(self, *args):
        """Filter files by search term"""
        # For now, just refresh - would implement filtering
        self.refresh_view()

    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.address_var.set(self.current_path)
            self.refresh_view()
            self.update_navigation_buttons()

    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.address_var.set(self.current_path)
            self.refresh_view()
            self.update_navigation_buttons()

    def go_up(self):
        """Go to parent directory"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.navigate_to(parent)

    def update_navigation_buttons(self):
        """Update navigation button states"""
        self.back_btn.config(state='normal' if self.history_index > 0 else 'disabled')
        self.forward_btn.config(state='normal' if self.history_index < len(self.history) - 1 else 'disabled')

    def item_double_clicked(self, event):
        """Handle double-click on item"""
        selection = self.file_tree.selection()
        if not selection:
            return

        item = self.file_tree.item(selection[0])
        name = item['text'].split('  ', 1)[1]  # Remove icon
        path = os.path.join(self.current_path, name)

        if os.path.isdir(path):
            self.navigate_to(path)
        else:
            self.open_file(path)

    def selection_changed(self, event):
        """Handle selection change"""
        self.selected_items = []
        for item_id in self.file_tree.selection():
            item = self.file_tree.item(item_id)
            name = item['text'].split('  ', 1)[1]
            self.selected_items.append(os.path.join(self.current_path, name))

    def get_selected_paths(self):
        """Get paths of selected items"""
        paths = []
        for item_id in self.file_tree.selection():
            item = self.file_tree.item(item_id)
            name = item['text'].split('  ', 1)[1]
            paths.append(os.path.join(self.current_path, name))
        return paths

    def open_selected(self):
        """Open selected file(s)"""
        paths = self.get_selected_paths()
        for path in paths:
            self.open_file(path)

    def open_file(self, path):
        """Open file with default application"""
        try:
            subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def open_with(self):
        """Open file with specific application"""
        paths = self.get_selected_paths()
        if not paths:
            return

        # Would show app chooser dialog
        messagebox.showinfo("Open With", "App chooser dialog would appear here")

    def copy_selected(self):
        """Copy selected items to clipboard"""
        self.clipboard = self.get_selected_paths()
        self.clipboard_action = 'copy'
        self.status_label.config(text=f"Copied {len(self.clipboard)} items")

    def cut_selected(self):
        """Cut selected items to clipboard"""
        self.clipboard = self.get_selected_paths()
        self.clipboard_action = 'cut'
        self.status_label.config(text=f"Cut {len(self.clipboard)} items")

    def paste(self):
        """Paste items from clipboard"""
        if not self.clipboard:
            return

        try:
            for source in self.clipboard:
                name = os.path.basename(source)
                dest = os.path.join(self.current_path, name)

                # Handle name conflicts
                if os.path.exists(dest):
                    dest = self.get_unique_name(dest)

                if self.clipboard_action == 'copy':
                    if os.path.isdir(source):
                        shutil.copytree(source, dest)
                    else:
                        shutil.copy2(source, dest)
                elif self.clipboard_action == 'cut':
                    shutil.move(source, dest)

            if self.clipboard_action == 'cut':
                self.clipboard = []
                self.clipboard_action = None

            self.refresh_view()
            self.status_label.config(text="Paste completed")

        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste: {e}")

    def get_unique_name(self, path):
        """Get unique filename if conflicts exist"""
        base, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists(path):
            path = f"{base} ({counter}){ext}"
            counter += 1
        return path

    def delete_selected(self):
        """Delete selected items"""
        paths = self.get_selected_paths()
        if not paths:
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete {len(paths)} item(s)?"):
            return

        try:
            for path in paths:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

            self.refresh_view()
            self.status_label.config(text=f"Deleted {len(paths)} items")

        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete: {e}")

    def rename_selected(self):
        """Rename selected item"""
        paths = self.get_selected_paths()
        if len(paths) != 1:
            messagebox.showwarning("Rename", "Please select exactly one item to rename")
            return

        old_path = paths[0]
        old_name = os.path.basename(old_path)

        new_name = simpledialog.askstring("Rename", "New name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return

        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            os.rename(old_path, new_path)
            self.refresh_view()
            self.status_label.config(text=f"Renamed to {new_name}")
        except Exception as e:
            messagebox.showerror("Rename Error", f"Failed to rename: {e}")

    def create_folder(self):
        """Create new folder"""
        name = simpledialog.askstring("New Folder", "Folder name:")
        if not name:
            return

        path = os.path.join(self.current_path, name)

        try:
            os.makedirs(path)
            self.refresh_view()
            self.status_label.config(text=f"Created folder: {name}")
        except Exception as e:
            messagebox.showerror("Create Folder Error", f"Failed to create folder: {e}")

    def create_file(self):
        """Create new file"""
        name = simpledialog.askstring("New File", "File name:")
        if not name:
            return

        path = os.path.join(self.current_path, name)

        try:
            Path(path).touch()
            self.refresh_view()
            self.status_label.config(text=f"Created file: {name}")
        except Exception as e:
            messagebox.showerror("Create File Error", f"Failed to create file: {e}")

    def show_properties(self):
        """Show properties of selected item"""
        paths = self.get_selected_paths()
        if not paths:
            return

        path = paths[0]

        try:
            stat = os.stat(path)
            is_dir = os.path.isdir(path)

            props = f"""Properties: {os.path.basename(path)}

Path: {path}
Type: {'Folder' if is_dir else 'File'}
Size: {self.format_size(stat.st_size) if not is_dir else self.get_folder_size(path)}
Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
Permissions: {oct(stat.st_mode)[-3:]}
Owner: {stat.st_uid}
"""
            messagebox.showinfo("Properties", props)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get properties: {e}")

    def get_folder_size(self, path):
        """Get total size of folder"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += self.get_folder_size(entry.path)
        except:
            pass
        return self.format_size(total)

    def select_all(self):
        """Select all items"""
        self.file_tree.selection_set(self.file_tree.get_children())

    def focus_search(self):
        """Focus the search box"""
        self.search_entry.focus()

    def show_context_menu(self, event):
        """Show context menu"""
        # Select item under cursor
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)

        self.context_menu.post(event.x_root, event.y_root)

    def set_view_mode(self, mode):
        """Set view mode (list or grid)"""
        self.view_mode = mode
        # Would switch between list and grid views
        # For now, just using list view

    def bookmark_selected(self, event):
        """Navigate to selected bookmark"""
        selection = self.bookmarks_listbox.curselection()
        if selection:
            index = selection[0]
            bookmark = self.bookmarks[index]
            self.navigate_to(bookmark['path'])

    def add_bookmark(self):
        """Add current location to bookmarks"""
        name = simpledialog.askstring("Add Bookmark", "Bookmark name:", initialvalue=os.path.basename(self.current_path))
        if not name:
            return

        self.bookmarks.append({'name': name, 'path': self.current_path})
        self.save_bookmarks()
        self.update_bookmarks_list()

    def update_bookmarks_list(self):
        """Update bookmarks listbox"""
        self.bookmarks_listbox.delete(0, tk.END)
        for bookmark in self.bookmarks:
            icon = '📁'
            self.bookmarks_listbox.insert(tk.END, f"{icon}  {bookmark['name']}")

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = FileManager()
    app.run()

if __name__ == '__main__':
    main()
