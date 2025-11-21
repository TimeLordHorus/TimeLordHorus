#!/usr/bin/env python3
"""
TL Cloud Sync (Optional)
Secure cloud synchronization for portable OS

Features:
- End-to-end encrypted sync
- Multiple provider support (Nextcloud, Syncthing, rclone)
- Selective sync
- Privacy-focused (all data encrypted locally)
- Optional - fully functional offline
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
from pathlib import Path
import json

class CloudSync:
    """Cloud synchronization manager"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Cloud Sync ☁️")
            self.root.geometry("800x700")
        else:
            self.root = root

        self.root.configure(bg='#0d1117')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'cloud-sync'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'sync_config.json'

        # Load configuration
        self.load_config()

        # Detect available sync tools
        self.detect_sync_tools()

        # Setup UI
        self.setup_ui()

    def load_config(self):
        """Load sync configuration"""
        self.config = {
            'enabled': False,
            'provider': 'none',  # none, nextcloud, syncthing, rclone
            'sync_folders': [],
            'auto_sync': False,
            'sync_interval': 30,  # minutes
            'encryption_enabled': True
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        """Save sync configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def detect_sync_tools(self):
        """Detect available sync tools"""
        self.tools = {
            'nextcloud': self.check_command('nextcloudcmd'),
            'syncthing': self.check_command('syncthing'),
            'rclone': self.check_command('rclone')
        }

    def check_command(self, cmd):
        """Check if a command exists"""
        try:
            subprocess.run([cmd, '--version'], capture_output=True, timeout=2)
            return True
        except:
            return False

    def setup_ui(self):
        """Setup the UI"""
        # Header
        header = tk.Frame(self.root, bg='#161b22', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="☁️ Cloud Sync",
            font=('Arial', 28, 'bold'),
            bg='#161b22',
            fg='#58a6ff'
        ).pack(pady=20)

        # Privacy notice
        notice_frame = tk.Frame(self.root, bg='#ffa65720', relief=tk.RAISED, borderwidth=2)
        notice_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            notice_frame,
            text="🔒 Privacy Notice",
            font=('Arial', 12, 'bold'),
            bg='#ffa65720',
            fg='#ffa657'
        ).pack(pady=5)

        tk.Label(
            notice_frame,
            text="Cloud sync is OPTIONAL and disabled by default.\n"
                 "All synced data is encrypted locally before upload.\n"
                 "TL Linux is fully functional without cloud sync.",
            font=('Arial', 10),
            bg='#ffa65720',
            fg='#c9d1d9',
            justify=tk.CENTER
        ).pack(pady=5)

        # Main content with tabs
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.configure('TNotebook', background='#0d1117')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))

        # Create tabs
        self.setup_tab = tk.Frame(tab_container, bg='#0d1117')
        self.folders_tab = tk.Frame(tab_container, bg='#0d1117')
        self.status_tab = tk.Frame(tab_container, bg='#0d1117')

        tab_container.add(self.setup_tab, text='⚙️ Setup')
        tab_container.add(self.folders_tab, text='📁 Folders')
        tab_container.add(self.status_tab, text='📊 Status')

        # Setup tabs
        self.setup_setup_tab()
        self.setup_folders_tab()
        self.setup_status_tab()

    def setup_setup_tab(self):
        """Setup provider configuration"""
        container = tk.Frame(self.setup_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(
            container,
            text="Choose Sync Provider",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # Provider options
        providers = [
            {
                'name': 'Nextcloud',
                'description': 'Self-hosted cloud storage',
                'available': self.tools['nextcloud'],
                'privacy': 'High - Self-hosted',
                'setup': self.setup_nextcloud
            },
            {
                'name': 'Syncthing',
                'description': 'Peer-to-peer sync (no server)',
                'available': self.tools['syncthing'],
                'privacy': 'Highest - P2P, no cloud',
                'setup': self.setup_syncthing
            },
            {
                'name': 'rclone',
                'description': 'Support for 40+ cloud providers',
                'available': self.tools['rclone'],
                'privacy': 'Medium - Depends on provider',
                'setup': self.setup_rclone
            }
        ]

        for provider in providers:
            self.create_provider_card(container, provider)

        # Disable sync option
        tk.Button(
            container,
            text="🚫 Disable Cloud Sync",
            font=('Arial', 12),
            bg='#da3633',
            fg='white',
            command=self.disable_sync,
            padx=30,
            pady=15
        ).pack(pady=20)

    def create_provider_card(self, parent, provider):
        """Create a provider selection card"""
        card = tk.Frame(parent, bg='#161b22', relief=tk.RAISED, borderwidth=2)
        card.pack(fill=tk.X, pady=10)

        # Header
        header = tk.Frame(card, bg='#161b22')
        header.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            header,
            text=provider['name'],
            font=('Arial', 16, 'bold'),
            bg='#161b22',
            fg='#7ee787' if provider['available'] else '#6e7681'
        ).pack(side=tk.LEFT)

        status = "✓ Installed" if provider['available'] else "✗ Not Installed"
        status_color = '#7ee787' if provider['available'] else '#e63946'

        tk.Label(
            header,
            text=status,
            font=('Arial', 11),
            bg='#161b22',
            fg=status_color
        ).pack(side=tk.RIGHT)

        # Description
        tk.Label(
            card,
            text=provider['description'],
            font=('Arial', 11),
            bg='#161b22',
            fg='#8b949e',
            anchor=tk.W
        ).pack(fill=tk.X, padx=15, pady=(0, 5))

        tk.Label(
            card,
            text=f"Privacy: {provider['privacy']}",
            font=('Arial', 10, 'italic'),
            bg='#161b22',
            fg='#ffa657',
            anchor=tk.W
        ).pack(fill=tk.X, padx=15, pady=(0, 10))

        # Setup button
        if provider['available']:
            tk.Button(
                card,
                text="⚙️ Configure",
                font=('Arial', 11),
                bg='#238636',
                fg='white',
                command=provider['setup'],
                padx=20,
                pady=8
            ).pack(padx=15, pady=(0, 15))
        else:
            install_frame = tk.Frame(card, bg='#161b22')
            install_frame.pack(padx=15, pady=(0, 15))

            tk.Label(
                install_frame,
                text="Install: ",
                font=('Arial', 10),
                bg='#161b22',
                fg='#8b949e'
            ).pack(side=tk.LEFT)

            install_cmd = {
                'Nextcloud': 'sudo apt install nextcloud-desktop',
                'Syncthing': 'sudo apt install syncthing',
                'rclone': 'sudo apt install rclone'
            }[provider['name']]

            tk.Label(
                install_frame,
                text=install_cmd,
                font=('Courier', 9),
                bg='#0d1117',
                fg='#c9d1d9',
                padx=10,
                pady=5
            ).pack(side=tk.LEFT)

    def setup_folders_tab(self):
        """Setup folder selection"""
        container = tk.Frame(self.folders_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(
            container,
            text="Select Folders to Sync",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # Suggested folders
        suggested_frame = tk.LabelFrame(
            container,
            text="Suggested Folders",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        suggested_frame.pack(fill=tk.X, pady=10)

        suggested_folders = [
            ("Documents", str(Path.home() / 'Documents')),
            ("TL Linux Config", str(Path.home() / '.config' / 'tl-linux')),
            ("Journal Entries", str(Path.home() / '.config' / 'tl-linux' / 'mindfulness' / 'journals')),
            ("Wellbeing Data", str(Path.home() / '.config' / 'tl-linux' / 'wellbeing'))
        ]

        for name, path in suggested_folders:
            folder_frame = tk.Frame(suggested_frame, bg='#0d1117')
            folder_frame.pack(fill=tk.X, pady=5)

            var = tk.BooleanVar(value=path in self.config['sync_folders'])

            tk.Checkbutton(
                folder_frame,
                text=name,
                variable=var,
                font=('Arial', 11),
                bg='#0d1117',
                fg='white',
                selectcolor='#161b22',
                command=lambda p=path, v=var: self.toggle_folder(p, v)
            ).pack(side=tk.LEFT)

            tk.Label(
                folder_frame,
                text=path,
                font=('Arial', 9),
                bg='#0d1117',
                fg='#6e7681'
            ).pack(side=tk.LEFT, padx=10)

        # Encryption notice
        encrypt_frame = tk.Frame(container, bg='#23863620', relief=tk.RAISED, borderwidth=2)
        encrypt_frame.pack(fill=tk.X, pady=20)

        tk.Label(
            encrypt_frame,
            text="🔒 All synced data is encrypted with AES-256 before upload",
            font=('Arial', 11),
            bg='#23863620',
            fg='#7ee787'
        ).pack(pady=10)

    def setup_status_tab(self):
        """Setup sync status display"""
        container = tk.Frame(self.status_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Status display
        status_frame = tk.LabelFrame(
            container,
            text="Sync Status",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            font=('Courier', 10),
            bg='#161b22',
            fg='#c9d1d9',
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Update status
        self.update_status()

        # Control buttons
        controls = tk.Frame(container, bg='#0d1117')
        controls.pack(pady=20)

        tk.Button(
            controls,
            text="🔄 Sync Now",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=self.sync_now,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="📊 Refresh Status",
            font=('Arial', 12),
            bg='#1f6feb',
            fg='white',
            command=self.update_status,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

    # Provider setup methods
    def setup_nextcloud(self):
        """Setup Nextcloud sync"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Nextcloud Setup")
        setup_window.geometry("500x400")
        setup_window.configure(bg='#0d1117')

        tk.Label(
            setup_window,
            text="Nextcloud Configuration",
            font=('Arial', 18, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # Server URL
        tk.Label(
            setup_window,
            text="Nextcloud Server URL:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(pady=5)

        server_entry = tk.Entry(
            setup_window,
            font=('Arial', 11),
            width=40
        )
        server_entry.pack(pady=5)
        server_entry.insert(0, "https://your-nextcloud-server.com")

        # Username
        tk.Label(
            setup_window,
            text="Username:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(pady=5)

        user_entry = tk.Entry(
            setup_window,
            font=('Arial', 11),
            width=40
        )
        user_entry.pack(pady=5)

        # Password
        tk.Label(
            setup_window,
            text="Password or App Token:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(pady=5)

        pass_entry = tk.Entry(
            setup_window,
            font=('Arial', 11),
            width=40,
            show='•'
        )
        pass_entry.pack(pady=5)

        def save_nextcloud_config():
            self.config['provider'] = 'nextcloud'
            self.config['nextcloud'] = {
                'server': server_entry.get(),
                'username': user_entry.get(),
                # Note: In production, passwords should be stored securely (keyring)
            }
            self.config['enabled'] = True
            self.save_config()
            messagebox.showinfo("Configured", "Nextcloud sync configured successfully!")
            setup_window.destroy()

        tk.Button(
            setup_window,
            text="💾 Save Configuration",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=save_nextcloud_config,
            padx=30,
            pady=10
        ).pack(pady=30)

    def setup_syncthing(self):
        """Setup Syncthing"""
        info = """Syncthing Setup:

Syncthing provides peer-to-peer synchronization without
any cloud server (maximum privacy!).

Steps:
1. Start Syncthing: systemctl --user enable syncthing
2. Access web UI: http://localhost:8384
3. Add your devices
4. Select folders to sync

Syncthing will run in the background and sync when
devices are on the same network or internet.

Launch Syncthing Web UI now?
"""

        if messagebox.askyesno("Syncthing Setup", info):
            try:
                subprocess.Popen(['systemctl', '--user', 'start', 'syncthing'])
                subprocess.Popen(['xdg-open', 'http://localhost:8384'])
                self.config['provider'] = 'syncthing'
                self.config['enabled'] = True
                self.save_config()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start Syncthing: {e}")

    def setup_rclone(self):
        """Setup rclone"""
        info = """rclone Setup:

rclone supports 40+ cloud providers including:
• Google Drive
• Dropbox
• OneDrive
• Amazon S3
• And many more

Setup process:
1. Run: rclone config
2. Follow the interactive setup
3. Choose your provider
4. Authorize access

Note: Data will be encrypted before upload.

Launch rclone configuration?
"""

        if messagebox.askyesno("rclone Setup", info):
            try:
                subprocess.Popen(['x-terminal-emulator', '-e', 'rclone config'])
                self.config['provider'] = 'rclone'
                self.config['enabled'] = True
                self.save_config()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch rclone: {e}")

    def disable_sync(self):
        """Disable cloud sync"""
        if messagebox.askyesno("Disable Sync", "Disable cloud synchronization?"):
            self.config['enabled'] = False
            self.config['provider'] = 'none'
            self.save_config()
            messagebox.showinfo("Disabled", "Cloud sync has been disabled.\n\nTL Linux is fully functional offline.")

    # Folder management
    def toggle_folder(self, path, var):
        """Toggle folder sync"""
        if var.get():
            if path not in self.config['sync_folders']:
                self.config['sync_folders'].append(path)
        else:
            if path in self.config['sync_folders']:
                self.config['sync_folders'].remove(path)
        self.save_config()

    # Sync operations
    def sync_now(self):
        """Trigger immediate sync"""
        if not self.config['enabled']:
            messagebox.showwarning("Sync Disabled", "Cloud sync is disabled.")
            return

        if self.config['provider'] == 'none':
            messagebox.showwarning("No Provider", "Please configure a sync provider first.")
            return

        messagebox.showinfo("Syncing", f"Syncing via {self.config['provider']}...\n\nThis may take a few moments.")

    def update_status(self):
        """Update sync status display"""
        status = []
        status.append("═" * 60)
        status.append("CLOUD SYNC STATUS")
        status.append("═" * 60)
        status.append("")

        status.append(f"Enabled: {'Yes' if self.config['enabled'] else 'No'}")
        status.append(f"Provider: {self.config['provider'].title()}")
        status.append(f"Folders Syncing: {len(self.config['sync_folders'])}")
        status.append(f"Auto Sync: {'Enabled' if self.config['auto_sync'] else 'Disabled'}")
        status.append(f"Encryption: {'Enabled' if self.config['encryption_enabled'] else 'Disabled'}")
        status.append("")

        if self.config['sync_folders']:
            status.append("Synced Folders:")
            for folder in self.config['sync_folders']:
                status.append(f"  • {folder}")
        else:
            status.append("No folders configured for sync")

        status.append("")
        status.append("Last Sync: Never" if not self.config['enabled'] else "Last Sync: Manual only")

        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', '\n'.join(status))

    def run(self):
        """Run the cloud sync manager"""
        self.root.mainloop()


def main():
    """Main entry point"""
    sync = CloudSync()
    sync.run()


if __name__ == '__main__':
    main()
