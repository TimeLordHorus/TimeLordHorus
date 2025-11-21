#!/usr/bin/env python3
"""
TL Linux - IPFS Storage Manager
Manage decentralized file storage with IPFS
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import sys
from pathlib import Path
from datetime import datetime
import threading

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.ipfs_node import IPFSNode, get_global_node

class IPFSStorageManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌐 TL IPFS Storage")
        self.root.geometry("1000x700")

        self.ipfs_node = get_global_node()
        self.config_file = Path.home() / '.config' / 'tl-linux' / 'ipfs_storage.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Storage index (maps friendly names to IPFS hashes)
        self.storage_index = self.load_index()

        self.setup_ui()
        self.check_ipfs_status()

    def load_index(self):
        """Load storage index"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'files': {}, 'folders': {}, 'media': {}}

    def save_index(self):
        """Save storage index"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.storage_index, f, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files", command=self.add_files)
        file_menu.add_command(label="Add Folder", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Import from Hash", command=self.import_from_hash)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        ipfs_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="IPFS", menu=ipfs_menu)
        ipfs_menu.add_command(label="Start Daemon", command=self.start_daemon)
        ipfs_menu.add_command(label="Stop Daemon", command=self.stop_daemon)
        ipfs_menu.add_separator()
        ipfs_menu.add_command(label="Node Info", command=self.show_node_info)
        ipfs_menu.add_command(label="Peers", command=self.show_peers)
        ipfs_menu.add_command(label="Statistics", command=self.show_stats)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2c3e50', pady=10)
        toolbar.pack(fill=tk.X)

        # IPFS Status
        status_frame = tk.Frame(toolbar, bg='#2c3e50')
        status_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(status_frame, text="IPFS Status:", bg='#2c3e50', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

        self.status_indicator = tk.Label(status_frame, text="●", font=('Arial', 16), bg='#2c3e50', fg='#e74c3c')
        self.status_indicator.pack(side=tk.LEFT)

        self.status_label = tk.Label(status_frame, text="Not Running", bg='#2c3e50', fg='white', font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="🚀 Start IPFS", command=self.start_daemon, bg='#27ae60', fg='white', relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="⏸️ Stop IPFS", command=self.stop_daemon, bg='#e74c3c', fg='white', relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=15, fill=tk.Y)

        tk.Button(toolbar, text="➕ Add Files", command=self.add_files, bg='#3498db', fg='white', relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="📁 Add Folder", command=self.add_folder, bg='#3498db', fg='white', relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        # Main content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook for different views
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Files tab
        files_frame = tk.Frame(notebook, bg='white')
        notebook.add(files_frame, text="📄 Files")

        # Files tree
        files_tree_frame = tk.Frame(files_frame)
        files_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        files_scroll = tk.Scrollbar(files_tree_frame)
        files_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.files_tree = ttk.Treeview(
            files_tree_frame,
            columns=('Hash', 'Size', 'Date', 'Pinned'),
            show='tree headings',
            yscrollcommand=files_scroll.set
        )

        self.files_tree.heading('#0', text='Name')
        self.files_tree.heading('Hash', text='IPFS Hash')
        self.files_tree.heading('Size', text='Size')
        self.files_tree.heading('Date', text='Date Added')
        self.files_tree.heading('Pinned', text='Pinned')

        self.files_tree.column('#0', width=250)
        self.files_tree.column('Hash', width=400)
        self.files_tree.column('Size', width=100)
        self.files_tree.column('Date', width=150)
        self.files_tree.column('Pinned', width=80)

        self.files_tree.pack(fill=tk.BOTH, expand=True)
        files_scroll.config(command=self.files_tree.yview)

        # Context menu for files
        self.files_tree.bind('<Button-3>', self.show_file_context_menu)

        # File actions
        files_actions = tk.Frame(files_frame, bg='white', pady=5)
        files_actions.pack(fill=tk.X)

        tk.Button(files_actions, text="📥 Download", command=self.download_selected, bg='#2ecc71', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(files_actions, text="📋 Copy Hash", command=self.copy_hash, bg='#3498db', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(files_actions, text="🌐 Open in Gateway", command=self.open_in_gateway, bg='#9b59b6', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(files_actions, text="📌 Pin/Unpin", command=self.toggle_pin, bg='#f39c12', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(files_actions, text="🗑️ Remove", command=self.remove_selected, bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        # Media tab
        media_frame = tk.Frame(notebook, bg='white')
        notebook.add(media_frame, text="🎵 Media Library")

        media_label = tk.Label(
            media_frame,
            text="Media files stored in IPFS\n(Audio, Video, Images)",
            font=('Arial', 12),
            bg='white',
            fg='#7f8c8d',
            pady=20
        )
        media_label.pack()

        # Media tree
        media_tree_frame = tk.Frame(media_frame)
        media_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        media_scroll = tk.Scrollbar(media_tree_frame)
        media_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.media_tree = ttk.Treeview(
            media_tree_frame,
            columns=('Hash', 'Type', 'Date'),
            show='tree headings',
            yscrollcommand=media_scroll.set
        )

        self.media_tree.heading('#0', text='Name')
        self.media_tree.heading('Hash', text='IPFS Hash')
        self.media_tree.heading('Type', text='Type')
        self.media_tree.heading('Date', text='Date Added')

        self.media_tree.column('#0', width=300)
        self.media_tree.column('Hash', width=400)
        self.media_tree.column('Type', width=100)
        self.media_tree.column('Date', width=150)

        self.media_tree.pack(fill=tk.BOTH, expand=True)
        media_scroll.config(command=self.media_tree.yview)

        self.media_tree.bind('<Double-1>', self.play_media)

        # Pins tab
        pins_frame = tk.Frame(notebook, bg='white')
        notebook.add(pins_frame, text="📌 Pinned Items")

        tk.Button(
            pins_frame,
            text="🔄 Refresh Pins",
            command=self.refresh_pins,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(pady=10)

        pins_tree_frame = tk.Frame(pins_frame)
        pins_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        pins_scroll = tk.Scrollbar(pins_tree_frame)
        pins_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.pins_tree = ttk.Treeview(
            pins_tree_frame,
            columns=('Type',),
            show='tree headings',
            yscrollcommand=pins_scroll.set
        )

        self.pins_tree.heading('#0', text='IPFS Hash')
        self.pins_tree.heading('Type', text='Pin Type')

        self.pins_tree.column('#0', width=600)
        self.pins_tree.column('Type', width=150)

        self.pins_tree.pack(fill=tk.BOTH, expand=True)
        pins_scroll.config(command=self.pins_tree.yview)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load initial data
        self.refresh_files_view()
        self.refresh_media_view()

    def check_ipfs_status(self):
        """Check IPFS daemon status"""
        def check():
            if self.ipfs_node.check_daemon_status():
                self.ipfs_node.is_running = True
                self.status_indicator.config(fg='#27ae60')
                self.status_label.config(text="Running")

                # Get node ID
                node_id, _ = self.ipfs_node.get_node_id()
                if node_id:
                    self.status_label.config(text=f"Running - {node_id[:8]}...")
            else:
                self.ipfs_node.is_running = False
                self.status_indicator.config(fg='#e74c3c')
                self.status_label.config(text="Not Running")

        threading.Thread(target=check, daemon=True).start()

    def start_daemon(self):
        """Start IPFS daemon"""
        self.status_bar.config(text="Starting IPFS daemon...")

        def start():
            if not self.ipfs_node.is_ipfs_installed():
                self.root.after(0, lambda: messagebox.showerror(
                    "IPFS Not Installed",
                    "IPFS is not installed on your system.\n\n"
                    "Please install IPFS:\n"
                    "• Visit https://docs.ipfs.tech/install/\n"
                    "• Or run: sudo snap install ipfs\n"
                    "• Or download from https://dist.ipfs.tech/"
                ))
                return

            success, msg = self.ipfs_node.start_daemon()

            self.root.after(0, lambda: self.status_bar.config(text=msg))

            if success:
                self.root.after(0, self.check_ipfs_status)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", msg))

        threading.Thread(target=start, daemon=True).start()

    def stop_daemon(self):
        """Stop IPFS daemon"""
        success, msg = self.ipfs_node.stop_daemon()
        self.status_bar.config(text=msg)
        self.check_ipfs_status()

    def add_files(self):
        """Add files to IPFS"""
        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        file_paths = filedialog.askopenfilenames(title="Select Files to Add to IPFS")

        if file_paths:
            self.status_bar.config(text=f"Adding {len(file_paths)} file(s) to IPFS...")

            def add():
                for file_path in file_paths:
                    ipfs_hash, error = self.ipfs_node.add_file(file_path)

                    if ipfs_hash:
                        file_name = Path(file_path).name
                        file_size = Path(file_path).stat().st_size

                        # Add to index
                        self.storage_index['files'][file_name] = {
                            'hash': ipfs_hash,
                            'size': file_size,
                            'date': datetime.now().isoformat(),
                            'pinned': True,
                            'path': str(file_path)
                        }

                        # Check if it's media
                        if self.is_media_file(file_name):
                            self.storage_index['media'][file_name] = {
                                'hash': ipfs_hash,
                                'type': Path(file_name).suffix[1:].upper(),
                                'date': datetime.now().isoformat()
                            }

                        self.root.after(0, lambda h=ipfs_hash: self.status_bar.config(text=f"Added: {h[:16]}..."))
                    else:
                        self.root.after(0, lambda e=error: messagebox.showerror("Error", f"Failed to add file: {e}"))

                self.save_index()
                self.root.after(0, self.refresh_files_view)
                self.root.after(0, self.refresh_media_view)
                self.root.after(0, lambda: self.status_bar.config(text="Files added successfully"))

            threading.Thread(target=add, daemon=True).start()

    def add_folder(self):
        """Add folder to IPFS"""
        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        folder_path = filedialog.askdirectory(title="Select Folder to Add to IPFS")

        if folder_path:
            self.status_bar.config(text="Adding folder to IPFS...")

            def add():
                ipfs_hash, error = self.ipfs_node.add_directory(folder_path)

                if ipfs_hash:
                    folder_name = Path(folder_path).name

                    self.storage_index['folders'][folder_name] = {
                        'hash': ipfs_hash,
                        'date': datetime.now().isoformat(),
                        'pinned': True,
                        'path': str(folder_path)
                    }

                    self.save_index()
                    self.root.after(0, self.refresh_files_view)
                    self.root.after(0, lambda: self.status_bar.config(text=f"Folder added: {ipfs_hash[:16]}..."))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to add folder: {error}"))

            threading.Thread(target=add, daemon=True).start()

    def import_from_hash(self):
        """Import file from IPFS hash"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import from IPFS Hash")
        dialog.geometry("500x150")
        dialog.transient(self.root)

        tk.Label(dialog, text="IPFS Hash:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        hash_entry = tk.Entry(dialog, width=60)
        hash_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Name (optional):", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        name_entry = tk.Entry(dialog, width=60)
        name_entry.grid(row=1, column=1, padx=10, pady=10)

        def do_import():
            ipfs_hash = hash_entry.get().strip()
            name = name_entry.get().strip() or f"imported_{ipfs_hash[:8]}"

            if not ipfs_hash:
                messagebox.showwarning("Invalid Input", "Please enter an IPFS hash")
                return

            # Add to index
            self.storage_index['files'][name] = {
                'hash': ipfs_hash,
                'size': 0,
                'date': datetime.now().isoformat(),
                'pinned': False
            }

            self.save_index()
            self.refresh_files_view()
            dialog.destroy()
            messagebox.showinfo("Imported", f"File imported: {name}")

        tk.Button(dialog, text="Import", command=do_import, bg='#3498db', fg='white', padx=20).grid(row=2, column=0, columnspan=2, pady=15)

    def is_media_file(self, filename):
        """Check if file is media"""
        media_extensions = {'.mp3', '.mp4', '.wav', '.ogg', '.flac', '.m4a', '.avi', '.mkv', '.webm', '.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        return Path(filename).suffix.lower() in media_extensions

    def refresh_files_view(self):
        """Refresh files tree view"""
        self.files_tree.delete(*self.files_tree.get_children())

        for name, info in self.storage_index.get('files', {}).items():
            size = self.format_size(info.get('size', 0))
            date = info.get('date', 'Unknown')[:19]
            pinned = '✓' if info.get('pinned', False) else ''

            self.files_tree.insert('', 'end', text=name, values=(
                info['hash'],
                size,
                date,
                pinned
            ))

        for name, info in self.storage_index.get('folders', {}).items():
            self.files_tree.insert('', 'end', text=f"📁 {name}", values=(
                info['hash'],
                'Folder',
                info.get('date', 'Unknown')[:19],
                '✓' if info.get('pinned', False) else ''
            ))

    def refresh_media_view(self):
        """Refresh media tree view"""
        self.media_tree.delete(*self.media_tree.get_children())

        for name, info in self.storage_index.get('media', {}).items():
            self.media_tree.insert('', 'end', text=name, values=(
                info['hash'],
                info.get('type', 'Unknown'),
                info.get('date', 'Unknown')[:19]
            ))

    def refresh_pins(self):
        """Refresh pinned items"""
        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        self.status_bar.config(text="Fetching pinned items...")

        def fetch():
            pins, error = self.ipfs_node.list_pins()

            if pins:
                self.pins_tree.delete(*self.pins_tree.get_children())

                for pin in pins:
                    self.root.after(0, lambda p=pin: self.pins_tree.insert('', 'end', text=p['hash'], values=(p['type'],)))

                self.root.after(0, lambda: self.status_bar.config(text=f"Found {len(pins)} pinned items"))
            elif error:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to list pins: {error}"))

        threading.Thread(target=fetch, daemon=True).start()

    def download_selected(self):
        """Download selected file"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to download")
            return

        item = self.files_tree.item(selection[0])
        ipfs_hash = item['values'][0]

        output_path = filedialog.asksaveasfilename(
            title="Save File As",
            initialfile=item['text']
        )

        if output_path:
            self.status_bar.config(text="Downloading from IPFS...")

            def download():
                success, error = self.ipfs_node.get_file(ipfs_hash, output_path)

                if success:
                    self.root.after(0, lambda: messagebox.showinfo("Downloaded", "File downloaded successfully!"))
                    self.root.after(0, lambda: self.status_bar.config(text="Download complete"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error}"))

            threading.Thread(target=download, daemon=True).start()

    def copy_hash(self):
        """Copy IPFS hash to clipboard"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return

        item = self.files_tree.item(selection[0])
        ipfs_hash = item['values'][0]

        self.root.clipboard_clear()
        self.root.clipboard_append(ipfs_hash)
        self.status_bar.config(text=f"Copied hash: {ipfs_hash[:16]}...")

    def open_in_gateway(self):
        """Open file in IPFS gateway"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return

        item = self.files_tree.item(selection[0])
        ipfs_hash = item['values'][0]

        url = self.ipfs_node.get_gateway_url(ipfs_hash)

        import webbrowser
        webbrowser.open(url)

        self.status_bar.config(text=f"Opening in gateway: {url}")

    def toggle_pin(self):
        """Toggle pin status"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return

        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        item = self.files_tree.item(selection[0])
        name = item['text']
        ipfs_hash = item['values'][0]
        is_pinned = item['values'][3] == '✓'

        def toggle():
            if is_pinned:
                success, error = self.ipfs_node.unpin_file(ipfs_hash)
                action = "unpinned"
            else:
                success, error = self.ipfs_node.pin_file(ipfs_hash)
                action = "pinned"

            if success:
                # Update index
                for category in ['files', 'folders']:
                    if name.replace('📁 ', '') in self.storage_index.get(category, {}):
                        self.storage_index[category][name.replace('📁 ', '')]['pinned'] = not is_pinned

                self.save_index()
                self.root.after(0, self.refresh_files_view)
                self.root.after(0, lambda: self.status_bar.config(text=f"File {action}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to toggle pin: {error}"))

        threading.Thread(target=toggle, daemon=True).start()

    def remove_selected(self):
        """Remove selected file from index"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return

        item = self.files_tree.item(selection[0])
        name = item['text'].replace('📁 ', '')

        if messagebox.askyesno("Confirm", f"Remove '{name}' from index?\n\nNote: File will remain in IPFS if pinned."):
            # Remove from index
            for category in ['files', 'folders', 'media']:
                if name in self.storage_index.get(category, {}):
                    del self.storage_index[category][name]

            self.save_index()
            self.refresh_files_view()
            self.refresh_media_view()
            self.status_bar.config(text=f"Removed: {name}")

    def play_media(self, event):
        """Play media file"""
        selection = self.media_tree.selection()
        if not selection:
            return

        item = self.media_tree.item(selection[0])
        name = item['text']
        ipfs_hash = item['values'][0]

        # Open in media player
        messagebox.showinfo(
            "Play Media",
            f"Opening {name} in TL Media Player\n\nHash: {ipfs_hash}\n\n"
            "Media will be streamed from IPFS gateway."
        )

        # TODO: Launch media player with IPFS URL
        url = self.ipfs_node.get_gateway_url(ipfs_hash)
        print(f"Play: {url}")

    def show_file_context_menu(self, event):
        """Show context menu for files"""
        # TODO: Implement context menu
        pass

    def show_node_info(self):
        """Show IPFS node information"""
        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        node_id, public_key = self.ipfs_node.get_node_id()

        if node_id:
            info = f"""IPFS Node Information

Node ID: {node_id}

Public Key: {public_key[:50]}...

API URL: {self.ipfs_node.api_url}
Gateway URL: {self.ipfs_node.gateway_url}
"""
            messagebox.showinfo("Node Info", info)

    def show_peers(self):
        """Show connected peers"""
        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        self.status_bar.config(text="Fetching peers...")

        def fetch():
            peers, error = self.ipfs_node.get_peers()

            if peers:
                peer_list = "\n".join([p.get('Peer', 'Unknown') for p in peers[:20]])
                self.root.after(0, lambda: messagebox.showinfo("Connected Peers", f"Connected to {len(peers)} peers:\n\n{peer_list}\n\n..."))
            elif error:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get peers: {error}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("No Peers", "Not connected to any peers"))

            self.root.after(0, lambda: self.status_bar.config(text="Ready"))

        threading.Thread(target=fetch, daemon=True).start()

    def show_stats(self):
        """Show IPFS statistics"""
        if not self.ipfs_node.is_running:
            messagebox.showwarning("IPFS Not Running", "Please start IPFS daemon first")
            return

        stats, error = self.ipfs_node.get_stats()

        if stats:
            repo_size = self.format_size(stats.get('RepoSize', 0))
            num_objects = stats.get('NumObjects', 0)

            info = f"""IPFS Repository Statistics

Repository Size: {repo_size}
Number of Objects: {num_objects}

Storage Path: {self.ipfs_node.ipfs_path}
"""
            messagebox.showinfo("Statistics", info)
        elif error:
            messagebox.showerror("Error", f"Failed to get stats: {error}")

    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    def run(self):
        """Run storage manager"""
        self.root.mainloop()

if __name__ == '__main__':
    manager = IPFSStorageManager()
    manager.run()
