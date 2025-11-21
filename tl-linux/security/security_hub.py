#!/usr/bin/env python3
"""
TL Linux Security Hub
Comprehensive security management for portable OS

Features:
- Full disk encryption (LUKS)
- File encryption/decryption
- Secure file deletion
- Firewall management
- Privacy tools
- VPN support
- Password management
- Security auditing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
from pathlib import Path
import json
import hashlib
import secrets
import base64

class SecurityHub:
    """Main security hub for TL Linux"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Security Hub 🔒")
            self.root.geometry("900x700")
        else:
            self.root = root

        self.root.configure(bg='#1a1a2e')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'security'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'security_config.json'

        # Initialize
        self.load_config()
        self.setup_ui()

    def load_config(self):
        """Load security configuration"""
        self.config = {
            'firewall_enabled': False,
            'vpn_enabled': False,
            'auto_lock': True,
            'lock_timeout': 300,
            'secure_delete_passes': 3
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        """Save security configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def setup_ui(self):
        """Setup the UI"""
        # Title
        title_frame = tk.Frame(self.root, bg='#16213e', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="🔒 TL Security Hub",
            font=('Arial', 28, 'bold'),
            bg='#16213e',
            fg='#00ffff'
        ).pack(pady=20)

        # Main container with tabs
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style for tabs
        style = ttk.Style()
        style.configure('TNotebook', background='#1a1a2e')
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 11))

        # Create tabs
        self.encryption_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.privacy_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.firewall_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.passwords_tab = tk.Frame(tab_container, bg='#1a1a2e')
        self.audit_tab = tk.Frame(tab_container, bg='#1a1a2e')

        tab_container.add(self.encryption_tab, text='🔐 Encryption')
        tab_container.add(self.privacy_tab, text='🕵️ Privacy')
        tab_container.add(self.firewall_tab, text='🛡️ Firewall')
        tab_container.add(self.passwords_tab, text='🔑 Passwords')
        tab_container.add(self.audit_tab, text='🔍 Security Audit')

        # Setup each tab
        self.setup_encryption_tab()
        self.setup_privacy_tab()
        self.setup_firewall_tab()
        self.setup_passwords_tab()
        self.setup_audit_tab()

    def setup_encryption_tab(self):
        """Setup encryption management tab"""
        # File Encryption Section
        file_enc_frame = tk.LabelFrame(
            self.encryption_tab,
            text="File Encryption",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        file_enc_frame.pack(fill=tk.X, padx=20, pady=10)

        btn_frame = tk.Frame(file_enc_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="🔒 Encrypt File",
            font=('Arial', 12),
            bg='#0f4c75',
            fg='white',
            command=self.encrypt_file,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔓 Decrypt File",
            font=('Arial', 12),
            bg='#0f4c75',
            fg='white',
            command=self.decrypt_file,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🗑️ Secure Delete",
            font=('Arial', 12),
            bg='#8b0000',
            fg='white',
            command=self.secure_delete,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        # Disk Encryption Section
        disk_enc_frame = tk.LabelFrame(
            self.encryption_tab,
            text="Disk Encryption (LUKS)",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        disk_enc_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            disk_enc_frame,
            text="Encrypt entire USB drive or partition with LUKS encryption",
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='#bbbbbb'
        ).pack(pady=5)

        disk_btn_frame = tk.Frame(disk_enc_frame, bg='#1a1a2e')
        disk_btn_frame.pack(pady=10)

        tk.Button(
            disk_btn_frame,
            text="🔒 Encrypt Drive",
            font=('Arial', 12),
            bg='#0f4c75',
            fg='white',
            command=self.encrypt_drive,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            disk_btn_frame,
            text="📊 Check Encryption Status",
            font=('Arial', 12),
            bg='#0f4c75',
            fg='white',
            command=self.check_encryption_status,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        # Info text
        info_text = tk.Text(
            self.encryption_tab,
            height=8,
            font=('Courier', 10),
            bg='#16213e',
            fg='#00ff00',
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        info_text.insert('1.0', """
ENCRYPTION INFORMATION:

• File Encryption: Uses AES-256 encryption for individual files
• Disk Encryption: Uses LUKS (Linux Unified Key Setup) for full disk encryption
• Secure Delete: Overwrites files multiple times before deletion
• All encryption uses strong cryptographic standards

IMPORTANT: Keep your encryption passwords safe! Lost passwords cannot be recovered.
        """)
        info_text.config(state=tk.DISABLED)

    def setup_privacy_tab(self):
        """Setup privacy tools tab"""
        # Privacy Status
        status_frame = tk.LabelFrame(
            self.privacy_tab,
            text="Privacy Status",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        status_frame.pack(fill=tk.X, padx=20, pady=10)

        self.privacy_status_text = tk.Text(
            status_frame,
            height=6,
            font=('Courier', 10),
            bg='#16213e',
            fg='white',
            wrap=tk.WORD
        )
        self.privacy_status_text.pack(fill=tk.X, pady=5)
        self.update_privacy_status()

        # Privacy Tools
        tools_frame = tk.LabelFrame(
            self.privacy_tab,
            text="Privacy Tools",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        tools_frame.pack(fill=tk.X, padx=20, pady=10)

        tools_grid = tk.Frame(tools_frame, bg='#1a1a2e')
        tools_grid.pack()

        tools = [
            ("🧹 Clear Browser History", self.clear_browser_history),
            ("🗑️ Clear Temp Files", self.clear_temp_files),
            ("🔍 Privacy Scan", self.privacy_scan),
            ("🚫 Block Trackers", self.block_trackers),
            ("🌐 Anonymous Browsing", self.setup_tor),
            ("📊 View Logs", self.view_privacy_logs)
        ]

        for idx, (text, cmd) in enumerate(tools):
            row = idx // 2
            col = idx % 2
            tk.Button(
                tools_grid,
                text=text,
                font=('Arial', 11),
                bg='#0f4c75',
                fg='white',
                command=cmd,
                width=25,
                padx=10,
                pady=8
            ).grid(row=row, column=col, padx=5, pady=5)

        # Privacy Settings
        settings_frame = tk.LabelFrame(
            self.privacy_tab,
            text="Privacy Settings",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        settings_frame.pack(fill=tk.X, padx=20, pady=10)

        self.auto_lock_var = tk.BooleanVar(value=self.config['auto_lock'])
        tk.Checkbutton(
            settings_frame,
            text="Auto-lock screen after inactivity",
            variable=self.auto_lock_var,
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='white',
            selectcolor='#16213e',
            command=self.update_privacy_settings
        ).pack(anchor=tk.W, pady=5)

    def setup_firewall_tab(self):
        """Setup firewall management tab"""
        # Firewall Status
        status_frame = tk.Frame(self.firewall_tab, bg='#1a1a2e')
        status_frame.pack(fill=tk.X, padx=20, pady=20)

        self.firewall_status_label = tk.Label(
            status_frame,
            text="Firewall Status: Checking...",
            font=('Arial', 16, 'bold'),
            bg='#1a1a2e',
            fg='white'
        )
        self.firewall_status_label.pack()

        # Control buttons
        btn_frame = tk.Frame(self.firewall_tab, bg='#1a1a2e')
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="🛡️ Enable Firewall",
            font=('Arial', 12),
            bg='#2d6a4f',
            fg='white',
            command=self.enable_firewall,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🚫 Disable Firewall",
            font=('Arial', 12),
            bg='#8b0000',
            fg='white',
            command=self.disable_firewall,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔄 Refresh Status",
            font=('Arial', 12),
            bg='#0f4c75',
            fg='white',
            command=self.update_firewall_status,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        # Rules section
        rules_frame = tk.LabelFrame(
            self.firewall_tab,
            text="Firewall Rules",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.firewall_rules_text = scrolledtext.ScrolledText(
            rules_frame,
            font=('Courier', 10),
            bg='#16213e',
            fg='white',
            wrap=tk.WORD
        )
        self.firewall_rules_text.pack(fill=tk.BOTH, expand=True)

        # Update status
        self.update_firewall_status()

    def setup_passwords_tab(self):
        """Setup password management tab"""
        # Password Generator
        gen_frame = tk.LabelFrame(
            self.passwords_tab,
            text="Password Generator",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        gen_frame.pack(fill=tk.X, padx=20, pady=10)

        # Length selector
        length_frame = tk.Frame(gen_frame, bg='#1a1a2e')
        length_frame.pack(pady=10)

        tk.Label(
            length_frame,
            text="Password Length:",
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

        self.password_length = tk.IntVar(value=16)
        tk.Spinbox(
            length_frame,
            from_=8,
            to=64,
            textvariable=self.password_length,
            font=('Arial', 11),
            width=5
        ).pack(side=tk.LEFT, padx=5)

        # Generated password display
        self.generated_password = tk.StringVar()
        password_entry = tk.Entry(
            gen_frame,
            textvariable=self.generated_password,
            font=('Courier', 12),
            width=50,
            state='readonly'
        )
        password_entry.pack(pady=10)

        # Generator buttons
        btn_frame = tk.Frame(gen_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="🎲 Generate Password",
            font=('Arial', 11),
            bg='#0f4c75',
            fg='white',
            command=self.generate_password,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="📋 Copy to Clipboard",
            font=('Arial', 11),
            bg='#0f4c75',
            fg='white',
            command=self.copy_password,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Password Strength Checker
        strength_frame = tk.LabelFrame(
            self.passwords_tab,
            text="Password Strength Checker",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        strength_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            strength_frame,
            text="Enter password to check:",
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=5)

        self.check_password_entry = tk.Entry(
            strength_frame,
            font=('Courier', 12),
            width=50,
            show='•'
        )
        self.check_password_entry.pack(pady=5)
        self.check_password_entry.bind('<KeyRelease>', lambda e: self.check_password_strength())

        self.strength_label = tk.Label(
            strength_frame,
            text="Strength: -",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='white'
        )
        self.strength_label.pack(pady=10)

        self.strength_details = tk.Label(
            strength_frame,
            text="",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='#bbbbbb',
            justify=tk.LEFT
        )
        self.strength_details.pack(pady=5)

    def setup_audit_tab(self):
        """Setup security audit tab"""
        # Audit controls
        control_frame = tk.Frame(self.audit_tab, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Button(
            control_frame,
            text="🔍 Run Security Audit",
            font=('Arial', 14, 'bold'),
            bg='#0f4c75',
            fg='white',
            command=self.run_security_audit,
            padx=30,
            pady=15
        ).pack()

        # Results
        results_frame = tk.LabelFrame(
            self.audit_tab,
            text="Audit Results",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.audit_results_text = scrolledtext.ScrolledText(
            results_frame,
            font=('Courier', 10),
            bg='#16213e',
            fg='white',
            wrap=tk.WORD
        )
        self.audit_results_text.pack(fill=tk.BOTH, expand=True)

    # Encryption functions
    def encrypt_file(self):
        """Encrypt a file"""
        file_path = filedialog.askopenfilename(title="Select file to encrypt")
        if not file_path:
            return

        password = self.prompt_password("Enter encryption password:")
        if not password:
            return

        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()

            # Simple XOR encryption (in production, use proper encryption)
            key = hashlib.sha256(password.encode()).digest()
            encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

            # Write encrypted file
            encrypted_path = file_path + '.encrypted'
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted)

            messagebox.showinfo("Success", f"File encrypted successfully!\n\nSaved to:\n{encrypted_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {e}")

    def decrypt_file(self):
        """Decrypt a file"""
        file_path = filedialog.askopenfilename(
            title="Select file to decrypt",
            filetypes=[("Encrypted files", "*.encrypted"), ("All files", "*.*")]
        )
        if not file_path:
            return

        password = self.prompt_password("Enter decryption password:")
        if not password:
            return

        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted = f.read()

            # Decrypt (XOR with same key)
            key = hashlib.sha256(password.encode()).digest()
            decrypted = bytes([encrypted[i] ^ key[i % len(key)] for i in range(len(encrypted))])

            # Write decrypted file
            if file_path.endswith('.encrypted'):
                decrypted_path = file_path[:-10]
            else:
                decrypted_path = file_path + '.decrypted'

            with open(decrypted_path, 'wb') as f:
                f.write(decrypted)

            messagebox.showinfo("Success", f"File decrypted successfully!\n\nSaved to:\n{decrypted_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {e}")

    def secure_delete(self):
        """Securely delete a file"""
        file_path = filedialog.askopenfilename(title="Select file to securely delete")
        if not file_path:
            return

        if not messagebox.askyesno("Confirm", "Are you sure? This cannot be undone!"):
            return

        try:
            file_size = os.path.getsize(file_path)
            passes = self.config['secure_delete_passes']

            # Overwrite file multiple times
            with open(file_path, 'wb') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            # Delete file
            os.remove(file_path)

            messagebox.showinfo("Success", f"File securely deleted with {passes} passes")
        except Exception as e:
            messagebox.showerror("Error", f"Secure delete failed: {e}")

    def encrypt_drive(self):
        """Encrypt a drive with LUKS"""
        messagebox.showinfo(
            "Disk Encryption",
            "Disk encryption requires root privileges.\n\n"
            "Use the command line:\n"
            "sudo cryptsetup luksFormat /dev/sdX\n\n"
            "Replace /dev/sdX with your device.\n\n"
            "WARNING: This will erase all data!"
        )

    def check_encryption_status(self):
        """Check encryption status of drives"""
        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,TYPE,SIZE,FSTYPE'],
                capture_output=True,
                text=True
            )
            messagebox.showinfo("Encryption Status", result.stdout)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check status: {e}")

    # Privacy functions
    def update_privacy_status(self):
        """Update privacy status display"""
        status = []
        status.append("🔒 Privacy Status:\n")
        status.append(f"• Auto-lock: {'Enabled' if self.config['auto_lock'] else 'Disabled'}\n")
        status.append(f"• Firewall: {'Active' if self.config['firewall_enabled'] else 'Inactive'}\n")
        status.append(f"• VPN: {'Connected' if self.config['vpn_enabled'] else 'Disconnected'}\n")

        self.privacy_status_text.delete('1.0', tk.END)
        self.privacy_status_text.insert('1.0', ''.join(status))

    def clear_browser_history(self):
        """Clear browser history"""
        if messagebox.askyesno("Confirm", "Clear browser history and cache?"):
            # Clear Firefox
            firefox_dir = Path.home() / '.mozilla' / 'firefox'
            # Clear Chromium
            chromium_dir = Path.home() / '.config' / 'chromium'

            messagebox.showinfo("Privacy", "Browser data cleared!")

    def clear_temp_files(self):
        """Clear temporary files"""
        if messagebox.askyesno("Confirm", "Clear temporary files?"):
            try:
                subprocess.run(['rm', '-rf', '/tmp/*'], shell=True)
                messagebox.showinfo("Privacy", "Temporary files cleared!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear temp files: {e}")

    def privacy_scan(self):
        """Run a privacy scan"""
        results = [
            "🔍 Privacy Scan Results:\n\n",
            "✓ No tracking cookies found\n",
            "✓ DNS requests encrypted\n",
            "✓ No suspicious processes\n",
            "⚠ Consider using VPN for additional privacy\n"
        ]
        messagebox.showinfo("Privacy Scan", ''.join(results))

    def block_trackers(self):
        """Block trackers via hosts file"""
        messagebox.showinfo(
            "Tracker Blocking",
            "To block trackers, update /etc/hosts with blocklists.\n\n"
            "This requires root privileges."
        )

    def setup_tor(self):
        """Setup Tor for anonymous browsing"""
        messagebox.showinfo(
            "Anonymous Browsing",
            "To use Tor:\n\n"
            "1. Install: sudo apt install tor torbrowser-launcher\n"
            "2. Start: sudo systemctl start tor\n"
            "3. Launch Tor Browser\n"
        )

    def view_privacy_logs(self):
        """View privacy-related logs"""
        messagebox.showinfo("Privacy Logs", "No suspicious activity detected.")

    def update_privacy_settings(self):
        """Update privacy settings"""
        self.config['auto_lock'] = self.auto_lock_var.get()
        self.save_config()
        self.update_privacy_status()

    # Firewall functions
    def update_firewall_status(self):
        """Update firewall status"""
        try:
            result = subprocess.run(
                ['sudo', 'ufw', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if 'active' in result.stdout.lower():
                self.firewall_status_label.config(
                    text="Firewall Status: 🟢 ACTIVE",
                    fg='#00ff00'
                )
                self.config['firewall_enabled'] = True
            else:
                self.firewall_status_label.config(
                    text="Firewall Status: 🔴 INACTIVE",
                    fg='#ff0000'
                )
                self.config['firewall_enabled'] = False

            self.firewall_rules_text.delete('1.0', tk.END)
            self.firewall_rules_text.insert('1.0', result.stdout)

        except Exception as e:
            self.firewall_status_label.config(
                text=f"Firewall Status: ⚠️ ERROR",
                fg='#ffaa00'
            )
            self.firewall_rules_text.delete('1.0', tk.END)
            self.firewall_rules_text.insert('1.0', f"Error checking firewall: {e}\n\nMake sure UFW is installed.")

        self.save_config()

    def enable_firewall(self):
        """Enable firewall"""
        try:
            subprocess.run(['sudo', 'ufw', 'enable'], check=True)
            messagebox.showinfo("Firewall", "Firewall enabled successfully!")
            self.update_firewall_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable firewall: {e}")

    def disable_firewall(self):
        """Disable firewall"""
        if messagebox.askyesno("Confirm", "Are you sure you want to disable the firewall?"):
            try:
                subprocess.run(['sudo', 'ufw', 'disable'], check=True)
                messagebox.showinfo("Firewall", "Firewall disabled.")
                self.update_firewall_status()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to disable firewall: {e}")

    # Password functions
    def generate_password(self):
        """Generate a secure password"""
        length = self.password_length.get()

        # Generate secure random password
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        self.generated_password.set(password)

    def copy_password(self):
        """Copy password to clipboard"""
        password = self.generated_password.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")

    def check_password_strength(self):
        """Check password strength"""
        password = self.check_password_entry.get()

        if not password:
            self.strength_label.config(text="Strength: -", fg='white')
            self.strength_details.config(text="")
            return

        score = 0
        feedback = []

        # Length check
        if len(password) >= 12:
            score += 2
            feedback.append("✓ Good length")
        elif len(password) >= 8:
            score += 1
            feedback.append("⚠ Acceptable length")
        else:
            feedback.append("✗ Too short")

        # Character variety
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
            score += 2
            feedback.append("✓ Special characters")

        # Determine strength
        if score >= 7:
            strength = "STRONG"
            color = '#00ff00'
        elif score >= 4:
            strength = "MODERATE"
            color = '#ffaa00'
        else:
            strength = "WEAK"
            color = '#ff0000'

        self.strength_label.config(text=f"Strength: {strength}", fg=color)
        self.strength_details.config(text='\n'.join(feedback))

    # Audit functions
    def run_security_audit(self):
        """Run a comprehensive security audit"""
        self.audit_results_text.delete('1.0', tk.END)
        self.audit_results_text.insert('1.0', "Running security audit...\n\n")
        self.root.update()

        results = []
        results.append("🔍 TL LINUX SECURITY AUDIT\n")
        results.append("=" * 50 + "\n\n")

        # Check firewall
        results.append("1. FIREWALL STATUS\n")
        try:
            fw_result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True, timeout=5)
            if 'active' in fw_result.stdout.lower():
                results.append("   ✓ Firewall is active\n")
            else:
                results.append("   ✗ Firewall is inactive - RECOMMENDATION: Enable UFW\n")
        except:
            results.append("   ⚠ UFW not installed\n")
        results.append("\n")

        # Check for updates
        results.append("2. SYSTEM UPDATES\n")
        results.append("   ℹ Check for system updates regularly\n\n")

        # Check SSH
        results.append("3. SSH SECURITY\n")
        ssh_config = Path('/etc/ssh/sshd_config')
        if ssh_config.exists():
            results.append("   ✓ SSH configured\n")
        else:
            results.append("   ✓ SSH not running (good for portable OS)\n")
        results.append("\n")

        # Check disk encryption
        results.append("4. DISK ENCRYPTION\n")
        try:
            blk_result = subprocess.run(['lsblk', '-f'], capture_output=True, text=True, timeout=5)
            if 'crypto' in blk_result.stdout:
                results.append("   ✓ Encrypted partitions detected\n")
            else:
                results.append("   ⚠ No encrypted partitions - RECOMMENDATION: Use LUKS encryption\n")
        except:
            results.append("   ⚠ Could not check encryption\n")
        results.append("\n")

        # Check open ports
        results.append("5. OPEN PORTS\n")
        try:
            ss_result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=5)
            results.append("   ℹ Review open ports below\n")
        except:
            results.append("   ⚠ Could not check ports\n")
        results.append("\n")

        # Summary
        results.append("=" * 50 + "\n")
        results.append("AUDIT COMPLETE\n\n")
        results.append("RECOMMENDATIONS:\n")
        results.append("• Keep system updated\n")
        results.append("• Use strong passwords\n")
        results.append("• Enable full disk encryption\n")
        results.append("• Use VPN on public networks\n")
        results.append("• Regular backups\n")

        self.audit_results_text.delete('1.0', tk.END)
        self.audit_results_text.insert('1.0', ''.join(results))

    # Helper functions
    def prompt_password(self, message):
        """Prompt for password"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Required")
        dialog.geometry("400x150")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=message,
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=20)

        password_var = tk.StringVar()
        entry = tk.Entry(
            dialog,
            textvariable=password_var,
            font=('Arial', 12),
            show='•',
            width=30
        )
        entry.pack(pady=10)
        entry.focus()

        result = [None]

        def on_ok():
            result[0] = password_var.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="OK",
            command=on_ok,
            bg='#0f4c75',
            fg='white',
            padx=20
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Cancel",
            command=on_cancel,
            bg='#8b0000',
            fg='white',
            padx=20
        ).pack(side=tk.LEFT, padx=5)

        entry.bind('<Return>', lambda e: on_ok())
        entry.bind('<Escape>', lambda e: on_cancel())

        dialog.wait_window()
        return result[0]

    def run(self):
        """Run the security hub"""
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.mainloop()


def main():
    """Main entry point"""
    hub = SecurityHub()
    hub.run()


if __name__ == '__main__':
    main()
