#!/usr/bin/env python3
"""
TL Linux - Modern Terminal Emulator
Tabbed terminal with split panes, profiles, and rich features
"""

import tkinter as tk
from tkinter import ttk, font, messagebox, simpledialog
import subprocess
import threading
import os
import json
import pty
import select
import termios
import struct
import fcntl

class TerminalPane:
    def __init__(self, parent, profile='default'):
        self.parent = parent
        self.profile = profile

        # Create frame
        self.frame = tk.Frame(parent, bg='#1a1a1a')

        # Terminal widget (Text widget for now, would use proper terminal emulator in production)
        self.terminal = tk.Text(
            self.frame,
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            font=('Courier', 11),
            wrap=tk.CHAR,
            bd=0,
            highlightthickness=0
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(self.frame, command=self.terminal.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal.config(yscrollcommand=scrollbar.set)

        # Shell process
        self.master_fd = None
        self.shell_pid = None
        self.running = False

        # Command history
        self.history = []
        self.history_index = 0
        self.current_command = ""

        # Bindings
        self.terminal.bind('<Return>', self.on_enter)
        self.terminal.bind('<Key>', self.on_key)
        self.terminal.bind('<Control-c>', self.on_ctrl_c)
        self.terminal.bind('<Control-v>', self.on_paste)
        self.terminal.bind('<Up>', self.on_up_arrow)
        self.terminal.bind('<Down>', self.on_down_arrow)

        # Start shell
        self.start_shell()

    def start_shell(self):
        """Start shell process"""
        try:
            # Start bash in a pseudo-terminal
            self.shell_pid, self.master_fd = pty.fork()

            if self.shell_pid == 0:
                # Child process - exec shell
                os.execvp('bash', ['bash'])
            else:
                # Parent process - read shell output
                self.running = True

                # Make non-blocking
                flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
                fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

                # Start output reader thread
                self.reader_thread = threading.Thread(target=self.read_output, daemon=True)
                self.reader_thread.start()

        except Exception as e:
            self.terminal.insert(tk.END, f"Error starting shell: {e}\n")
            self.terminal.see(tk.END)

    def read_output(self):
        """Read shell output continuously"""
        while self.running:
            try:
                # Check if there's data to read
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)

                if ready:
                    try:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            text = data.decode('utf-8', errors='replace')
                            self.terminal.after(0, lambda: self.append_output(text))
                    except OSError:
                        break

            except Exception as e:
                print(f"Terminal read error: {e}")
                break

    def append_output(self, text):
        """Append output to terminal"""
        try:
            self.terminal.insert(tk.END, text)
            self.terminal.see(tk.END)
        except:
            pass

    def on_enter(self, event):
        """Handle Enter key"""
        # Get current command
        command = self.terminal.get("insert linestart", "insert lineend")

        # Send to shell
        try:
            os.write(self.master_fd, (command + '\n').encode())

            # Add to history
            if command.strip():
                self.history.append(command)
                self.history_index = len(self.history)
        except:
            pass

        return "break"

    def on_key(self, event):
        """Handle key press"""
        # Allow typing
        return None

    def on_ctrl_c(self, event):
        """Handle Ctrl+C (interrupt)"""
        try:
            os.write(self.master_fd, b'\x03')  # Send Ctrl+C
        except:
            pass
        return "break"

    def on_paste(self, event):
        """Handle paste"""
        try:
            text = self.terminal.clipboard_get()
            os.write(self.master_fd, text.encode())
        except:
            pass
        return "break"

    def on_up_arrow(self, event):
        """Navigate command history up"""
        if self.history and self.history_index > 0:
            self.history_index -= 1
            # Would replace current line with history item
        return "break"

    def on_down_arrow(self, event):
        """Navigate command history down"""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            # Would replace current line with history item
        return "break"

    def send_command(self, command):
        """Send command to shell"""
        try:
            os.write(self.master_fd, (command + '\n').encode())
        except:
            pass

    def close(self):
        """Close terminal"""
        self.running = False
        try:
            if self.master_fd:
                os.close(self.master_fd)
        except:
            pass

class TerminalTab:
    def __init__(self, notebook, name="Terminal"):
        self.notebook = notebook
        self.name = name

        # Create tab frame
        self.tab_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(self.tab_frame, text=name)

        # Panes container
        self.panes_container = tk.Frame(self.tab_frame, bg='#1a1a1a')
        self.panes_container.pack(fill=tk.BOTH, expand=True)

        # Start with single pane
        self.panes = []
        self.add_pane()

    def add_pane(self, orientation='horizontal'):
        """Add a new terminal pane"""
        pane = TerminalPane(self.panes_container)
        pane.frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.panes.append(pane)
        return pane

    def close(self):
        """Close all panes in tab"""
        for pane in self.panes:
            pane.close()

class ModernTerminal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux Terminal")
        self.root.geometry("900x600")
        self.root.configure(bg='#1a1a1a')

        # Config
        self.config_dir = os.path.expanduser('~/.tl-linux/terminal')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

        # Tabs
        self.tabs = []

        self.setup_ui()

        # Keyboard shortcuts
        self.root.bind('<Control-t>', lambda e: self.new_tab())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<Control-plus>', lambda e: self.increase_font_size())
        self.root.bind('<Control-minus>', lambda e: self.decrease_font_size())
        self.root.bind('<Control-0>', lambda e: self.reset_font_size())

        # Create first tab
        self.new_tab()

    def load_config(self):
        """Load configuration"""
        default_config = {
            'font_family': 'Courier',
            'font_size': 11,
            'color_scheme': 'matrix',  # matrix, dracula, solarized, monokai
            'scrollback_lines': 10000,
            'profiles': {
                'default': {
                    'name': 'Default',
                    'command': 'bash',
                    'bg': '#1a1a1a',
                    'fg': '#00ff00'
                }
            }
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except:
            pass

        return default_config

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        """Create the UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Tab", command=self.new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="New Window", command=self.new_window)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+Shift+C")
        edit_menu.add_command(label="Paste", accelerator="Ctrl+Shift+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self.show_preferences)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.increase_font_size, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.decrease_font_size, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_font_size, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_command(label="Split Horizontally")
        view_menu.add_command(label="Split Vertically")

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2b2b2b', height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        # New tab button
        tk.Button(
            toolbar,
            text="➕ New Tab",
            command=self.new_tab,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Font size controls
        font_frame = tk.Frame(toolbar, bg='#2b2b2b')
        font_frame.pack(side=tk.RIGHT, padx=10)

        tk.Button(
            font_frame,
            text="A-",
            command=self.decrease_font_size,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(
            font_frame,
            text="Font Size",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            font_frame,
            text="A+",
            command=self.increase_font_size,
            bg='#2b2b2b',
            fg='white',
            bd=0,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=2)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Style for notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Status bar
        self.status_bar = tk.Frame(self.root, bg='#2b2b2b', height=25)
        self.status_bar.pack(fill=tk.X)
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

    def new_tab(self, name=None):
        """Create new terminal tab"""
        if name is None:
            name = f"Terminal {len(self.tabs) + 1}"

        tab = TerminalTab(self.notebook, name)
        self.tabs.append(tab)
        self.notebook.select(len(self.tabs) - 1)
        self.update_status(f"Created {name}")

    def close_current_tab(self):
        """Close current tab"""
        current = self.notebook.index(self.notebook.select())
        if 0 <= current < len(self.tabs):
            tab = self.tabs[current]
            tab.close()
            self.notebook.forget(current)
            self.tabs.pop(current)
            self.update_status("Tab closed")

            # Exit if no tabs left
            if not self.tabs:
                self.quit()

    def new_window(self):
        """Open new terminal window"""
        subprocess.Popen(['python3', __file__])

    def increase_font_size(self):
        """Increase font size"""
        self.config['font_size'] = min(24, self.config['font_size'] + 1)
        self.apply_font_size()
        self.save_config()

    def decrease_font_size(self):
        """Decrease font size"""
        self.config['font_size'] = max(8, self.config['font_size'] - 1)
        self.apply_font_size()
        self.save_config()

    def reset_font_size(self):
        """Reset font size to default"""
        self.config['font_size'] = 11
        self.apply_font_size()
        self.save_config()

    def apply_font_size(self):
        """Apply font size to all terminals"""
        # Would update all terminal panes with new font size
        self.update_status(f"Font size: {self.config['font_size']}")

    def show_preferences(self):
        """Show preferences dialog"""
        pref_window = tk.Toplevel(self.root)
        pref_window.title("Terminal Preferences")
        pref_window.geometry("500x400")
        pref_window.configure(bg='#2b2b2b')

        tk.Label(
            pref_window,
            text="Terminal Preferences",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)

        # Color scheme selection
        scheme_frame = tk.Frame(pref_window, bg='#2b2b2b')
        scheme_frame.pack(pady=10)

        tk.Label(
            scheme_frame,
            text="Color Scheme:",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=10)

        schemes = ['matrix', 'dracula', 'solarized', 'monokai', 'nord']
        scheme_var = tk.StringVar(value=self.config.get('color_scheme', 'matrix'))

        for scheme in schemes:
            tk.Radiobutton(
                scheme_frame,
                text=scheme.title(),
                variable=scheme_var,
                value=scheme,
                bg='#2b2b2b',
                fg='white',
                selectcolor='#1a1a1a'
            ).pack(anchor='w', padx=20)

        # Save button
        tk.Button(
            pref_window,
            text="Save",
            command=lambda: [
                self.config.update({'color_scheme': scheme_var.get()}),
                self.save_config(),
                pref_window.destroy()
            ],
            bg='#4a9eff',
            fg='white',
            padx=30,
            pady=10,
            bd=0,
            font=('Arial', 10)
        ).pack(pady=20)

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        # Auto-clear after 3 seconds
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    def quit(self):
        """Quit terminal"""
        # Close all tabs
        for tab in self.tabs:
            tab.close()

        self.root.destroy()

    def run(self):
        """Run the terminal"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

def main():
    terminal = ModernTerminal()
    terminal.run()

if __name__ == '__main__':
    main()
