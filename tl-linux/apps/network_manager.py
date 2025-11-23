#!/usr/bin/env python3
"""
TL Linux - Network Manager
Visual interface for WiFi, Bluetooth, VPN, and network configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import json
import os
import threading
import re

class NetworkManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Network Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')

        self.config_dir = os.path.expanduser('~/.tl-linux/network')
        os.makedirs(self.config_dir, exist_ok=True)

        self.saved_networks = self.load_saved_networks()

        self.setup_ui()
        self.refresh_networks()

    def load_saved_networks(self):
        """Load saved network configurations"""
        config_file = os.path.join(self.config_dir, 'saved_networks.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_networks(self):
        """Save network configurations"""
        config_file = os.path.join(self.config_dir, 'saved_networks.json')
        try:
            with open(config_file, 'w') as f:
                json.dump(self.saved_networks, f, indent=2)
        except Exception as e:
            print(f"Error saving networks: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🌐 Network Manager",
            font=('Arial', 18, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Connection status
        self.status_label = tk.Label(
            header,
            text="● Checking...",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # WiFi tab
        self.wifi_frame = self.create_wifi_tab()
        notebook.add(self.wifi_frame, text="  📶 WiFi  ")

        # Bluetooth tab
        self.bluetooth_frame = self.create_bluetooth_tab()
        notebook.add(self.bluetooth_frame, text="  🔵 Bluetooth  ")

        # VPN tab
        self.vpn_frame = self.create_vpn_tab()
        notebook.add(self.vpn_frame, text="  🔒 VPN  ")

        # Ethernet/Wired tab
        self.wired_frame = self.create_wired_tab()
        notebook.add(self.wired_frame, text="  🔌 Wired  ")

        # Advanced tab
        self.advanced_frame = self.create_advanced_tab()
        notebook.add(self.advanced_frame, text="  ⚙️ Advanced  ")

        # Update status
        self.update_connection_status()

    def create_wifi_tab(self):
        """Create WiFi management tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        # Controls
        controls = tk.Frame(frame, bg='#2b2b2b')
        controls.pack(fill=tk.X, padx=20, pady=10)

        self.wifi_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            controls,
            text="WiFi Enabled",
            variable=self.wifi_enabled_var,
            command=self.toggle_wifi,
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT)

        tk.Button(
            controls,
            text="🔄 Refresh",
            command=self.refresh_networks,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.RIGHT)

        # Available networks
        tk.Label(
            frame,
            text="Available Networks:",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=20, pady=(10, 5))

        # Networks listbox with scrollbar
        list_frame = tk.Frame(frame, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.networks_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            selectbackground='#4a9eff',
            selectforeground='white',
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.networks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.networks_listbox.yview)

        self.networks_listbox.bind('<Double-Button-1>', lambda e: self.connect_to_network())

        # Connect button
        tk.Button(
            frame,
            text="Connect to Selected Network",
            command=self.connect_to_network,
            font=('Arial', 11, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        ).pack(pady=10)

        # Current connection info
        self.wifi_info_label = tk.Label(
            frame,
            text="Not connected",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888',
            justify=tk.LEFT
        )
        self.wifi_info_label.pack(anchor='w', padx=20, pady=10)

        return frame

    def create_bluetooth_tab(self):
        """Create Bluetooth management tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        # Controls
        controls = tk.Frame(frame, bg='#2b2b2b')
        controls.pack(fill=tk.X, padx=20, pady=10)

        self.bt_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="Bluetooth Enabled",
            variable=self.bt_enabled_var,
            command=self.toggle_bluetooth,
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='white',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT)

        self.bt_discoverable_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="Discoverable",
            variable=self.bt_discoverable_var,
            command=self.toggle_discoverable,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            controls,
            text="🔍 Scan",
            command=self.scan_bluetooth,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=5,
            bd=0
        ).pack(side=tk.RIGHT)

        # Paired devices
        tk.Label(
            frame,
            text="Paired Devices:",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=20, pady=(10, 5))

        self.paired_listbox = tk.Listbox(
            frame,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            selectbackground='#4a9eff',
            height=6
        )
        self.paired_listbox.pack(fill=tk.X, padx=20, pady=5)

        # Available devices
        tk.Label(
            frame,
            text="Available Devices:",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w', padx=20, pady=(20, 5))

        self.bt_devices_listbox = tk.Listbox(
            frame,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            selectbackground='#4a9eff',
            height=8
        )
        self.bt_devices_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Buttons
        btn_frame = tk.Frame(frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="Pair Device",
            command=self.pair_bluetooth_device,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Unpair",
            command=self.unpair_bluetooth_device,
            font=('Arial', 10),
            bg='#6a6a6a',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def create_vpn_tab(self):
        """Create VPN management tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="VPN Connections",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        # VPN list
        self.vpn_listbox = tk.Listbox(
            frame,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white',
            selectbackground='#4a9eff',
            height=10
        )
        self.vpn_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Buttons
        btn_frame = tk.Frame(frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="➕ Add VPN",
            command=self.add_vpn,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔌 Connect",
            command=self.connect_vpn,
            font=('Arial', 10),
            bg='#5cb85c',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="✖️ Disconnect",
            command=self.disconnect_vpn,
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🗑️ Remove",
            command=self.remove_vpn,
            font=('Arial', 10),
            bg='#6a6a6a',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        # Status
        self.vpn_status_label = tk.Label(
            frame,
            text="No VPN connections configured",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.vpn_status_label.pack(pady=10)

        self.load_vpn_connections()

        return frame

    def create_wired_tab(self):
        """Create wired/ethernet tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="Wired Connection",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        # Connection info
        info_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        self.wired_info_text = tk.Text(
            info_frame,
            font=('Courier', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            height=20,
            wrap=tk.WORD,
            state='disabled'
        )
        self.wired_info_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Button(
            frame,
            text="🔄 Refresh Connection Info",
            command=self.refresh_wired_info,
            font=('Arial', 11),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        ).pack(pady=10)

        self.refresh_wired_info()

        return frame

    def create_advanced_tab(self):
        """Create advanced settings tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="Advanced Network Settings",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        # Settings
        settings_frame = tk.Frame(frame, bg='#2b2b2b')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=40)

        # DNS
        dns_frame = tk.Frame(settings_frame, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        dns_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            dns_frame,
            text="DNS Servers",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', padx=15, pady=10)

        tk.Label(
            dns_frame,
            text="Primary DNS:",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc'
        ).pack(anchor='w', padx=15)

        self.dns_primary = tk.Entry(
            dns_frame,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white'
        )
        self.dns_primary.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(
            dns_frame,
            text="Secondary DNS:",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc'
        ).pack(anchor='w', padx=15, pady=(10, 0))

        self.dns_secondary = tk.Entry(
            dns_frame,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white'
        )
        self.dns_secondary.pack(fill=tk.X, padx=15, pady=(5, 15))

        # Proxy
        proxy_frame = tk.Frame(settings_frame, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        proxy_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            proxy_frame,
            text="Proxy Settings",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', padx=15, pady=10)

        self.proxy_enabled_var = tk.BooleanVar()
        tk.Checkbutton(
            proxy_frame,
            text="Use Proxy Server",
            variable=self.proxy_enabled_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b'
        ).pack(anchor='w', padx=15, pady=5)

        tk.Label(
            proxy_frame,
            text="Proxy Address:",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc'
        ).pack(anchor='w', padx=15, pady=(10, 0))

        self.proxy_address = tk.Entry(
            proxy_frame,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white'
        )
        self.proxy_address.pack(fill=tk.X, padx=15, pady=(5, 15))

        # Firewall
        firewall_frame = tk.Frame(settings_frame, bg='#1a1a1a', bd=1, relief=tk.SOLID)
        firewall_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            firewall_frame,
            text="Firewall",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(anchor='w', padx=15, pady=10)

        self.firewall_enabled_var = tk.BooleanVar()
        tk.Checkbutton(
            firewall_frame,
            text="Enable Firewall",
            variable=self.firewall_enabled_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            selectcolor='#2b2b2b',
            command=self.toggle_firewall
        ).pack(anchor='w', padx=15, pady=(5, 15))

        # Save button
        tk.Button(
            frame,
            text="💾 Save Advanced Settings",
            command=self.save_advanced_settings,
            font=('Arial', 11, 'bold'),
            bg='#4a9eff',
            fg='white',
            padx=20,
            pady=10,
            bd=0
        ).pack(pady=20)

        self.load_advanced_settings()

        return frame

    def refresh_networks(self):
        """Scan for available WiFi networks"""
        self.networks_listbox.delete(0, tk.END)
        self.networks_listbox.insert(tk.END, "Scanning...")

        def scan():
            try:
                # Try nmcli first
                result = subprocess.run(
                    ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            ssid = parts[0]
                            signal = parts[1]
                            security = parts[2] if parts[2] else 'Open'

                            if ssid:  # Ignore hidden networks
                                # Signal strength indicator
                                if signal:
                                    sig_int = int(signal)
                                    if sig_int >= 75:
                                        bars = '▰▰▰▰'
                                    elif sig_int >= 50:
                                        bars = '▰▰▰▱'
                                    elif sig_int >= 25:
                                        bars = '▰▰▱▱'
                                    else:
                                        bars = '▰▱▱▱'
                                else:
                                    bars = '▱▱▱▱'

                                lock = '🔒' if security and security != '--' else '🔓'
                                networks.append((ssid, f"{lock} {bars} {ssid} ({signal}%)"))

                self.root.after(0, lambda: self.update_network_list(networks))

            except FileNotFoundError:
                self.root.after(0, lambda: self.update_network_list([
                    ('Demo Network 1', '🔒 ▰▰▰▰ Demo Network 1 (85%)'),
                    ('Demo Network 2', '🔓 ▰▰▱▱ Demo Network 2 (40%)')
                ]))
            except Exception as e:
                print(f"WiFi scan error: {e}")
                self.root.after(0, lambda: self.networks_listbox.delete(0, tk.END))

        threading.Thread(target=scan, daemon=True).start()

    def update_network_list(self, networks):
        """Update networks listbox"""
        self.networks_listbox.delete(0, tk.END)
        self.network_map = {}

        if networks:
            for ssid, display in networks:
                self.networks_listbox.insert(tk.END, display)
                self.network_map[display] = ssid
        else:
            self.networks_listbox.insert(tk.END, "No networks found")

    def connect_to_network(self):
        """Connect to selected WiFi network"""
        selection = self.networks_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a network first")
            return

        display_name = self.networks_listbox.get(selection[0])
        if display_name in self.network_map:
            ssid = self.network_map[display_name]

            # Check if password needed
            if '🔒' in display_name:
                password = simpledialog.askstring(
                    "WiFi Password",
                    f"Enter password for '{ssid}':",
                    show='*'
                )
                if not password:
                    return

                # Try to connect
                try:
                    subprocess.run(
                        ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password],
                        check=True
                    )
                    messagebox.showinfo("Success", f"Connected to {ssid}")
                    self.update_connection_status()
                except:
                    messagebox.showerror("Connection Failed", f"Could not connect to {ssid}")
            else:
                # Open network
                try:
                    subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], check=True)
                    messagebox.showinfo("Success", f"Connected to {ssid}")
                    self.update_connection_status()
                except:
                    messagebox.showerror("Connection Failed", f"Could not connect to {ssid}")

    def toggle_wifi(self):
        """Toggle WiFi on/off"""
        enabled = self.wifi_enabled_var.get()
        try:
            if enabled:
                subprocess.run(['nmcli', 'radio', 'wifi', 'on'])
            else:
                subprocess.run(['nmcli', 'radio', 'wifi', 'off'])
        except:
            pass

    def toggle_bluetooth(self):
        """Toggle Bluetooth on/off"""
        enabled = self.bt_enabled_var.get()
        try:
            if enabled:
                subprocess.run(['bluetoothctl', 'power', 'on'])
            else:
                subprocess.run(['bluetoothctl', 'power', 'off'])
        except:
            pass

    def toggle_discoverable(self):
        """Toggle Bluetooth discoverable mode"""
        discoverable = self.bt_discoverable_var.get()
        try:
            if discoverable:
                subprocess.run(['bluetoothctl', 'discoverable', 'on'])
            else:
                subprocess.run(['bluetoothctl', 'discoverable', 'off'])
        except:
            pass

    def scan_bluetooth(self):
        """Scan for Bluetooth devices"""
        self.bt_devices_listbox.delete(0, tk.END)
        self.bt_devices_listbox.insert(tk.END, "Scanning for devices...")

        # Would use bluetoothctl scan on
        # For demo, show placeholder
        self.root.after(2000, lambda: self.bt_devices_listbox.delete(0, tk.END))

    def pair_bluetooth_device(self):
        """Pair with selected Bluetooth device"""
        messagebox.showinfo("Bluetooth", "Pairing functionality will be implemented with bluetoothctl")

    def unpair_bluetooth_device(self):
        """Unpair Bluetooth device"""
        messagebox.showinfo("Bluetooth", "Unpairing functionality will be implemented")

    def load_vpn_connections(self):
        """Load saved VPN connections"""
        self.vpn_listbox.delete(0, tk.END)
        # Would load from NetworkManager connections
        self.vpn_listbox.insert(tk.END, "No VPN connections configured")

    def add_vpn(self):
        """Add new VPN connection"""
        messagebox.showinfo("VPN", "VPN configuration dialog would open here")

    def connect_vpn(self):
        """Connect to VPN"""
        selection = self.vpn_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a VPN connection")
            return

    def disconnect_vpn(self):
        """Disconnect VPN"""
        messagebox.showinfo("VPN", "Disconnecting VPN...")

    def remove_vpn(self):
        """Remove VPN connection"""
        selection = self.vpn_listbox.curselection()
        if selection:
            if messagebox.askyesno("Confirm", "Remove this VPN connection?"):
                self.vpn_listbox.delete(selection)

    def refresh_wired_info(self):
        """Refresh wired connection information"""
        self.wired_info_text.config(state='normal')
        self.wired_info_text.delete('1.0', tk.END)

        try:
            # Get interface info
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            self.wired_info_text.insert('1.0', result.stdout)
        except:
            self.wired_info_text.insert('1.0', "Could not retrieve network information")

        self.wired_info_text.config(state='disabled')

    def load_advanced_settings(self):
        """Load advanced network settings"""
        # Would load from system configuration
        pass

    def save_advanced_settings(self):
        """Save advanced network settings"""
        messagebox.showinfo("Settings", "Advanced settings saved")

    def toggle_firewall(self):
        """Toggle firewall on/off"""
        enabled = self.firewall_enabled_var.get()
        # Would use ufw enable/disable
        messagebox.showinfo("Firewall", f"Firewall {'enabled' if enabled else 'disabled'}")

    def update_connection_status(self):
        """Update connection status display"""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'STATE,CONNECTIVITY', 'general', 'status'],
                capture_output=True,
                text=True
            )

            if 'connected' in result.stdout.lower():
                # Get active connection
                conn_result = subprocess.run(
                    ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
                    capture_output=True,
                    text=True
                )

                if conn_result.stdout:
                    conn_name = conn_result.stdout.split(':')[0]
                    self.status_label.config(text=f"● Connected to {conn_name}", fg='#5cb85c')
                else:
                    self.status_label.config(text="● Connected", fg='#5cb85c')
            else:
                self.status_label.config(text="● Disconnected", fg='#d9534f')

        except:
            self.status_label.config(text="● Status Unknown", fg='#888888')

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = NetworkManager()
    app.run()

if __name__ == '__main__':
    main()
