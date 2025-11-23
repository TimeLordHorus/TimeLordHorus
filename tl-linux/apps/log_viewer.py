#!/usr/bin/env python3
"""
TL Linux - System Log Viewer
View, search, and monitor system logs with filtering and export
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import re
from datetime import datetime

class LogViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - System Logs")
        self.root.geometry("1100x700")
        self.root.configure(bg='#1a1a1a')

        # Available logs
        self.log_files = {
            'System Log': '/var/log/syslog',
            'Authentication': '/var/log/auth.log',
            'Kernel Log': '/var/log/kern.log',
            'System Messages': '/var/log/messages',
            'Boot Log': '/var/log/boot.log',
            'Application Log': '/var/log/application.log',
            'X11 Log': '/var/log/Xorg.0.log',
            'Package Manager': '/var/log/dpkg.log',
            'System Services': '/var/log/daemon.log',
            'Custom': None  # User selects file
        }

        # Current log
        self.current_log = None
        self.current_log_name = None

        # Monitoring
        self.monitoring = False
        self.monitor_thread = None
        self.last_position = 0

        # Filter settings
        self.filter_text = ""
        self.filter_level = "ALL"
        self.case_sensitive = False

        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📋 System Log Viewer",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#1a1a1a', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))
        toolbar.pack_propagate(False)

        # Log selection
        tk.Label(
            toolbar,
            text="Select Log:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.log_var = tk.StringVar()
        log_combo = ttk.Combobox(
            toolbar,
            textvariable=self.log_var,
            values=list(self.log_files.keys()),
            state='readonly',
            width=20
        )
        log_combo.pack(side=tk.LEFT, padx=5)
        log_combo.bind('<<ComboboxSelected>>', self.on_log_selected)

        # Load button
        tk.Button(
            toolbar,
            text="📂 Load",
            command=self.load_log,
            bg='#4a9eff',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)

        # Monitor toggle
        self.monitor_var = tk.BooleanVar()
        tk.Checkbutton(
            toolbar,
            text="🔄 Auto-refresh",
            variable=self.monitor_var,
            command=self.toggle_monitoring,
            bg='#1a1a1a',
            fg='white',
            selectcolor='#2b2b2b',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)

        # Export button
        tk.Button(
            toolbar,
            text="💾 Export",
            command=self.export_log,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.RIGHT, padx=5)

        # Clear button
        tk.Button(
            toolbar,
            text="🗑️ Clear",
            command=self.clear_display,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=('Arial', 9)
        ).pack(side=tk.RIGHT, padx=5)

        # Filter bar
        filter_bar = tk.Frame(self.root, bg='#1a1a1a')
        filter_bar.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            filter_bar,
            text="🔍 Filter:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.filter_entry = tk.Entry(
            filter_bar,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            bd=0,
            font=('Arial', 10),
            width=30
        )
        self.filter_entry.pack(side=tk.LEFT, padx=5, ipady=5)
        self.filter_entry.bind('<KeyRelease>', lambda e: self.apply_filter())

        tk.Label(
            filter_bar,
            text="Level:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.level_var = tk.StringVar(value="ALL")
        levels = ['ALL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        level_combo = ttk.Combobox(
            filter_bar,
            textvariable=self.level_var,
            values=levels,
            state='readonly',
            width=10
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())

        self.case_var = tk.BooleanVar()
        tk.Checkbutton(
            filter_bar,
            text="Case sensitive",
            variable=self.case_var,
            command=self.apply_filter,
            bg='#1a1a1a',
            fg='white',
            selectcolor='#2b2b2b',
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=10)

        # Main content
        content = tk.Frame(self.root, bg='#1a1a1a')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Log display (with line numbers)
        log_frame = tk.Frame(content, bg='#1a1a1a')
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            log_frame,
            width=6,
            bg='#2b2b2b',
            fg='#888888',
            font=('Courier', 9),
            state=tk.DISABLED,
            bd=0,
            highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Log text
        self.log_text = tk.Text(
            log_frame,
            bg='#1a1a1a',
            fg='#cccccc',
            font=('Courier', 9),
            wrap=tk.NONE,
            bd=0,
            highlightthickness=0
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        y_scroll = tk.Scrollbar(log_frame, command=self.on_scroll)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=y_scroll.set)

        x_scroll = tk.Scrollbar(content, orient=tk.HORIZONTAL, command=self.log_text.xview)
        x_scroll.pack(fill=tk.X)
        self.log_text.config(xscrollcommand=x_scroll.set)

        # Configure tags for log levels
        self.log_text.tag_config('ERROR', foreground='#ff5555')
        self.log_text.tag_config('WARNING', foreground='#ffb86c')
        self.log_text.tag_config('INFO', foreground='#8be9fd')
        self.log_text.tag_config('DEBUG', foreground='#bd93f9')
        self.log_text.tag_config('SUCCESS', foreground='#50fa7b')
        self.log_text.tag_config('highlight', background='#f1fa8c', foreground='#000000')

        # Status bar
        status_bar = tk.Frame(self.root, bg='#2b2b2b', height=25)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="No log loaded",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.line_count_label = tk.Label(
            status_bar,
            text="0 lines",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='e'
        )
        self.line_count_label.pack(side=tk.RIGHT, padx=10)

    def on_scroll(self, *args):
        """Synchronize line numbers with log text"""
        self.line_numbers.yview(*args)
        self.log_text.yview(*args)

    def on_log_selected(self, event):
        """Handle log selection"""
        log_name = self.log_var.get()
        if log_name == 'Custom':
            # Let user select file
            file_path = filedialog.askopenfilename(
                title="Select Log File",
                initialdir="/var/log",
                filetypes=[("Log files", "*.log"), ("All files", "*")]
            )
            if file_path:
                self.current_log = file_path
                self.current_log_name = os.path.basename(file_path)
                self.load_log()
        else:
            self.current_log = self.log_files.get(log_name)
            self.current_log_name = log_name
            # Don't auto-load, wait for user to click Load button

    def load_log(self):
        """Load selected log file"""
        if not self.current_log:
            messagebox.showwarning("No Log Selected", "Please select a log file first.")
            return

        if not os.path.exists(self.current_log):
            messagebox.showerror("File Not Found", f"Log file not found:\n{self.current_log}")
            return

        self.clear_display()

        try:
            # Try to read with sudo if permission denied
            try:
                with open(self.current_log, 'r') as f:
                    content = f.read()
            except PermissionError:
                # Try with sudo
                result = subprocess.run(
                    ['sudo', 'cat', self.current_log],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    content = result.stdout
                else:
                    raise PermissionError("Access denied")

            # Display content
            lines = content.split('\n')
            self.display_lines(lines)

            # Update status
            self.status_label.config(text=f"Loaded: {self.current_log_name} ({len(lines)} lines)")
            self.line_count_label.config(text=f"{len(lines)} lines")

            # Remember position for monitoring
            self.last_position = len(content)

        except Exception as e:
            messagebox.showerror("Error Loading Log", f"Failed to load log file:\n{str(e)}")

    def display_lines(self, lines):
        """Display log lines with syntax highlighting"""
        self.log_text.config(state=tk.NORMAL)
        self.line_numbers.config(state=tk.NORMAL)

        for i, line in enumerate(lines, 1):
            # Add line number
            self.line_numbers.insert(tk.END, f"{i:>5}\n")

            # Detect log level and apply tag
            tags = []
            if 'ERROR' in line.upper() or 'FATAL' in line.upper() or 'FAIL' in line.upper():
                tags.append('ERROR')
            elif 'WARNING' in line.upper() or 'WARN' in line.upper():
                tags.append('WARNING')
            elif 'INFO' in line.upper():
                tags.append('INFO')
            elif 'DEBUG' in line.upper():
                tags.append('DEBUG')
            elif 'SUCCESS' in line.upper() or 'OK' in line.upper():
                tags.append('SUCCESS')

            # Insert line
            if tags:
                self.log_text.insert(tk.END, line + '\n', tags)
            else:
                self.log_text.insert(tk.END, line + '\n')

        self.log_text.config(state=tk.DISABLED)
        self.line_numbers.config(state=tk.DISABLED)

    def clear_display(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)

        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.config(state=tk.DISABLED)

    def toggle_monitoring(self):
        """Toggle real-time log monitoring"""
        if self.monitor_var.get():
            # Start monitoring
            if not self.current_log:
                messagebox.showwarning("No Log Selected", "Please load a log file first.")
                self.monitor_var.set(False)
                return

            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_log, daemon=True)
            self.monitor_thread.start()
            self.status_label.config(text=f"Monitoring: {self.current_log_name}")
        else:
            # Stop monitoring
            self.monitoring = False
            self.status_label.config(text=f"Loaded: {self.current_log_name}")

    def monitor_log(self):
        """Monitor log file for changes (tail -f behavior)"""
        while self.monitoring:
            try:
                # Check if file has new content
                file_size = os.path.getsize(self.current_log)

                if file_size > self.last_position:
                    # Read new content
                    with open(self.current_log, 'r') as f:
                        f.seek(self.last_position)
                        new_content = f.read()

                    if new_content:
                        # Update display
                        new_lines = new_content.split('\n')
                        self.root.after(0, lambda: self.append_lines(new_lines))

                    self.last_position = file_size

            except Exception as e:
                print(f"Monitor error: {e}")

            # Wait before next check
            import time
            time.sleep(1)

    def append_lines(self, lines):
        """Append new lines to display"""
        self.log_text.config(state=tk.NORMAL)
        self.line_numbers.config(state=tk.NORMAL)

        current_line_count = int(self.line_numbers.index('end-1c').split('.')[0])

        for i, line in enumerate(lines):
            if not line:
                continue

            line_num = current_line_count + i

            # Add line number
            self.line_numbers.insert(tk.END, f"{line_num:>5}\n")

            # Detect log level
            tags = []
            if 'ERROR' in line.upper() or 'FATAL' in line.upper():
                tags.append('ERROR')
            elif 'WARNING' in line.upper() or 'WARN' in line.upper():
                tags.append('WARNING')
            elif 'INFO' in line.upper():
                tags.append('INFO')
            elif 'DEBUG' in line.upper():
                tags.append('DEBUG')

            # Insert line
            if tags:
                self.log_text.insert(tk.END, line + '\n', tags)
            else:
                self.log_text.insert(tk.END, line + '\n')

        # Auto-scroll to bottom
        self.log_text.see(tk.END)
        self.line_numbers.see(tk.END)

        self.log_text.config(state=tk.DISABLED)
        self.line_numbers.config(state=tk.DISABLED)

        # Update line count
        total_lines = int(self.line_numbers.index('end-1c').split('.')[0]) - 1
        self.line_count_label.config(text=f"{total_lines} lines")

    def apply_filter(self):
        """Apply search filter to displayed logs"""
        filter_text = self.filter_entry.get()
        filter_level = self.level_var.get()
        case_sensitive = self.case_var.get()

        # Remove previous highlights
        self.log_text.tag_remove('highlight', '1.0', tk.END)

        if not filter_text and filter_level == 'ALL':
            return

        # Apply filter
        # For now, just highlight matching text
        if filter_text:
            self.log_text.config(state=tk.NORMAL)

            # Search and highlight
            start_pos = '1.0'
            while True:
                if case_sensitive:
                    pos = self.log_text.search(filter_text, start_pos, tk.END)
                else:
                    pos = self.log_text.search(filter_text, start_pos, tk.END, nocase=True)

                if not pos:
                    break

                end_pos = f"{pos}+{len(filter_text)}c"
                self.log_text.tag_add('highlight', pos, end_pos)
                start_pos = end_pos

            self.log_text.config(state=tk.DISABLED)

    def export_log(self):
        """Export current log view to file"""
        if not self.log_text.get('1.0', tk.END).strip():
            messagebox.showwarning("No Content", "No log content to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*")]
        )

        if file_path:
            try:
                content = self.log_text.get('1.0', tk.END)
                with open(file_path, 'w') as f:
                    f.write(content)

                messagebox.showinfo("Export Successful", f"Log exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export log:\n{str(e)}")

    def run(self):
        """Run the log viewer"""
        self.root.mainloop()

def main():
    viewer = LogViewer()
    viewer.run()

if __name__ == '__main__':
    main()
