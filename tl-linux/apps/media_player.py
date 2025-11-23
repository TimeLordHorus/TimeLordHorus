#!/usr/bin/env python3
"""
TL Linux - Media Player with IPFS Support
Play audio and video from local storage or IPFS
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import sys
from pathlib import Path
from datetime import timedelta
import threading
import tempfile
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.ipfs_node import get_global_node

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

class MediaPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎵 TL Media Player")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')

        self.ipfs_node = get_global_node()
        self.config_file = Path.home() / '.config' / 'tl-linux' / 'media_library.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Media library
        self.library = self.load_library()

        # Playlist
        self.current_playlist = []
        self.current_index = 0

        # Player state
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        self.volume = 70

        # Initialize pygame mixer if available
        if HAS_PYGAME:
            try:
                pygame.mixer.init()
            except:
                HAS_PYGAME = False

        self.setup_ui()

        # Update timer
        if HAS_PYGAME:
            self.update_playback()

    def load_library(self):
        """Load media library"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'playlists': {},
            'local_files': [],
            'ipfs_files': [],
            'recent': []
        }

    def save_library(self):
        """Save media library"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.library, f, indent=2)
        except Exception as e:
            print(f"Error saving library: {e}")

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files", command=self.add_local_files)
        file_menu.add_command(label="Add Folder", command=self.add_local_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Add from IPFS", command=self.add_from_ipfs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        playlist_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Playlist", menu=playlist_menu)
        playlist_menu.add_command(label="New Playlist", command=self.create_playlist)
        playlist_menu.add_command(label="Save Current as Playlist", command=self.save_current_playlist)
        playlist_menu.add_separator()
        playlist_menu.add_command(label="Clear Playlist", command=self.clear_playlist)

        # Player section
        player_frame = tk.Frame(self.root, bg='#2c2c2c', height=200)
        player_frame.pack(fill=tk.X, padx=10, pady=10)
        player_frame.pack_propagate(False)

        # Album art / visualization
        art_frame = tk.Frame(player_frame, bg='#1e1e1e', width=180, height=180)
        art_frame.pack(side=tk.LEFT, padx=10, pady=10)
        art_frame.pack_propagate(False)

        self.art_label = tk.Label(art_frame, text="♪", font=('Arial', 60), bg='#1e1e1e', fg='#3498db')
        self.art_label.pack(expand=True)

        # Player info and controls
        controls_frame = tk.Frame(player_frame, bg='#2c2c2c')
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Now playing
        self.now_playing_label = tk.Label(
            controls_frame,
            text="No media loaded",
            font=('Arial', 14, 'bold'),
            bg='#2c2c2c',
            fg='white',
            anchor='w'
        )
        self.now_playing_label.pack(fill=tk.X, pady=(0, 5))

        self.artist_label = tk.Label(
            controls_frame,
            text="",
            font=('Arial', 10),
            bg='#2c2c2c',
            fg='#95a5a6',
            anchor='w'
        )
        self.artist_label.pack(fill=tk.X, pady=(0, 15))

        # Progress bar
        progress_frame = tk.Frame(controls_frame, bg='#2c2c2c')
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.time_label = tk.Label(progress_frame, text="0:00", bg='#2c2c2c', fg='white', font=('Arial', 9))
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.seek
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.duration_label = tk.Label(progress_frame, text="0:00", bg='#2c2c2c', fg='white', font=('Arial', 9))
        self.duration_label.pack(side=tk.LEFT, padx=(10, 0))

        # Playback controls
        buttons_frame = tk.Frame(controls_frame, bg='#2c2c2c')
        buttons_frame.pack(pady=10)

        self.shuffle_btn = tk.Button(buttons_frame, text="🔀", font=('Arial', 14), bg='#34495e', fg='white', relief=tk.FLAT, width=3, command=self.toggle_shuffle)
        self.shuffle_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="⏮️", font=('Arial', 14), bg='#34495e', fg='white', relief=tk.FLAT, width=3, command=self.previous_track).pack(side=tk.LEFT, padx=5)

        self.play_pause_btn = tk.Button(
            buttons_frame,
            text="▶️",
            font=('Arial', 20),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            width=3,
            command=self.toggle_play_pause
        )
        self.play_pause_btn.pack(side=tk.LEFT, padx=15)

        tk.Button(buttons_frame, text="⏭️", font=('Arial', 14), bg='#34495e', fg='white', relief=tk.FLAT, width=3, command=self.next_track).pack(side=tk.LEFT, padx=5)

        self.repeat_btn = tk.Button(buttons_frame, text="🔁", font=('Arial', 14), bg='#34495e', fg='white', relief=tk.FLAT, width=3, command=self.toggle_repeat)
        self.repeat_btn.pack(side=tk.LEFT, padx=5)

        # Volume control
        volume_frame = tk.Frame(controls_frame, bg='#2c2c2c')
        volume_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(volume_frame, text="🔊", bg='#2c2c2c', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=(0, 10))

        self.volume_var = tk.IntVar(value=self.volume)
        volume_slider = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.change_volume
        )
        volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.volume_label = tk.Label(volume_frame, text=f"{self.volume}%", bg='#2c2c2c', fg='white', font=('Arial', 9), width=5)
        self.volume_label.pack(side=tk.LEFT, padx=(10, 0))

        # Main content - Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Playlist tab
        playlist_frame = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(playlist_frame, text="📋 Current Playlist")

        # Playlist toolbar
        playlist_toolbar = tk.Frame(playlist_frame, bg='#2c2c2c', pady=5)
        playlist_toolbar.pack(fill=tk.X)

        tk.Button(playlist_toolbar, text="➕ Add Files", command=self.add_local_files, bg='#3498db', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(playlist_toolbar, text="🌐 Add from IPFS", command=self.add_from_ipfs, bg='#9b59b6', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(playlist_toolbar, text="🗑️ Clear", command=self.clear_playlist, bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        # Playlist tree
        playlist_tree_frame = tk.Frame(playlist_frame)
        playlist_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        playlist_scroll = tk.Scrollbar(playlist_tree_frame)
        playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.playlist_tree = ttk.Treeview(
            playlist_tree_frame,
            columns=('Duration', 'Source', 'Path'),
            show='tree headings',
            yscrollcommand=playlist_scroll.set
        )

        self.playlist_tree.heading('#0', text='Title')
        self.playlist_tree.heading('Duration', text='Duration')
        self.playlist_tree.heading('Source', text='Source')
        self.playlist_tree.heading('Path', text='Path/Hash')

        self.playlist_tree.column('#0', width=300)
        self.playlist_tree.column('Duration', width=80)
        self.playlist_tree.column('Source', width=80)
        self.playlist_tree.column('Path', width=400)

        self.playlist_tree.pack(fill=tk.BOTH, expand=True)
        playlist_scroll.config(command=self.playlist_tree.yview)

        self.playlist_tree.bind('<Double-1>', self.play_selected)

        # Library tab
        library_frame = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(library_frame, text="📚 Library")

        # Library categories
        library_toolbar = tk.Frame(library_frame, bg='#2c2c2c', pady=5)
        library_toolbar.pack(fill=tk.X)

        tk.Label(library_toolbar, text="Filter:", bg='#2c2c2c', fg='white').pack(side=tk.LEFT, padx=10)

        self.filter_var = tk.StringVar(value="All")
        for filter_name in ["All", "Local", "IPFS", "Audio", "Video"]:
            tk.Radiobutton(
                library_toolbar,
                text=filter_name,
                variable=self.filter_var,
                value=filter_name,
                bg='#2c2c2c',
                fg='white',
                selectcolor='#34495e',
                command=self.refresh_library_view
            ).pack(side=tk.LEFT, padx=5)

        # Library tree
        library_tree_frame = tk.Frame(library_frame)
        library_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        library_scroll = tk.Scrollbar(library_tree_frame)
        library_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.library_tree = ttk.Treeview(
            library_tree_frame,
            columns=('Type', 'Source', 'Location'),
            show='tree headings',
            yscrollcommand=library_scroll.set
        )

        self.library_tree.heading('#0', text='Name')
        self.library_tree.heading('Type', text='Type')
        self.library_tree.heading('Source', text='Source')
        self.library_tree.heading('Location', text='Location')

        self.library_tree.column('#0', width=350)
        self.library_tree.column('Type', width=100)
        self.library_tree.column('Source', width=100)
        self.library_tree.column('Location', width=400)

        self.library_tree.pack(fill=tk.BOTH, expand=True)
        library_scroll.config(command=self.library_tree.yview)

        self.library_tree.bind('<Double-1>', self.add_library_to_playlist)

        # IPFS tab
        ipfs_frame = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(ipfs_frame, text="🌐 IPFS Media")

        tk.Label(
            ipfs_frame,
            text="Media files stored in IPFS",
            font=('Arial', 12),
            bg='#1e1e1e',
            fg='#95a5a6',
            pady=20
        ).pack()

        ipfs_btn_frame = tk.Frame(ipfs_frame, bg='#1e1e1e')
        ipfs_btn_frame.pack(pady=10)

        tk.Button(
            ipfs_btn_frame,
            text="📁 Open IPFS Storage Manager",
            command=self.open_ipfs_storage,
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack()

        # IPFS media tree
        ipfs_tree_frame = tk.Frame(ipfs_frame)
        ipfs_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ipfs_scroll = tk.Scrollbar(ipfs_tree_frame)
        ipfs_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.ipfs_tree = ttk.Treeview(
            ipfs_tree_frame,
            columns=('Hash', 'Type'),
            show='tree headings',
            yscrollcommand=ipfs_scroll.set
        )

        self.ipfs_tree.heading('#0', text='Name')
        self.ipfs_tree.heading('Hash', text='IPFS Hash')
        self.ipfs_tree.heading('Type', text='Type')

        self.ipfs_tree.column('#0', width=300)
        self.ipfs_tree.column('Hash', width=450)
        self.ipfs_tree.column('Type', width=100)

        self.ipfs_tree.pack(fill=tk.BOTH, expand=True)
        ipfs_scroll.config(command=self.ipfs_tree.yview)

        self.ipfs_tree.bind('<Double-1>', self.play_from_ipfs)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready" + ("" if HAS_PYGAME else " - Warning: pygame not installed, audio playback disabled"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#2c2c2c',
            fg='white',
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load initial data
        self.refresh_library_view()
        self.refresh_ipfs_view()

    def add_local_files(self):
        """Add local media files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Media Files",
            filetypes=[
                ("Media files", "*.mp3 *.mp4 *.wav *.ogg *.flac *.m4a *.avi *.mkv *.webm"),
                ("Audio files", "*.mp3 *.wav *.ogg *.flac *.m4a"),
                ("Video files", "*.mp4 *.avi *.mkv *.webm"),
                ("All files", "*.*")
            ]
        )

        if file_paths:
            for file_path in file_paths:
                self.current_playlist.append({
                    'title': Path(file_path).stem,
                    'source': 'Local',
                    'path': str(file_path),
                    'type': self.get_media_type(file_path)
                })

                # Add to library
                if file_path not in self.library['local_files']:
                    self.library['local_files'].append({
                        'name': Path(file_path).name,
                        'path': str(file_path),
                        'type': self.get_media_type(file_path)
                    })

            self.save_library()
            self.refresh_playlist_view()
            self.refresh_library_view()
            self.status_bar.config(text=f"Added {len(file_paths)} file(s)")

    def add_local_folder(self):
        """Add media from folder"""
        folder_path = filedialog.askdirectory(title="Select Media Folder")

        if folder_path:
            media_extensions = {'.mp3', '.mp4', '.wav', '.ogg', '.flac', '.m4a', '.avi', '.mkv', '.webm'}
            count = 0

            for file_path in Path(folder_path).rglob('*'):
                if file_path.suffix.lower() in media_extensions:
                    self.current_playlist.append({
                        'title': file_path.stem,
                        'source': 'Local',
                        'path': str(file_path),
                        'type': self.get_media_type(str(file_path))
                    })

                    if str(file_path) not in [f['path'] for f in self.library['local_files']]:
                        self.library['local_files'].append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'type': self.get_media_type(str(file_path))
                        })

                    count += 1

            self.save_library()
            self.refresh_playlist_view()
            self.refresh_library_view()
            self.status_bar.config(text=f"Added {count} file(s) from folder")

    def add_from_ipfs(self):
        """Add media from IPFS"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add from IPFS")
        dialog.geometry("500x150")
        dialog.transient(self.root)
        dialog.configure(bg='#2c2c2c')

        tk.Label(dialog, text="IPFS Hash:", bg='#2c2c2c', fg='white', font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        hash_entry = tk.Entry(dialog, width=50, bg='#34495e', fg='white')
        hash_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Title:", bg='#2c2c2c', fg='white', font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        title_entry = tk.Entry(dialog, width=50, bg='#34495e', fg='white')
        title_entry.grid(row=1, column=1, padx=10, pady=10)

        def do_add():
            ipfs_hash = hash_entry.get().strip()
            title = title_entry.get().strip() or f"IPFS_{ipfs_hash[:8]}"

            if not ipfs_hash:
                messagebox.showwarning("Invalid Input", "Please enter an IPFS hash")
                return

            self.current_playlist.append({
                'title': title,
                'source': 'IPFS',
                'path': ipfs_hash,
                'type': 'Audio'  # Default to audio
            })

            # Add to library
            self.library['ipfs_files'].append({
                'name': title,
                'hash': ipfs_hash,
                'type': 'Audio'
            })

            self.save_library()
            self.refresh_playlist_view()
            self.refresh_ipfs_view()
            dialog.destroy()
            self.status_bar.config(text=f"Added from IPFS: {title}")

        tk.Button(dialog, text="Add", command=do_add, bg='#3498db', fg='white', padx=20, pady=5).grid(row=2, column=0, columnspan=2, pady=15)

    def get_media_type(self, file_path):
        """Get media type from file extension"""
        ext = Path(file_path).suffix.lower()
        audio_exts = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
        video_exts = {'.mp4', '.avi', '.mkv', '.webm'}

        if ext in audio_exts:
            return 'Audio'
        elif ext in video_exts:
            return 'Video'
        return 'Unknown'

    def refresh_playlist_view(self):
        """Refresh playlist tree"""
        self.playlist_tree.delete(*self.playlist_tree.get_children())

        for idx, item in enumerate(self.current_playlist):
            icon = "🎵" if item['type'] == 'Audio' else "🎬"
            self.playlist_tree.insert('', 'end', text=f"{icon} {item['title']}", values=(
                '',  # Duration (if we had metadata)
                item['source'],
                item['path'][:50] + '...' if len(item['path']) > 50 else item['path']
            ), tags=(str(idx),))

    def refresh_library_view(self):
        """Refresh library tree"""
        self.library_tree.delete(*self.library_tree.get_children())

        filter_val = self.filter_var.get()

        # Local files
        for item in self.library.get('local_files', []):
            if filter_val in ['All', 'Local'] or filter_val == item['type']:
                self.library_tree.insert('', 'end', text=item['name'], values=(
                    item['type'],
                    'Local',
                    item['path']
                ))

        # IPFS files
        for item in self.library.get('ipfs_files', []):
            if filter_val in ['All', 'IPFS']:
                self.library_tree.insert('', 'end', text=item['name'], values=(
                    item['type'],
                    'IPFS',
                    item['hash']
                ))

    def refresh_ipfs_view(self):
        """Refresh IPFS media view"""
        self.ipfs_tree.delete(*self.ipfs_tree.get_children())

        for item in self.library.get('ipfs_files', []):
            icon = "🎵" if item['type'] == 'Audio' else "🎬"
            self.ipfs_tree.insert('', 'end', text=f"{icon} {item['name']}", values=(
                item['hash'],
                item['type']
            ))

    def play_selected(self, event):
        """Play selected item from playlist"""
        selection = self.playlist_tree.selection()
        if selection:
            item = self.playlist_tree.item(selection[0])
            idx = int(item['tags'][0])
            self.current_index = idx
            self.play_current()

    def add_library_to_playlist(self, event):
        """Add library item to playlist"""
        selection = self.library_tree.selection()
        if selection:
            item = self.library_tree.item(selection[0])
            source = item['values'][1]
            location = item['values'][2]

            self.current_playlist.append({
                'title': item['text'],
                'source': source,
                'path': location,
                'type': item['values'][0]
            })

            self.refresh_playlist_view()
            self.status_bar.config(text=f"Added to playlist: {item['text']}")

    def play_from_ipfs(self, event):
        """Play selected IPFS media"""
        selection = self.ipfs_tree.selection()
        if selection:
            item = self.ipfs_tree.item(selection[0])
            ipfs_hash = item['values'][0]

            # Add to playlist and play
            self.current_playlist.append({
                'title': item['text'],
                'source': 'IPFS',
                'path': ipfs_hash,
                'type': item['values'][1]
            })

            self.refresh_playlist_view()
            self.current_index = len(self.current_playlist) - 1
            self.play_current()

    def play_current(self):
        """Play current track"""
        if not self.current_playlist or self.current_index >= len(self.current_playlist):
            return

        current = self.current_playlist[self.current_index]

        if not HAS_PYGAME:
            messagebox.showwarning(
                "Pygame Not Installed",
                "Audio playback requires pygame.\n\nInstall with: pip install pygame"
            )
            return

        try:
            if current['source'] == 'Local':
                # Play local file
                pygame.mixer.music.load(current['path'])
                pygame.mixer.music.play()
                self.current_file = current['path']

            elif current['source'] == 'IPFS':
                # Download from IPFS to temp file and play
                self.status_bar.config(text=f"Streaming from IPFS: {current['title']}...")

                # Use gateway URL for streaming
                url = self.ipfs_node.get_gateway_url(current['path'])

                # For now, show URL (actual streaming would require additional libraries)
                messagebox.showinfo(
                    "IPFS Streaming",
                    f"Streaming from IPFS:\n\n{url}\n\n"
                    "You can open this URL in a web browser to play the media."
                )

                # TODO: Implement actual streaming with requests + tempfile
                return

            self.is_playing = True
            self.is_paused = False
            self.play_pause_btn.config(text="⏸️")
            self.now_playing_label.config(text=current['title'])
            self.artist_label.config(text=f"{current['source']} - {current['type']}")

            self.status_bar.config(text=f"Playing: {current['title']}")

        except Exception as e:
            messagebox.showerror("Playback Error", f"Could not play media:\n{e}")
            self.status_bar.config(text="Playback error")

    def toggle_play_pause(self):
        """Toggle play/pause"""
        if not HAS_PYGAME:
            return

        if not self.current_playlist:
            messagebox.showinfo("No Media", "Please add media to the playlist first")
            return

        if not self.is_playing:
            self.play_current()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_pause_btn.config(text="⏸️")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_pause_btn.config(text="▶️")

    def next_track(self):
        """Play next track"""
        if self.current_playlist:
            self.current_index = (self.current_index + 1) % len(self.current_playlist)
            self.play_current()

    def previous_track(self):
        """Play previous track"""
        if self.current_playlist:
            self.current_index = (self.current_index - 1) % len(self.current_playlist)
            self.play_current()

    def seek(self, value):
        """Seek to position"""
        # TODO: Implement seeking
        pass

    def change_volume(self, value):
        """Change volume"""
        self.volume = int(float(value))
        self.volume_label.config(text=f"{self.volume}%")

        if HAS_PYGAME:
            pygame.mixer.music.set_volume(self.volume / 100)

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        # TODO: Implement shuffle
        pass

    def toggle_repeat(self):
        """Toggle repeat mode"""
        # TODO: Implement repeat
        pass

    def clear_playlist(self):
        """Clear current playlist"""
        if messagebox.askyesno("Clear Playlist", "Clear current playlist?"):
            self.current_playlist = []
            self.current_index = 0
            self.refresh_playlist_view()
            self.status_bar.config(text="Playlist cleared")

    def create_playlist(self):
        """Create new playlist"""
        # TODO: Implement playlist creation
        messagebox.showinfo("Coming Soon", "Playlist creation feature coming soon!")

    def save_current_playlist(self):
        """Save current playlist"""
        # TODO: Implement playlist saving
        messagebox.showinfo("Coming Soon", "Playlist saving feature coming soon!")

    def open_ipfs_storage(self):
        """Open IPFS storage manager"""
        import subprocess
        script_path = Path(__file__).parent / 'ipfs_storage.py'
        subprocess.Popen([sys.executable, str(script_path)])

    def update_playback(self):
        """Update playback progress"""
        if HAS_PYGAME and self.is_playing and not self.is_paused:
            try:
                if pygame.mixer.music.get_busy():
                    # Update progress (this is approximate, pygame doesn't provide exact position)
                    pass
                else:
                    # Track ended, play next
                    if self.current_playlist:
                        self.next_track()
            except:
                pass

        # Schedule next update
        self.root.after(1000, self.update_playback)

    def run(self):
        """Run media player"""
        self.root.mainloop()

if __name__ == '__main__':
    player = MediaPlayer()
    player.run()
