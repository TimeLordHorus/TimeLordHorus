#!/usr/bin/env python3
"""
TL Hardware Optimization Manager
Optimize system performance and hardware acceleration

Features:
- GPU acceleration detection and configuration
- CPU governor optimization
- RAM optimization
- Storage performance tuning
- Power management
- USB optimization for portable drives
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import subprocess
import re
from pathlib import Path

class HardwareOptimizer:
    """Hardware optimization and acceleration manager"""

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("TL Hardware Optimizer ⚡")
            self.root.geometry("800x700")
        else:
            self.root = root

        self.root.configure(bg='#0d1117')

        # Detect hardware
        self.detect_hardware()

        # Setup UI
        self.setup_ui()

    def detect_hardware(self):
        """Detect available hardware"""
        self.hardware = {
            'cpu_info': self.get_cpu_info(),
            'gpu_info': self.get_gpu_info(),
            'ram_info': self.get_ram_info(),
            'storage_info': self.get_storage_info()
        }

    def get_cpu_info(self):
        """Get CPU information"""
        try:
            result = subprocess.run(['lscpu'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            cpu_info = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    cpu_info[key.strip()] = value.strip()

            return cpu_info
        except:
            return {}

    def get_gpu_info(self):
        """Get GPU information"""
        gpu_info = {'has_nvidia': False, 'has_amd': False, 'has_intel': False}

        try:
            # Check for NVIDIA
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            if 'NVIDIA' in result.stdout:
                gpu_info['has_nvidia'] = True
            if 'AMD' in result.stdout and ('VGA' in result.stdout or 'Display' in result.stdout):
                gpu_info['has_amd'] = True
            if 'Intel' in result.stdout and ('VGA' in result.stdout or 'Display' in result.stdout):
                gpu_info['has_intel'] = True

            # Get more details
            gpu_info['details'] = [line for line in result.stdout.split('\n') if 'VGA' in line or 'Display' in line]

        except:
            pass

        return gpu_info

    def get_ram_info(self):
        """Get RAM information"""
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            return result.stdout
        except:
            return "Unable to get RAM info"

    def get_storage_info(self):
        """Get storage information"""
        try:
            result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,TRAN'], capture_output=True, text=True)
            return result.stdout
        except:
            return "Unable to get storage info"

    def setup_ui(self):
        """Setup the UI"""
        # Header
        header = tk.Frame(self.root, bg='#161b22', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚡ Hardware Optimizer",
            font=('Arial', 28, 'bold'),
            bg='#161b22',
            fg='#58a6ff'
        ).pack(pady=20)

        # Tabs
        tab_container = ttk.Notebook(self.root)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style
        style = ttk.Style()
        style.configure('TNotebook', background='#0d1117')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))

        # Create tabs
        self.overview_tab = tk.Frame(tab_container, bg='#0d1117')
        self.gpu_tab = tk.Frame(tab_container, bg='#0d1117')
        self.cpu_tab = tk.Frame(tab_container, bg='#0d1117')
        self.storage_tab = tk.Frame(tab_container, bg='#0d1117')
        self.power_tab = tk.Frame(tab_container, bg='#0d1117')

        tab_container.add(self.overview_tab, text='📊 Overview')
        tab_container.add(self.gpu_tab, text='🎮 GPU')
        tab_container.add(self.cpu_tab, text='⚙️ CPU')
        tab_container.add(self.storage_tab, text='💾 Storage')
        tab_container.add(self.power_tab, text='🔋 Power')

        # Setup tabs
        self.setup_overview_tab()
        self.setup_gpu_tab()
        self.setup_cpu_tab()
        self.setup_storage_tab()
        self.setup_power_tab()

    def setup_overview_tab(self):
        """Setup system overview"""
        container = tk.Frame(self.overview_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # System info display
        info_frame = tk.LabelFrame(
            container,
            text="System Information",
            font=('Arial', 14, 'bold'),
            bg='#0d1117',
            fg='#58a6ff',
            padx=15,
            pady=15
        )
        info_frame.pack(fill=tk.BOTH, expand=True)

        self.overview_text = scrolledtext.ScrolledText(
            info_frame,
            font=('Courier', 10),
            bg='#161b22',
            fg='#c9d1d9',
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True)

        # Display system info
        self.update_overview()

        # Refresh button
        tk.Button(
            container,
            text="🔄 Refresh",
            font=('Arial', 12),
            bg='#238636',
            fg='white',
            command=self.update_overview,
            padx=20,
            pady=10
        ).pack(pady=10)

    def update_overview(self):
        """Update system overview"""
        info = []
        info.append("═" * 60)
        info.append("SYSTEM OVERVIEW")
        info.append("═" * 60)
        info.append("")

        # CPU
        info.append("CPU:")
        cpu = self.hardware['cpu_info']
        if 'Model name' in cpu:
            info.append(f"  Model: {cpu['Model name']}")
        if 'CPU(s)' in cpu:
            info.append(f"  Cores: {cpu['CPU(s)']}")
        if 'CPU MHz' in cpu:
            info.append(f"  Speed: {cpu['CPU MHz']} MHz")
        info.append("")

        # GPU
        info.append("GPU:")
        gpu = self.hardware['gpu_info']
        if gpu['has_nvidia']:
            info.append("  ✓ NVIDIA GPU detected")
        if gpu['has_amd']:
            info.append("  ✓ AMD GPU detected")
        if gpu['has_intel']:
            info.append("  ✓ Intel GPU detected")
        if not (gpu['has_nvidia'] or gpu['has_amd'] or gpu['has_intel']):
            info.append("  No discrete GPU detected")
        info.append("")

        # RAM
        info.append("RAM:")
        info.append(self.hardware['ram_info'])
        info.append("")

        # Storage
        info.append("STORAGE:")
        info.append(self.hardware['storage_info'])

        self.overview_text.delete('1.0', tk.END)
        self.overview_text.insert('1.0', '\n'.join(info))

    def setup_gpu_tab(self):
        """Setup GPU optimization"""
        container = tk.Frame(self.gpu_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="GPU Acceleration",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # GPU status
        status_frame = tk.LabelFrame(
            container,
            text="GPU Status",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        status_frame.pack(fill=tk.X, pady=10)

        gpu = self.hardware['gpu_info']

        if gpu['has_nvidia']:
            tk.Label(
                status_frame,
                text="✓ NVIDIA GPU Detected",
                font=('Arial', 12),
                bg='#0d1117',
                fg='#7ee787'
            ).pack(anchor=tk.W, pady=5)

            tk.Button(
                status_frame,
                text="Install NVIDIA Drivers",
                font=('Arial', 11),
                bg='#238636',
                fg='white',
                command=self.install_nvidia_drivers,
                padx=15,
                pady=8
            ).pack(pady=5)

        if gpu['has_amd']:
            tk.Label(
                status_frame,
                text="✓ AMD GPU Detected",
                font=('Arial', 12),
                bg='#0d1117',
                fg='#7ee787'
            ).pack(anchor=tk.W, pady=5)

            tk.Button(
                status_frame,
                text="Install AMD Drivers",
                font=('Arial', 11),
                bg='#238636',
                fg='white',
                command=self.install_amd_drivers,
                padx=15,
                pady=8
            ).pack(pady=5)

        if gpu['has_intel']:
            tk.Label(
                status_frame,
                text="✓ Intel GPU Detected",
                font=('Arial', 12),
                bg='#0d1117',
                fg='#7ee787'
            ).pack(anchor=tk.W, pady=5)

            tk.Label(
                status_frame,
                text="Intel GPU drivers are included in the kernel",
                font=('Arial', 10),
                bg='#0d1117',
                fg='#8b949e'
            ).pack(anchor=tk.W, pady=5)

        # OpenGL/Vulkan
        accel_frame = tk.LabelFrame(
            container,
            text="Graphics Acceleration",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        accel_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            accel_frame,
            text="Check OpenGL Support",
            font=('Arial', 11),
            bg='#1f6feb',
            fg='white',
            command=self.check_opengl,
            padx=15,
            pady=8
        ).pack(pady=5)

        tk.Button(
            accel_frame,
            text="Check Vulkan Support",
            font=('Arial', 11),
            bg='#1f6feb',
            fg='white',
            command=self.check_vulkan,
            padx=15,
            pady=8
        ).pack(pady=5)

    def setup_cpu_tab(self):
        """Setup CPU optimization"""
        container = tk.Frame(self.cpu_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="CPU Optimization",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # Governor selection
        governor_frame = tk.LabelFrame(
            container,
            text="CPU Governor",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        governor_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            governor_frame,
            text="Select CPU scaling governor:",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(pady=5)

        governors = [
            ("Performance", "Maximum performance, higher power usage"),
            ("Powersave", "Minimum power usage, lower performance"),
            ("Ondemand", "Dynamic scaling (recommended)"),
            ("Conservative", "Gradual scaling, balanced"),
            ("Schedutil", "Scheduler-based scaling (modern kernels)")
        ]

        for gov_name, description in governors:
            frame = tk.Frame(governor_frame, bg='#0d1117')
            frame.pack(fill=tk.X, pady=5)

            tk.Button(
                frame,
                text=f"Set {gov_name}",
                font=('Arial', 10),
                bg='#238636',
                fg='white',
                command=lambda g=gov_name.lower(): self.set_cpu_governor(g),
                width=15
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                frame,
                text=description,
                font=('Arial', 9),
                bg='#0d1117',
                fg='#8b949e'
            ).pack(side=tk.LEFT, padx=10)

    def setup_storage_tab(self):
        """Setup storage optimization"""
        container = tk.Frame(self.storage_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Storage Optimization",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # USB optimization
        usb_frame = tk.LabelFrame(
            container,
            text="USB Drive Optimization",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        usb_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            usb_frame,
            text="Optimize USB drive performance (portable OS)",
            font=('Arial', 11),
            bg='#0d1117',
            fg='white'
        ).pack(pady=5)

        tk.Button(
            usb_frame,
            text="Optimize USB Performance",
            font=('Arial', 11),
            bg='#238636',
            fg='white',
            command=self.optimize_usb,
            padx=20,
            pady=10
        ).pack(pady=10)

        # SSD optimization
        ssd_frame = tk.LabelFrame(
            container,
            text="SSD Optimization",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        ssd_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            ssd_frame,
            text="Enable TRIM",
            font=('Arial', 11),
            bg='#238636',
            fg='white',
            command=self.enable_trim,
            padx=20,
            pady=10
        ).pack(pady=5)

    def setup_power_tab(self):
        """Setup power management"""
        container = tk.Frame(self.power_tab, bg='#0d1117')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Power Management",
            font=('Arial', 20, 'bold'),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(pady=20)

        # Power profiles
        profiles_frame = tk.LabelFrame(
            container,
            text="Power Profiles",
            font=('Arial', 12, 'bold'),
            bg='#0d1117',
            fg='white',
            padx=20,
            pady=20
        )
        profiles_frame.pack(fill=tk.X, pady=10)

        profiles = [
            ("⚡ Performance", "Maximum performance", self.set_performance_mode),
            ("⚖️ Balanced", "Balanced power/performance", self.set_balanced_mode),
            ("🔋 Battery Saver", "Maximum battery life", self.set_powersave_mode)
        ]

        for name, desc, cmd in profiles:
            frame = tk.Frame(profiles_frame, bg='#0d1117')
            frame.pack(fill=tk.X, pady=10)

            tk.Button(
                frame,
                text=name,
                font=('Arial', 12),
                bg='#238636',
                fg='white',
                command=cmd,
                width=20,
                padx=10,
                pady=10
            ).pack(side=tk.LEFT, padx=10)

            tk.Label(
                frame,
                text=desc,
                font=('Arial', 10),
                bg='#0d1117',
                fg='#8b949e'
            ).pack(side=tk.LEFT)

    # Implementation methods
    def install_nvidia_drivers(self):
        """Install NVIDIA drivers"""
        messagebox.showinfo(
            "NVIDIA Drivers",
            "To install NVIDIA drivers:\n\n"
            "sudo apt install nvidia-driver\n\n"
            "Then reboot your system."
        )

    def install_amd_drivers(self):
        """Install AMD drivers"""
        messagebox.showinfo(
            "AMD Drivers",
            "AMD drivers are included in the Linux kernel.\n\n"
            "For newer GPUs, install mesa drivers:\n"
            "sudo apt install mesa-vulkan-drivers"
        )

    def check_opengl(self):
        """Check OpenGL support"""
        try:
            result = subprocess.run(['glxinfo'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract OpenGL version
                for line in result.stdout.split('\n'):
                    if 'OpenGL version' in line:
                        messagebox.showinfo("OpenGL Support", line.strip())
                        return
            messagebox.showinfo("OpenGL Support", "OpenGL supported!")
        except:
            messagebox.showwarning(
                "OpenGL",
                "glxinfo not found. Install with:\nsudo apt install mesa-utils"
            )

    def check_vulkan(self):
        """Check Vulkan support"""
        try:
            result = subprocess.run(['vulkaninfo'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                messagebox.showinfo("Vulkan Support", "Vulkan is supported!")
            else:
                messagebox.showwarning("Vulkan", "Vulkan not detected")
        except:
            messagebox.showwarning(
                "Vulkan",
                "vulkaninfo not found. Install with:\nsudo apt install vulkan-tools"
            )

    def set_cpu_governor(self, governor):
        """Set CPU governor"""
        messagebox.showinfo(
            "CPU Governor",
            f"To set {governor} governor:\n\n"
            f"echo {governor} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor\n\n"
            "This requires root privileges."
        )

    def optimize_usb(self):
        """Optimize USB drive performance"""
        tips = """USB Optimization Tips:

1. Use USB 3.0 ports and drives
2. Disable journaling on ext4:
   sudo tune2fs -O ^has_journal /dev/sdX

3. Use noatime mount option in /etc/fstab:
   /dev/sdX / ext4 defaults,noatime 0 1

4. Enable write caching:
   sudo hdparm -W1 /dev/sdX

5. Increase readahead:
   sudo blockdev --setra 8192 /dev/sdX
"""
        messagebox.showinfo("USB Optimization", tips)

    def enable_trim(self):
        """Enable TRIM for SSDs"""
        messagebox.showinfo(
            "TRIM Support",
            "To enable TRIM on SSD:\n\n"
            "1. Check if TRIM is supported:\n"
            "   sudo hdparm -I /dev/sdX | grep TRIM\n\n"
            "2. Enable fstrim timer:\n"
            "   sudo systemctl enable fstrim.timer\n"
            "   sudo systemctl start fstrim.timer"
        )

    def set_performance_mode(self):
        """Set performance mode"""
        self.set_cpu_governor('performance')
        messagebox.showinfo("Performance Mode", "Performance mode will maximize CPU speed.")

    def set_balanced_mode(self):
        """Set balanced mode"""
        self.set_cpu_governor('ondemand')
        messagebox.showinfo("Balanced Mode", "Balanced mode will dynamically adjust CPU speed.")

    def set_powersave_mode(self):
        """Set powersave mode"""
        self.set_cpu_governor('powersave')
        messagebox.showinfo("Power Save Mode", "Power save mode will minimize CPU power usage.")

    def run(self):
        """Run the optimizer"""
        self.root.mainloop()


def main():
    """Main entry point"""
    optimizer = HardwareOptimizer()
    optimizer.run()


if __name__ == '__main__':
    main()
