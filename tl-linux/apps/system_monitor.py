#!/usr/bin/env python3
"""
TL Linux - System Monitor
Real-time system resource monitor and task manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os

class SystemMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - System Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # Monitoring state
        self.monitoring = True
        self.update_interval = 2000  # milliseconds

        # Process list
        self.processes = []
        self.sort_column = 'cpu'
        self.sort_reverse = True

        # History for graphs
        self.cpu_history = [0] * 60
        self.memory_history = [0] * 60
        self.network_history = [0] * 60

        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📊 System Monitor",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # System info
        self.uptime_label = tk.Label(
            header,
            text="Uptime: --",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='white'
        )
        self.uptime_label.pack(side=tk.RIGHT, padx=20)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Tab 1: Overview
        self.create_overview_tab()

        # Tab 2: Processes
        self.create_processes_tab()

        # Tab 3: Resources
        self.create_resources_tab()

        # Tab 4: System Info
        self.create_system_info_tab()

        # Status bar
        status_bar = tk.Frame(self.root, bg='#2b2b2b', height=25)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="Monitoring...",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

    def create_overview_tab(self):
        """Create overview tab with key metrics"""
        overview_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(overview_tab, text="Overview")

        # Grid layout for metrics
        metrics_container = tk.Frame(overview_tab, bg='#1a1a1a')
        metrics_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # CPU Card
        cpu_card = self.create_metric_card(metrics_container, "CPU Usage", "#ff79c6")
        cpu_card.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.cpu_percent_label = tk.Label(
            cpu_card,
            text="0%",
            font=('Arial', 32, 'bold'),
            bg='#2b2b2b',
            fg='#ff79c6'
        )
        self.cpu_percent_label.pack(pady=10)

        self.cpu_cores_label = tk.Label(
            cpu_card,
            text="Cores: --",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.cpu_cores_label.pack()

        # Memory Card
        mem_card = self.create_metric_card(metrics_container, "Memory Usage", "#50fa7b")
        mem_card.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.mem_percent_label = tk.Label(
            mem_card,
            text="0%",
            font=('Arial', 32, 'bold'),
            bg='#2b2b2b',
            fg='#50fa7b'
        )
        self.mem_percent_label.pack(pady=10)

        self.mem_details_label = tk.Label(
            mem_card,
            text="0 GB / 0 GB",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.mem_details_label.pack()

        # Disk Card
        disk_card = self.create_metric_card(metrics_container, "Disk Usage", "#8be9fd")
        disk_card.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.disk_percent_label = tk.Label(
            disk_card,
            text="0%",
            font=('Arial', 32, 'bold'),
            bg='#2b2b2b',
            fg='#8be9fd'
        )
        self.disk_percent_label.pack(pady=10)

        self.disk_details_label = tk.Label(
            disk_card,
            text="0 GB / 0 GB",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.disk_details_label.pack()

        # Network Card
        net_card = self.create_metric_card(metrics_container, "Network", "#f1fa8c")
        net_card.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

        self.net_download_label = tk.Label(
            net_card,
            text="↓ 0 KB/s",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#f1fa8c'
        )
        self.net_download_label.pack(pady=5)

        self.net_upload_label = tk.Label(
            net_card,
            text="↑ 0 KB/s",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#f1fa8c'
        )
        self.net_upload_label.pack(pady=5)

        # Configure grid
        metrics_container.columnconfigure(0, weight=1)
        metrics_container.columnconfigure(1, weight=1)
        metrics_container.rowconfigure(0, weight=1)
        metrics_container.rowconfigure(1, weight=1)

    def create_metric_card(self, parent, title, color):
        """Create a metric card"""
        card = tk.Frame(parent, bg='#2b2b2b', relief=tk.SOLID, bd=1)

        # Title bar
        title_bar = tk.Frame(card, bg=color, height=5)
        title_bar.pack(fill=tk.X)

        tk.Label(
            card,
            text=title,
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=(15, 5))

        return card

    def create_processes_tab(self):
        """Create processes tab"""
        processes_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(processes_tab, text="Processes")

        # Toolbar
        toolbar = tk.Frame(processes_tab, bg='#1a1a1a')
        toolbar.pack(fill=tk.X, pady=10, padx=10)

        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_processes,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="❌ Kill Process",
            command=self.kill_process,
            bg='#ff5555',
            fg='white',
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Search
        search_frame = tk.Frame(toolbar, bg='#1a1a1a')
        search_frame.pack(side=tk.RIGHT)

        tk.Label(search_frame, text="🔍", bg='#1a1a1a', fg='white').pack(side=tk.LEFT, padx=5)

        self.process_search_var = tk.StringVar()
        self.process_search_var.trace('w', lambda *args: self.filter_processes())

        tk.Entry(
            search_frame,
            textvariable=self.process_search_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            bd=0,
            width=25
        ).pack(side=tk.LEFT, ipady=5)

        # Process list
        list_frame = tk.Frame(processes_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.process_tree = ttk.Treeview(
            list_frame,
            columns=('PID', 'CPU', 'Memory', 'User'),
            yscrollcommand=scrollbar.set
        )
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.process_tree.yview)

        # Configure columns
        self.process_tree.heading('#0', text='Process', anchor='w', command=lambda: self.sort_processes('name'))
        self.process_tree.heading('PID', text='PID', anchor='w', command=lambda: self.sort_processes('pid'))
        self.process_tree.heading('CPU', text='CPU %', anchor='w', command=lambda: self.sort_processes('cpu'))
        self.process_tree.heading('Memory', text='Memory', anchor='w', command=lambda: self.sort_processes('mem'))
        self.process_tree.heading('User', text='User', anchor='w', command=lambda: self.sort_processes('user'))

        self.process_tree.column('#0', width=300)
        self.process_tree.column('PID', width=80)
        self.process_tree.column('CPU', width=80)
        self.process_tree.column('Memory', width=100)
        self.process_tree.column('User', width=100)

        # Style
        style = ttk.Style()
        style.configure('Treeview', background='#2b2b2b', foreground='white', fieldbackground='#2b2b2b')
        style.map('Treeview', background=[('selected', '#4a9eff')])

    def create_resources_tab(self):
        """Create resources tab with graphs"""
        resources_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(resources_tab, text="Resources")

        # CPU Graph
        cpu_frame = tk.LabelFrame(
            resources_tab,
            text="CPU Usage History",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        cpu_frame.pack(fill=tk.X, padx=20, pady=10)

        self.cpu_canvas = tk.Canvas(
            cpu_frame,
            bg='#2b2b2b',
            height=100,
            highlightthickness=0
        )
        self.cpu_canvas.pack(fill=tk.X, padx=10, pady=10)

        # Memory Graph
        mem_frame = tk.LabelFrame(
            resources_tab,
            text="Memory Usage History",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        mem_frame.pack(fill=tk.X, padx=20, pady=10)

        self.mem_canvas = tk.Canvas(
            mem_frame,
            bg='#2b2b2b',
            height=100,
            highlightthickness=0
        )
        self.mem_canvas.pack(fill=tk.X, padx=10, pady=10)

        # Network Graph
        net_frame = tk.LabelFrame(
            resources_tab,
            text="Network Activity",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        net_frame.pack(fill=tk.X, padx=20, pady=10)

        self.net_canvas = tk.Canvas(
            net_frame,
            bg='#2b2b2b',
            height=100,
            highlightthickness=0
        )
        self.net_canvas.pack(fill=tk.X, padx=10, pady=10)

    def create_system_info_tab(self):
        """Create system info tab"""
        info_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(info_tab, text="System Info")

        # System information
        info_frame = tk.Frame(info_tab, bg='#1a1a1a')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.system_info_text = tk.Text(
            info_frame,
            bg='#2b2b2b',
            fg='white',
            font=('Courier', 10),
            wrap=tk.WORD,
            bd=0,
            highlightthickness=0
        )
        self.system_info_text.pack(fill=tk.BOTH, expand=True)

        self.load_system_info()

    def start_monitoring(self):
        """Start monitoring thread"""
        def monitor():
            while self.monitoring:
                try:
                    self.root.after(0, self.update_metrics)
                except:
                    pass

                time.sleep(self.update_interval / 1000)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def update_metrics(self):
        """Update all metrics"""
        self.update_cpu()
        self.update_memory()
        self.update_disk()
        self.update_network()
        self.update_uptime()
        self.refresh_processes()
        self.draw_graphs()

    def update_cpu(self):
        """Update CPU metrics"""
        try:
            # Get CPU usage from /proc/stat
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                values = line.split()[1:]
                total = sum(int(v) for v in values)
                idle = int(values[3])

                # Calculate percentage (simplified)
                if hasattr(self, 'prev_total'):
                    total_delta = total - self.prev_total
                    idle_delta = idle - self.prev_idle
                    if total_delta > 0:
                        cpu_percent = 100 * (1 - idle_delta / total_delta)
                    else:
                        cpu_percent = 0
                else:
                    cpu_percent = 0

                self.prev_total = total
                self.prev_idle = idle

            # Get CPU cores
            cpu_count = os.cpu_count() or 1

            self.cpu_percent_label.config(text=f"{cpu_percent:.1f}%")
            self.cpu_cores_label.config(text=f"Cores: {cpu_count}")

            # Update history
            self.cpu_history.pop(0)
            self.cpu_history.append(cpu_percent)

        except Exception as e:
            print(f"CPU update error: {e}")

    def update_memory(self):
        """Update memory metrics"""
        try:
            # Parse /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()

            mem_info = {}
            for line in lines:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = int(parts[1].strip().split()[0])  # kB
                    mem_info[key] = value

            total = mem_info.get('MemTotal', 0) / 1024 / 1024  # GB
            available = mem_info.get('MemAvailable', 0) / 1024 / 1024  # GB
            used = total - available

            if total > 0:
                mem_percent = (used / total) * 100
            else:
                mem_percent = 0

            self.mem_percent_label.config(text=f"{mem_percent:.1f}%")
            self.mem_details_label.config(text=f"{used:.1f} GB / {total:.1f} GB")

            # Update history
            self.memory_history.pop(0)
            self.memory_history.append(mem_percent)

        except Exception as e:
            print(f"Memory update error: {e}")

    def update_disk(self):
        """Update disk metrics"""
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    total = parts[1]
                    used = parts[2]
                    percent = parts[4].rstrip('%')

                    self.disk_percent_label.config(text=f"{percent}%")
                    self.disk_details_label.config(text=f"{used} / {total}")

        except Exception as e:
            print(f"Disk update error: {e}")

    def update_network(self):
        """Update network metrics"""
        try:
            # Read /proc/net/dev
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip header

            total_rx = 0
            total_tx = 0

            for line in lines:
                parts = line.split(':')
                if len(parts) == 2:
                    stats = parts[1].split()
                    total_rx += int(stats[0])  # Received bytes
                    total_tx += int(stats[8])  # Transmitted bytes

            # Calculate speed (simplified)
            if hasattr(self, 'prev_rx'):
                rx_speed = (total_rx - self.prev_rx) / (self.update_interval / 1000) / 1024  # KB/s
                tx_speed = (total_tx - self.prev_tx) / (self.update_interval / 1000) / 1024  # KB/s
            else:
                rx_speed = 0
                tx_speed = 0

            self.prev_rx = total_rx
            self.prev_tx = total_tx

            self.net_download_label.config(text=f"↓ {rx_speed:.1f} KB/s")
            self.net_upload_label.config(text=f"↑ {tx_speed:.1f} KB/s")

            # Update history
            self.network_history.pop(0)
            self.network_history.append(rx_speed)

        except Exception as e:
            print(f"Network update error: {e}")

    def update_uptime(self):
        """Update system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])

            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            self.uptime_label.config(text=f"Uptime: {hours}h {minutes}m")

        except:
            pass

    def refresh_processes(self):
        """Refresh process list"""
        try:
            result = subprocess.run(
                ['ps', 'aux', '--sort=-%cpu'],
                capture_output=True,
                text=True
            )

            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            self.processes = []

            for line in lines[:100]:  # Limit to top 100 processes
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    self.processes.append({
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'name': parts[10]
                    })

            self.display_processes()

        except Exception as e:
            print(f"Process refresh error: {e}")

    def display_processes(self):
        """Display processes in tree"""
        search_term = self.process_search_var.get().lower()

        self.process_tree.delete(*self.process_tree.get_children())

        for proc in self.processes:
            if not search_term or search_term in proc['name'].lower():
                self.process_tree.insert(
                    '',
                    tk.END,
                    text=proc['name'],
                    values=(proc['pid'], f"{proc['cpu']}%", f"{proc['mem']}%", proc['user'])
                )

    def filter_processes(self):
        """Filter processes based on search"""
        self.display_processes()

    def sort_processes(self, column):
        """Sort processes by column"""
        self.sort_column = column
        self.sort_reverse = not self.sort_reverse

        # Sort processes list
        if column == 'name':
            self.processes.sort(key=lambda p: p['name'], reverse=self.sort_reverse)
        elif column == 'pid':
            self.processes.sort(key=lambda p: int(p['pid']), reverse=self.sort_reverse)
        elif column == 'cpu':
            self.processes.sort(key=lambda p: float(p['cpu']), reverse=self.sort_reverse)
        elif column == 'mem':
            self.processes.sort(key=lambda p: float(p['mem']), reverse=self.sort_reverse)
        elif column == 'user':
            self.processes.sort(key=lambda p: p['user'], reverse=self.sort_reverse)

        self.display_processes()

    def kill_process(self):
        """Kill selected process"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process to kill")
            return

        item = selection[0]
        pid = self.process_tree.item(item)['values'][0]
        name = self.process_tree.item(item)['text']

        if messagebox.askyesno("Kill Process", f"Kill process '{name}' (PID: {pid})?"):
            try:
                subprocess.run(['kill', str(pid)])
                self.status_label.config(text=f"Killed process {pid}")
                self.refresh_processes()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill process:\n{str(e)}")

    def draw_graphs(self):
        """Draw resource usage graphs"""
        self.draw_graph(self.cpu_canvas, self.cpu_history, '#ff79c6', 100)
        self.draw_graph(self.mem_canvas, self.memory_history, '#50fa7b', 100)
        self.draw_graph(self.net_canvas, self.network_history, '#f1fa8c', max(self.network_history) or 100)

    def draw_graph(self, canvas, data, color, max_value):
        """Draw a line graph"""
        canvas.delete('all')

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 10 or height < 10:
            return

        # Draw grid lines
        for i in range(0, 101, 25):
            y = height - (i / 100 * height)
            canvas.create_line(0, y, width, y, fill='#444444', dash=(2, 4))

        # Draw data line
        if len(data) > 1:
            points = []
            step = width / (len(data) - 1)

            for i, value in enumerate(data):
                x = i * step
                y = height - (min(value, max_value) / max_value * height)
                points.extend([x, y])

            if len(points) >= 4:
                canvas.create_line(points, fill=color, width=2, smooth=True)

    def load_system_info(self):
        """Load system information"""
        info_lines = []

        # OS info
        try:
            result = subprocess.run(['lsb_release', '-a'], capture_output=True, text=True)
            info_lines.append("=== Operating System ===")
            info_lines.append(result.stdout)
        except:
            pass

        # Kernel
        try:
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
            info_lines.append("\n=== Kernel ===")
            info_lines.append(result.stdout)
        except:
            pass

        # CPU info
        try:
            with open('/proc/cpuinfo', 'r') as f:
                lines = f.readlines()

            info_lines.append("\n=== CPU ===")
            for line in lines:
                if 'model name' in line:
                    info_lines.append(line.split(':')[1].strip())
                    break
        except:
            pass

        # Memory
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            info_lines.append("\n=== Memory ===")
            info_lines.append(result.stdout)
        except:
            pass

        # Disk
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            info_lines.append("\n=== Disk ===")
            info_lines.append(result.stdout)
        except:
            pass

        self.system_info_text.insert('1.0', '\n'.join(info_lines))
        self.system_info_text.config(state=tk.DISABLED)

    def run(self):
        """Run the system monitor"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window close"""
        self.monitoring = False
        self.root.destroy()

def main():
    monitor = SystemMonitor()
    monitor.run()

if __name__ == '__main__':
    main()
