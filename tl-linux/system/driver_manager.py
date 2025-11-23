#!/usr/bin/env python3
"""
TL Linux - Automatic Driver Manager
Intelligent driver detection, installation, and management
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import json
from pathlib import Path
import threading
import time
import re

class DriverManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔧 TL Driver Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')

        self.config_file = Path.home() / '.config' / 'tl-linux' / 'driver_manager.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self.load_config()

        # Driver database
        self.detected_hardware = []
        self.available_drivers = []
        self.installed_drivers = []
        self.driver_database = self.load_driver_database()

        self.setup_ui()

        # Auto-detect on startup
        if self.config.get('auto_detect', True):
            self.root.after(1000, self.detect_hardware)

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'auto_detect': True,
            'auto_install': False,
            'check_updates': True,
            'proprietary_allowed': True,
            'backup_before_install': True
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_driver_database(self):
        """Load driver database"""
        return {
            'graphics': {
                'nvidia': {
                    'name': 'NVIDIA Proprietary',
                    'packages': ['nvidia-driver-535', 'nvidia-settings'],
                    'detect': ['nvidia', 'geforce', 'quadro'],
                    'priority': 1
                },
                'nvidia-open': {
                    'name': 'NVIDIA Open Source',
                    'packages': ['nvidia-driver-535-open'],
                    'detect': ['nvidia'],
                    'priority': 2
                },
                'amd': {
                    'name': 'AMD AMDGPU',
                    'packages': ['xserver-xorg-video-amdgpu', 'mesa-vulkan-drivers'],
                    'detect': ['amd', 'radeon', 'ati'],
                    'priority': 1
                },
                'intel': {
                    'name': 'Intel Graphics',
                    'packages': ['xserver-xorg-video-intel', 'intel-media-va-driver'],
                    'detect': ['intel'],
                    'priority': 1
                }
            },
            'wifi': {
                'broadcom': {
                    'name': 'Broadcom Wireless',
                    'packages': ['broadcom-sta-dkms'],
                    'detect': ['broadcom', 'bcm'],
                    'priority': 1
                },
                'realtek': {
                    'name': 'Realtek Wireless',
                    'packages': ['rtl8192eu-dkms', 'rtl8812au-dkms'],
                    'detect': ['realtek', 'rtl'],
                    'priority': 1
                }
            },
            'audio': {
                'generic': {
                    'name': 'PulseAudio + ALSA',
                    'packages': ['pulseaudio', 'alsa-utils', 'pavucontrol'],
                    'detect': ['audio', 'sound'],
                    'priority': 1
                }
            },
            'bluetooth': {
                'generic': {
                    'name': 'Bluetooth Support',
                    'packages': ['bluez', 'bluez-tools', 'blueman'],
                    'detect': ['bluetooth'],
                    'priority': 1
                }
            },
            'printer': {
                'generic': {
                    'name': 'CUPS Printing',
                    'packages': ['cups', 'system-config-printer'],
                    'detect': ['printer', 'hp', 'epson', 'canon'],
                    'priority': 1
                }
            }
        }

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', pady=20)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🔧 TL Driver Manager",
            font=('Arial', 22, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Automatic hardware detection and driver installation",
            font=('Arial', 11),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack()

        # Control buttons
        control_frame = tk.Frame(self.root, bg='#34495e', pady=15)
        control_frame.pack(fill=tk.X)

        tk.Button(
            control_frame,
            text="🔍 Detect Hardware",
            command=self.detect_hardware,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            control_frame,
            text="⚡ Install Recommended",
            command=self.install_recommended,
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
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Detected Hardware tab
        hardware_frame = tk.Frame(notebook, bg='white')
        notebook.add(hardware_frame, text="💻 Detected Hardware")

        tk.Label(
            hardware_frame,
            text="Your Hardware:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        # Hardware tree
        hardware_tree_frame = tk.Frame(hardware_frame)
        hardware_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        hardware_scroll = tk.Scrollbar(hardware_tree_frame)
        hardware_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.hardware_tree = ttk.Treeview(
            hardware_tree_frame,
            columns=('Type', 'Vendor', 'Model', 'Status'),
            show='tree headings',
            yscrollcommand=hardware_scroll.set
        )

        self.hardware_tree.heading('#0', text='Device')
        self.hardware_tree.heading('Type', text='Type')
        self.hardware_tree.heading('Vendor', text='Vendor')
        self.hardware_tree.heading('Model', text='Model')
        self.hardware_tree.heading('Status', text='Driver Status')

        self.hardware_tree.column('#0', width=200)
        self.hardware_tree.column('Type', width=120)
        self.hardware_tree.column('Vendor', width=150)
        self.hardware_tree.column('Model', width=200)
        self.hardware_tree.column('Status', width=150)

        self.hardware_tree.pack(fill=tk.BOTH, expand=True)
        hardware_scroll.config(command=self.hardware_tree.yview)

        # Available Drivers tab
        drivers_frame = tk.Frame(notebook, bg='white')
        notebook.add(drivers_frame, text="📦 Available Drivers")

        tk.Label(
            drivers_frame,
            text="Recommended Drivers:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        # Drivers tree
        drivers_tree_frame = tk.Frame(drivers_frame)
        drivers_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        drivers_scroll = tk.Scrollbar(drivers_tree_frame)
        drivers_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.drivers_tree = ttk.Treeview(
            drivers_tree_frame,
            columns=('Type', 'Driver', 'Status', 'Action'),
            show='tree headings',
            yscrollcommand=drivers_scroll.set
        )

        self.drivers_tree.heading('#0', text='Package')
        self.drivers_tree.heading('Type', text='Type')
        self.drivers_tree.heading('Driver', text='Driver Name')
        self.drivers_tree.heading('Status', text='Status')
        self.drivers_tree.heading('Action', text='Recommended Action')

        self.drivers_tree.column('#0', width=200)
        self.drivers_tree.column('Type', width=120)
        self.drivers_tree.column('Driver', width=200)
        self.drivers_tree.column('Status', width=150)
        self.drivers_tree.column('Action', width=150)

        self.drivers_tree.pack(fill=tk.BOTH, expand=True)
        drivers_scroll.config(command=self.drivers_tree.yview)

        # Driver actions
        action_frame = tk.Frame(drivers_frame, bg='white', pady=10)
        action_frame.pack(fill=tk.X)

        tk.Button(
            action_frame,
            text="Install Selected",
            command=self.install_selected,
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            action_frame,
            text="Remove Selected",
            command=self.remove_selected,
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        # Log tab
        log_frame = tk.Frame(notebook, bg='white')
        notebook.add(log_frame, text="📋 Installation Log")

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Courier', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

    def detect_hardware(self):
        """Detect system hardware"""
        self.status_bar.config(text="Detecting hardware...")
        self.log("=== Hardware Detection Started ===")

        def detect_thread():
            self.detected_hardware = []

            # Detect PCI devices
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.parse_pci_devices(result.stdout)
            except Exception as e:
                self.log(f"Error detecting PCI devices: {e}")

            # Detect USB devices
            try:
                result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.parse_usb_devices(result.stdout)
            except Exception as e:
                self.log(f"Error detecting USB devices: {e}")

            # Match drivers
            self.match_drivers()

            # Update UI
            self.root.after(0, self.update_hardware_display)
            self.root.after(0, self.update_drivers_display)
            self.root.after(0, lambda: self.status_bar.config(text=f"Detected {len(self.detected_hardware)} devices"))

            self.log(f"=== Detection Complete: {len(self.detected_hardware)} devices found ===")

        threading.Thread(target=detect_thread, daemon=True).start()

    def parse_pci_devices(self, output):
        """Parse lspci output"""
        for line in output.split('\n'):
            if not line.strip():
                continue

            # Parse PCI device info
            parts = line.split(':',1)
            if len(parts) < 2:
                continue

            device_info = parts[1].strip()

            # Detect device type
            device_type = 'Other'
            if 'VGA' in line or 'Display' in line or '3D' in line:
                device_type = 'Graphics'
            elif 'Network' in line or 'Wireless' in line or 'Ethernet' in line:
                device_type = 'Network'
            elif 'Audio' in line or 'Sound' in line:
                device_type = 'Audio'
            elif 'USB' in line:
                device_type = 'USB Controller'
            elif 'SATA' in line or 'IDE' in line:
                device_type = 'Storage'

            # Extract vendor and model
            vendor = ''
            model = device_info

            if ':' in device_info:
                vendor_parts = device_info.split(':', 1)
                vendor = vendor_parts[0].strip()
                model = vendor_parts[1].strip() if len(vendor_parts) > 1 else model

            self.detected_hardware.append({
                'type': device_type,
                'vendor': vendor,
                'model': model,
                'bus': 'PCI',
                'driver_status': 'Unknown'
            })

            self.log(f"Detected: {device_type} - {vendor} {model}")

    def parse_usb_devices(self, output):
        """Parse lsusb output"""
        for line in output.split('\n'):
            if not line.strip() or 'Bus' not in line:
                continue

            # Simple USB device parsing
            if 'ID' in line:
                parts = line.split('ID', 1)
                if len(parts) > 1:
                    device_info = parts[1].strip()

                    self.detected_hardware.append({
                        'type': 'USB Device',
                        'vendor': '',
                        'model': device_info[:50],
                        'bus': 'USB',
                        'driver_status': 'Unknown'
                    })

    def match_drivers(self):
        """Match detected hardware with available drivers"""
        self.available_drivers = []

        for device in self.detected_hardware:
            device_str = f"{device['vendor']} {device['model']}".lower()

            # Check each driver category
            for category, drivers in self.driver_database.items():
                for driver_id, driver_info in drivers.items():
                    # Check if any detection keyword matches
                    for keyword in driver_info['detect']:
                        if keyword.lower() in device_str:
                            # Check if already installed
                            is_installed = self.check_package_installed(driver_info['packages'][0])

                            driver_entry = {
                                'category': category,
                                'driver_id': driver_id,
                                'name': driver_info['name'],
                                'packages': driver_info['packages'],
                                'priority': driver_info['priority'],
                                'device': device,
                                'installed': is_installed,
                                'recommended': driver_info['priority'] == 1
                            }

                            self.available_drivers.append(driver_entry)
                            device['driver_status'] = 'Installed' if is_installed else 'Available'

                            self.log(f"Matched driver: {driver_info['name']} for {device['type']}")
                            break

    def check_package_installed(self, package):
        """Check if package is installed"""
        try:
            result = subprocess.run(
                ['dpkg', '-s', package],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def update_hardware_display(self):
        """Update hardware tree"""
        self.hardware_tree.delete(*self.hardware_tree.get_children())

        for device in self.detected_hardware:
            icon = self.get_device_icon(device['type'])

            self.hardware_tree.insert('', 'end', text=f"{icon} {device['type']}", values=(
                device['type'],
                device['vendor'],
                device['model'],
                device['driver_status']
            ))

    def update_drivers_display(self):
        """Update drivers tree"""
        self.drivers_tree.delete(*self.drivers_tree.get_children())

        for driver in self.available_drivers:
            icon = '✅' if driver['installed'] else '📦'
            status = 'Installed' if driver['installed'] else 'Not Installed'
            action = 'Installed' if driver['installed'] else 'Install Recommended' if driver['recommended'] else 'Available'

            self.drivers_tree.insert('', 'end', text=f"{icon} {driver['packages'][0]}", values=(
                driver['category'].capitalize(),
                driver['name'],
                status,
                action
            ), tags=(driver['driver_id'],))

    def get_device_icon(self, device_type):
        """Get icon for device type"""
        icons = {
            'Graphics': '🎨',
            'Network': '🌐',
            'Audio': '🔊',
            'USB Controller': '🔌',
            'Storage': '💾',
            'USB Device': '🔌',
            'Other': '🔧'
        }
        return icons.get(device_type, '🔧')

    def install_recommended(self):
        """Install all recommended drivers"""
        recommended = [d for d in self.available_drivers if d['recommended'] and not d['installed']]

        if not recommended:
            messagebox.showinfo("No Action Needed", "All recommended drivers are already installed!")
            return

        driver_list = '\n'.join([f"• {d['name']}" for d in recommended])

        if messagebox.askyesno("Install Drivers", f"Install the following recommended drivers?\n\n{driver_list}"):
            self.install_drivers(recommended)

    def install_selected(self):
        """Install selected driver"""
        selection = self.drivers_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a driver to install")
            return

        # Get selected drivers
        selected_ids = [self.drivers_tree.item(item)['tags'][0] for item in selection]
        drivers_to_install = [d for d in self.available_drivers if d['driver_id'] in selected_ids and not d['installed']]

        if not drivers_to_install:
            messagebox.showinfo("Already Installed", "Selected drivers are already installed")
            return

        self.install_drivers(drivers_to_install)

    def install_drivers(self, drivers):
        """Install driver packages"""
        self.status_bar.config(text="Installing drivers...")
        self.log("\n=== Driver Installation Started ===")

        def install_thread():
            for driver in drivers:
                self.log(f"\nInstalling {driver['name']}...")
                self.root.after(0, lambda d=driver: self.status_bar.config(text=f"Installing {d['name']}..."))

                for package in driver['packages']:
                    self.log(f"  Installing package: {package}")

                    try:
                        # Update package list
                        subprocess.run(['sudo', 'apt-get', 'update'],
                                     capture_output=True, timeout=60)

                        # Install package
                        result = subprocess.run(
                            ['sudo', 'apt-get', 'install', '-y', package],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )

                        if result.returncode == 0:
                            self.log(f"  ✓ Successfully installed {package}")
                            driver['installed'] = True
                        else:
                            self.log(f"  ✗ Failed to install {package}")
                            self.log(f"    Error: {result.stderr[:200]}")

                    except Exception as e:
                        self.log(f"  ✗ Error installing {package}: {e}")

            self.log("\n=== Installation Complete ===")
            self.root.after(0, lambda: self.status_bar.config(text="Installation complete"))
            self.root.after(0, self.detect_hardware)

            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo(
                "Installation Complete",
                "Driver installation finished!\n\nYou may need to restart for changes to take effect."
            ))

        threading.Thread(target=install_thread, daemon=True).start()

    def remove_selected(self):
        """Remove selected driver"""
        messagebox.showinfo("Coming Soon", "Driver removal feature coming soon!")

    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Driver Manager Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.configure(bg='white')

        tk.Label(
            settings_window,
            text="Driver Manager Settings",
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(pady=20)

        # Settings options
        options_frame = tk.Frame(settings_window, bg='white', padx=30)
        options_frame.pack(fill=tk.BOTH, expand=True)

        self.auto_detect_var = tk.BooleanVar(value=self.config.get('auto_detect', True))
        tk.Checkbutton(
            options_frame,
            text="Auto-detect hardware on startup",
            variable=self.auto_detect_var,
            bg='white',
            font=('Arial', 11)
        ).pack(anchor='w', pady=5)

        self.auto_install_var = tk.BooleanVar(value=self.config.get('auto_install', False))
        tk.Checkbutton(
            options_frame,
            text="Automatically install recommended drivers",
            variable=self.auto_install_var,
            bg='white',
            font=('Arial', 11)
        ).pack(anchor='w', pady=5)

        self.check_updates_var = tk.BooleanVar(value=self.config.get('check_updates', True))
        tk.Checkbutton(
            options_frame,
            text="Check for driver updates",
            variable=self.check_updates_var,
            bg='white',
            font=('Arial', 11)
        ).pack(anchor='w', pady=5)

        self.proprietary_var = tk.BooleanVar(value=self.config.get('proprietary_allowed', True))
        tk.Checkbutton(
            options_frame,
            text="Allow proprietary drivers",
            variable=self.proprietary_var,
            bg='white',
            font=('Arial', 11)
        ).pack(anchor='w', pady=5)

        self.backup_var = tk.BooleanVar(value=self.config.get('backup_before_install', True))
        tk.Checkbutton(
            options_frame,
            text="Backup before driver installation",
            variable=self.backup_var,
            bg='white',
            font=('Arial', 11)
        ).pack(anchor='w', pady=5)

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
        self.config['auto_detect'] = self.auto_detect_var.get()
        self.config['auto_install'] = self.auto_install_var.get()
        self.config['check_updates'] = self.check_updates_var.get()
        self.config['proprietary_allowed'] = self.proprietary_var.get()
        self.config['backup_before_install'] = self.backup_var.get()

        self.save_config()
        window.destroy()
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")

    def log(self, message):
        """Log message"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        print(message)

    def run(self):
        """Run driver manager"""
        self.root.mainloop()

if __name__ == '__main__':
    manager = DriverManager()
    manager.run()
