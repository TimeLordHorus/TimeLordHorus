#!/usr/bin/env python3
"""
TL Linux - Trash Bin
Graphical trash/recycle bin viewer and manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Add system path
sys.path.insert(0, os.path.expanduser('~/tl-linux/system'))
from trash_manager import get_trash_manager

class TrashBin:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Trash Bin")
        self.root.geometry("900x600")
        self.root.configure(bg='#2b2b2b')

        self.trash_manager = get_trash_manager()

        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🗑️ Trash Bin",
            font=('Arial', 20, 'bold'),
            bg='#1a1a1a',
            fg='#d9534f'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Trash size
        self.size_label = tk.Label(
            header,
            text="0 B",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.size_label.pack(side=tk.RIGHT, padx=20)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2b2b2b')
        toolbar.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            toolbar,
            text="↺ Restore",
            command=self.restore_selected,
            font=('Arial', 10),
            bg='#5cb85c',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="✖ Delete Permanently",
            command=self.delete_selected,
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🗑️ Empty Trash",
            command=self.empty_trash,
            font=('Arial', 10),
            bg='#6a6a6a',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.RIGHT)

        # File list
        list_frame = tk.Frame(self.root, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ('Original Path', 'Deleted', 'Size', 'Type')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=vsb.set,
            selectmode='extended'
        )

        vsb.config(command=self.tree.yview)

        # Column headings
        self.tree.heading('#0', text='Name')
        self.tree.heading('Original Path', text='Original Location')
        self.tree.heading('Deleted', text='Deleted')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Type', text='Type')

        # Column widths
        self.tree.column('#0', width=200)
        self.tree.column('Original Path', width=300)
        self.tree.column('Deleted', width=150)
        self.tree.column('Size', width=100)
        self.tree.column('Type', width=100)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Double-click to restore
        self.tree.bind('<Double-Button-1>', lambda e: self.restore_selected())

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
        self.status_label.pack(side=tk.LEFT, padx=20, pady=5)

        self.item_count_label = tk.Label(
            statusbar,
            text="0 items",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.item_count_label.pack(side=tk.RIGHT, padx=20, pady=5)

    def refresh(self):
        """Refresh trash contents"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get trash items
        try:
            items = self.trash_manager.list_trash()

            for item in items:
                icon = '📁' if item['is_dir'] else '📄'

                self.tree.insert(
                    '',
                    'end',
                    text=f"{icon}  {item['name']}",
                    values=(
                        item.get('original_path', 'Unknown'),
                        self.format_date(item.get('deletion_date')),
                        self.format_size(item['size']),
                        'Folder' if item['is_dir'] else 'File'
                    )
                )

            # Update status
            self.item_count_label.config(text=f"{len(items)} items")

            # Update size
            total_size = self.trash_manager.get_trash_size()
            self.size_label.config(text=self.format_size(total_size))

            if not items:
                self.status_label.config(text="Trash is empty")
            else:
                self.status_label.config(text=f"Showing {len(items)} items")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh trash: {e}")

    def restore_selected(self):
        """Restore selected items"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select items to restore")
            return

        items = [self.tree.item(item_id)['text'].split('  ', 1)[1] for item_id in selection]

        if not messagebox.askyesno("Restore", f"Restore {len(items)} item(s)?"):
            return

        try:
            restored = 0
            for item_name in items:
                self.trash_manager.restore(item_name)
                restored += 1

            self.status_label.config(text=f"Restored {restored} items")
            self.refresh()

        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore: {e}")

    def delete_selected(self):
        """Permanently delete selected items"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select items to delete")
            return

        items = [self.tree.item(item_id)['text'].split('  ', 1)[1] for item_id in selection]

        if not messagebox.askyesno(
            "Permanent Delete",
            f"Permanently delete {len(items)} item(s)?\n\nThis action cannot be undone!",
            icon='warning'
        ):
            return

        try:
            deleted = 0
            for item_name in items:
                self.trash_manager.delete_permanently(item_name)
                deleted += 1

            self.status_label.config(text=f"Permanently deleted {deleted} items")
            self.refresh()

        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete: {e}")

    def empty_trash(self):
        """Empty the entire trash"""
        items = self.trash_manager.list_trash()
        if not items:
            messagebox.showinfo("Empty Trash", "Trash is already empty")
            return

        if not messagebox.askyesno(
            "Empty Trash",
            f"Permanently delete all {len(items)} items?\n\nThis action cannot be undone!",
            icon='warning'
        ):
            return

        try:
            self.trash_manager.empty_trash()
            self.status_label.config(text="Trash emptied")
            self.refresh()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to empty trash: {e}")

    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def format_date(self, date_str):
        """Format deletion date"""
        if not date_str:
            return "Unknown"

        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d %H:%M")
        except:
            return date_str

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = TrashBin()
    app.run()

if __name__ == '__main__':
    main()
