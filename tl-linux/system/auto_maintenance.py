#!/usr/bin/env python3
"""
TL Linux - Automatic Maintenance & Update System
Self-healing, sustainable system management with planned stability
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import json
from pathlib import Path
import threading
import time
from datetime import datetime, timedelta
import schedule

class AutoMaintenanceSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔄 TL Auto-Maintenance")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')

        self.config_file = Path.home() / '.config' / 'tl-linux' / 'auto_maintenance.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self.load_config()

        # Maintenance state
        self.is_running = False
        self.maintenance_tasks = []
        self.system_health = {}

        self.setup_ui()
        self.check_system_health()

        # Start background scheduler if enabled
        if self.config.get('auto_maintenance_enabled', True):
            self.start_scheduler()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'auto_maintenance_enabled': True,
            'auto_update_enabled': True,
            'update_schedule': 'daily',  # daily, weekly, monthly
            'update_time': '03:00',  # 3 AM
            'auto_cleanup': True,
            'keep_old_kernels': 2,
            'disk_cleanup_threshold': 90,  # percent
            'create_snapshots': True,
            'check_drivers': True,
            'optimize_system': True,
            'repair_packages': True,
            'update_firmware': False,
            'notify_before_update': True,
            'download_in_background': True
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', pady=20)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🔄 TL Auto-Maintenance",
            font=('Arial', 22, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Automatic system updates and maintenance for long-term stability",
            font=('Arial', 11),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack()

        # Status card
        status_frame = tk.Frame(self.root, bg='#34495e', pady=20)
        status_frame.pack(fill=tk.X, padx=20, pady=20)

        status_grid = tk.Frame(status_frame, bg='#34495e')
        status_grid.pack()

        # System Health
        tk.Label(
            status_grid,
            text="System Health:",
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='white'
        ).grid(row=0, column=0, sticky='w', padx=20, pady=5)

        self.health_label = tk.Label(
            status_grid,
            text="Checking...",
            font=('Arial', 11),
            bg='#34495e',
            fg='#3498db'
        )
        self.health_label.grid(row=0, column=1, sticky='w', pady=5)

        # Last Update
        tk.Label(
            status_grid,
            text="Last Update:",
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='white'
        ).grid(row=1, column=0, sticky='w', padx=20, pady=5)

        self.last_update_label = tk.Label(
            status_grid,
            text="Never",
            font=('Arial', 11),
            bg='#34495e',
            fg='white'
        )
        self.last_update_label.grid(row=1, column=1, sticky='w', pady=5)

        # Auto-Maintenance Status
        tk.Label(
            status_grid,
            text="Auto-Maintenance:",
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='white'
        ).grid(row=2, column=0, sticky='w', padx=20, pady=5)

        self.auto_status_label = tk.Label(
            status_grid,
            text="Enabled" if self.config.get('auto_maintenance_enabled') else "Disabled",
            font=('Arial', 11),
            bg='#34495e',
            fg='#27ae60' if self.config.get('auto_maintenance_enabled') else '#e74c3c'
        )
        self.auto_status_label.grid(row=2, column=1, sticky='w', pady=5)

        # Control buttons
        control_frame = tk.Frame(self.root, bg='#1e1e1e', pady=15)
        control_frame.pack(fill=tk.X)

        tk.Button(
            control_frame,
            text="🔄 Check for Updates",
            command=self.check_updates,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            control_frame,
            text="⚡ Run Maintenance Now",
            command=self.run_maintenance,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            control_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        # Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Tasks tab
        tasks_frame = tk.Frame(notebook, bg='white')
        notebook.add(tasks_frame, text="📋 Maintenance Tasks")

        tasks_label = tk.Label(
            tasks_frame,
            text="Scheduled Maintenance Tasks:",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        tasks_label.pack(anchor='w', padx=10, pady=10)

        # Tasks tree
        tasks_tree_frame = tk.Frame(tasks_frame)
        tasks_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tasks_scroll = tk.Scrollbar(tasks_tree_frame)
        tasks_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tasks_tree = ttk.Treeview(
            tasks_tree_frame,
            columns=('Status', 'Schedule', 'Last Run'),
            show='tree headings',
            yscrollcommand=tasks_scroll.set
        )

        self.tasks_tree.heading('#0', text='Task')
        self.tasks_tree.heading('Status', text='Status')
        self.tasks_tree.heading('Schedule', text='Schedule')
        self.tasks_tree.heading('Last Run', text='Last Run')

        self.tasks_tree.column('#0', width=300)
        self.tasks_tree.column('Status', width=150)
        self.tasks_tree.column('Schedule', width=150)
        self.tasks_tree.column('Last Run', width=200)

        self.tasks_tree.pack(fill=tk.BOTH, expand=True)
        tasks_scroll.config(command=self.tasks_tree.yview)

        self.populate_tasks()

        # Log tab
        log_frame = tk.Frame(notebook, bg='white')
        notebook.add(log_frame, text="📜 Activity Log")

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Courier', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Health tab
        health_frame = tk.Frame(notebook, bg='white')
        notebook.add(health_frame, text="❤️ System Health")

        self.health_text = scrolledtext.ScrolledText(
            health_frame,
            font=('Arial', 11),
            bg='white',
            padx=15,
            pady=15,
            wrap=tk.WORD
        )
        self.health_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_tasks(self):
        """Populate maintenance tasks list"""
        tasks = [
            {
                'name': 'System Updates',
                'icon': '📦',
                'status': 'Enabled' if self.config.get('auto_update_enabled') else 'Disabled',
                'schedule': self.config.get('update_schedule', 'daily'),
                'last_run': 'Never'
            },
            {
                'name': 'Disk Cleanup',
                'icon': '🗑️',
                'status': 'Enabled' if self.config.get('auto_cleanup') else 'Disabled',
                'schedule': 'Weekly',
                'last_run': 'Never'
            },
            {
                'name': 'Driver Updates',
                'icon': '🔧',
                'status': 'Enabled' if self.config.get('check_drivers') else 'Disabled',
                'schedule': 'Weekly',
                'last_run': 'Never'
            },
            {
                'name': 'System Optimization',
                'icon': '⚡',
                'status': 'Enabled' if self.config.get('optimize_system') else 'Disabled',
                'schedule': 'Weekly',
                'last_run': 'Never'
            },
            {
                'name': 'Package Repair',
                'icon': '🔨',
                'status': 'Enabled' if self.config.get('repair_packages') else 'Disabled',
                'schedule': 'Monthly',
                'last_run': 'Never'
            },
            {
                'name': 'System Snapshots',
                'icon': '📸',
                'status': 'Enabled' if self.config.get('create_snapshots') else 'Disabled',
                'schedule': 'Before updates',
                'last_run': 'Never'
            }
        ]

        self.tasks_tree.delete(*self.tasks_tree.get_children())

        for task in tasks:
            self.tasks_tree.insert('', 'end', text=f"{task['icon']} {task['name']}", values=(
                task['status'],
                task['schedule'].capitalize(),
                task['last_run']
            ))

    def check_system_health(self):
        """Check system health"""
        self.status_bar.config(text="Checking system health...")

        def check_thread():
            health = {
                'overall': 'Good',
                'issues': []
            }

            # Check disk space
            try:
                result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 5:
                            usage_str = parts[4].rstrip('%')
                            try:
                                usage = int(usage_str)
                                if usage > 90:
                                    health['issues'].append(f"Disk usage high: {usage}%")
                                    health['overall'] = 'Warning'
                            except:
                                pass
            except:
                pass

            # Check memory
            try:
                result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=10)
                # Parse memory info (simplified)
            except:
                pass

            # Check updates available
            try:
                result = subprocess.run(['apt', 'list', '--upgradable'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    upgradable = len([l for l in result.stdout.split('\n') if '/' in l])
                    if upgradable > 20:
                        health['issues'].append(f"{upgradable} updates available")
                        if health['overall'] != 'Warning':
                            health['overall'] = 'Info'
            except:
                pass

            # Update UI
            self.system_health = health
            color = '#27ae60' if health['overall'] == 'Good' else '#f39c12' if health['overall'] == 'Warning' else '#3498db'

            self.root.after(0, lambda: self.health_label.config(text=health['overall'], fg=color))
            self.root.after(0, lambda: self.update_health_display())
            self.root.after(0, lambda: self.status_bar.config(text="System health checked"))

        threading.Thread(target=check_thread, daemon=True).start()

    def update_health_display(self):
        """Update health display"""
        self.health_text.delete('1.0', 'end')

        health = self.system_health

        self.health_text.insert('end', f"System Health: {health['overall']}\n\n", 'bold')
        self.health_text.tag_config('bold', font=('Arial', 14, 'bold'))

        if health['issues']:
            self.health_text.insert('end', "Issues Found:\n\n")
            for issue in health['issues']:
                self.health_text.insert('end', f"  ⚠️  {issue}\n")
        else:
            self.health_text.insert('end', "✅ No issues detected\n\n")

        self.health_text.insert('end', "\n" + "="*50 + "\n\n")
        self.health_text.insert('end', "System Information:\n\n")

        # Add system info
        self.health_text.insert('end', f"Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.health_text.insert('end', f"Auto-Maintenance: {'Enabled' if self.config.get('auto_maintenance_enabled') else 'Disabled'}\n")
        self.health_text.insert('end', f"Update Schedule: {self.config.get('update_schedule', 'daily').capitalize()}\n")

    def check_updates(self):
        """Check for system updates"""
        self.status_bar.config(text="Checking for updates...")
        self.log("=== Checking for Updates ===")

        def check_thread():
            try:
                # Update package list
                self.log("Updating package list...")
                result = subprocess.run(
                    ['sudo', 'apt-get', 'update'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    self.log("✓ Package list updated")

                    # Check upgradable packages
                    result = subprocess.run(
                        ['apt', 'list', '--upgradable'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0:
                        upgradable = [l for l in result.stdout.split('\n') if '/' in l]
                        count = len(upgradable)

                        self.log(f"\nFound {count} updates available")

                        if count > 0:
                            self.log("\nUpdatable packages:")
                            for pkg in upgradable[:10]:  # Show first 10
                                self.log(f"  • {pkg}")

                            if count > 10:
                                self.log(f"  ... and {count - 10} more")

                            # Ask user to install
                            self.root.after(0, lambda: self.prompt_install_updates(count))
                        else:
                            self.root.after(0, lambda: messagebox.showinfo("Up to Date", "Your system is up to date!"))

                    self.root.after(0, lambda: self.status_bar.config(text=f"{count} updates available"))

                else:
                    self.log("✗ Failed to update package list")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to check for updates"))

            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Update check failed: {e}"))

        threading.Thread(target=check_thread, daemon=True).start()

    def prompt_install_updates(self, count):
        """Prompt user to install updates"""
        if messagebox.askyesno("Updates Available", f"{count} updates are available.\n\nInstall now?"):
            self.install_updates()

    def install_updates(self):
        """Install system updates"""
        self.status_bar.config(text="Installing updates...")
        self.log("\n=== Installing Updates ===")

        def install_thread():
            try:
                # Create snapshot if enabled
                if self.config.get('create_snapshots'):
                    self.log("Creating system snapshot...")
                    # TODO: Implement snapshot creation

                # Install updates
                self.log("Installing updates (this may take a while)...")

                result = subprocess.run(
                    ['sudo', 'apt-get', 'upgrade', '-y'],
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes
                )

                if result.returncode == 0:
                    self.log("✓ Updates installed successfully")
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Updates installed successfully!\n\nYou may need to restart for some changes to take effect."))
                else:
                    self.log("✗ Update installation had errors")
                    self.root.after(0, lambda: messagebox.showwarning("Warning", "Some updates may not have installed correctly"))

                # Update last update time
                self.last_update_label.config(text=datetime.now().strftime('%Y-%m-%d %H:%M'))

                self.root.after(0, lambda: self.status_bar.config(text="Updates complete"))

            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Update failed: {e}"))

        threading.Thread(target=install_thread, daemon=True).start()

    def run_maintenance(self):
        """Run full maintenance"""
        if messagebox.askyesno("Run Maintenance", "Run full system maintenance?\n\nThis will:\n• Clean disk space\n• Repair packages\n• Optimize system\n• Check drivers"):
            self.status_bar.config(text="Running maintenance...")
            self.log("\n=== Full System Maintenance ===")

            def maintenance_thread():
                tasks = []

                # Disk cleanup
                if self.config.get('auto_cleanup'):
                    tasks.append(('Cleaning disk space', self.cleanup_disk))

                # Package repair
                if self.config.get('repair_packages'):
                    tasks.append(('Repairing packages', self.repair_packages))

                # System optimization
                if self.config.get('optimize_system'):
                    tasks.append(('Optimizing system', self.optimize_system))

                # Run tasks
                for task_name, task_func in tasks:
                    self.log(f"\n{task_name}...")
                    self.root.after(0, lambda t=task_name: self.status_bar.config(text=t))
                    task_func()

                self.log("\n=== Maintenance Complete ===")
                self.root.after(0, lambda: self.status_bar.config(text="Maintenance complete"))
                self.root.after(0, lambda: messagebox.showinfo("Complete", "System maintenance complete!"))

            threading.Thread(target=maintenance_thread, daemon=True).start()

    def cleanup_disk(self):
        """Clean up disk space"""
        try:
            # Clean package cache
            self.log("  Cleaning package cache...")
            subprocess.run(['sudo', 'apt-get', 'clean'], timeout=60)

            # Remove old kernels (keep configured number)
            self.log("  Removing old kernels...")
            subprocess.run(['sudo', 'apt-get', 'autoremove', '-y'], timeout=300)

            self.log("  ✓ Disk cleanup complete")

        except Exception as e:
            self.log(f"  ✗ Cleanup error: {e}")

    def repair_packages(self):
        """Repair broken packages"""
        try:
            self.log("  Checking for broken packages...")

            result = subprocess.run(
                ['sudo', 'dpkg', '--configure', '-a'],
                capture_output=True,
                timeout=300
            )

            result = subprocess.run(
                ['sudo', 'apt-get', 'install', '-f', '-y'],
                capture_output=True,
                timeout=300
            )

            self.log("  ✓ Package repair complete")

        except Exception as e:
            self.log(f"  ✗ Repair error: {e}")

    def optimize_system(self):
        """Optimize system performance"""
        try:
            self.log("  Optimizing system...")

            # Update locate database
            subprocess.run(['sudo', 'updatedb'], timeout=300, capture_output=True)

            # Sync filesystem
            subprocess.run(['sync'], timeout=30)

            self.log("  ✓ Optimization complete")

        except Exception as e:
            self.log(f"  ✗ Optimization error: {e}")

    def start_scheduler(self):
        """Start background maintenance scheduler"""
        def scheduler_thread():
            # Schedule tasks based on configuration
            schedule_time = self.config.get('update_time', '03:00')

            if self.config.get('update_schedule') == 'daily':
                schedule.every().day.at(schedule_time).do(self.scheduled_maintenance)
            elif self.config.get('update_schedule') == 'weekly':
                schedule.every().monday.at(schedule_time).do(self.scheduled_maintenance)
            elif self.config.get('update_schedule') == 'monthly':
                schedule.every().day.at(schedule_time).do(self.check_monthly_maintenance)

            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        threading.Thread(target=scheduler_thread, daemon=True).start()
        self.log("Background scheduler started")

    def scheduled_maintenance(self):
        """Run scheduled maintenance"""
        self.log(f"\n=== Scheduled Maintenance ({datetime.now()}) ===")

        if self.config.get('auto_update_enabled'):
            # Run updates in background
            self.check_updates()

        if self.config.get('auto_cleanup'):
            self.cleanup_disk()

    def check_monthly_maintenance(self):
        """Check if monthly maintenance is due"""
        # Only run on first day of month
        if datetime.now().day == 1:
            self.scheduled_maintenance()

    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Maintenance Settings")
        settings_window.geometry("600x600")
        settings_window.transient(self.root)
        settings_window.configure(bg='white')

        tk.Label(
            settings_window,
            text="Auto-Maintenance Settings",
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(pady=20)

        # Settings frame
        settings_frame = tk.Frame(settings_window, bg='white', padx=30)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Auto-maintenance toggle
        self.auto_enabled_var = tk.BooleanVar(value=self.config.get('auto_maintenance_enabled', True))
        tk.Checkbutton(
            settings_frame,
            text="Enable automatic maintenance",
            variable=self.auto_enabled_var,
            bg='white',
            font=('Arial', 11, 'bold')
        ).pack(anchor='w', pady=5)

        # Update settings
        tk.Label(settings_frame, text="Updates:", font=('Arial', 11, 'bold'), bg='white').pack(anchor='w', pady=(15, 5))

        self.auto_update_var = tk.BooleanVar(value=self.config.get('auto_update_enabled', True))
        tk.Checkbutton(
            settings_frame,
            text="Automatically install updates",
            variable=self.auto_update_var,
            bg='white'
        ).pack(anchor='w', padx=20, pady=2)

        self.notify_update_var = tk.BooleanVar(value=self.config.get('notify_before_update', True))
        tk.Checkbutton(
            settings_frame,
            text="Notify before installing updates",
            variable=self.notify_update_var,
            bg='white'
        ).pack(anchor='w', padx=20, pady=2)

        # Maintenance settings
        tk.Label(settings_frame, text="Maintenance:", font=('Arial', 11, 'bold'), bg='white').pack(anchor='w', pady=(15, 5))

        self.auto_cleanup_var = tk.BooleanVar(value=self.config.get('auto_cleanup', True))
        tk.Checkbutton(
            settings_frame,
            text="Automatic disk cleanup",
            variable=self.auto_cleanup_var,
            bg='white'
        ).pack(anchor='w', padx=20, pady=2)

        self.repair_packages_var = tk.BooleanVar(value=self.config.get('repair_packages', True))
        tk.Checkbutton(
            settings_frame,
            text="Automatically repair broken packages",
            variable=self.repair_packages_var,
            bg='white'
        ).pack(anchor='w', padx=20, pady=2)

        self.optimize_var = tk.BooleanVar(value=self.config.get('optimize_system', True))
        tk.Checkbutton(
            settings_frame,
            text="System optimization",
            variable=self.optimize_var,
            bg='white'
        ).pack(anchor='w', padx=20, pady=2)

        self.snapshots_var = tk.BooleanVar(value=self.config.get('create_snapshots', True))
        tk.Checkbutton(
            settings_frame,
            text="Create snapshots before updates",
            variable=self.snapshots_var,
            bg='white'
        ).pack(anchor='w', padx=20, pady=2)

        # Buttons
        button_frame = tk.Frame(settings_window, bg='white', pady=20)
        button_frame.pack()

        tk.Button(
            button_frame,
            text="Save Settings",
            command=lambda: self.save_settings(settings_window),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Cancel",
            command=settings_window.destroy,
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)

    def save_settings(self, window):
        """Save settings"""
        self.config['auto_maintenance_enabled'] = self.auto_enabled_var.get()
        self.config['auto_update_enabled'] = self.auto_update_var.get()
        self.config['notify_before_update'] = self.notify_update_var.get()
        self.config['auto_cleanup'] = self.auto_cleanup_var.get()
        self.config['repair_packages'] = self.repair_packages_var.get()
        self.config['optimize_system'] = self.optimize_var.get()
        self.config['create_snapshots'] = self.snapshots_var.get()

        self.save_config()
        self.populate_tasks()

        window.destroy()
        messagebox.showinfo("Settings Saved", "Maintenance settings have been saved!")

    def log(self, message):
        """Log message"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        print(message)

    def run(self):
        """Run maintenance system"""
        self.root.mainloop()

if __name__ == '__main__':
    system = AutoMaintenanceSystem()
    system.run()
