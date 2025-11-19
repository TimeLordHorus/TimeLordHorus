#!/usr/bin/env python3
"""
TL Linux - Video Player
Video player with subtitle support and playback controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json
from pathlib import Path
import threading
import time
import re

class VideoPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Video Player")
        self.root.geometry("1200x750")
        self.root.configure(bg='#1a1a1a')

        # Configuration
        self.config_dir = Path.home() / '.tl-linux'
        self.config_file = self.config_dir / 'video_player_config.json'
        self.config_dir.mkdir(exist_ok=True)

        # Video state
        self.current_video = None
        self.current_subtitle = None
        self.playlist = []
        self.playlist_index = -1
        self.is_playing = False
        self.is_fullscreen = False
        self.playback_speed = 1.0
        self.volume = 100

        # MPV process
        self.mpv_process = None
        self.mpv_socket = "/tmp/tl-video-player-socket"

        # Recent videos
        self.recent_videos = []

        self.load_config()
        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🎬 Video Player",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel - Playlist
        left_panel = tk.Frame(main_container, bg='#1a1a1a', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="Playlist",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(0, 10))

        # Playlist buttons
        playlist_btn_frame = tk.Frame(left_panel, bg='#1a1a1a')
        playlist_btn_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            playlist_btn_frame,
            text="+ Add",
            command=self.add_to_playlist,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            playlist_btn_frame,
            text="- Remove",
            command=self.remove_from_playlist,
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            playlist_btn_frame,
            text="Clear",
            command=self.clear_playlist,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=2)

        # Playlist
        playlist_frame = tk.Frame(left_panel, bg='#1a1a1a')
        playlist_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(playlist_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.playlist_box = tk.Listbox(
            playlist_frame,
            bg='#2b2b2b',
            fg='white',
            selectbackground='#4a9eff',
            selectforeground='white',
            font=('Arial', 10),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_box.yview)

        self.playlist_box.bind('<Double-Button-1>', lambda e: self.play_from_playlist())

        # Recent videos
        tk.Label(
            left_panel,
            text="Recent",
            font=('Arial', 11, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=(15, 5))

        recent_frame = tk.Frame(left_panel, bg='#1a1a1a')
        recent_frame.pack(fill=tk.BOTH)

        self.recent_box = tk.Listbox(
            recent_frame,
            bg='#2b2b2b',
            fg='#888888',
            selectbackground='#4a9eff',
            selectforeground='white',
            font=('Arial', 9),
            bd=0,
            highlightthickness=0,
            height=5
        )
        self.recent_box.pack(fill=tk.BOTH)

        self.recent_box.bind('<Double-Button-1>', lambda e: self.play_recent())

        # Right panel - Video and controls
        right_panel = tk.Frame(main_container, bg='#1a1a1a')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Video display area (placeholder)
        self.video_frame = tk.Frame(right_panel, bg='black', relief=tk.SOLID, bd=1)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.video_placeholder = tk.Label(
            self.video_frame,
            text="No video loaded\n\nClick 'Open Video' to start",
            font=('Arial', 14),
            bg='black',
            fg='#888888'
        )
        self.video_placeholder.pack(expand=True)

        # Current video info
        info_frame = tk.Frame(right_panel, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, pady=(10, 5))

        self.video_title_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white',
            anchor='w'
        )
        self.video_title_label.pack(fill=tk.X)

        # Subtitle display
        self.subtitle_label = tk.Label(
            right_panel,
            text="",
            font=('Arial', 12),
            bg='#1a1a1a',
            fg='#f1fa8c',
            wraplength=700,
            justify=tk.CENTER
        )
        self.subtitle_label.pack(pady=5)

        # Progress bar
        progress_frame = tk.Frame(right_panel, bg='#1a1a1a')
        progress_frame.pack(fill=tk.X, pady=5)

        self.time_label = tk.Label(
            progress_frame,
            text="0:00 / 0:00",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_slider = ttk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.seek_video
        )
        self.progress_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Controls
        controls_frame = tk.Frame(right_panel, bg='#1a1a1a')
        controls_frame.pack(pady=10)

        # Row 1: Playback controls
        playback_frame = tk.Frame(controls_frame, bg='#1a1a1a')
        playback_frame.pack()

        tk.Button(
            playback_frame,
            text="⏮ Previous",
            command=self.previous_video,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            playback_frame,
            text="⏪ -10s",
            command=lambda: self.skip_time(-10),
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(
            playback_frame,
            text="▶ Play",
            command=self.toggle_play_pause,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            font=('Arial', 12, 'bold')
        )
        self.play_button.pack(side=tk.LEFT, padx=5)

        tk.Button(
            playback_frame,
            text="+10s ⏩",
            command=lambda: self.skip_time(10),
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            playback_frame,
            text="Next ⏭",
            command=self.next_video,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Row 2: Additional controls
        additional_frame = tk.Frame(controls_frame, bg='#1a1a1a')
        additional_frame.pack(pady=(10, 0))

        tk.Button(
            additional_frame,
            text="📂 Open Video",
            command=self.open_video,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            additional_frame,
            text="📄 Load Subtitle",
            command=self.load_subtitle,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Speed control
        speed_frame = tk.Frame(additional_frame, bg='#1a1a1a')
        speed_frame.pack(side=tk.LEFT, padx=(10, 5))

        tk.Label(
            speed_frame,
            text="Speed:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.speed_var = tk.StringVar(value="1.0x")
        speed_combo = ttk.Combobox(
            speed_frame,
            textvariable=self.speed_var,
            values=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"],
            width=8,
            state='readonly'
        )
        speed_combo.pack(side=tk.LEFT)
        speed_combo.bind('<<ComboboxSelected>>', self.change_speed)

        # Volume control
        volume_frame = tk.Frame(additional_frame, bg='#1a1a1a')
        volume_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(
            volume_frame,
            text="🔊",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.volume_var = tk.IntVar(value=100)
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

        tk.Button(
            additional_frame,
            text="⛶ Fullscreen",
            command=self.toggle_fullscreen,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Update recent videos display
        self.update_recent_display()

    def open_video(self):
        """Open a video file"""
        filetypes = [
            ("Video files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Open Video",
            filetypes=filetypes
        )

        if filename:
            self.load_video(filename)

    def load_video(self, filepath):
        """Load and play a video"""
        self.current_video = filepath
        self.video_title_label.config(text=Path(filepath).name)
        self.video_placeholder.config(text=f"Playing:\n{Path(filepath).name}")

        # Add to recent
        self.add_to_recent(filepath)

        # Stop current playback
        self.stop_video()

        # Start MPV
        self.start_mpv(filepath)

        self.is_playing = True
        self.play_button.config(text="⏸ Pause")

    def start_mpv(self, filepath):
        """Start MPV player"""
        try:
            # Remove old socket
            if os.path.exists(self.mpv_socket):
                os.remove(self.mpv_socket)

            # Start MPV with IPC socket
            cmd = [
                'mpv',
                '--no-terminal',
                '--force-window=immediate',
                '--keep-open=yes',
                '--wid=' + str(self.video_frame.winfo_id()),
                '--input-ipc-server=' + self.mpv_socket,
                '--osd-level=0',
                filepath
            ]

            if self.current_subtitle:
                cmd.extend(['--sub-file=' + self.current_subtitle])

            self.mpv_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Start monitoring thread
            threading.Thread(target=self.monitor_playback, daemon=True).start()

        except FileNotFoundError:
            messagebox.showerror(
                "MPV Not Found",
                "MPV player is not installed.\n\n"
                "Install it with:\nsudo apt install mpv"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start video:\n{str(e)}")

    def stop_video(self):
        """Stop current video"""
        if self.mpv_process:
            try:
                self.mpv_process.terminate()
                self.mpv_process.wait(timeout=2)
            except:
                self.mpv_process.kill()

            self.mpv_process = None

        self.is_playing = False
        self.play_button.config(text="▶ Play")

    def toggle_play_pause(self):
        """Toggle play/pause"""
        if not self.mpv_process:
            if self.current_video:
                self.load_video(self.current_video)
            else:
                self.open_video()
            return

        self.send_mpv_command('cycle pause')

        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.config(text="⏸ Pause")
        else:
            self.play_button.config(text="▶ Play")

    def seek_video(self, value):
        """Seek to position"""
        if self.mpv_process:
            self.send_mpv_command(f'seek {value} absolute-percent')

    def skip_time(self, seconds):
        """Skip forward or backward"""
        if self.mpv_process:
            self.send_mpv_command(f'seek {seconds}')

    def change_speed(self, event=None):
        """Change playback speed"""
        speed_str = self.speed_var.get().rstrip('x')
        try:
            speed = float(speed_str)
            self.playback_speed = speed

            if self.mpv_process:
                self.send_mpv_command(f'set speed {speed}')
        except ValueError:
            pass

    def change_volume(self, value):
        """Change volume"""
        volume = int(float(value))
        self.volume = volume

        if self.mpv_process:
            self.send_mpv_command(f'set volume {volume}')

    def send_mpv_command(self, command):
        """Send command to MPV via IPC"""
        try:
            cmd = {
                'command': command.split()
            }

            # Use socat to send command
            subprocess.run(
                ['socat', '-', self.mpv_socket],
                input=json.dumps(cmd).encode(),
                timeout=1,
                capture_output=True
            )
        except Exception as e:
            print(f"MPV command error: {e}")

    def monitor_playback(self):
        """Monitor playback progress"""
        while self.mpv_process and self.mpv_process.poll() is None:
            try:
                # Get playback position
                # This is a simplified version - full implementation would query MPV
                time.sleep(0.5)
            except:
                pass

        # Video finished
        if self.is_playing:
            self.root.after(0, self.next_video)

    def load_subtitle(self):
        """Load subtitle file"""
        filetypes = [
            ("Subtitle files", "*.srt *.ass *.ssa *.sub"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Load Subtitle",
            filetypes=filetypes
        )

        if filename:
            self.current_subtitle = filename

            if self.mpv_process:
                self.send_mpv_command(f'sub-add "{filename}"')

            self.subtitle_label.config(text=f"Subtitle loaded: {Path(filename).name}")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.mpv_process:
            self.send_mpv_command('cycle fullscreen')
            self.is_fullscreen = not self.is_fullscreen

    def add_to_playlist(self):
        """Add videos to playlist"""
        filetypes = [
            ("Video files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v"),
            ("All files", "*.*")
        ]

        filenames = filedialog.askopenfilenames(
            title="Add to Playlist",
            filetypes=filetypes
        )

        for filename in filenames:
            if filename not in self.playlist:
                self.playlist.append(filename)
                self.playlist_box.insert(tk.END, Path(filename).name)

    def remove_from_playlist(self):
        """Remove selected video from playlist"""
        selection = self.playlist_box.curselection()
        if selection:
            index = selection[0]
            self.playlist_box.delete(index)
            self.playlist.pop(index)

            # Adjust current index if needed
            if self.playlist_index >= index:
                self.playlist_index -= 1

    def clear_playlist(self):
        """Clear playlist"""
        self.playlist.clear()
        self.playlist_box.delete(0, tk.END)
        self.playlist_index = -1

    def play_from_playlist(self):
        """Play selected video from playlist"""
        selection = self.playlist_box.curselection()
        if selection:
            self.playlist_index = selection[0]
            video_path = self.playlist[self.playlist_index]
            self.load_video(video_path)

    def next_video(self):
        """Play next video in playlist"""
        if not self.playlist:
            return

        self.playlist_index = (self.playlist_index + 1) % len(self.playlist)
        video_path = self.playlist[self.playlist_index]
        self.load_video(video_path)

        # Update selection
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(self.playlist_index)
        self.playlist_box.see(self.playlist_index)

    def previous_video(self):
        """Play previous video in playlist"""
        if not self.playlist:
            return

        self.playlist_index = (self.playlist_index - 1) % len(self.playlist)
        video_path = self.playlist[self.playlist_index]
        self.load_video(video_path)

        # Update selection
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(self.playlist_index)
        self.playlist_box.see(self.playlist_index)

    def play_recent(self):
        """Play video from recent list"""
        selection = self.recent_box.curselection()
        if selection:
            video_path = self.recent_videos[selection[0]]
            if os.path.exists(video_path):
                self.load_video(video_path)
            else:
                messagebox.showwarning("File Not Found", "Video file no longer exists")
                self.recent_videos.pop(selection[0])
                self.update_recent_display()

    def add_to_recent(self, filepath):
        """Add video to recent list"""
        if filepath in self.recent_videos:
            self.recent_videos.remove(filepath)

        self.recent_videos.insert(0, filepath)
        self.recent_videos = self.recent_videos[:10]  # Keep last 10

        self.update_recent_display()
        self.save_config()

    def update_recent_display(self):
        """Update recent videos display"""
        self.recent_box.delete(0, tk.END)

        for video_path in self.recent_videos:
            self.recent_box.insert(tk.END, Path(video_path).name)

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.recent_videos = config.get('recent_videos', [])
            except:
                pass

    def save_config(self):
        """Save configuration"""
        config = {
            'recent_videos': self.recent_videos
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def run(self):
        """Run the video player"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        self.stop_video()
        self.save_config()
        self.root.destroy()

def main():
    player = VideoPlayer()
    player.run()

if __name__ == '__main__':
    main()
