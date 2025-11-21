#!/usr/bin/env python3
"""
TL Linux - IPFS Settings & Configuration
Configure IPFS node and view system information
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
from pathlib import Path
import subprocess
import threading

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.ipfs_node import get_global_node

class IPFSSettings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚙️ TL IPFS Settings")
        self.root.geometry("800x600")

        self.ipfs_node = get_global_node()
        self.config_file = Path.home() / '.config' / 'tl-linux' / 'ipfs_config.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()

        self.setup_ui()
        self.load_current_settings()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'auto_start': False,
            'ipfs_path': str(Path.home() / '.ipfs'),
            'api_port': 5001,
            'gateway_port': 8080,
            'swarm_port': 4001
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config: {e}")
            return False

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#34495e', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="⚙️ IPFS Configuration",
            font=('Arial', 18, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack()

        # Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # General tab
        general_frame = tk.Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(general_frame, text="General")

        # Auto-start
        row = 0
        tk.Label(general_frame, text="Auto-start IPFS daemon:", bg='white', font=('Arial', 11)).grid(row=row, column=0, sticky='w', pady=10)

        self.auto_start_var = tk.BooleanVar(value=self.config.get('auto_start', False))
        tk.Checkbutton(general_frame, text="Start IPFS daemon on application launch", variable=self.auto_start_var, bg='white').grid(row=row, column=1, sticky='w', pady=10)

        # IPFS path
        row += 1
        tk.Label(general_frame, text="IPFS Repository Path:", bg='white', font=('Arial', 11)).grid(row=row, column=0, sticky='w', pady=10)

        path_frame = tk.Frame(general_frame, bg='white')
        path_frame.grid(row=row, column=1, sticky='ew', pady=10)

        self.ipfs_path_var = tk.StringVar(value=self.config.get('ipfs_path', ''))
        tk.Entry(path_frame, textvariable=self.ipfs_path_var, width=40).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(path_frame, text="Browse", command=self.browse_ipfs_path).pack(side=tk.LEFT)

        # Ports
        row += 1
        tk.Label(general_frame, text="Network Ports:", bg='white', font=('Arial', 11, 'bold')).grid(row=row, column=0, sticky='w', pady=(20, 10))

        row += 1
        tk.Label(general_frame, text="API Port:", bg='white').grid(row=row, column=0, sticky='w', pady=5)
        self.api_port_var = tk.IntVar(value=self.config.get('api_port', 5001))
        tk.Spinbox(general_frame, from_=1024, to=65535, textvariable=self.api_port_var, width=10).grid(row=row, column=1, sticky='w', pady=5)

        row += 1
        tk.Label(general_frame, text="Gateway Port:", bg='white').grid(row=row, column=0, sticky='w', pady=5)
        self.gateway_port_var = tk.IntVar(value=self.config.get('gateway_port', 8080))
        tk.Spinbox(general_frame, from_=1024, to=65535, textvariable=self.gateway_port_var, width=10).grid(row=row, column=1, sticky='w', pady=5)

        row += 1
        tk.Label(general_frame, text="Swarm Port:", bg='white').grid(row=row, column=0, sticky='w', pady=5)
        self.swarm_port_var = tk.IntVar(value=self.config.get('swarm_port', 4001))
        tk.Spinbox(general_frame, from_=1024, to=65535, textvariable=self.swarm_port_var, width=10).grid(row=row, column=1, sticky='w', pady=5)

        # Info tab
        info_frame = tk.Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(info_frame, text="Node Info")

        # Node status
        tk.Label(info_frame, text="Node Status", bg='white', font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        status_frame = tk.Frame(info_frame, bg='#ecf0f1', relief=tk.GROOVE, borderwidth=2)
        status_frame.pack(fill=tk.X, pady=(0, 20))

        self.node_status_label = tk.Label(status_frame, text="Status: Checking...", bg='#ecf0f1', font=('Arial', 10), anchor='w', padx=10, pady=5)
        self.node_status_label.pack(fill=tk.X)

        self.node_id_label = tk.Label(status_frame, text="Node ID: -", bg='#ecf0f1', font=('Arial', 10), anchor='w', padx=10, pady=5)
        self.node_id_label.pack(fill=tk.X)

        self.peers_label = tk.Label(status_frame, text="Connected Peers: -", bg='#ecf0f1', font=('Arial', 10), anchor='w', padx=10, pady=5)
        self.peers_label.pack(fill=tk.X)

        self.repo_size_label = tk.Label(status_frame, text="Repository Size: -", bg='#ecf0f1', font=('Arial', 10), anchor='w', padx=10, pady=5)
        self.repo_size_label.pack(fill=tk.X)

        tk.Button(info_frame, text="🔄 Refresh Info", command=self.refresh_node_info, bg='#3498db', fg='white', relief=tk.FLAT, padx=20, pady=5).pack(pady=10)

        # Installation info
        tk.Label(info_frame, text="IPFS Installation", bg='white', font=('Arial', 12, 'bold')).pack(anchor='w', pady=(20, 10))

        install_frame = tk.Frame(info_frame, bg='#ecf0f1', relief=tk.GROOVE, borderwidth=2)
        install_frame.pack(fill=tk.X)

        self.install_status_label = tk.Label(install_frame, text="Checking installation...", bg='#ecf0f1', font=('Arial', 10), anchor='w', padx=10, pady=5)
        self.install_status_label.pack(fill=tk.X)

        self.version_label = tk.Label(install_frame, text="Version: -", bg='#ecf0f1', font=('Arial', 10), anchor='w', padx=10, pady=5)
        self.version_label.pack(fill=tk.X)

        # Advanced tab
        advanced_frame = tk.Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(advanced_frame, text="Advanced")

        tk.Label(advanced_frame, text="Advanced Operations", bg='white', font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 20))

        tk.Button(
            advanced_frame,
            text="🗑️ Clean Repository (Garbage Collection)",
            command=self.run_garbage_collection,
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            advanced_frame,
            text="🔄 Reinitialize Repository",
            command=self.reinitialize_repo,
            bg='#f39c12',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            advanced_frame,
            text="📊 View Configuration File",
            command=self.view_ipfs_config,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(fill=tk.X, pady=5)

        tk.Label(
            advanced_frame,
            text="⚠️ Warning: Advanced operations may affect your IPFS data",
            bg='white',
            fg='#e74c3c',
            font=('Arial', 9)
        ).pack(pady=(20, 0))

        # Button frame
        button_frame = tk.Frame(self.root, bg='white', pady=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(button_frame, text="💾 Save Settings", command=self.save_settings, bg='#27ae60', fg='white', relief=tk.FLAT, padx=30, pady=8, font=('Arial', 11)).pack(side=tk.RIGHT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.root.destroy, bg='#95a5a6', fg='white', relief=tk.FLAT, padx=30, pady=8, font=('Arial', 11)).pack(side=tk.RIGHT, padx=10)

    def load_current_settings(self):
        """Load current settings and update UI"""
        # Update IPFS node path
        self.ipfs_node.ipfs_path = self.config.get('ipfs_path', str(Path.home() / '.ipfs'))

        # Check installation
        threading.Thread(target=self.check_installation, daemon=True).start()

        # Refresh node info
        self.refresh_node_info()

    def check_installation(self):
        """Check IPFS installation"""
        if self.ipfs_node.is_ipfs_installed():
            # Get version
            try:
                result = subprocess.run(['ipfs', 'version'], capture_output=True, text=True, timeout=5)
                version = result.stdout.strip()

                self.root.after(0, lambda: self.install_status_label.config(text="✓ IPFS is installed", fg='#27ae60'))
                self.root.after(0, lambda: self.version_label.config(text=f"Version: {version}"))
            except:
                self.root.after(0, lambda: self.install_status_label.config(text="✓ IPFS is installed", fg='#27ae60'))
                self.root.after(0, lambda: self.version_label.config(text="Version: Unknown"))

            # Check if initialized
            if self.ipfs_node.is_initialized():
                self.root.after(0, lambda: self.node_status_label.config(text="Status: Initialized ✓", fg='#27ae60'))
            else:
                self.root.after(0, lambda: self.node_status_label.config(text="Status: Not initialized", fg='#f39c12'))
        else:
            self.root.after(0, lambda: self.install_status_label.config(text="✗ IPFS is not installed", fg='#e74c3c'))
            self.root.after(0, lambda: self.version_label.config(text="Please install IPFS to use this feature"))

    def refresh_node_info(self):
        """Refresh node information"""
        def fetch():
            # Check if running
            if self.ipfs_node.check_daemon_status():
                self.root.after(0, lambda: self.node_status_label.config(text="Status: Running ✓", fg='#27ae60'))

                # Get node ID
                node_id, _ = self.ipfs_node.get_node_id()
                if node_id:
                    self.root.after(0, lambda: self.node_id_label.config(text=f"Node ID: {node_id}"))

                # Get peers
                peers, _ = self.ipfs_node.get_peers()
                if peers:
                    self.root.after(0, lambda: self.peers_label.config(text=f"Connected Peers: {len(peers)}"))

                # Get stats
                stats, _ = self.ipfs_node.get_stats()
                if stats:
                    size = self.format_size(stats.get('RepoSize', 0))
                    self.root.after(0, lambda: self.repo_size_label.config(text=f"Repository Size: {size}"))
            else:
                self.root.after(0, lambda: self.node_status_label.config(text="Status: Not running", fg='#e74c3c'))
                self.root.after(0, lambda: self.node_id_label.config(text="Node ID: -"))
                self.root.after(0, lambda: self.peers_label.config(text="Connected Peers: -"))
                self.root.after(0, lambda: self.repo_size_label.config(text="Repository Size: -"))

        threading.Thread(target=fetch, daemon=True).start()

    def browse_ipfs_path(self):
        """Browse for IPFS path"""
        path = filedialog.askdirectory(title="Select IPFS Repository Path", initialdir=str(Path.home()))
        if path:
            self.ipfs_path_var.set(path)

    def save_settings(self):
        """Save settings"""
        self.config['auto_start'] = self.auto_start_var.get()
        self.config['ipfs_path'] = self.ipfs_path_var.get()
        self.config['api_port'] = self.api_port_var.get()
        self.config['gateway_port'] = self.gateway_port_var.get()
        self.config['swarm_port'] = self.swarm_port_var.get()

        if self.save_config():
            messagebox.showinfo("Saved", "Settings saved successfully!\n\nRestart IPFS daemon for changes to take effect.")
            self.root.destroy()

    def run_garbage_collection(self):
        """Run IPFS garbage collection"""
        if messagebox.askyesno("Garbage Collection", "Run garbage collection to free up space?\n\nThis will remove unpinned data."):
            try:
                result = subprocess.run(
                    ['ipfs', 'repo', 'gc'],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env={'IPFS_PATH': self.ipfs_node.ipfs_path}
                )

                if result.returncode == 0:
                    messagebox.showinfo("Success", "Garbage collection completed successfully!")
                    self.refresh_node_info()
                else:
                    messagebox.showerror("Error", f"Garbage collection failed:\n{result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not run garbage collection:\n{e}")

    def reinitialize_repo(self):
        """Reinitialize IPFS repository"""
        if messagebox.askyesno(
            "Reinitialize Repository",
            "⚠️ WARNING ⚠️\n\n"
            "This will DELETE all IPFS data and reinitialize the repository.\n\n"
            "Are you sure you want to continue?"
        ):
            try:
                # Remove existing repo
                import shutil
                repo_path = Path(self.ipfs_node.ipfs_path)
                if repo_path.exists():
                    shutil.rmtree(repo_path)

                # Reinitialize
                success, msg = self.ipfs_node.initialize()

                if success:
                    messagebox.showinfo("Success", "Repository reinitialized successfully!")
                    self.refresh_node_info()
                else:
                    messagebox.showerror("Error", f"Reinitialization failed:\n{msg}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not reinitialize repository:\n{e}")

    def view_ipfs_config(self):
        """View IPFS configuration file"""
        config_path = Path(self.ipfs_node.ipfs_path) / 'config'

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_content = f.read()

                # Show in dialog
                dialog = tk.Toplevel(self.root)
                dialog.title("IPFS Configuration")
                dialog.geometry("700x500")

                text = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
                text.pack(fill=tk.BOTH, expand=True)

                text.insert('1.0', config_content)
                text.config(state=tk.DISABLED)

                tk.Button(dialog, text="Close", command=dialog.destroy, padx=20, pady=5).pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"Could not read config file:\n{e}")
        else:
            messagebox.showwarning("Not Found", "IPFS config file not found. Repository may not be initialized.")

    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    def run(self):
        """Run settings"""
        self.root.mainloop()

if __name__ == '__main__':
    settings = IPFSSettings()
    settings.run()
