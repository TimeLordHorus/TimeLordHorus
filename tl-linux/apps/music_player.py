#!/usr/bin/env python3
"""
TL Linux - Music Player
Full-featured music player with playlists, equalizer, and visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time
from pathlib import Path

# Note: Would use pygame.mixer for actual audio playback
# For now, simulating with placeholders

class MusicPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Music Player")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')

        # Config
        self.config_dir = os.path.expanduser('~/.tl-linux/music-player')
        self.playlists_file = os.path.join(self.config_dir, 'playlists.json')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        os.makedirs(self.config_dir, exist_ok=True)

        # Load config
        self.config = self.load_config()
        self.playlists = self.load_playlists()

        # Playback state
        self.current_playlist = None
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 70
        self.position = 0  # seconds
        self.duration = 0  # seconds

        # Repeat/shuffle
        self.repeat_mode = 'off'  # off, one, all
        self.shuffle = False

        # Library
        self.library = []
        self.music_dirs = self.config.get('music_directories', [os.path.expanduser('~/Music')])

        self.setup_ui()
        self.scan_library()

    def load_config(self):
        """Load configuration"""
        default_config = {
            'music_directories': [os.path.expanduser('~/Music')],
            'volume': 70,
            'equalizer': {
                '60Hz': 0,
                '230Hz': 0,
                '910Hz': 0,
                '3.6kHz': 0,
                '14kHz': 0
            }
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except:
            pass

        return default_config

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_playlists(self):
        """Load playlists"""
        default_playlists = {
            'Favorites': [],
            'Recently Played': []
        }

        try:
            if os.path.exists(self.playlists_file):
                with open(self.playlists_file, 'r') as f:
                    return json.load(f)
        except:
            pass

        return default_playlists

    def save_playlists(self):
        """Save playlists"""
        try:
            with open(self.playlists_file, 'w') as f:
                json.dump(self.playlists, f, indent=2)
        except Exception as e:
            print(f"Error saving playlists: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Top section - Now Playing
        now_playing = tk.Frame(self.root, bg='#2b2b2b', height=180)
        now_playing.pack(fill=tk.X)
        now_playing.pack_propagate(False)

        # Album art (placeholder)
        art_frame = tk.Frame(now_playing, bg='#1a1a1a', width=150, height=150)
        art_frame.pack(side=tk.LEFT, padx=20, pady=15)
        art_frame.pack_propagate(False)

        tk.Label(
            art_frame,
            text="🎵",
            font=('Arial', 64),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(expand=True)

        # Track info
        info_frame = tk.Frame(now_playing, bg='#2b2b2b')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=15)

        self.track_title = tk.Label(
            info_frame,
            text="No track playing",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='white',
            anchor='w'
        )
        self.track_title.pack(fill=tk.X)

        self.track_artist = tk.Label(
            info_frame,
            text="",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        )
        self.track_artist.pack(fill=tk.X, pady=(5, 10))

        # Progress bar
        progress_frame = tk.Frame(info_frame, bg='#2b2b2b')
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        self.time_label = tk.Label(
            progress_frame,
            text="0:00",
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.seek
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.duration_label = tk.Label(
            progress_frame,
            text="0:00",
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.duration_label.pack(side=tk.LEFT, padx=(10, 0))

        # Controls
        controls_frame = tk.Frame(info_frame, bg='#2b2b2b')
        controls_frame.pack(fill=tk.X, pady=(15, 0))

        # Shuffle button
        self.shuffle_btn = tk.Button(
            controls_frame,
            text="🔀",
            command=self.toggle_shuffle,
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 14),
            bd=0,
            width=3
        )
        self.shuffle_btn.pack(side=tk.LEFT, padx=5)

        # Previous button
        tk.Button(
            controls_frame,
            text="⏮",
            command=self.previous_track,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 18),
            bd=0,
            width=3
        ).pack(side=tk.LEFT, padx=5)

        # Play/Pause button
        self.play_btn = tk.Button(
            controls_frame,
            text="▶",
            command=self.play_pause,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 24),
            bd=0,
            width=3
        )
        self.play_btn.pack(side=tk.LEFT, padx=10)

        # Next button
        tk.Button(
            controls_frame,
            text="⏭",
            command=self.next_track,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 18),
            bd=0,
            width=3
        ).pack(side=tk.LEFT, padx=5)

        # Repeat button
        self.repeat_btn = tk.Button(
            controls_frame,
            text="🔁",
            command=self.toggle_repeat,
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 14),
            bd=0,
            width=3
        )
        self.repeat_btn.pack(side=tk.LEFT, padx=5)

        # Volume control (right side)
        volume_frame = tk.Frame(info_frame, bg='#2b2b2b')
        volume_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            volume_frame,
            text="🔊",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 14)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.volume_var = tk.IntVar(value=self.volume)
        volume_slider = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.change_volume,
            length=100
        )
        volume_slider.pack(side=tk.LEFT)

        # Main content - Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Tab 1: Library
        self.create_library_tab()

        # Tab 2: Playlists
        self.create_playlists_tab()

        # Tab 3: Equalizer
        self.create_equalizer_tab()

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

        self.track_count_label = tk.Label(
            status_bar,
            text="0 tracks",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8)
        )
        self.track_count_label.pack(side=tk.RIGHT, padx=10)

    def create_library_tab(self):
        """Create library tab"""
        library_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(library_tab, text="Library")

        # Toolbar
        toolbar = tk.Frame(library_tab, bg='#1a1a1a')
        toolbar.pack(fill=tk.X, pady=10, padx=10)

        tk.Button(
            toolbar,
            text="➕ Add Files",
            command=self.add_files,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="📁 Add Folder",
            command=self.add_folder,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🔄 Rescan",
            command=self.scan_library,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Search
        search_frame = tk.Frame(toolbar, bg='#1a1a1a')
        search_frame.pack(side=tk.RIGHT)

        tk.Label(
            search_frame,
            text="🔍",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_library())

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            bd=0,
            width=30
        ).pack(side=tk.LEFT, ipady=5)

        # Library list
        list_frame = tk.Frame(library_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.library_tree = ttk.Treeview(
            list_frame,
            columns=('Artist', 'Album', 'Duration'),
            yscrollcommand=scrollbar.set
        )
        self.library_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.library_tree.yview)

        self.library_tree.heading('#0', text='Title', anchor='w')
        self.library_tree.heading('Artist', text='Artist', anchor='w')
        self.library_tree.heading('Album', text='Album', anchor='w')
        self.library_tree.heading('Duration', text='Duration', anchor='w')

        self.library_tree.column('#0', width=300)
        self.library_tree.column('Artist', width=200)
        self.library_tree.column('Album', width=200)
        self.library_tree.column('Duration', width=80)

        # Double-click to play
        self.library_tree.bind('<Double-1>', lambda e: self.play_selected())

        # Right-click menu
        self.library_tree.bind('<Button-3>', self.show_track_menu)

        # Style
        style = ttk.Style()
        style.configure('Treeview', background='#2b2b2b', foreground='white', fieldbackground='#2b2b2b')
        style.map('Treeview', background=[('selected', '#4a9eff')])

    def create_playlists_tab(self):
        """Create playlists tab"""
        playlists_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(playlists_tab, text="Playlists")

        # Split into playlist list and playlist contents
        paned = tk.PanedWindow(playlists_tab, orient=tk.HORIZONTAL, bg='#1a1a1a', sashwidth=2)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left - Playlist list
        left_panel = tk.Frame(paned, bg='#1a1a1a', width=250)
        paned.add(left_panel)

        tk.Label(
            left_panel,
            text="Playlists",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=10)

        # New playlist button
        tk.Button(
            left_panel,
            text="➕ New Playlist",
            command=self.create_playlist,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8
        ).pack(pady=(0, 10))

        # Playlist listbox
        self.playlist_listbox = tk.Listbox(
            left_panel,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 11),
            selectbackground='#4a9eff',
            bd=0,
            highlightthickness=0
        )
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.playlist_listbox.bind('<<ListboxSelect>>', self.on_playlist_select)

        # Load playlists
        for playlist_name in self.playlists.keys():
            self.playlist_listbox.insert(tk.END, playlist_name)

        # Right - Playlist contents
        right_panel = tk.Frame(paned, bg='#1a1a1a')
        paned.add(right_panel)

        tk.Label(
            right_panel,
            text="Playlist Contents",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=10)

        # Playlist contents tree
        self.playlist_tree = ttk.Treeview(
            right_panel,
            columns=('Artist', 'Duration'),
        )
        self.playlist_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.playlist_tree.heading('#0', text='Title', anchor='w')
        self.playlist_tree.heading('Artist', text='Artist', anchor='w')
        self.playlist_tree.heading('Duration', text='Duration', anchor='w')

    def create_equalizer_tab(self):
        """Create equalizer tab"""
        eq_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(eq_tab, text="Equalizer")

        tk.Label(
            eq_tab,
            text="Equalizer",
            font=('Arial', 16, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=20)

        # Equalizer sliders
        eq_frame = tk.Frame(eq_tab, bg='#1a1a1a')
        eq_frame.pack(expand=True)

        frequencies = ['60Hz', '230Hz', '910Hz', '3.6kHz', '14kHz']

        self.eq_vars = {}

        for freq in frequencies:
            freq_frame = tk.Frame(eq_frame, bg='#1a1a1a')
            freq_frame.pack(side=tk.LEFT, padx=20)

            # Slider (vertical)
            var = tk.IntVar(value=self.config['equalizer'].get(freq, 0))
            self.eq_vars[freq] = var

            slider = ttk.Scale(
                freq_frame,
                from_=12,
                to=-12,
                orient=tk.VERTICAL,
                variable=var,
                command=lambda v, f=freq: self.update_eq(f, v),
                length=200
            )
            slider.pack()

            # Value label
            value_label = tk.Label(
                freq_frame,
                textvariable=var,
                bg='#1a1a1a',
                fg='white',
                font=('Arial', 9)
            )
            value_label.pack(pady=(5, 0))

            # Frequency label
            tk.Label(
                freq_frame,
                text=freq,
                bg='#1a1a1a',
                fg='#888888',
                font=('Arial', 10)
            ).pack()

        # Presets
        preset_frame = tk.Frame(eq_tab, bg='#1a1a1a')
        preset_frame.pack(pady=20)

        tk.Label(
            preset_frame,
            text="Presets:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=10)

        presets = ['Flat', 'Rock', 'Pop', 'Classical', 'Bass Boost']
        for preset in presets:
            tk.Button(
                preset_frame,
                text=preset,
                command=lambda p=preset: self.apply_eq_preset(p),
                bg='#2b2b2b',
                fg='white',
                bd=0,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)

    def scan_library(self):
        """Scan music directories for audio files"""
        self.status_label.config(text="Scanning library...")

        def scan():
            audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
            found_tracks = []

            for music_dir in self.music_dirs:
                if os.path.exists(music_dir):
                    for root, dirs, files in os.walk(music_dir):
                        for file in files:
                            if Path(file).suffix.lower() in audio_extensions:
                                full_path = os.path.join(root, file)
                                found_tracks.append({
                                    'path': full_path,
                                    'title': Path(file).stem,
                                    'artist': 'Unknown Artist',
                                    'album': 'Unknown Album',
                                    'duration': '0:00'
                                })

            self.library = found_tracks
            self.root.after(0, self.display_library)

        threading.Thread(target=scan, daemon=True).start()

    def display_library(self):
        """Display library in tree"""
        self.library_tree.delete(*self.library_tree.get_children())

        for track in self.library:
            self.library_tree.insert(
                '',
                tk.END,
                text=track['title'],
                values=(track['artist'], track['album'], track['duration'])
            )

        self.track_count_label.config(text=f"{len(self.library)} tracks")
        self.status_label.config(text=f"Library loaded: {len(self.library)} tracks")

    def filter_library(self):
        """Filter library based on search"""
        search_term = self.search_var.get().lower()

        self.library_tree.delete(*self.library_tree.get_children())

        for track in self.library:
            if (search_term in track['title'].lower() or
                search_term in track['artist'].lower() or
                search_term in track['album'].lower()):

                self.library_tree.insert(
                    '',
                    tk.END,
                    text=track['title'],
                    values=(track['artist'], track['album'], track['duration'])
                )

    def add_files(self):
        """Add files to library"""
        files = filedialog.askopenfilenames(
            title="Add Music Files",
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.ogg *.flac *.m4a"),
                ("All files", "*.*")
            ]
        )

        if files:
            for file_path in files:
                self.library.append({
                    'path': file_path,
                    'title': Path(file_path).stem,
                    'artist': 'Unknown Artist',
                    'album': 'Unknown Album',
                    'duration': '0:00'
                })

            self.display_library()

    def add_folder(self):
        """Add folder to library"""
        folder = filedialog.askdirectory(title="Add Music Folder")

        if folder and folder not in self.music_dirs:
            self.music_dirs.append(folder)
            self.config['music_directories'] = self.music_dirs
            self.save_config()
            self.scan_library()

    def play_selected(self):
        """Play selected track"""
        selection = self.library_tree.selection()
        if selection:
            index = self.library_tree.index(selection[0])
            if index < len(self.library):
                self.play_track(index)

    def play_track(self, index):
        """Play track at index"""
        if 0 <= index < len(self.library):
            track = self.library[index]

            self.current_track_index = index
            self.is_playing = True
            self.is_paused = False

            # Update UI
            self.track_title.config(text=track['title'])
            self.track_artist.config(text=track['artist'])
            self.play_btn.config(text="⏸")

            # Simulate playback (would use pygame.mixer in production)
            self.duration = 180  # 3 minutes simulated
            self.position = 0

            self.status_label.config(text=f"Playing: {track['title']}")

            # Add to recently played
            if 'Recently Played' in self.playlists:
                if track['path'] not in self.playlists['Recently Played']:
                    self.playlists['Recently Played'].insert(0, track['path'])
                    self.playlists['Recently Played'] = self.playlists['Recently Played'][:50]  # Keep last 50
                    self.save_playlists()

    def play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            if self.is_paused:
                # Resume
                self.is_paused = False
                self.play_btn.config(text="⏸")
                self.status_label.config(text="Playing")
            else:
                # Pause
                self.is_paused = True
                self.play_btn.config(text="▶")
                self.status_label.config(text="Paused")
        else:
            # Play first track or selected
            if self.library:
                self.play_track(0)

    def next_track(self):
        """Play next track"""
        if self.library:
            next_index = (self.current_track_index + 1) % len(self.library)
            self.play_track(next_index)

    def previous_track(self):
        """Play previous track"""
        if self.library:
            prev_index = (self.current_track_index - 1) % len(self.library)
            self.play_track(prev_index)

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle = not self.shuffle

        if self.shuffle:
            self.shuffle_btn.config(fg='#4a9eff')
            self.status_label.config(text="Shuffle: ON")
        else:
            self.shuffle_btn.config(fg='#888888')
            self.status_label.config(text="Shuffle: OFF")

    def toggle_repeat(self):
        """Cycle through repeat modes"""
        modes = ['off', 'one', 'all']
        current_index = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_index + 1) % 3]

        colors = {'off': '#888888', 'one': '#4a9eff', 'all': '#50fa7b'}
        self.repeat_btn.config(fg=colors[self.repeat_mode])

        labels = {'off': 'Repeat: OFF', 'one': 'Repeat: One', 'all': 'Repeat: All'}
        self.status_label.config(text=labels[self.repeat_mode])

    def change_volume(self, value):
        """Change volume"""
        self.volume = int(float(value))
        self.config['volume'] = self.volume
        # Would set actual volume here

    def seek(self, value):
        """Seek to position"""
        # Would seek in actual playback
        pass

    def update_eq(self, freq, value):
        """Update equalizer band"""
        self.config['equalizer'][freq] = int(float(value))
        # Would apply to actual audio

    def apply_eq_preset(self, preset):
        """Apply equalizer preset"""
        presets = {
            'Flat': {'60Hz': 0, '230Hz': 0, '910Hz': 0, '3.6kHz': 0, '14kHz': 0},
            'Rock': {'60Hz': 8, '230Hz': 5, '910Hz': -2, '3.6kHz': 4, '14kHz': 6},
            'Pop': {'60Hz': -2, '230Hz': 2, '910Hz': 4, '3.6kHz': 4, '14kHz': -1},
            'Classical': {'60Hz': 0, '230Hz': 0, '910Hz': 0, '3.6kHz': 3, '14kHz': 4},
            'Bass Boost': {'60Hz': 10, '230Hz': 8, '910Hz': 0, '3.6kHz': 0, '14kHz': 0}
        }

        if preset in presets:
            for freq, value in presets[preset].items():
                self.eq_vars[freq].set(value)
                self.config['equalizer'][freq] = value

            self.status_label.config(text=f"Preset applied: {preset}")

    def create_playlist(self):
        """Create new playlist"""
        from tkinter import simpledialog

        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name and name not in self.playlists:
            self.playlists[name] = []
            self.save_playlists()
            self.playlist_listbox.insert(tk.END, name)
            messagebox.showinfo("Success", f"Playlist '{name}' created!")

    def on_playlist_select(self, event):
        """Handle playlist selection"""
        selection = self.playlist_listbox.curselection()
        if selection:
            playlist_name = self.playlist_listbox.get(selection[0])
            self.current_playlist = playlist_name
            self.load_playlist_contents(playlist_name)

    def load_playlist_contents(self, playlist_name):
        """Load playlist contents into tree"""
        self.playlist_tree.delete(*self.playlist_tree.get_children())

        if playlist_name in self.playlists:
            for track_path in self.playlists[playlist_name]:
                # Find track in library
                track = next((t for t in self.library if t['path'] == track_path), None)
                if track:
                    self.playlist_tree.insert(
                        '',
                        tk.END,
                        text=track['title'],
                        values=(track['artist'], track['duration'])
                    )

    def show_track_menu(self, event):
        """Show context menu for track"""
        menu = tk.Menu(self.root, tearoff=0, bg='#2b2b2b', fg='white')

        menu.add_command(label="Play", command=self.play_selected)
        menu.add_separator()
        menu.add_command(label="Add to Favorites", command=lambda: self.add_to_playlist('Favorites'))

        # Add submenu for other playlists
        playlist_menu = tk.Menu(menu, tearoff=0, bg='#2b2b2b', fg='white')
        for playlist_name in self.playlists.keys():
            if playlist_name not in ['Favorites', 'Recently Played']:
                playlist_menu.add_command(
                    label=playlist_name,
                    command=lambda p=playlist_name: self.add_to_playlist(p)
                )

        menu.add_cascade(label="Add to Playlist", menu=playlist_menu)

        menu.post(event.x_root, event.y_root)

    def add_to_playlist(self, playlist_name):
        """Add selected track to playlist"""
        selection = self.library_tree.selection()
        if selection and playlist_name in self.playlists:
            index = self.library_tree.index(selection[0])
            if index < len(self.library):
                track_path = self.library[index]['path']
                if track_path not in self.playlists[playlist_name]:
                    self.playlists[playlist_name].append(track_path)
                    self.save_playlists()
                    self.status_label.config(text=f"Added to {playlist_name}")

    def run(self):
        """Run the music player"""
        self.root.mainloop()

def main():
    # Note: In production, would initialize pygame.mixer here
    # import pygame
    # pygame.mixer.init()

    player = MusicPlayer()
    player.run()

if __name__ == '__main__':
    main()
