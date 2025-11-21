#!/usr/bin/env python3
"""
TL Linux - Firewall Manager
Simple GUI for managing UFW (Uncomplicated Firewall)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import re
from datetime import datetime

class FirewallManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Firewall Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')

        # Firewall status
        self.firewall_enabled = False
        self.default_incoming = "deny"
        self.default_outgoing = "allow"

        # Rules
        self.rules = []

        self.setup_ui()
        self.refresh_status()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🛡️ Firewall Manager",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Status indicator
        self.status_indicator = tk.Label(
            header,
            text="● Disabled",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='#ff5555'
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=20)

        # Main toggle
        toggle_frame = tk.Frame(self.root, bg='#1a1a1a')
        toggle_frame.pack(fill=tk.X, padx=20, pady=20)

        self.toggle_btn = tk.Button(
            toggle_frame,
            text="Enable Firewall",
            command=self.toggle_firewall,
            bg='#50fa7b',
            fg='#000000',
            font=('Arial', 12, 'bold'),
            bd=0,
            padx=30,
            pady=15
        )
        self.toggle_btn.pack(side=tk.LEFT)

        tk.Button(
            toggle_frame,
            text="🔄 Refresh",
            command=self.refresh_status,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            toggle_frame,
            text="📊 View Logs",
            command=self.view_logs,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Tab 1: Rules
        self.create_rules_tab()

        # Tab 2: Applications
        self.create_applications_tab()

        # Tab 3: Advanced
        self.create_advanced_tab()

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
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)

    def create_rules_tab(self):
        """Create rules management tab"""
        rules_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(rules_tab, text="Rules")

        # Toolbar
        toolbar = tk.Frame(rules_tab, bg='#1a1a1a')
        toolbar.pack(fill=tk.X, pady=10)

        tk.Button(
            toolbar,
            text="➕ Add Rule",
            command=self.add_rule_dialog,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="✏️ Edit",
            command=self.edit_rule,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🗑️ Delete",
            command=self.delete_rule,
            bg='#ff5555',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Rules list
        list_frame = tk.Frame(rules_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.rules_tree = ttk.Treeview(
            list_frame,
            columns=('Action', 'From', 'To', 'Port', 'Protocol'),
            yscrollcommand=scrollbar.set
        )
        self.rules_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.rules_tree.yview)

        # Configure columns
        self.rules_tree.heading('#0', text='#', anchor='w')
        self.rules_tree.heading('Action', text='Action', anchor='w')
        self.rules_tree.heading('From', text='From', anchor='w')
        self.rules_tree.heading('To', text='To', anchor='w')
        self.rules_tree.heading('Port', text='Port', anchor='w')
        self.rules_tree.heading('Protocol', text='Protocol', anchor='w')

        self.rules_tree.column('#0', width=50)
        self.rules_tree.column('Action', width=100)
        self.rules_tree.column('From', width=150)
        self.rules_tree.column('To', width=150)
        self.rules_tree.column('Port', width=100)
        self.rules_tree.column('Protocol', width=100)

        # Style
        style = ttk.Style()
        style.configure('Treeview', background='#2b2b2b', foreground='white', fieldbackground='#2b2b2b')
        style.map('Treeview', background=[('selected', '#4a9eff')])

    def create_applications_tab(self):
        """Create applications presets tab"""
        apps_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(apps_tab, text="Applications")

        tk.Label(
            apps_tab,
            text="Common Application Presets",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=20)

        # Application presets
        presets = [
            ("Web Server (HTTP/HTTPS)", ["80/tcp", "443/tcp"]),
            ("SSH Server", ["22/tcp"]),
            ("FTP Server", ["21/tcp", "20/tcp"]),
            ("Mail Server (SMTP/IMAP/POP3)", ["25/tcp", "143/tcp", "110/tcp", "587/tcp", "993/tcp", "995/tcp"]),
            ("DNS Server", ["53/tcp", "53/udp"]),
            ("MySQL/MariaDB", ["3306/tcp"]),
            ("PostgreSQL", ["5432/tcp"]),
            ("Samba (File Sharing)", ["139/tcp", "445/tcp"]),
            ("Remote Desktop (RDP)", ["3389/tcp"]),
            ("VNC", ["5900/tcp"]),
        ]

        # Create buttons for presets
        preset_frame = tk.Frame(apps_tab, bg='#1a1a1a')
        preset_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        for i, (name, ports) in enumerate(presets):
            row = i // 2
            col = i % 2

            btn_frame = tk.Frame(preset_frame, bg='#2b2b2b', relief=tk.SOLID, bd=1)
            btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')

            tk.Label(
                btn_frame,
                text=name,
                bg='#2b2b2b',
                fg='white',
                font=('Arial', 10, 'bold')
            ).pack(anchor='w', padx=10, pady=(10, 5))

            tk.Label(
                btn_frame,
                text="Ports: " + ", ".join(ports),
                bg='#2b2b2b',
                fg='#888888',
                font=('Arial', 8)
            ).pack(anchor='w', padx=10)

            tk.Button(
                btn_frame,
                text="Allow",
                command=lambda p=ports: self.allow_preset(p),
                bg='#50fa7b',
                fg='#000000',
                bd=0,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=10, pady=10)

            tk.Button(
                btn_frame,
                text="Deny",
                command=lambda p=ports: self.deny_preset(p),
                bg='#ff5555',
                fg='white',
                bd=0,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, pady=10)

        preset_frame.columnconfigure(0, weight=1)
        preset_frame.columnconfigure(1, weight=1)

    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(advanced_tab, text="Advanced")

        # Default policies
        policy_frame = tk.LabelFrame(
            advanced_tab,
            text="Default Policies",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        policy_frame.pack(fill=tk.X, padx=20, pady=20)

        # Incoming
        incoming_frame = tk.Frame(policy_frame, bg='#1a1a1a')
        incoming_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            incoming_frame,
            text="Default Incoming:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        self.incoming_var = tk.StringVar(value="deny")
        for policy in ["allow", "deny", "reject"]:
            tk.Radiobutton(
                incoming_frame,
                text=policy.capitalize(),
                variable=self.incoming_var,
                value=policy,
                bg='#1a1a1a',
                fg='white',
                selectcolor='#2b2b2b',
                command=self.update_default_incoming
            ).pack(side=tk.LEFT, padx=10)

        # Outgoing
        outgoing_frame = tk.Frame(policy_frame, bg='#1a1a1a')
        outgoing_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            outgoing_frame,
            text="Default Outgoing:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        self.outgoing_var = tk.StringVar(value="allow")
        for policy in ["allow", "deny", "reject"]:
            tk.Radiobutton(
                outgoing_frame,
                text=policy.capitalize(),
                variable=self.outgoing_var,
                value=policy,
                bg='#1a1a1a',
                fg='white',
                selectcolor='#2b2b2b',
                command=self.update_default_outgoing
            ).pack(side=tk.LEFT, padx=10)

        # Logging
        logging_frame = tk.LabelFrame(
            advanced_tab,
            text="Logging",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        logging_frame.pack(fill=tk.X, padx=20, pady=20)

        log_inner = tk.Frame(logging_frame, bg='#1a1a1a')
        log_inner.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            log_inner,
            text="Logging Level:",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        self.logging_var = tk.StringVar(value="low")
        for level in ["off", "low", "medium", "high", "full"]:
            tk.Radiobutton(
                log_inner,
                text=level.capitalize(),
                variable=self.logging_var,
                value=level,
                bg='#1a1a1a',
                fg='white',
                selectcolor='#2b2b2b',
                command=self.update_logging
            ).pack(side=tk.LEFT, padx=10)

        # Quick actions
        actions_frame = tk.LabelFrame(
            advanced_tab,
            text="Quick Actions",
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        actions_frame.pack(fill=tk.X, padx=20, pady=20)

        actions_inner = tk.Frame(actions_frame, bg='#1a1a1a')
        actions_inner.pack(fill=tk.X, padx=15, pady=15)

        tk.Button(
            actions_inner,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            bg='#ffb86c',
            fg='#000000',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions_inner,
            text="Delete All Rules",
            command=self.delete_all_rules,
            bg='#ff5555',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

    def check_ufw_installed(self):
        """Check if UFW is installed"""
        try:
            subprocess.run(['which', 'ufw'], check=True, capture_output=True)
            return True
        except:
            return False

    def run_ufw_command(self, command):
        """Run a UFW command with sudo"""
        try:
            full_command = ['sudo', 'ufw'] + command
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def refresh_status(self):
        """Refresh firewall status"""
        if not self.check_ufw_installed():
            messagebox.showerror(
                "UFW Not Installed",
                "UFW (Uncomplicated Firewall) is not installed.\n\n"
                "Install with: sudo apt install ufw"
            )
            return

        # Get status
        success, stdout, stderr = self.run_ufw_command(['status', 'verbose'])

        if success:
            # Parse status
            self.firewall_enabled = 'Status: active' in stdout

            # Update UI
            if self.firewall_enabled:
                self.status_indicator.config(text="● Enabled", fg='#50fa7b')
                self.toggle_btn.config(text="Disable Firewall", bg='#ff5555', fg='white')
            else:
                self.status_indicator.config(text="● Disabled", fg='#ff5555')
                self.toggle_btn.config(text="Enable Firewall", bg='#50fa7b', fg='#000000')

            # Parse default policies
            for line in stdout.split('\n'):
                if 'Default:' in line:
                    if 'incoming' in line.lower():
                        if 'deny' in line:
                            self.incoming_var.set('deny')
                        elif 'allow' in line:
                            self.incoming_var.set('allow')
                    elif 'outgoing' in line.lower():
                        if 'allow' in line:
                            self.outgoing_var.set('allow')
                        elif 'deny' in line:
                            self.outgoing_var.set('deny')

            # Get rules
            self.refresh_rules()

            self.status_label.config(text="Status refreshed")

    def refresh_rules(self):
        """Refresh rules list"""
        # Clear tree
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)

        # Get rules
        success, stdout, stderr = self.run_ufw_command(['status', 'numbered'])

        if success:
            lines = stdout.split('\n')
            for line in lines:
                # Parse rule line (format: [ 1] 22/tcp ALLOW IN Anywhere)
                match = re.match(r'\[\s*(\d+)\]\s+(.+?)\s+(ALLOW|DENY|REJECT)\s+(IN|OUT)\s+(.+)', line)
                if match:
                    num, to, action, direction, from_addr = match.groups()

                    # Parse port/protocol
                    port_proto = to.split()
                    port = port_proto[0] if port_proto else ""

                    # Extract port and protocol
                    if '/' in port:
                        port_num, proto = port.split('/')
                    else:
                        port_num = port
                        proto = "any"

                    self.rules_tree.insert(
                        '',
                        tk.END,
                        text=num,
                        values=(action, from_addr, to, port_num, proto)
                    )

    def toggle_firewall(self):
        """Toggle firewall on/off"""
        if self.firewall_enabled:
            # Disable
            if messagebox.askyesno("Disable Firewall", "Are you sure you want to disable the firewall?\n\nThis will leave your system unprotected."):
                success, stdout, stderr = self.run_ufw_command(['disable'])
                if success:
                    self.refresh_status()
                    messagebox.showinfo("Success", "Firewall disabled")
                else:
                    messagebox.showerror("Error", f"Failed to disable firewall:\n{stderr}")
        else:
            # Enable
            success, stdout, stderr = self.run_ufw_command(['enable'])
            if success:
                self.refresh_status()
                messagebox.showinfo("Success", "Firewall enabled")
            else:
                messagebox.showerror("Error", f"Failed to enable firewall:\n{stderr}")

    def add_rule_dialog(self):
        """Show add rule dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Firewall Rule")
        dialog.geometry("500x400")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Add Firewall Rule",
            font=('Arial', 14, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)

        # Action
        action_frame = tk.Frame(dialog, bg='#2b2b2b')
        action_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(action_frame, text="Action:", bg='#2b2b2b', fg='white', width=12, anchor='w').pack(side=tk.LEFT)
        action_var = tk.StringVar(value="allow")
        for act in ["allow", "deny", "reject"]:
            tk.Radiobutton(action_frame, text=act.capitalize(), variable=action_var, value=act,
                          bg='#2b2b2b', fg='white', selectcolor='#1a1a1a').pack(side=tk.LEFT, padx=5)

        # Direction
        dir_frame = tk.Frame(dialog, bg='#2b2b2b')
        dir_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(dir_frame, text="Direction:", bg='#2b2b2b', fg='white', width=12, anchor='w').pack(side=tk.LEFT)
        dir_var = tk.StringVar(value="in")
        for d in ["in", "out"]:
            tk.Radiobutton(dir_frame, text=d.upper(), variable=dir_var, value=d,
                          bg='#2b2b2b', fg='white', selectcolor='#1a1a1a').pack(side=tk.LEFT, padx=5)

        # Port
        port_frame = tk.Frame(dialog, bg='#2b2b2b')
        port_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(port_frame, text="Port:", bg='#2b2b2b', fg='white', width=12, anchor='w').pack(side=tk.LEFT)
        port_entry = tk.Entry(port_frame, bg='#1a1a1a', fg='white', insertbackground='white')
        port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Protocol
        proto_frame = tk.Frame(dialog, bg='#2b2b2b')
        proto_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(proto_frame, text="Protocol:", bg='#2b2b2b', fg='white', width=12, anchor='w').pack(side=tk.LEFT)
        proto_var = tk.StringVar(value="tcp")
        tk.Radiobutton(proto_frame, text="TCP", variable=proto_var, value="tcp",
                      bg='#2b2b2b', fg='white', selectcolor='#1a1a1a').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(proto_frame, text="UDP", variable=proto_var, value="udp",
                      bg='#2b2b2b', fg='white', selectcolor='#1a1a1a').pack(side=tk.LEFT, padx=5)

        # From address (optional)
        from_frame = tk.Frame(dialog, bg='#2b2b2b')
        from_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(from_frame, text="From (optional):", bg='#2b2b2b', fg='white', width=12, anchor='w').pack(side=tk.LEFT)
        from_entry = tk.Entry(from_frame, bg='#1a1a1a', fg='white', insertbackground='white')
        from_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        from_entry.insert(0, "any")

        # Add button
        def add_rule():
            port = port_entry.get()
            if not port:
                messagebox.showwarning("Missing Port", "Please specify a port number")
                return

            # Build command
            cmd = [action_var.get(), dir_var.get()]

            if from_entry.get() and from_entry.get() != "any":
                cmd.extend(['from', from_entry.get()])

            cmd.extend(['to', 'any', 'port', port, 'proto', proto_var.get()])

            success, stdout, stderr = self.run_ufw_command(cmd)
            if success:
                dialog.destroy()
                self.refresh_rules()
                messagebox.showinfo("Success", "Rule added successfully")
            else:
                messagebox.showerror("Error", f"Failed to add rule:\n{stderr}")

        tk.Button(
            dialog,
            text="Add Rule",
            command=add_rule,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=10
        ).pack(pady=20)

    def edit_rule(self):
        """Edit selected rule"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a rule to edit")
            return

        messagebox.showinfo("Edit Rule", "To edit a rule:\n1. Delete the old rule\n2. Add a new rule with updated settings")

    def delete_rule(self):
        """Delete selected rule"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a rule to delete")
            return

        item = selection[0]
        rule_num = self.rules_tree.item(item)['text']

        if messagebox.askyesno("Delete Rule", f"Delete rule #{rule_num}?"):
            success, stdout, stderr = self.run_ufw_command(['delete', rule_num])
            if success:
                self.refresh_rules()
                messagebox.showinfo("Success", "Rule deleted")
            else:
                messagebox.showerror("Error", f"Failed to delete rule:\n{stderr}")

    def allow_preset(self, ports):
        """Allow preset ports"""
        for port in ports:
            self.run_ufw_command(['allow', port])

        self.refresh_rules()
        messagebox.showinfo("Success", f"Added allow rules for {len(ports)} ports")

    def deny_preset(self, ports):
        """Deny preset ports"""
        for port in ports:
            self.run_ufw_command(['deny', port])

        self.refresh_rules()
        messagebox.showinfo("Success", f"Added deny rules for {len(ports)} ports")

    def update_default_incoming(self):
        """Update default incoming policy"""
        policy = self.incoming_var.get()
        success, stdout, stderr = self.run_ufw_command(['default', policy, 'incoming'])
        if success:
            self.status_label.config(text=f"Default incoming policy set to {policy}")
        else:
            messagebox.showerror("Error", f"Failed to update policy:\n{stderr}")

    def update_default_outgoing(self):
        """Update default outgoing policy"""
        policy = self.outgoing_var.get()
        success, stdout, stderr = self.run_ufw_command(['default', policy, 'outgoing'])
        if success:
            self.status_label.config(text=f"Default outgoing policy set to {policy}")
        else:
            messagebox.showerror("Error", f"Failed to update policy:\n{stderr}")

    def update_logging(self):
        """Update logging level"""
        level = self.logging_var.get()
        success, stdout, stderr = self.run_ufw_command(['logging', level])
        if success:
            self.status_label.config(text=f"Logging set to {level}")
        else:
            messagebox.showerror("Error", f"Failed to update logging:\n{stderr}")

    def reset_to_defaults(self):
        """Reset firewall to defaults"""
        if messagebox.askyesno("Reset Firewall", "Reset firewall to default settings?\n\nThis will delete all rules."):
            self.run_ufw_command(['--force', 'reset'])
            self.refresh_status()
            messagebox.showinfo("Success", "Firewall reset to defaults")

    def delete_all_rules(self):
        """Delete all firewall rules"""
        if messagebox.askyesno("Delete All Rules", "Delete ALL firewall rules?\n\nDefault policies will remain."):
            # Get all rule numbers
            success, stdout, stderr = self.run_ufw_command(['status', 'numbered'])
            if success:
                # Extract rule numbers
                nums = []
                for line in stdout.split('\n'):
                    match = re.match(r'\[\s*(\d+)\]', line)
                    if match:
                        nums.append(match.group(1))

                # Delete in reverse order (highest first)
                for num in reversed(nums):
                    self.run_ufw_command(['delete', num])

                self.refresh_rules()
                messagebox.showinfo("Success", f"Deleted {len(nums)} rules")

    def view_logs(self):
        """View firewall logs"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Firewall Logs")
        log_window.geometry("800x600")
        log_window.configure(bg='#1a1a1a')

        # Text widget
        text = tk.Text(
            log_window,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier', 9),
            wrap=tk.WORD
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = tk.Scrollbar(text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)

        # Load logs
        try:
            result = subprocess.run(
                ['sudo', 'grep', 'UFW', '/var/log/syslog'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                text.insert('1.0', result.stdout)
            else:
                text.insert('1.0', "No UFW logs found or insufficient permissions")
        except Exception as e:
            text.insert('1.0', f"Error loading logs: {e}")

        text.config(state=tk.DISABLED)

    def run(self):
        """Run the firewall manager"""
        self.root.mainloop()

def main():
    manager = FirewallManager()
    manager.run()

if __name__ == '__main__':
    main()
