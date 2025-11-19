#!/usr/bin/env python3
"""
TL Linux - Backup & Restore Center
Manage both A/B system partitions and user data backups
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import threading
from datetime import datetime

# Add system path
sys.path.insert(0, os.path.expanduser('~/tl-linux/system'))
from ab_system_manager import get_ab_manager
from backup_manager import get_backup_manager

class BackupRestoreCenter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Backup & Restore")
        self.root.geometry("1000x750")
        self.root.configure(bg='#2b2b2b')

        self.ab_manager = get_ab_manager()
        self.backup_manager = get_backup_manager()

        self.backup_in_progress = False

        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="💾 Backup & Restore Center",
            font=('Arial', 20, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # System Protection tab (A/B)
        self.system_frame = self.create_system_tab()
        notebook.add(self.system_frame, text="  🛡️ System Protection  ")

        # User Data Backups tab
        self.data_frame = self.create_data_tab()
        notebook.add(self.data_frame, text="  📁 User Data Backups  ")

        # Settings tab
        self.settings_frame = self.create_settings_tab()
        notebook.add(self.settings_frame, text="  ⚙️ Settings  ")

    def create_system_tab(self):
        """Create A/B system protection tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="Dual Partition System Protection",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        tk.Label(
            frame,
            text="TL Linux uses two system partitions (A and B). If one fails, the system automatically boots from the other.",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            wraplength=900
        ).pack(pady=(0, 20))

        # Status container
        status_container = tk.Frame(frame, bg='#2b2b2b')
        status_container.pack(fill=tk.BOTH, expand=True, padx=40)

        # Partition A
        self.create_partition_card(status_container, 'A', side=tk.LEFT)

        # Status indicator
        center_frame = tk.Frame(status_container, bg='#2b2b2b', width=100)
        center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        center_frame.pack_propagate(False)

        self.system_status_label = tk.Label(
            center_frame,
            text="⟷",
            font=('Arial', 48),
            bg='#2b2b2b',
            fg='#4a9eff'
        )
        self.system_status_label.pack(expand=True)

        # Partition B
        self.create_partition_card(status_container, 'B', side=tk.LEFT)

        # Actions
        actions_frame = tk.Frame(frame, bg='#2b2b2b')
        actions_frame.pack(fill=tk.X, padx=40, pady=20)

        tk.Button(
            actions_frame,
            text="🔄 Check System Health",
            command=self.check_system_health,
            font=('Arial', 11),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="🔧 Repair Standby Partition",
            command=self.repair_standby,
            font=('Arial', 11),
            bg='#5cb85c',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="⏪ Rollback to Previous",
            command=self.rollback_system,
            font=('Arial', 11),
            bg='#f0ad4e',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def create_partition_card(self, parent, partition_name, side):
        """Create partition status card"""
        card = tk.Frame(parent, bg='#1a1a1a', bd=2, relief=tk.SOLID, width=350)
        card.pack(side=side, fill=tk.BOTH, expand=True)
        card.pack_propagate(False)

        # Header
        header = tk.Frame(card, bg='#1a1a1a')
        header.pack(fill=tk.X, pady=15, padx=20)

        # Store reference for updates
        if partition_name == 'A':
            self.partition_a_card = card

            self.partition_a_icon = tk.Label(
                header,
                text="💿",
                font=('Arial', 32),
                bg='#1a1a1a'
            )
            self.partition_a_icon.pack(side=tk.LEFT, padx=(0, 15))

            info_frame = tk.Frame(header, bg='#1a1a1a')
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                info_frame,
                text=f"Partition {partition_name}",
                font=('Arial', 14, 'bold'),
                bg='#1a1a1a',
                fg='white'
            ).pack(anchor='w')

            self.partition_a_status = tk.Label(
                info_frame,
                text="Active",
                font=('Arial', 10),
                bg='#1a1a1a',
                fg='#5cb85c'
            )
            self.partition_a_status.pack(anchor='w')

            # Details
            details = tk.Frame(card, bg='#1a1a1a')
            details.pack(fill=tk.X, padx=20, pady=(0, 15))

            self.partition_a_health = self.create_detail_row(details, "Health:", "100%")
            self.partition_a_version = self.create_detail_row(details, "Version:", "1.0.0")
            self.partition_a_boot = self.create_detail_row(details, "Last Boot:", "Now")

        else:  # Partition B
            self.partition_b_card = card

            self.partition_b_icon = tk.Label(
                header,
                text="💿",
                font=('Arial', 32),
                bg='#1a1a1a'
            )
            self.partition_b_icon.pack(side=tk.LEFT, padx=(0, 15))

            info_frame = tk.Frame(header, bg='#1a1a1a')
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                info_frame,
                text=f"Partition {partition_name}",
                font=('Arial', 14, 'bold'),
                bg='#1a1a1a',
                fg='white'
            ).pack(anchor='w')

            self.partition_b_status = tk.Label(
                info_frame,
                text="Standby",
                font=('Arial', 10),
                bg='#1a1a1a',
                fg='#888888'
            )
            self.partition_b_status.pack(anchor='w')

            # Details
            details = tk.Frame(card, bg='#1a1a1a')
            details.pack(fill=tk.X, padx=20, pady=(0, 15))

            self.partition_b_health = self.create_detail_row(details, "Health:", "100%")
            self.partition_b_version = self.create_detail_row(details, "Version:", "1.0.0")
            self.partition_b_boot = self.create_detail_row(details, "Ready for:", "Failover")

    def create_detail_row(self, parent, label, value):
        """Create a detail row in partition card"""
        row = tk.Frame(parent, bg='#1a1a1a')
        row.pack(fill=tk.X, pady=3)

        tk.Label(
            row,
            text=label,
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        ).pack(side=tk.LEFT)

        value_label = tk.Label(
            row,
            text=value,
            font=('Arial', 10, 'bold'),
            bg='#1a1a1a',
            fg='white'
        )
        value_label.pack(side=tk.RIGHT)

        return value_label

    def create_data_tab(self):
        """Create user data backups tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        # Header
        header = tk.Frame(frame, bg='#2b2b2b')
        header.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header,
            text="Your Data Backups",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="➕ Create Backup Now",
            command=self.create_backup_now,
            font=('Arial', 11, 'bold'),
            bg='#5cb85c',
            fg='white',
            padx=20,
            pady=8,
            bd=0
        ).pack(side=tk.RIGHT)

        # Progress bar
        self.progress_frame = tk.Frame(frame, bg='#2b2b2b')
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white'
        )
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=860,
            mode='determinate'
        )
        self.progress_bar.pack()

        self.progress_frame.pack_forget()  # Hide initially

        # Backup list
        list_frame = tk.Frame(frame, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Treeview
        columns = ('Date', 'Type', 'Size', 'Files', 'Status')
        self.backup_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            selectmode='browse'
        )

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.backup_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.backup_tree.configure(yscrollcommand=vsb.set)

        self.backup_tree.heading('#0', text='Backup Name')
        for col in columns:
            self.backup_tree.heading(col, text=col)

        self.backup_tree.column('#0', width=250)
        self.backup_tree.column('Date', width=150)
        self.backup_tree.column('Type', width=100)
        self.backup_tree.column('Size', width=100)
        self.backup_tree.column('Files', width=80)
        self.backup_tree.column('Status', width=100)

        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Actions
        actions_frame = tk.Frame(frame, bg='#2b2b2b')
        actions_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(
            actions_frame,
            text="↺ Restore",
            command=self.restore_selected_backup,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="🔍 Verify",
            command=self.verify_selected_backup,
            font=('Arial', 10),
            bg='#6a6a6a',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="🗑️ Delete",
            command=self.delete_selected_backup,
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_frame,
            text="📂 Open Backup Folder",
            command=self.open_backup_folder,
            font=('Arial', 10),
            bg='#3a3a3a',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.RIGHT, padx=5)

        return frame

    def create_settings_tab(self):
        """Create backup settings tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="Backup Settings",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        # Settings container
        settings = tk.Frame(frame, bg='#2b2b2b')
        settings.pack(fill=tk.BOTH, expand=True, padx=60)

        # Schedule
        schedule_frame = tk.Frame(settings, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        schedule_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            schedule_frame,
            text="Automatic Backup Schedule",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', padx=15, pady=10)

        schedule_opt = tk.Frame(schedule_frame, bg='#1a1a1a')
        schedule_opt.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.schedule_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            schedule_opt,
            text="Enable automatic backups",
            variable=self.schedule_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).pack(anchor='w', pady=5)

        freq_frame = tk.Frame(schedule_opt, bg='#1a1a1a')
        freq_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            freq_frame,
            text="Frequency:",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.freq_var = tk.StringVar(value='daily')
        for freq in ['daily', 'weekly', 'monthly']:
            tk.Radiobutton(
                freq_frame,
                text=freq.capitalize(),
                variable=self.freq_var,
                value=freq,
                font=('Arial', 9),
                bg='#1a1a1a',
                fg='#cccccc',
                selectcolor='#2b2b2b'
            ).pack(side=tk.LEFT, padx=10)

        # Retention
        retention_frame = tk.Frame(settings, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        retention_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            retention_frame,
            text="Backup Retention",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', padx=15, pady=10)

        ret_opt = tk.Frame(retention_frame, bg='#1a1a1a')
        ret_opt.pack(fill=tk.X, padx=15, pady=(0, 15))

        tk.Label(
            ret_opt,
            text="Keep last:",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc'
        ).pack(anchor='w', pady=(0, 5))

        self.keep_var = tk.IntVar(value=10)
        keep_scale = tk.Scale(
            ret_opt,
            from_=3,
            to=30,
            orient=tk.HORIZONTAL,
            variable=self.keep_var,
            bg='#1a1a1a',
            fg='white',
            highlightthickness=0,
            length=400
        )
        keep_scale.pack(anchor='w')

        tk.Label(
            ret_opt,
            text="backups (older backups will be automatically deleted)",
            font=('Arial', 9),
            bg='#1a1a1a',
            fg='#888888'
        ).pack(anchor='w')

        # Options
        options_frame = tk.Frame(settings, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        options_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            options_frame,
            text="Backup Options",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', padx=15, pady=10)

        opt_frame = tk.Frame(options_frame, bg='#1a1a1a')
        opt_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.incremental_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            opt_frame,
            text="Use incremental backups (faster, smaller)",
            variable=self.incremental_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).pack(anchor='w', pady=3)

        self.compression_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            opt_frame,
            text="Compress backups (save space)",
            variable=self.compression_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).pack(anchor='w', pady=3)

        self.encryption_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opt_frame,
            text="Encrypt backups (requires password)",
            variable=self.encryption_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).pack(anchor='w', pady=3)

        # Save button
        tk.Button(
            frame,
            text="💾 Save Settings",
            command=self.save_backup_settings,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=12,
            bd=0
        ).pack(pady=20)

        return frame

    def refresh_all(self):
        """Refresh all data"""
        self.refresh_system_status()
        self.refresh_backup_list()

    def refresh_system_status(self):
        """Refresh A/B system status"""
        status = self.ab_manager.get_status()

        # Update partition A
        if status['active_partition'] == 'A':
            self.partition_a_status.config(text="Active ●", fg='#5cb85c')
            self.partition_a_icon.config(text="💿")
        else:
            self.partition_a_status.config(text="Standby", fg='#888888')
            self.partition_a_icon.config(text="💿")

        health_a = status['partition_a_health']
        self.partition_a_health.config(text=f"{health_a}%", fg=self.get_health_color(health_a))
        self.partition_a_version.config(text=status['partition_a_version'])

        # Update partition B
        if status['active_partition'] == 'B':
            self.partition_b_status.config(text="Active ●", fg='#5cb85c')
            self.partition_b_icon.config(text="💿")
        else:
            self.partition_b_status.config(text="Standby", fg='#888888')
            self.partition_b_icon.config(text="💿")

        health_b = status['partition_b_health']
        self.partition_b_health.config(text=f"{health_b}%", fg=self.get_health_color(health_b))
        self.partition_b_version.config(text=status['partition_b_version'])

    def get_health_color(self, health):
        """Get color for health percentage"""
        if health >= 90:
            return '#5cb85c'
        elif health >= 70:
            return '#f0ad4e'
        else:
            return '#d9534f'

    def refresh_backup_list(self):
        """Refresh backup list"""
        # Clear tree
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)

        # Get backups
        backups = self.backup_manager.get_backups()

        for backup in reversed(backups):  # Most recent first
            date_str = datetime.fromisoformat(backup['timestamp']).strftime('%Y-%m-%d %H:%M')
            size_str = self.format_size(backup.get('size', 0))

            self.backup_tree.insert(
                '',
                'end',
                text=backup['name'],
                values=(
                    date_str,
                    backup.get('type', 'full').capitalize(),
                    size_str,
                    backup.get('file_count', 0),
                    backup.get('status', 'unknown').capitalize()
                )
            )

    def check_system_health(self):
        """Check system health"""
        messagebox.showinfo("System Health", "Checking system health...\nThis may take a few minutes.")

        # Run health check in thread
        def check():
            health_a = self.ab_manager.check_partition_health('A')
            health_b = self.ab_manager.check_partition_health('B')

            self.root.after(0, lambda: self.show_health_results(health_a, health_b))

        threading.Thread(target=check, daemon=True).start()

    def show_health_results(self, health_a, health_b):
        """Show health check results"""
        self.refresh_system_status()

        result = f"""System Health Check Results:

Partition A: {health_a}% {'✅' if health_a >= 90 else '⚠️' if health_a >= 70 else '❌'}
Partition B: {health_b}% {'✅' if health_b >= 90 else '⚠️' if health_b >= 70 else '❌'}

Status: {'All systems operational' if min(health_a, health_b) >= 90 else 'Repair recommended'}
"""
        messagebox.showinfo("Health Check Complete", result)

    def repair_standby(self):
        """Repair standby partition"""
        if not messagebox.askyesno("Repair Standby", "Repair the standby partition? This will copy data from the active partition."):
            return

        status = self.ab_manager.get_status()
        standby = status['standby_partition']

        messagebox.showinfo("Repair", f"Repairing partition {standby}...\nThis may take a while.")

        def repair():
            success = self.ab_manager.repair_partition(standby)
            self.root.after(0, lambda: self.show_repair_result(success))

        threading.Thread(target=repair, daemon=True).start()

    def show_repair_result(self, success):
        """Show repair result"""
        self.refresh_system_status()

        if success:
            messagebox.showinfo("Repair Complete", "Standby partition repaired successfully!")
        else:
            messagebox.showerror("Repair Failed", "Partition repair failed. Check logs for details.")

    def rollback_system(self):
        """Rollback to previous partition"""
        if not messagebox.askyesno("Rollback", "Switch to the standby partition and reboot?\n\nThis is useful if the current system has issues."):
            return

        success = self.ab_manager.rollback()

        if success:
            messagebox.showinfo("Rollback", "Rollback initiated. System will reboot now.")
            # Would trigger reboot
        else:
            messagebox.showerror("Rollback Failed", "Rollback not available or failed.")

    def create_backup_now(self):
        """Create backup now"""
        if self.backup_in_progress:
            messagebox.showwarning("Backup in Progress", "A backup is already running")
            return

        # Show progress
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting backup...")

        self.backup_in_progress = True

        def backup():
            def progress_callback(current, total, message):
                if total > 0:
                    progress = (current / total) * 100
                    self.root.after(0, lambda: self.update_progress(progress, message))

            result = self.backup_manager.create_backup(callback=progress_callback)

            self.root.after(0, lambda: self.backup_complete(result))

        threading.Thread(target=backup, daemon=True).start()

    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar['value'] = value
        self.progress_label.config(text=message)

    def backup_complete(self, result):
        """Handle backup completion"""
        self.backup_in_progress = False
        self.progress_frame.pack_forget()

        if result.get('status') == 'completed':
            messagebox.showinfo("Backup Complete", f"Backup created successfully!\n\nFiles: {result['file_count']}\nSize: {self.format_size(result['size'])}")
            self.refresh_backup_list()
        else:
            messagebox.showerror("Backup Failed", f"Backup failed: {result.get('error', 'Unknown error')}")

    def restore_selected_backup(self):
        """Restore selected backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to restore")
            return

        item = self.backup_tree.item(selection[0])
        backup_name = item['text']

        if not messagebox.askyesno("Confirm Restore", f"Restore backup '{backup_name}'?\n\nThis will overwrite your current files!"):
            return

        # Restore in thread
        def restore():
            success = self.backup_manager.restore_backup(backup_name)
            self.root.after(0, lambda: self.restore_complete(success, backup_name))

        threading.Thread(target=restore, daemon=True).start()

    def restore_complete(self, success, backup_name):
        """Handle restore completion"""
        if success:
            messagebox.showinfo("Restore Complete", f"Backup '{backup_name}' restored successfully!")
        else:
            messagebox.showerror("Restore Failed", "Restore operation failed")

    def verify_selected_backup(self):
        """Verify selected backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to verify")
            return

        item = self.backup_tree.item(selection[0])
        backup_name = item['text']

        # Verify in thread
        def verify():
            success = self.backup_manager.verify_backup(backup_name)
            self.root.after(0, lambda: self.verify_complete(success, backup_name))

        threading.Thread(target=verify, daemon=True).start()

    def verify_complete(self, success, backup_name):
        """Handle verification completion"""
        if success:
            messagebox.showinfo("Verification Passed", f"Backup '{backup_name}' is valid and can be restored.")
        else:
            messagebox.showwarning("Verification Failed", f"Backup '{backup_name}' has integrity issues.")

    def delete_selected_backup(self):
        """Delete selected backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to delete")
            return

        item = self.backup_tree.item(selection[0])
        backup_name = item['text']

        if not messagebox.askyesno("Confirm Delete", f"Permanently delete backup '{backup_name}'?"):
            return

        success = self.backup_manager.delete_backup(backup_name)

        if success:
            messagebox.showinfo("Deleted", "Backup deleted")
            self.refresh_backup_list()
        else:
            messagebox.showerror("Delete Failed", "Failed to delete backup")

    def open_backup_folder(self):
        """Open backup folder in file manager"""
        import subprocess
        try:
            subprocess.Popen(['xdg-open', self.backup_manager.backup_dir])
        except:
            messagebox.showerror("Error", "Could not open backup folder")

    def save_backup_settings(self):
        """Save backup settings"""
        self.backup_manager.config['schedule_enabled'] = self.schedule_var.get()
        self.backup_manager.config['schedule_frequency'] = self.freq_var.get()
        self.backup_manager.config['keep_count'] = self.keep_var.get()
        self.backup_manager.config['incremental_enabled'] = self.incremental_var.get()
        self.backup_manager.config['compression_enabled'] = self.compression_var.get()
        self.backup_manager.config['encryption_enabled'] = self.encryption_var.get()

        self.backup_manager.save_config()

        messagebox.showinfo("Settings Saved", "Backup settings saved successfully!")

    def format_size(self, bytes_val):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = BackupRestoreCenter()
    app.run()

if __name__ == '__main__':
    main()
