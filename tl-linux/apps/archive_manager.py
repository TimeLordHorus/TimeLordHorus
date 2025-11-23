#!/usr/bin/env python3
"""
TL Linux - Archive Manager
Create, extract, and browse compressed archives (.zip, .tar, .7z, etc.)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import tarfile
import zipfile
import shutil
from pathlib import Path

class ArchiveManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Archive Manager")
        self.root.geometry("900x650")
        self.root.configure(bg='#1a1a1a')

        # Current archive
        self.current_archive = None
        self.archive_type = None

        # Supported formats
        self.archive_formats = {
            '.zip': 'ZIP Archive',
            '.tar': 'TAR Archive',
            '.tar.gz': 'Gzip Compressed TAR',
            '.tgz': 'Gzip Compressed TAR',
            '.tar.bz2': 'Bzip2 Compressed TAR',
            '.tbz2': 'Bzip2 Compressed TAR',
            '.tar.xz': 'XZ Compressed TAR',
            '.7z': '7-Zip Archive',
            '.rar': 'RAR Archive',
            '.gz': 'Gzip Compressed File',
            '.bz2': 'Bzip2 Compressed File',
            '.xz': 'XZ Compressed File'
        }

        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🗜️ Archive Manager",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#1a1a1a')
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        # Create archive button
        tk.Button(
            toolbar,
            text="➕ Create Archive",
            command=self.create_archive_dialog,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)

        # Open archive button
        tk.Button(
            toolbar,
            text="📂 Open Archive",
            command=self.open_archive,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Extract button
        tk.Button(
            toolbar,
            text="📤 Extract",
            command=self.extract_archive_dialog,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Extract here button
        tk.Button(
            toolbar,
            text="📥 Extract Here",
            command=self.extract_here,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Main content area
        content = tk.Frame(self.root, bg='#1a1a1a')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Archive info panel
        info_panel = tk.LabelFrame(
            content,
            text="Archive Information",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        info_panel.pack(fill=tk.X, pady=(0, 10))

        info_grid = tk.Frame(info_panel, bg='#1a1a1a')
        info_grid.pack(fill=tk.X, padx=10, pady=10)

        # Archive name
        tk.Label(
            info_grid,
            text="Archive:",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 9)
        ).grid(row=0, column=0, sticky='w', pady=2)

        self.archive_name_label = tk.Label(
            info_grid,
            text="No archive loaded",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        )
        self.archive_name_label.grid(row=0, column=1, sticky='w', padx=10, pady=2)

        # Type
        tk.Label(
            info_grid,
            text="Type:",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 9)
        ).grid(row=1, column=0, sticky='w', pady=2)

        self.archive_type_label = tk.Label(
            info_grid,
            text="-",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        )
        self.archive_type_label.grid(row=1, column=1, sticky='w', padx=10, pady=2)

        # Size
        tk.Label(
            info_grid,
            text="Size:",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 9)
        ).grid(row=2, column=0, sticky='w', pady=2)

        self.archive_size_label = tk.Label(
            info_grid,
            text="-",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        )
        self.archive_size_label.grid(row=2, column=1, sticky='w', padx=10, pady=2)

        # Files
        tk.Label(
            info_grid,
            text="Files:",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 9)
        ).grid(row=3, column=0, sticky='w', pady=2)

        self.archive_files_label = tk.Label(
            info_grid,
            text="-",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        )
        self.archive_files_label.grid(row=3, column=1, sticky='w', padx=10, pady=2)

        # Contents tree
        tree_frame = tk.Frame(content, bg='#1a1a1a')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            tree_frame,
            text="Archive Contents:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10, 'bold'),
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))

        # Treeview
        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Size', 'Modified'),
            yscrollcommand=tree_scroll.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Configure columns
        self.tree.heading('#0', text='Name', anchor='w')
        self.tree.heading('Size', text='Size', anchor='w')
        self.tree.heading('Modified', text='Modified', anchor='w')

        self.tree.column('#0', width=400)
        self.tree.column('Size', width=100)
        self.tree.column('Modified', width=200)

        # Style treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview', background='#2b2b2b', foreground='white', fieldbackground='#2b2b2b')
        style.map('Treeview', background=[('selected', '#4a9eff')])

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

    def create_archive_dialog(self):
        """Show create archive dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Archive")
        dialog.geometry("500x400")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Create New Archive",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)

        # Archive type
        type_frame = tk.Frame(dialog, bg='#2b2b2b')
        type_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(
            type_frame,
            text="Archive Type:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(anchor='w')

        archive_type_var = tk.StringVar(value='.tar.gz')
        for ext, desc in [('.zip', 'ZIP'), ('.tar.gz', 'TAR.GZ'), ('.tar.bz2', 'TAR.BZ2'), ('.7z', '7-Zip')]:
            tk.Radiobutton(
                type_frame,
                text=desc,
                variable=archive_type_var,
                value=ext,
                bg='#2b2b2b',
                fg='white',
                selectcolor='#1a1a1a',
                font=('Arial', 9)
            ).pack(anchor='w', padx=20)

        # Output location
        output_frame = tk.Frame(dialog, bg='#2b2b2b')
        output_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(
            output_frame,
            text="Save As:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(anchor='w')

        output_entry = tk.Entry(
            output_frame,
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            font=('Arial', 10)
        )
        output_entry.pack(fill=tk.X, pady=(5, 0))

        def browse_output():
            ext = archive_type_var.get()
            filename = filedialog.asksaveasfilename(
                defaultextension=ext,
                filetypes=[(f"{ext} archive", f"*{ext}"), ("All files", "*")]
            )
            if filename:
                output_entry.delete(0, tk.END)
                output_entry.insert(0, filename)

        tk.Button(
            output_frame,
            text="Browse...",
            command=browse_output,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=('Arial', 9)
        ).pack(anchor='e', pady=(5, 0))

        # Files to add
        files_frame = tk.Frame(dialog, bg='#2b2b2b')
        files_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(
            files_frame,
            text="Files/Folders to Add:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(anchor='w')

        files_list = tk.Listbox(
            files_frame,
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        )
        files_list.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        def add_files():
            files = filedialog.askopenfilenames()
            for file in files:
                files_list.insert(tk.END, file)

        def add_folder():
            folder = filedialog.askdirectory()
            if folder:
                files_list.insert(tk.END, folder)

        buttons_frame = tk.Frame(files_frame, bg='#2b2b2b')
        buttons_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Button(
            buttons_frame,
            text="Add Files",
            command=add_files,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            buttons_frame,
            text="Add Folder",
            command=add_folder,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=('Arial', 8)
        ).pack(side=tk.LEFT)

        # Create button
        def do_create():
            output_file = output_entry.get()
            if not output_file:
                messagebox.showwarning("Missing Information", "Please specify output file.")
                return

            items = list(files_list.get(0, tk.END))
            if not items:
                messagebox.showwarning("Missing Information", "Please add files or folders to archive.")
                return

            dialog.destroy()
            self.create_archive(output_file, items, archive_type_var.get())

        tk.Button(
            dialog,
            text="Create Archive",
            command=do_create,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=30,
            pady=10,
            font=('Arial', 10, 'bold')
        ).pack(pady=20)

    def create_archive(self, output_file, items, archive_type):
        """Create archive from files/folders"""
        self.status_label.config(text=f"Creating archive: {os.path.basename(output_file)}...")

        def create():
            try:
                if archive_type == '.zip':
                    self.create_zip(output_file, items)
                elif archive_type in ['.tar.gz', '.tar.bz2', '.tar']:
                    self.create_tar(output_file, items, archive_type)
                elif archive_type == '.7z':
                    self.create_7z(output_file, items)
                else:
                    raise ValueError(f"Unsupported archive type: {archive_type}")

                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Archive created successfully:\n{output_file}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="Archive created"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to create archive:\n{str(e)}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="Error creating archive"))

        threading.Thread(target=create, daemon=True).start()

    def create_zip(self, output_file, items):
        """Create ZIP archive"""
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in items:
                if os.path.isfile(item):
                    zipf.write(item, os.path.basename(item))
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(item))
                            zipf.write(file_path, arcname)

    def create_tar(self, output_file, items, archive_type):
        """Create TAR archive"""
        mode_map = {
            '.tar': 'w',
            '.tar.gz': 'w:gz',
            '.tar.bz2': 'w:bz2'
        }
        mode = mode_map.get(archive_type, 'w')

        with tarfile.open(output_file, mode) as tar:
            for item in items:
                tar.add(item, arcname=os.path.basename(item))

    def create_7z(self, output_file, items):
        """Create 7z archive using 7z command"""
        cmd = ['7z', 'a', output_file] + items
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"7z command failed: {result.stderr}")

    def open_archive(self):
        """Open and browse archive"""
        file_path = filedialog.askopenfilename(
            title="Open Archive",
            filetypes=[
                ("All archives", "*.zip *.tar *.tar.gz *.tgz *.tar.bz2 *.7z *.rar"),
                ("ZIP files", "*.zip"),
                ("TAR files", "*.tar *.tar.gz *.tar.bz2"),
                ("All files", "*")
            ]
        )

        if file_path:
            self.load_archive(file_path)

    def load_archive(self, file_path):
        """Load and display archive contents"""
        self.current_archive = file_path
        self.archive_type = self.detect_archive_type(file_path)

        # Update info
        self.archive_name_label.config(text=os.path.basename(file_path))
        self.archive_type_label.config(text=self.archive_formats.get(self.archive_type, 'Unknown'))

        file_size = os.path.getsize(file_path)
        self.archive_size_label.config(text=self.format_size(file_size))

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # List contents
        try:
            if self.archive_type == '.zip':
                self.list_zip_contents(file_path)
            elif self.archive_type in ['.tar', '.tar.gz', '.tar.bz2', '.tgz', '.tbz2']:
                self.list_tar_contents(file_path)
            elif self.archive_type == '.7z':
                self.list_7z_contents(file_path)

            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read archive:\n{str(e)}")

    def detect_archive_type(self, file_path):
        """Detect archive type from file extension"""
        file_path_lower = file_path.lower()
        for ext in ['.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2']:
            if file_path_lower.endswith(ext):
                return ext
        return os.path.splitext(file_path)[1].lower()

    def list_zip_contents(self, file_path):
        """List ZIP archive contents"""
        with zipfile.ZipFile(file_path, 'r') as zipf:
            file_count = 0
            for info in zipf.filelist:
                self.tree.insert(
                    '',
                    tk.END,
                    text=info.filename,
                    values=(self.format_size(info.file_size), info.date_time)
                )
                file_count += 1

            self.archive_files_label.config(text=str(file_count))

    def list_tar_contents(self, file_path):
        """List TAR archive contents"""
        with tarfile.open(file_path, 'r:*') as tar:
            file_count = 0
            for member in tar.getmembers():
                mtime = ""
                if member.mtime:
                    from datetime import datetime
                    mtime = datetime.fromtimestamp(member.mtime).strftime('%Y-%m-%d %H:%M:%S')

                self.tree.insert(
                    '',
                    tk.END,
                    text=member.name,
                    values=(self.format_size(member.size), mtime)
                )
                file_count += 1

            self.archive_files_label.config(text=str(file_count))

    def list_7z_contents(self, file_path):
        """List 7z archive contents using 7z command"""
        result = subprocess.run(['7z', 'l', file_path], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse 7z output
            lines = result.stdout.split('\n')
            file_count = 0
            for line in lines:
                # Simple parsing - would need more robust parsing in production
                if line.strip() and not line.startswith('-'):
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            date = parts[0]
                            time = parts[1]
                            size = parts[3]
                            name = ' '.join(parts[5:])
                            if name and name not in ['Name', 'Path']:
                                self.tree.insert(
                                    '',
                                    tk.END,
                                    text=name,
                                    values=(size, f"{date} {time}")
                                )
                                file_count += 1
                        except:
                            pass

            self.archive_files_label.config(text=str(file_count))

    def extract_archive_dialog(self):
        """Show extract dialog"""
        if not self.current_archive:
            messagebox.showwarning("No Archive", "Please open an archive first.")
            return

        output_dir = filedialog.askdirectory(title="Extract To")
        if output_dir:
            self.extract_archive(self.current_archive, output_dir)

    def extract_here(self):
        """Extract archive to its current directory"""
        if not self.current_archive:
            messagebox.showwarning("No Archive", "Please open an archive first.")
            return

        output_dir = os.path.dirname(self.current_archive)
        self.extract_archive(self.current_archive, output_dir)

    def extract_archive(self, archive_path, output_dir):
        """Extract archive"""
        self.status_label.config(text=f"Extracting {os.path.basename(archive_path)}...")

        def extract():
            try:
                archive_type = self.detect_archive_type(archive_path)

                if archive_type == '.zip':
                    with zipfile.ZipFile(archive_path, 'r') as zipf:
                        zipf.extractall(output_dir)
                elif archive_type in ['.tar', '.tar.gz', '.tar.bz2', '.tgz', '.tbz2', '.tar.xz']:
                    with tarfile.open(archive_path, 'r:*') as tar:
                        tar.extractall(output_dir)
                elif archive_type == '.7z':
                    subprocess.run(['7z', 'x', archive_path, f'-o{output_dir}'], check=True)
                else:
                    raise ValueError(f"Unsupported archive type: {archive_type}")

                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Archive extracted to:\n{output_dir}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="Extraction complete"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to extract archive:\n{str(e)}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="Extraction failed"))

        threading.Thread(target=extract, daemon=True).start()

    def format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def run(self):
        """Run the archive manager"""
        self.root.mainloop()

def main():
    manager = ArchiveManager()
    manager.run()

if __name__ == '__main__':
    main()
