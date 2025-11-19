#!/usr/bin/env python3
"""
TL Linux - Software Center
Simple GUI for managing system packages (APT)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import re

class SoftwareCenter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Linux - Software Center")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # Package lists
        self.installed_packages = []
        self.available_packages = []
        self.filtered_packages = []

        # Featured applications
        self.featured_apps = {
            "Development": [
                ("Visual Studio Code", "code", "Modern code editor"),
                ("Git", "git", "Version control system"),
                ("Python 3", "python3", "Python programming language"),
                ("Node.js", "nodejs", "JavaScript runtime"),
                ("Docker", "docker.io", "Container platform"),
            ],
            "Internet": [
                ("Firefox", "firefox-esr", "Web browser"),
                ("Chromium", "chromium", "Web browser"),
                ("Thunderbird", "thunderbird", "Email client"),
                ("FileZilla", "filezilla", "FTP client"),
                ("Transmission", "transmission-gtk", "BitTorrent client"),
            ],
            "Multimedia": [
                ("VLC", "vlc", "Media player"),
                ("GIMP", "gimp", "Image editor"),
                ("Inkscape", "inkscape", "Vector graphics editor"),
                ("Audacity", "audacity", "Audio editor"),
                ("Blender", "blender", "3D creation suite"),
            ],
            "Office": [
                ("LibreOffice", "libreoffice", "Office suite"),
                ("Thunderbird", "thunderbird", "Email client"),
                ("Evince", "evince", "PDF viewer"),
                ("Calibre", "calibre", "E-book manager"),
            ],
            "Utilities": [
                ("GParted", "gparted", "Partition editor"),
                ("BleachBit", "bleachbit", "System cleaner"),
                ("KeePassXC", "keepassxc", "Password manager"),
                ("Synaptic", "synaptic", "Advanced package manager"),
            ]
        }

        self.setup_ui()

    def setup_ui(self):
        """Create the UI"""
        # Header
        header = tk.Frame(self.root, bg='#2b2b2b', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📦 Software Center",
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # Update button
        tk.Button(
            header,
            text="🔄 Update Package List",
            command=self.update_package_list,
            bg='#50fa7b',
            fg='#000000',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=20)

        # Search bar
        search_frame = tk.Frame(self.root, bg='#1a1a1a')
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            search_frame,
            text="🔍",
            font=('Arial', 16),
            bg='#1a1a1a',
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_packages())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            font=('Arial', 12),
            bd=0
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2b2b2b', foreground='white', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])

        # Tab 1: Featured
        self.create_featured_tab()

        # Tab 2: Installed
        self.create_installed_tab()

        # Tab 3: All Packages
        self.create_all_packages_tab()

        # Tab 4: Updates
        self.create_updates_tab()

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

    def create_featured_tab(self):
        """Create featured applications tab"""
        featured_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(featured_tab, text="Featured")

        # Create scrollable frame
        canvas = tk.Canvas(featured_tab, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(featured_tab, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add categories
        for category, apps in self.featured_apps.items():
            # Category header
            tk.Label(
                scrollable_frame,
                text=category,
                font=('Arial', 13, 'bold'),
                bg='#1a1a1a',
                fg='white',
                anchor='w'
            ).pack(fill=tk.X, padx=20, pady=(20, 10))

            # Apps in category
            for app_name, package_name, description in apps:
                self.create_app_card(scrollable_frame, app_name, package_name, description)

    def create_app_card(self, parent, app_name, package_name, description):
        """Create an application card"""
        card = tk.Frame(parent, bg='#2b2b2b', relief=tk.SOLID, bd=1)
        card.pack(fill=tk.X, padx=20, pady=5)

        # App info
        info_frame = tk.Frame(card, bg='#2b2b2b')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(
            info_frame,
            text=app_name,
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='white',
            anchor='w'
        ).pack(anchor='w')

        tk.Label(
            info_frame,
            text=description,
            font=('Arial', 9),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        ).pack(anchor='w', pady=(2, 0))

        tk.Label(
            info_frame,
            text=f"Package: {package_name}",
            font=('Arial', 8),
            bg='#2b2b2b',
            fg='#666666',
            anchor='w'
        ).pack(anchor='w', pady=(2, 0))

        # Install button
        btn_frame = tk.Frame(card, bg='#2b2b2b')
        btn_frame.pack(side=tk.RIGHT, padx=15)

        # Check if installed
        is_installed = self.check_package_installed(package_name)

        if is_installed:
            tk.Button(
                btn_frame,
                text="✓ Installed",
                state=tk.DISABLED,
                bg='#50fa7b',
                fg='#000000',
                bd=0,
                padx=20,
                pady=8,
                font=('Arial', 9)
            ).pack()
        else:
            tk.Button(
                btn_frame,
                text="Install",
                command=lambda: self.install_package(package_name),
                bg='#4a9eff',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                font=('Arial', 9, 'bold')
            ).pack()

    def create_installed_tab(self):
        """Create installed packages tab"""
        installed_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(installed_tab, text="Installed")

        # List
        list_frame = tk.Frame(installed_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.installed_tree = ttk.Treeview(
            list_frame,
            columns=('Version', 'Size'),
            yscrollcommand=scrollbar.set
        )
        self.installed_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.installed_tree.yview)

        self.installed_tree.heading('#0', text='Package', anchor='w')
        self.installed_tree.heading('Version', text='Version', anchor='w')
        self.installed_tree.heading('Size', text='Size', anchor='w')

        self.installed_tree.column('#0', width=400)
        self.installed_tree.column('Version', width=150)
        self.installed_tree.column('Size', width=100)

        # Buttons
        btn_frame = tk.Frame(installed_tab, bg='#1a1a1a')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(
            btn_frame,
            text="🗑️ Remove Selected",
            command=self.remove_selected_package,
            bg='#ff5555',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔄 Refresh List",
            command=self.load_installed_packages,
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)

        # Load packages
        self.load_installed_packages()

    def create_all_packages_tab(self):
        """Create all packages tab"""
        all_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(all_tab, text="All Packages")

        tk.Label(
            all_tab,
            text="Use the search bar to find packages",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#888888'
        ).pack(pady=50)

        # Results list
        list_frame = tk.Frame(all_tab, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.all_packages_tree = ttk.Treeview(
            list_frame,
            columns=('Description',),
            yscrollcommand=scrollbar.set
        )
        self.all_packages_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.all_packages_tree.yview)

        self.all_packages_tree.heading('#0', text='Package', anchor='w')
        self.all_packages_tree.heading('Description', text='Description', anchor='w')

    def create_updates_tab(self):
        """Create updates tab"""
        updates_tab = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(updates_tab, text="Updates")

        tk.Label(
            updates_tab,
            text="System Updates",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='white'
        ).pack(pady=20)

        # Update button
        tk.Button(
            updates_tab,
            text="Check for Updates",
            command=self.check_updates,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 12, 'bold'),
            bd=0,
            padx=40,
            pady=15
        ).pack()

        # Output text
        self.update_text = scrolledtext.ScrolledText(
            updates_tab,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.update_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def check_package_installed(self, package_name):
        """Check if a package is installed"""
        try:
            result = subprocess.run(
                ['dpkg', '-l', package_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and 'ii' in result.stdout
        except:
            return False

    def load_installed_packages(self):
        """Load list of installed packages"""
        self.status_label.config(text="Loading installed packages...")

        def load():
            try:
                result = subprocess.run(
                    ['dpkg', '-l'],
                    capture_output=True,
                    text=True
                )

                packages = []
                for line in result.stdout.split('\n'):
                    if line.startswith('ii'):
                        parts = line.split()
                        if len(parts) >= 4:
                            packages.append({
                                'name': parts[1],
                                'version': parts[2],
                                'arch': parts[3]
                            })

                self.root.after(0, lambda: self.display_installed_packages(packages))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load packages:\n{str(e)}"))

        threading.Thread(target=load, daemon=True).start()

    def display_installed_packages(self, packages):
        """Display installed packages in tree"""
        self.installed_tree.delete(*self.installed_tree.get_children())

        for pkg in packages:
            self.installed_tree.insert(
                '',
                tk.END,
                text=pkg['name'],
                values=(pkg['version'], pkg.get('size', 'N/A'))
            )

        self.status_label.config(text=f"Loaded {len(packages)} installed packages")

    def install_package(self, package_name):
        """Install a package"""
        if messagebox.askyesno("Install Package", f"Install {package_name}?"):
            self.status_label.config(text=f"Installing {package_name}...")

            def install():
                try:
                    # Run apt install
                    process = subprocess.Popen(
                        ['pkexec', 'apt', 'install', '-y', package_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    stdout, stderr = process.communicate()

                    if process.returncode == 0:
                        self.root.after(0, lambda: messagebox.showinfo("Success", f"{package_name} installed successfully!"))
                        self.root.after(0, self.load_installed_packages)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to install {package_name}:\n{stderr}"))

                    self.root.after(0, lambda: self.status_label.config(text="Ready"))

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Installation error:\n{str(e)}"))

            threading.Thread(target=install, daemon=True).start()

    def remove_selected_package(self):
        """Remove selected package"""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a package to remove")
            return

        package_name = self.installed_tree.item(selection[0])['text']

        if messagebox.askyesno("Remove Package", f"Remove {package_name}?"):
            self.status_label.config(text=f"Removing {package_name}...")

            def remove():
                try:
                    process = subprocess.Popen(
                        ['pkexec', 'apt', 'remove', '-y', package_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    stdout, stderr = process.communicate()

                    if process.returncode == 0:
                        self.root.after(0, lambda: messagebox.showinfo("Success", f"{package_name} removed successfully!"))
                        self.root.after(0, self.load_installed_packages)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to remove {package_name}:\n{stderr}"))

                    self.root.after(0, lambda: self.status_label.config(text="Ready"))

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Removal error:\n{str(e)}"))

            threading.Thread(target=remove, daemon=True).start()

    def update_package_list(self):
        """Update package lists"""
        self.status_label.config(text="Updating package lists...")

        def update():
            try:
                process = subprocess.Popen(
                    ['pkexec', 'apt', 'update'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Package lists updated!"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Update failed:\n{stderr}"))

                self.root.after(0, lambda: self.status_label.config(text="Ready"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Update error:\n{str(e)}"))

        threading.Thread(target=update, daemon=True).start()

    def check_updates(self):
        """Check for system updates"""
        self.update_text.config(state=tk.NORMAL)
        self.update_text.delete('1.0', tk.END)
        self.update_text.insert('1.0', "Checking for updates...\n")
        self.update_text.config(state=tk.DISABLED)

        def check():
            try:
                # First update package lists
                subprocess.run(['pkexec', 'apt', 'update'], capture_output=True)

                # Then check for upgrades
                result = subprocess.run(
                    ['apt', 'list', '--upgradable'],
                    capture_output=True,
                    text=True
                )

                self.update_text.config(state=tk.NORMAL)
                self.update_text.delete('1.0', tk.END)
                self.update_text.insert('1.0', result.stdout)
                self.update_text.config(state=tk.DISABLED)

            except Exception as e:
                self.update_text.config(state=tk.NORMAL)
                self.update_text.insert(tk.END, f"\nError: {str(e)}")
                self.update_text.config(state=tk.DISABLED)

        threading.Thread(target=check, daemon=True).start()

    def filter_packages(self):
        """Filter packages based on search"""
        search_term = self.search_var.get().lower()

        if len(search_term) < 2:
            return

        # Search through apt cache
        self.status_label.config(text=f"Searching for: {search_term}")

        def search():
            try:
                result = subprocess.run(
                    ['apt-cache', 'search', search_term],
                    capture_output=True,
                    text=True
                )

                matches = []
                for line in result.stdout.split('\n'):
                    if ' - ' in line:
                        pkg_name, description = line.split(' - ', 1)
                        matches.append((pkg_name.strip(), description.strip()))

                self.root.after(0, lambda: self.display_search_results(matches))

            except Exception as e:
                print(f"Search error: {e}")

        threading.Thread(target=search, daemon=True).start()

    def display_search_results(self, matches):
        """Display search results"""
        self.all_packages_tree.delete(*self.all_packages_tree.get_children())

        for pkg_name, description in matches[:100]:  # Limit to 100 results
            self.all_packages_tree.insert(
                '',
                tk.END,
                text=pkg_name,
                values=(description,)
            )

        self.status_label.config(text=f"Found {len(matches)} packages")

    def run(self):
        """Run the software center"""
        self.root.mainloop()

def main():
    center = SoftwareCenter()
    center.run()

if __name__ == '__main__':
    main()
