#!/usr/bin/env python3
"""
TL Linux Emulator Hub
Central hub for retro gaming emulators
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import shutil
from pathlib import Path

class EmulatorHub:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 TL Emulator Hub")
        self.root.geometry("900x700")

        self.roms_dir = Path.home() / 'ROMs'
        self.roms_dir.mkdir(exist_ok=True)

        # Emulator configurations
        self.emulators = {
            'NES': {
                'name': 'Nintendo Entertainment System',
                'icon': '🎮',
                'emulator': 'fceux',
                'extensions': ['.nes'],
                'install_cmd': 'sudo apt install fceux',
            },
            'SNES': {
                'name': 'Super Nintendo',
                'icon': '🎯',
                'emulator': 'snes9x-gtk',
                'extensions': ['.smc', '.sfc'],
                'install_cmd': 'sudo apt install snes9x-gtk',
            },
            'GB': {
                'name': 'Game Boy / Game Boy Color',
                'icon': '📱',
                'emulator': 'mgba-qt',
                'extensions': ['.gb', '.gbc'],
                'install_cmd': 'sudo apt install mgba-qt',
            },
            'GBA': {
                'name': 'Game Boy Advance',
                'icon': '🎪',
                'emulator': 'mgba-qt',
                'extensions': ['.gba'],
                'install_cmd': 'sudo apt install mgba-qt',
            },
            'N64': {
                'name': 'Nintendo 64',
                'icon': '🎲',
                'emulator': 'mupen64plus',
                'extensions': ['.n64', '.z64', '.v64'],
                'install_cmd': 'sudo apt install mupen64plus',
            },
            'Genesis': {
                'name': 'Sega Genesis / Mega Drive',
                'icon': '⚡',
                'emulator': 'gens',
                'extensions': ['.bin', '.md', '.smd'],
                'install_cmd': 'sudo apt install gens',
            },
            'PS1': {
                'name': 'PlayStation 1',
                'icon': '💿',
                'emulator': 'pcsx',
                'extensions': ['.bin', '.cue', '.img', '.iso'],
                'install_cmd': 'sudo apt install pcsxr',
            },
            'Arcade': {
                'name': 'Arcade (MAME)',
                'icon': '🕹️',
                'emulator': 'mame',
                'extensions': ['.zip'],
                'install_cmd': 'sudo apt install mame',
            },
            'DOS': {
                'name': 'DOS Games',
                'icon': '💻',
                'emulator': 'dosbox',
                'extensions': ['.exe', '.com', '.bat'],
                'install_cmd': 'sudo apt install dosbox',
            }
        }

        self.check_installed_emulators()
        self.setup_ui()

    def check_installed_emulators(self):
        """Check which emulators are installed"""
        for system, config in self.emulators.items():
            config['installed'] = shutil.which(config['emulator']) is not None

    def setup_ui(self):
        """Setup emulator hub UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a1a', pady=15)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="🎮 TL Emulator Hub",
            font=('Sans', 24, 'bold'),
            bg='#1a1a1a',
            fg='#FF00FF'
        ).pack()

        tk.Label(
            header_frame,
            text="Play classic games from multiple platforms",
            font=('Sans', 11),
            bg='#1a1a1a',
            fg='#00FF00'
        ).pack()

        # Main content
        content_frame = tk.Frame(self.root, bg='#0a0a0a')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left panel - System selection
        left_panel = tk.Frame(content_frame, bg='#1a1a1a', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="Gaming Systems",
            font=('Sans', 12, 'bold'),
            bg='#1a1a1a',
            fg='#00FFFF',
            pady=10
        ).pack()

        # System buttons
        self.system_buttons = {}
        for system, config in self.emulators.items():
            btn_frame = tk.Frame(left_panel, bg='#1a1a1a')
            btn_frame.pack(fill=tk.X, padx=10, pady=3)

            status = "✓" if config['installed'] else "✗"
            status_color = '#00FF00' if config['installed'] else '#666666'

            btn = tk.Button(
                btn_frame,
                text=f"{config['icon']} {system}",
                command=lambda s=system: self.select_system(s),
                bg='#333333',
                fg='#00FF00',
                font=('Sans', 10),
                relief=tk.FLAT,
                anchor='w',
                padx=10,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.system_buttons[system] = btn

            tk.Label(
                btn_frame,
                text=status,
                bg='#333333',
                fg=status_color,
                font=('Sans', 10, 'bold'),
                width=2
            ).pack(side=tk.RIGHT)

        # Right panel - ROM list and controls
        self.right_panel = tk.Frame(content_frame, bg='#0a0a0a')
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initial welcome message
        self.show_welcome()

        # Bottom toolbar
        toolbar = tk.Frame(self.root, bg='#1a1a1a', pady=10)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            toolbar,
            text="📁 Open ROMs Folder",
            command=self.open_roms_folder,
            bg='#333333',
            fg='#00FF00',
            font=('Sans', 10),
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            toolbar,
            text="⚙️ Install Emulators",
            command=self.install_emulators_dialog,
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 10, 'bold'),
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="❓ Help",
            command=self.show_help,
            bg='#333333',
            fg='#00FF00',
            font=('Sans', 10),
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=10)

    def show_welcome(self):
        """Show welcome screen"""
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        welcome_text = """
        Welcome to TL Emulator Hub!

        Select a gaming system from the left panel to begin.

        🎮 Getting Started:
        1. Choose a system (NES, SNES, etc.)
        2. Install the emulator if needed
        3. Add ROM files to your ROMs folder
        4. Select and play!

        💡 Tips:
        • ROMs folder: ~/ROMs/
        • Organize ROMs by system
        • Check emulator status (✓/✗) in left panel
        """

        tk.Label(
            self.right_panel,
            text=welcome_text,
            font=('Monospace', 11),
            bg='#0a0a0a',
            fg='#00FF00',
            justify=tk.LEFT,
            anchor='nw'
        ).pack(expand=True, padx=30, pady=30)

    def select_system(self, system):
        """Select gaming system"""
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        config = self.emulators[system]

        # System header
        header = tk.Frame(self.right_panel, bg='#1a1a1a', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=f"{config['icon']} {config['name']}",
            font=('Sans', 18, 'bold'),
            bg='#1a1a1a',
            fg='#FF00FF'
        ).pack()

        # Check if emulator is installed
        if not config['installed']:
            self.show_install_prompt(system, config)
            return

        # ROM list
        roms_frame = tk.Frame(self.right_panel, bg='#0a0a0a')
        roms_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            roms_frame,
            text="Available ROMs:",
            font=('Sans', 11, 'bold'),
            bg='#0a0a0a',
            fg='#00FFFF',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))

        # ROM listbox
        rom_list_frame = tk.Frame(roms_frame, bg='#0a0a0a')
        rom_list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(rom_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        rom_listbox = tk.Listbox(
            rom_list_frame,
            bg='#000000',
            fg='#00FF00',
            font=('Monospace', 10),
            selectbackground='#333333',
            yscrollcommand=scrollbar.set,
            bd=0
        )
        rom_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=rom_listbox.yview)

        # Find ROMs
        system_roms_dir = self.roms_dir / system
        system_roms_dir.mkdir(exist_ok=True)

        roms = []
        for ext in config['extensions']:
            roms.extend(system_roms_dir.glob(f"*{ext}"))

        if roms:
            for rom in sorted(roms):
                rom_listbox.insert(tk.END, rom.name)
        else:
            rom_listbox.insert(tk.END, f"No ROMs found in {system_roms_dir}")
            rom_listbox.config(fg='#666666')

        # Control buttons
        controls = tk.Frame(roms_frame, bg='#0a0a0a', pady=10)
        controls.pack(fill=tk.X)

        def play_selected():
            selection = rom_listbox.curselection()
            if selection and roms:
                rom_path = roms[selection[0]]
                self.launch_emulator(system, rom_path)

        tk.Button(
            controls,
            text="▶ Play Selected",
            command=play_selected,
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 12, 'bold'),
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="➕ Add ROMs",
            command=lambda: self.add_roms(system),
            bg='#333333',
            fg='#00FF00',
            font=('Sans', 10),
            bd=0,
            padx=15,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)

        # Double-click to play
        rom_listbox.bind('<Double-1>', lambda e: play_selected())

    def show_install_prompt(self, system, config):
        """Show emulator installation prompt"""
        prompt_frame = tk.Frame(self.right_panel, bg='#0a0a0a')
        prompt_frame.pack(expand=True)

        tk.Label(
            prompt_frame,
            text="⚠ Emulator Not Installed",
            font=('Sans', 16, 'bold'),
            bg='#0a0a0a',
            fg='#FFFF00'
        ).pack(pady=20)

        tk.Label(
            prompt_frame,
            text=f"The {config['name']} emulator is not installed.\n\n"
                 f"Emulator: {config['emulator']}\n"
                 f"Install command: {config['install_cmd']}",
            font=('Monospace', 10),
            bg='#0a0a0a',
            fg='#00FF00',
            justify=tk.CENTER
        ).pack(pady=10)

        tk.Button(
            prompt_frame,
            text="Install Emulator",
            command=lambda: self.install_emulator(system),
            bg='#FF00FF',
            fg='#000000',
            font=('Sans', 12, 'bold'),
            bd=0,
            padx=30,
            pady=15,
            cursor='hand2'
        ).pack(pady=20)

    def install_emulator(self, system):
        """Install emulator for system"""
        config = self.emulators[system]
        if messagebox.askyesno("Install Emulator",
                              f"Install {config['name']} emulator?\n\n{config['install_cmd']}"):
            try:
                subprocess.run(config['install_cmd'].split(), check=True)
                messagebox.showinfo("Success", f"{config['name']} emulator installed!")
                self.check_installed_emulators()
                self.select_system(system)
            except Exception as e:
                messagebox.showerror("Error", f"Installation failed:\n{e}")

    def launch_emulator(self, system, rom_path):
        """Launch emulator with ROM"""
        config = self.emulators[system]

        try:
            print(f"Launching {config['emulator']} with {rom_path}")
            subprocess.Popen([config['emulator'], str(rom_path)])
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch emulator:\n{e}")

    def add_roms(self, system):
        """Add ROMs for system"""
        config = self.emulators[system]
        files = filedialog.askopenfilenames(
            title=f"Select {system} ROMs",
            filetypes=[("ROM Files", " ".join(f"*{ext}" for ext in config['extensions'])),
                      ("All Files", "*.*")]
        )

        if files:
            system_roms_dir = self.roms_dir / system
            count = 0
            for file_path in files:
                import shutil as sh
                sh.copy(file_path, system_roms_dir)
                count += 1

            messagebox.showinfo("ROMs Added", f"Added {count} ROM(s) to {system}")
            self.select_system(system)

    def open_roms_folder(self):
        """Open ROMs folder in file manager"""
        try:
            subprocess.Popen(['xdg-open', str(self.roms_dir)])
        except:
            messagebox.showinfo("ROMs Folder", f"ROMs location:\n{self.roms_dir}")

    def install_emulators_dialog(self):
        """Show emulator installation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Install Emulators")
        dialog.geometry("500x400")
        dialog.configure(bg='#1a1a1a')

        tk.Label(
            dialog,
            text="Available Emulators",
            font=('Sans', 14, 'bold'),
            bg='#1a1a1a',
            fg='#FF00FF'
        ).pack(pady=10)

        for system, config in self.emulators.items():
            frame = tk.Frame(dialog, bg='#0a0a0a', pady=5)
            frame.pack(fill=tk.X, padx=20, pady=2)

            status = "Installed ✓" if config['installed'] else "Not Installed"
            color = '#00FF00' if config['installed'] else '#FF3333'

            tk.Label(
                frame,
                text=f"{config['icon']} {system}",
                bg='#0a0a0a',
                fg='#00FF00',
                font=('Sans', 10),
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)

            tk.Label(
                frame,
                text=status,
                bg='#0a0a0a',
                fg=color,
                font=('Sans', 9),
                width=15
            ).pack(side=tk.LEFT)

            if not config['installed']:
                tk.Button(
                    frame,
                    text="Install",
                    command=lambda s=system: self.install_emulator(s),
                    bg='#FF00FF',
                    fg='#000000',
                    font=('Sans', 8, 'bold'),
                    bd=0,
                    cursor='hand2',
                    padx=10
                ).pack(side=tk.RIGHT)

    def show_help(self):
        """Show help information"""
        help_text = """
TL Emulator Hub Help

🎮 Supported Systems:
• NES, SNES, Game Boy, GBA
• Nintendo 64, Sega Genesis
• PlayStation 1, Arcade (MAME)
• DOS Games

📁 ROM Management:
• ROMs folder: ~/ROMs/
• Organize by system subfolder
• Supported formats vary by system

⚙️ Installation:
• Click "Install Emulators" button
• Or select a system and install individually

▶ Playing Games:
• Select system from left panel
• Double-click ROM to play
• Or select and click "Play Selected"
        """

        messagebox.showinfo("Help", help_text)

    def run(self):
        """Run emulator hub"""
        self.root.mainloop()

if __name__ == '__main__':
    hub = EmulatorHub()
    hub.run()
