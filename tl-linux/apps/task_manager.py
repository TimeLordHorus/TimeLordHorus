#!/usr/bin/env python3
"""
TL Linux - Task Manager
System monitor for processes, resources, performance, and startup apps
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import psutil
import threading
import time
import os

class TaskManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Task Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')

        self.update_interval = 2000  # ms
        self.processes = []

        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        """Create the UI"""
        # Header with system overview
        header = tk.Frame(self.root, bg='#1a1a1a', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙️ Task Manager",
            font=('Arial', 18, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=10)

        # System stats
        stats_frame = tk.Frame(header, bg='#1a1a1a')
        stats_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        self.cpu_label = tk.Label(
            stats_frame,
            text="CPU: 0%",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#5cb85c'
        )
        self.cpu_label.grid(row=0, column=0, padx=15)

        self.mem_label = tk.Label(
            stats_frame,
            text="Memory: 0%",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#4a9eff'
        )
        self.mem_label.grid(row=0, column=1, padx=15)

        self.disk_label = tk.Label(
            stats_frame,
            text="Disk: 0%",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#f0ad4e'
        )
        self.disk_label.grid(row=0, column=2, padx=15)

        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Processes tab
        self.processes_frame = self.create_processes_tab()
        notebook.add(self.processes_frame, text="  📋 Processes  ")

        # Performance tab
        self.performance_frame = self.create_performance_tab()
        notebook.add(self.performance_frame, text="  📊 Performance  ")

        # Startup tab
        self.startup_frame = self.create_startup_tab()
        notebook.add(self.startup_frame, text="  🚀 Startup  ")

        # Services tab
        self.services_frame = self.create_services_tab()
        notebook.add(self.services_frame, text="  ⚙️ Services  ")

    def create_processes_tab(self):
        """Create processes tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        # Controls
        controls = tk.Frame(frame, bg='#2b2b2b')
        controls.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            controls,
            text="Search:",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_processes)

        search_entry = tk.Entry(
            controls,
            textvariable=self.search_var,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='white',
            insertbackground='white',
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=5)

        self.show_user_only_var = tk.BooleanVar()
        tk.Checkbutton(
            controls,
            text="My processes only",
            variable=self.show_user_only_var,
            command=self.filter_processes,
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#cccccc',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            controls,
            text="🔄 Refresh",
            command=self.update_processes,
            font=('Arial', 9),
            bg='#4a9eff',
            fg='white',
            padx=10,
            pady=5,
            bd=0
        ).pack(side=tk.RIGHT)

        # Process tree
        tree_frame = tk.Frame(frame, bg='#2b2b2b')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ('PID', 'Name', 'CPU%', 'Memory', 'Status', 'User')
        self.process_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.process_tree.yview)
        hsb.config(command=self.process_tree.xview)

        # Column headings
        headings = {
            'PID': 80,
            'Name': 250,
            'CPU%': 80,
            'Memory': 100,
            'Status': 100,
            'User': 120
        }

        for col, width in headings.items():
            self.process_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.process_tree.column(col, width=width)

        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Action buttons
        btn_frame = tk.Frame(frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="❌ End Task",
            command=self.kill_process,
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="⏸ Suspend",
            command=self.suspend_process,
            font=('Arial', 10),
            bg='#f0ad4e',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="▶ Resume",
            command=self.resume_process,
            font=('Arial', 10),
            bg='#5cb85c',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="ℹ️ Details",
            command=self.show_process_details,
            font=('Arial', 10),
            bg='#6a6a6a',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def create_performance_tab(self):
        """Create performance monitoring tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        # CPU usage
        cpu_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        cpu_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            cpu_frame,
            text="🖥️ CPU Usage",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#5cb85c'
        ).pack(pady=(10, 5))

        self.cpu_percent_label = tk.Label(
            cpu_frame,
            text="0%",
            font=('Arial', 32, 'bold'),
            bg='#1a1a1a',
            fg='white'
        )
        self.cpu_percent_label.pack(pady=10)

        self.cpu_cores_label = tk.Label(
            cpu_frame,
            text="",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.cpu_cores_label.pack(pady=(0, 10))

        # Memory usage
        mem_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        mem_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            mem_frame,
            text="💾 Memory Usage",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#4a9eff'
        ).pack(pady=(10, 5))

        self.mem_percent_label = tk.Label(
            mem_frame,
            text="0%",
            font=('Arial', 32, 'bold'),
            bg='#1a1a1a',
            fg='white'
        )
        self.mem_percent_label.pack(pady=10)

        self.mem_details_label = tk.Label(
            mem_frame,
            text="",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.mem_details_label.pack(pady=(0, 10))

        # Disk usage
        disk_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        disk_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            disk_frame,
            text="💿 Disk Usage",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#f0ad4e'
        ).pack(pady=(10, 5))

        self.disk_percent_label = tk.Label(
            disk_frame,
            text="0%",
            font=('Arial', 32, 'bold'),
            bg='#1a1a1a',
            fg='white'
        )
        self.disk_percent_label.pack(pady=10)

        self.disk_details_label = tk.Label(
            disk_frame,
            text="",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.disk_details_label.pack(pady=(0, 10))

        # Network
        net_frame = tk.Frame(frame, bg='#1a1a1a', bd=2, relief=tk.SOLID)
        net_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            net_frame,
            text="🌐 Network",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#9b59b6'
        ).pack(pady=(10, 5))

        self.network_label = tk.Label(
            net_frame,
            text="Checking...",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='white'
        )
        self.network_label.pack(pady=(0, 10))

        return frame

    def create_startup_tab(self):
        """Create startup applications tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="Startup Applications",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        tk.Label(
            frame,
            text="Manage which applications start automatically when you log in",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        ).pack(pady=(0, 20))

        # Startup apps list
        list_frame = tk.Frame(frame, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        columns = ('Enabled', 'Name', 'Command', 'Impact')
        self.startup_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15
        )

        for col in columns:
            self.startup_tree.heading(col, text=col)

        widths = {'Enabled': 80, 'Name': 200, 'Command': 300, 'Impact': 100}
        for col, width in widths.items():
            self.startup_tree.column(col, width=width)

        self.startup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.startup_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.startup_tree.configure(yscrollcommand=scrollbar.set)

        # Populate startup apps
        self.load_startup_apps()

        # Buttons
        btn_frame = tk.Frame(frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Button(
            btn_frame,
            text="✅ Enable",
            command=lambda: self.toggle_startup(True),
            font=('Arial', 10),
            bg='#5cb85c',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🚫 Disable",
            command=lambda: self.toggle_startup(False),
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="➕ Add",
            command=self.add_startup_app,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def create_services_tab(self):
        """Create system services tab"""
        frame = tk.Frame(self.root, bg='#2b2b2b')

        tk.Label(
            frame,
            text="System Services",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)

        # Services list
        list_frame = tk.Frame(frame, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        columns = ('Service', 'Status', 'Description')
        self.services_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=20
        )

        for col in columns:
            self.services_tree.heading(col, text=col)

        widths = {'Service': 200, 'Status': 100, 'Description': 400}
        for col, width in widths.items():
            self.services_tree.column(col, width=width)

        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.services_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.services_tree.configure(yscrollcommand=scrollbar.set)

        # Load services
        self.load_services()

        # Buttons
        btn_frame = tk.Frame(frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Button(
            btn_frame,
            text="▶ Start",
            command=lambda: self.control_service('start'),
            font=('Arial', 10),
            bg='#5cb85c',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="⏹ Stop",
            command=lambda: self.control_service('stop'),
            font=('Arial', 10),
            bg='#d9534f',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔄 Restart",
            command=lambda: self.control_service('restart'),
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8,
            bd=0
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def start_monitoring(self):
        """Start continuous system monitoring"""
        self.update_processes()
        self.update_performance()
        self.schedule_updates()

    def schedule_updates(self):
        """Schedule periodic updates"""
        self.root.after(self.update_interval, self.update_processes)
        self.root.after(1000, self.update_performance)

    def update_processes(self):
        """Update process list"""
        # Clear existing
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        # Get processes
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'username']):
                try:
                    info = proc.info
                    pid = info['pid']
                    name = info['name']
                    cpu = f"{info['cpu_percent']:.1f}%"
                    mem = self.format_bytes(info['memory_info'].rss) if info.get('memory_info') else 'N/A'
                    status = info.get('status', 'unknown')
                    user = info.get('username', 'unknown')

                    self.process_tree.insert('', 'end', values=(pid, name, cpu, mem, status, user))

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except Exception as e:
            print(f"Error updating processes: {e}")

        # Schedule next update
        self.root.after(self.update_interval, self.update_processes)

    def update_performance(self):
        """Update performance metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.5)
        self.cpu_percent_label.config(text=f"{cpu_percent:.1f}%")
        self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")

        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        freq_text = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        self.cpu_cores_label.config(text=f"{cpu_count} cores @ {freq_text}")

        # Memory
        mem = psutil.virtual_memory()
        self.mem_percent_label.config(text=f"{mem.percent:.1f}%")
        self.mem_label.config(text=f"Memory: {mem.percent:.1f}%")
        self.mem_details_label.config(
            text=f"{self.format_bytes(mem.used)} / {self.format_bytes(mem.total)}"
        )

        # Disk
        disk = psutil.disk_usage('/')
        self.disk_percent_label.config(text=f"{disk.percent:.1f}%")
        self.disk_label.config(text=f"Disk: {disk.percent:.1f}%")
        self.disk_details_label.config(
            text=f"{self.format_bytes(disk.used)} / {self.format_bytes(disk.total)}"
        )

        # Network
        net_io = psutil.net_io_counters()
        self.network_label.config(
            text=f"↓ {self.format_bytes(net_io.bytes_recv)}  ↑ {self.format_bytes(net_io.bytes_sent)}"
        )

        # Schedule next update
        self.root.after(1000, self.update_performance)

    def filter_processes(self, *args):
        """Filter processes based on search"""
        # Would implement process filtering
        pass

    def sort_by_column(self, col):
        """Sort processes by column"""
        # Would implement sorting
        pass

    def kill_process(self):
        """Kill selected process"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process first")
            return

        item = self.process_tree.item(selection[0])
        pid = int(item['values'][0])
        name = item['values'][1]

        if messagebox.askyesno("Confirm", f"End process '{name}' (PID: {pid})?"):
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                messagebox.showinfo("Success", f"Process {name} terminated")
                self.update_processes()
            except psutil.NoSuchProcess:
                messagebox.showerror("Error", "Process no longer exists")
            except psutil.AccessDenied:
                messagebox.showerror("Error", "Permission denied. Try running as administrator.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill process: {e}")

    def suspend_process(self):
        """Suspend selected process"""
        messagebox.showinfo("Suspend", "Suspend process functionality")

    def resume_process(self):
        """Resume selected process"""
        messagebox.showinfo("Resume", "Resume process functionality")

    def show_process_details(self):
        """Show detailed process information"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process first")
            return

        item = self.process_tree.item(selection[0])
        pid = int(item['values'][0])

        try:
            proc = psutil.Process(pid)
            details = f"""Process Details:

PID: {proc.pid}
Name: {proc.name()}
Status: {proc.status()}
CPU: {proc.cpu_percent()}%
Memory: {self.format_bytes(proc.memory_info().rss)}
User: {proc.username()}
Create Time: {time.ctime(proc.create_time())}
Command: {' '.join(proc.cmdline())}
"""
            messagebox.showinfo("Process Details", details)

        except Exception as e:
            messagebox.showerror("Error", f"Could not get process details: {e}")

    def load_startup_apps(self):
        """Load startup applications"""
        # Clear existing
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)

        # Add sample startup apps
        samples = [
            ("✓", "Network Manager", "nm-applet", "Low"),
            ("✓", "Bluetooth Manager", "blueman-applet", "Low"),
            ("", "Steam", "steam -silent", "High"),
            ("✓", "Backup Service", "tl-backup-daemon", "Medium")
        ]

        for enabled, name, command, impact in samples:
            self.startup_tree.insert('', 'end', values=(enabled, name, command, impact))

    def toggle_startup(self, enable):
        """Enable/disable startup app"""
        selection = self.startup_tree.selection()
        if selection:
            messagebox.showinfo("Startup", f"{'Enable' if enable else 'Disable'} startup app")

    def add_startup_app(self):
        """Add new startup application"""
        messagebox.showinfo("Add Startup", "Add startup application dialog")

    def load_services(self):
        """Load system services"""
        # Clear existing
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)

        # Try to get systemd services
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager'],
                capture_output=True,
                text=True
            )

            for line in result.stdout.split('\n'):
                if '.service' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        service = parts[0]
                        status = parts[3]
                        desc = ' '.join(parts[4:]) if len(parts) > 4 else ''
                        self.services_tree.insert('', 'end', values=(service, status, desc))

        except:
            # Sample data if systemctl not available
            samples = [
                ("NetworkManager.service", "running", "Network connection manager"),
                ("bluetooth.service", "running", "Bluetooth service"),
                ("cups.service", "inactive", "Printing service")
            ]
            for service, status, desc in samples:
                self.services_tree.insert('', 'end', values=(service, status, desc))

    def control_service(self, action):
        """Control systemd service"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a service first")
            return

        item = self.services_tree.item(selection[0])
        service = item['values'][0]

        messagebox.showinfo("Service Control", f"{action.capitalize()} service: {service}")

    def format_bytes(self, bytes_val):
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
    app = TaskManager()
    app.run()

if __name__ == '__main__':
    main()
