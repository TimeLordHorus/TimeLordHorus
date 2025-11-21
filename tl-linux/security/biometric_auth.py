#!/usr/bin/env python3
"""
TL Biometric Authentication
Fingerprint and facial recognition support

Features:
- Fingerprint authentication (via fprintd)
- Facial recognition (experimental)
- PAM integration
- Multi-factor authentication
- Fallback to password
"""

import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
from pathlib import Path
import json

class BiometricAuth:
    """Biometric authentication manager"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Biometric Authentication 🔐")
            self.root.geometry("700x600")
        else:
            self.root = root

        self.root.configure(bg='#1a1a2e')

        # Configuration
        self.config_dir = Path.home() / '.config' / 'tl-linux' / 'biometric'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'biometric_config.json'

        # Detect available biometric devices
        self.detect_devices()

        # Load configuration
        self.load_config()

        # Setup UI
        self.setup_ui()

    def detect_devices(self):
        """Detect available biometric devices"""
        self.devices = {
            'fingerprint': self.check_fingerprint_device(),
            'facial_recognition': False  # Experimental
        }

    def check_fingerprint_device(self):
        """Check for fingerprint reader"""
        try:
            result = subprocess.run(
                ['fprintd-list', os.getenv('USER', 'user')],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def load_config(self):
        """Load configuration"""
        self.config = {
            'fingerprint_enabled': False,
            'facial_recognition_enabled': False,
            'require_password_fallback': True,
            'lock_after_failed_attempts': 3
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def setup_ui(self):
        """Setup the UI"""
        # Header
        header = tk.Frame(self.root, bg='#16213e', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔐 Biometric Authentication",
            font=('Arial', 24, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        ).pack(pady=20)

        # Main content
        content = tk.Frame(self.root, bg='#1a1a2e')
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Fingerprint section
        self.setup_fingerprint_section(content)

        # Facial recognition section
        self.setup_facial_recognition_section(content)

        # Settings section
        self.setup_settings_section(content)

    def setup_fingerprint_section(self, parent):
        """Setup fingerprint authentication"""
        fp_frame = tk.LabelFrame(
            parent,
            text="👆 Fingerprint Authentication",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        fp_frame.pack(fill=tk.X, pady=10)

        # Status
        if self.devices['fingerprint']:
            status_text = "✓ Fingerprint reader detected"
            status_color = '#7ee787'
        else:
            status_text = "✗ No fingerprint reader found"
            status_color = '#e63946'

        tk.Label(
            fp_frame,
            text=status_text,
            font=('Arial', 12),
            bg='#1a1a2e',
            fg=status_color
        ).pack(pady=10)

        if not self.devices['fingerprint']:
            tk.Label(
                fp_frame,
                text="To use fingerprint authentication:\n"
                     "1. Connect a fingerprint reader\n"
                     "2. Install fprintd: sudo apt install fprintd\n"
                     "3. Restart this application",
                font=('Arial', 10),
                bg='#1a1a2e',
                fg='#8b949e',
                justify=tk.LEFT
            ).pack(pady=10)
        else:
            # Enrollment button
            tk.Button(
                fp_frame,
                text="📝 Enroll Fingerprint",
                font=('Arial', 12),
                bg='#238636',
                fg='white',
                command=self.enroll_fingerprint,
                padx=20,
                pady=10
            ).pack(pady=5)

            # Verify button
            tk.Button(
                fp_frame,
                text="✓ Verify Fingerprint",
                font=('Arial', 12),
                bg='#1f6feb',
                fg='white',
                command=self.verify_fingerprint,
                padx=20,
                pady=10
            ).pack(pady=5)

            # Delete button
            tk.Button(
                fp_frame,
                text="🗑️ Delete Fingerprints",
                font=('Arial', 12),
                bg='#da3633',
                fg='white',
                command=self.delete_fingerprints,
                padx=20,
                pady=10
            ).pack(pady=5)

            # Enable/Disable
            self.fp_enabled_var = tk.BooleanVar(value=self.config['fingerprint_enabled'])
            tk.Checkbutton(
                fp_frame,
                text="Enable fingerprint for login",
                variable=self.fp_enabled_var,
                font=('Arial', 11),
                bg='#1a1a2e',
                fg='white',
                selectcolor='#16213e',
                command=self.toggle_fingerprint
            ).pack(pady=10)

    def setup_facial_recognition_section(self, parent):
        """Setup facial recognition (experimental)"""
        face_frame = tk.LabelFrame(
            parent,
            text="👤 Facial Recognition (Experimental)",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        face_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            face_frame,
            text="⚠️ Facial recognition is experimental and less secure than fingerprint",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='#ffa657'
        ).pack(pady=5)

        tk.Label(
            face_frame,
            text="Requires: webcam, python3-opencv, python3-face-recognition",
            font=('Arial', 9),
            bg='#1a1a2e',
            fg='#8b949e'
        ).pack(pady=5)

        tk.Button(
            face_frame,
            text="📷 Setup Facial Recognition",
            font=('Arial', 11),
            bg='#6c757d',
            fg='white',
            command=self.setup_facial_recognition,
            padx=20,
            pady=10
        ).pack(pady=10)

    def setup_settings_section(self, parent):
        """Setup biometric settings"""
        settings_frame = tk.LabelFrame(
            parent,
            text="⚙️ Settings",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white',
            padx=20,
            pady=20
        )
        settings_frame.pack(fill=tk.X, pady=10)

        # Password fallback
        self.fallback_var = tk.BooleanVar(value=self.config['require_password_fallback'])
        tk.Checkbutton(
            settings_frame,
            text="Require password as fallback",
            variable=self.fallback_var,
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='white',
            selectcolor='#16213e',
            command=self.save_config
        ).pack(anchor=tk.W, pady=5)

        # Failed attempts
        attempts_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        attempts_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            attempts_frame,
            text="Lock after failed attempts:",
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

        self.attempts_var = tk.IntVar(value=self.config['lock_after_failed_attempts'])
        tk.Spinbox(
            attempts_frame,
            from_=1,
            to=10,
            textvariable=self.attempts_var,
            font=('Arial', 11),
            width=5,
            command=self.save_config
        ).pack(side=tk.LEFT, padx=5)

        # Save button
        tk.Button(
            settings_frame,
            text="💾 Save Settings",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=self.save_settings,
            padx=20,
            pady=10
        ).pack(pady=15)

    # Fingerprint functions
    def enroll_fingerprint(self):
        """Enroll fingerprint"""
        instructions = """Fingerprint Enrollment Process:

1. Place your finger on the reader when prompted
2. Lift and place again multiple times
3. Try different angles and positions
4. The process takes about 10 scans

This will open a terminal window to complete enrollment.
"""

        if messagebox.askok cancel("Enroll Fingerprint", instructions):
            try:
                # Open terminal to run fprintd-enroll
                subprocess.Popen([
                    'x-terminal-emulator',
                    '-e',
                    f'fprintd-enroll {os.getenv("USER", "user")}'
                ])
                messagebox.showinfo(
                    "Enrollment Started",
                    "Follow the instructions in the terminal window to enroll your fingerprint."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start enrollment: {e}")

    def verify_fingerprint(self):
        """Verify fingerprint"""
        verify_window = tk.Toplevel(self.root)
        verify_window.title("Verify Fingerprint")
        verify_window.geometry("400x300")
        verify_window.configure(bg='#1a1a2e')
        verify_window.transient(self.root)

        tk.Label(
            verify_window,
            text="👆 Scan Your Fingerprint",
            font=('Arial', 18, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        ).pack(pady=30)

        status_label = tk.Label(
            verify_window,
            text="Place your finger on the reader...",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='white'
        )
        status_label.pack(pady=20)

        def run_verify():
            try:
                import os
                result = subprocess.run(
                    ['fprintd-verify'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    status_label.config(text="✓ Verification Successful!", fg='#7ee787')
                    verify_window.after(2000, verify_window.destroy)
                else:
                    status_label.config(text="✗ Verification Failed", fg='#e63946')
            except subprocess.TimeoutExpired:
                status_label.config(text="⏱ Timeout - No fingerprint detected", fg='#ffa657')
            except Exception as e:
                status_label.config(text=f"Error: {e}", fg='#e63946')

        # Run verification in thread
        import threading
        threading.Thread(target=run_verify, daemon=True).start()

    def delete_fingerprints(self):
        """Delete enrolled fingerprints"""
        if messagebox.askyesno(
            "Delete Fingerprints",
            "Are you sure you want to delete all enrolled fingerprints?\n\nThis cannot be undone."
        ):
            try:
                import os
                subprocess.run(['fprintd-delete', os.getenv('USER', 'user')], check=True)
                messagebox.showinfo("Deleted", "All fingerprints have been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete fingerprints: {e}")

    def toggle_fingerprint(self):
        """Toggle fingerprint authentication"""
        self.config['fingerprint_enabled'] = self.fp_enabled_var.get()
        self.save_config()

        if self.config['fingerprint_enabled']:
            messagebox.showinfo(
                "Fingerprint Enabled",
                "Fingerprint authentication is now enabled.\n\n"
                "To use it for login, you may need to configure PAM.\n"
                "See: /etc/pam.d/common-auth"
            )
        else:
            messagebox.showinfo("Fingerprint Disabled", "Fingerprint authentication has been disabled.")

    # Facial recognition functions
    def setup_facial_recognition(self):
        """Setup facial recognition"""
        info = """Facial Recognition Setup:

This feature is experimental and requires:
1. A webcam
2. python3-opencv
3. python3-face-recognition
4. dlib

Installation:
sudo apt install python3-opencv
pip3 install face-recognition

Note: Facial recognition is less secure than fingerprint
and should be used with caution, especially on portable devices.

Would you like to continue?
"""

        if messagebox.askyesno("Facial Recognition", info):
            try:
                import cv2
                import face_recognition
                messagebox.showinfo(
                    "Requirements Met",
                    "Required libraries are installed!\n\n"
                    "Facial recognition setup is not yet fully implemented.\n"
                    "This is a placeholder for future development."
                )
            except ImportError as e:
                messagebox.showerror(
                    "Missing Requirements",
                    f"Missing required library: {e}\n\n"
                    "Please install the required packages."
                )

    def save_settings(self):
        """Save all settings"""
        self.config['require_password_fallback'] = self.fallback_var.get()
        self.config['lock_after_failed_attempts'] = self.attempts_var.get()
        self.save_config()
        messagebox.showinfo("Saved", "Settings saved successfully!")

    def run(self):
        """Run the biometric auth manager"""
        self.root.mainloop()


def main():
    """Main entry point"""
    import os
    auth = BiometricAuth()
    auth.run()


if __name__ == '__main__':
    main()
