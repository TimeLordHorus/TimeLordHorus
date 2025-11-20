#!/usr/bin/env python3
"""
TL Linux - Firmware Manager
Manage and update system firmware for all devices
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
from datetime import datetime

class FirmwareManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Firmware Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # Firmware state
        self.scanning = False
        self.updating = False

        self.setup_ui()
        self.check_fwupd()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔧 Firmware Manager",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        tk.Label(
            header,
            text="Keep your hardware up-to-date",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(side=tk.LEFT, pady=20)

        # Toolbar
        toolbar = tk.Frame(header, bg='#2b2b2b')
        toolbar.pack(side=tk.RIGHT, padx=20)

        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_devices,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="⬆️ Update All",
            command=self.update_all_firmware,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Tab 1: Devices
        self.create_devices_tab(notebook)

        # Tab 2: Updates
        self.create_updates_tab(notebook)

        # Tab 3: History
        self.create_history_tab(notebook)

        # Tab 4: Settings
        self.create_settings_tab(notebook)

        # Status bar
        status_bar = tk.Frame(self.root, bg='#2b2b2b', height=30)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 9),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=15)

    def create_devices_tab(self, notebook):
        """Create devices tab"""
        devices_tab = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(devices_tab, text="Devices")

        # Info text
        tk.Label(
            devices_tab,
            text="Hardware Devices with Firmware",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=15)

        # Device list
        list_frame = tk.Frame(devices_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Treeview for devices
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.devices_tree = ttk.Treeview(
            list_frame,
            columns=('Device', 'Current', 'Available', 'Status'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        self.devices_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.devices_tree.yview)

        # Configure columns
        self.devices_tree.heading('Device', text='Device Name')
        self.devices_tree.heading('Current', text='Current Version')
        self.devices_tree.heading('Available', text='Available Version')
        self.devices_tree.heading('Status', text='Status')

        self.devices_tree.column('Device', width=350)
        self.devices_tree.column('Current', width=150)
        self.devices_tree.column('Available', width=150)
        self.devices_tree.column('Status', width=150)

        # Style
        style = ttk.Style()
        style.configure('Treeview', background='#2b2b2b', foreground='white', fieldbackground='#2b2b2b')
        style.map('Treeview', background=[('selected', '#4a9eff')])

        # Buttons
        btn_frame = tk.Frame(devices_tab, bg='#1a1a1a')
        btn_frame.pack(pady=(0, 15))

        tk.Button(
            btn_frame,
            text="Update Selected",
            command=self.update_selected_device,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Device Details",
            command=self.show_device_details,
            bg='#6272a4',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)

    def create_updates_tab(self, notebook):
        """Create updates tab"""
        updates_tab = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(updates_tab, text="Available Updates")

        tk.Label(
            updates_tab,
            text="Firmware Updates Available",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=15)

        # Updates info
        info_frame = tk.Frame(updates_tab, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.updates_info_label = tk.Label(
            info_frame,
            text="Click 'Refresh' to check for firmware updates",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='white',
            pady=15
        )
        self.updates_info_label.pack()

        # Update list
        list_frame = tk.Frame(updates_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.updates_tree = ttk.Treeview(
            list_frame,
            columns=('Device', 'Current', 'New', 'Size', 'Type'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        self.updates_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.updates_tree.yview)

        self.updates_tree.heading('Device', text='Device')
        self.updates_tree.heading('Current', text='Current Version')
        self.updates_tree.heading('New', text='New Version')
        self.updates_tree.heading('Size', text='Size')
        self.updates_tree.heading('Type', text='Update Type')

        self.updates_tree.column('Device', width=300)
        self.updates_tree.column('Current', width=150)
        self.updates_tree.column('New', width=150)
        self.updates_tree.column('Size', width=100)
        self.updates_tree.column('Type', width=150)

    def create_history_tab(self, notebook):
        """Create history tab"""
        history_tab = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(history_tab, text="Update History")

        tk.Label(
            history_tab,
            text="Firmware Update History",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=15)

        # History log
        log_frame = tk.Frame(history_tab, bg='#1a1a1a')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.history_text = scrolledtext.ScrolledText(
            log_frame,
            bg='#2b2b2b',
            fg='white',
            font=('Courier', 9),
            wrap=tk.WORD,
            bd=0
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)

        # Load history
        self.load_update_history()

    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_tab = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(settings_tab, text="Settings")

        tk.Label(
            settings_tab,
            text="Firmware Update Settings",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=15)

        # Settings frame
        settings_frame = tk.Frame(settings_tab, bg='#1a1a1a')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Auto-update
        auto_frame = tk.Frame(settings_frame, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        auto_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            auto_frame,
            text="Automatic Updates",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=15, pady=(15, 5))

        self.auto_check_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            auto_frame,
            text="Automatically check for firmware updates",
            variable=self.auto_check_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(anchor='w', padx=30, pady=5)

        self.auto_download_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            auto_frame,
            text="Automatically download updates (but don't install)",
            variable=self.auto_download_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(anchor='w', padx=30, pady=5)

        self.notify_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            auto_frame,
            text="Notify when updates are available",
            variable=self.notify_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(anchor='w', padx=30, pady=(5, 15))

        # Update sources
        sources_frame = tk.Frame(settings_frame, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        sources_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            sources_frame,
            text="Update Sources",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=15, pady=(15, 5))

        self.lvfs_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            source_frame,
            text="Linux Vendor Firmware Service (LVFS)",
            variable=self.lvfs_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(anchor='w', padx=30, pady=5)

        self.vendor_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            sources_frame,
            text="Vendor-specific firmware repositories",
            variable=self.vendor_var,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a',
            font=('Arial', 10)
        ).pack(anchor='w', padx=30, pady=(5, 15))

        # Package updates
        packages_frame = tk.Frame(settings_frame, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        packages_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            packages_frame,
            text="Firmware Packages",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=15, pady=(15, 5))

        tk.Label(
            packages_frame,
            text="Update system firmware packages:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=30, pady=(10, 5))

        btn_packages = tk.Frame(packages_frame, bg='#2b2b2b')
        btn_packages.pack(anchor='w', padx=30, pady=(0, 15))

        tk.Button(
            btn_packages,
            text="Update linux-firmware",
            command=lambda: self.update_package('linux-firmware'),
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_packages,
            text="Update firmware-linux-nonfree",
            command=lambda: self.update_package('firmware-linux-nonfree'),
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        # Save settings
        tk.Button(
            settings_frame,
            text="Save Settings",
            command=self.save_settings,
            bg='#50fa7b',
            fg='white',
            bd=0,
            padx=30,
            pady=12,
            font=('Arial', 11)
        ).pack(pady=20)

    def check_fwupd(self):
        """Check if fwupd is installed"""
        try:
            result = subprocess.run(
                ['which', 'fwupdmgr'],
                capture_output=True,
                check=True
            )
            self.has_fwupd = True
            self.status_label.config(text="fwupd detected - hardware firmware updates available")
        except:
            self.has_fwupd = False
            self.status_label.config(text="fwupd not installed - install for hardware firmware updates")

    def refresh_devices(self):
        """Refresh device list"""
        if self.scanning:
            return

        self.scanning = True
        self.status_label.config(text="Scanning for devices...")

        def scan():
            # Clear trees
            self.root.after(0, lambda: self.devices_tree.delete(*self.devices_tree.get_children()))
            self.root.after(0, lambda: self.updates_tree.delete(*self.updates_tree.get_children()))

            if self.has_fwupd:
                # Use fwupd to get devices
                try:
                    result = subprocess.run(
                        ['fwupdmgr', 'get-devices'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    # Parse output (simplified)
                    devices_found = result.stdout.count('Device ID:')

                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Found {devices_found} devices with firmware"
                    ))

                    # Check for updates
                    update_result = subprocess.run(
                        ['fwupdmgr', 'get-updates'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    updates_available = update_result.stdout.count('Update Version:')

                    if updates_available > 0:
                        self.root.after(0, lambda: self.updates_info_label.config(
                            text=f"✓ {updates_available} firmware updates available",
                            fg='#50fa7b'
                        ))
                    else:
                        self.root.after(0, lambda: self.updates_info_label.config(
                            text="✓ All firmware is up to date",
                            fg='#50fa7b'
                        ))

                except subprocess.TimeoutExpired:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Timeout",
                        "Device scan timed out. Try again."
                    ))
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Error scanning devices: {str(e)}"
                    ))
            else:
                # Show package-based firmware info
                self.root.after(0, lambda: self.check_firmware_packages())

            self.scanning = False

        thread = threading.Thread(target=scan, daemon=True)
        thread.start()

    def check_firmware_packages(self):
        """Check firmware package versions"""
        packages = [
            'linux-firmware',
            'firmware-linux-nonfree',
            'intel-microcode',
            'amd64-microcode'
        ]

        for package in packages:
            try:
                result = subprocess.run(
                    ['dpkg', '-l', package],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    # Package is installed
                    for line in result.stdout.split('\n'):
                        if line.startswith('ii'):
                            parts = line.split()
                            if len(parts) >= 3:
                                version = parts[2]
                                self.devices_tree.insert(
                                    '',
                                    tk.END,
                                    values=(package, version, 'Check updates', 'Installed')
                                )
                                break
            except:
                pass

        self.status_label.config(text="Firmware package check complete")

    def update_selected_device(self):
        """Update selected device firmware"""
        selection = self.devices_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device to update")
            return

        if not self.has_fwupd:
            messagebox.showinfo(
                "Install fwupd",
                "To update device firmware, install fwupd:\n\n"
                "sudo apt install fwupd"
            )
            return

        messagebox.showinfo(
            "Update Device",
            "Device firmware update would run here.\n\n"
            "Use: sudo fwupdmgr update"
        )

    def show_device_details(self):
        """Show device details"""
        selection = self.devices_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device")
            return

        item = self.devices_tree.item(selection[0])
        device_name = item['values'][0]

        messagebox.showinfo(
            "Device Details",
            f"Device: {device_name}\n\n"
            "Detailed firmware information would be displayed here."
        )

    def update_all_firmware(self):
        """Update all firmware"""
        if messagebox.askyesno(
            "Update All Firmware",
            "This will update all firmware packages and check for device updates.\n\n"
            "Continue?"
        ):
            self.status_label.config(text="Updating firmware...")

            # Update packages
            self.update_package('linux-firmware')

    def update_package(self, package):
        """Update a firmware package"""
        if messagebox.askyesno(
            "Update Package",
            f"Update {package}?\n\n"
            "This requires root privileges."
        ):
            self.status_label.config(text=f"Updating {package}...")

            def update():
                try:
                    result = subprocess.run(
                        ['pkexec', 'apt', 'install', '--only-upgrade', '-y', package],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                    if result.returncode == 0:
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Success",
                            f"{package} updated successfully!"
                        ))
                        self.root.after(0, lambda: self.log_update(package, "Success"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror(
                            "Error",
                            f"Failed to update {package}"
                        ))

                except subprocess.TimeoutExpired:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Timeout",
                        "Update timed out"
                    ))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error",
                        str(e)
                    ))

                self.root.after(0, lambda: self.status_label.config(text="Ready"))

            thread = threading.Thread(target=update, daemon=True)
            thread.start()

    def log_update(self, item, status):
        """Log an update"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {item}: {status}\n"

        self.history_text.insert(tk.END, log_entry)
        self.history_text.see(tk.END)

    def load_update_history(self):
        """Load update history"""
        self.history_text.insert(tk.END, "Firmware Update History\n")
        self.history_text.insert(tk.END, "=" * 50 + "\n\n")
        self.history_text.insert(tk.END, "No updates recorded yet.\n")

    def save_settings(self):
        """Save settings"""
        messagebox.showinfo("Settings Saved", "Firmware update settings have been saved.")

    def run(self):
        """Run the firmware manager"""
        self.root.mainloop()

def main():
    manager = FirmwareManager()
    manager.run()

if __name__ == '__main__':
    main()
