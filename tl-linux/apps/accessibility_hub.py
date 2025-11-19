#!/usr/bin/env python3
"""
TL Linux - Accessibility Hub
Central launcher for all accessibility tools
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from pathlib import Path

class AccessibilityHub:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("♿ TL Accessibility Hub")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')

        self.base_path = Path(__file__).parent / "accessibility"

        self.tools = [
            {
                'name': 'Screen Reader',
                'icon': '👁️',
                'description': 'Text-to-speech for visually impaired users. Read UI elements, documents, and clipboard content.',
                'script': 'screen_reader.py',
                'color': '#3498db',
                'category': 'Visual'
            },
            {
                'name': 'Voice Control',
                'icon': '🎤',
                'description': 'Control OS with voice commands. Wake word detection and natural language processing.',
                'script': 'voice_control.py',
                'color': '#9b59b6',
                'category': 'Motor'
            },
            {
                'name': 'AI Dictation Assistant',
                'icon': '🤖',
                'description': 'Intelligent voice-to-text with goal-based structured responses and learning capabilities.',
                'script': 'ai_dictation.py',
                'color': '#e74c3c',
                'category': 'Motor'
            }
        ]

        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#34495e', pady=25)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="♿ TL Accessibility Hub",
            font=('Arial', 26, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Tools to make TL Linux accessible to everyone",
            font=('Arial', 12),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(5, 0))

        # Main content
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tools grid
        tools_container = tk.Frame(main_frame, bg='#2c3e50')
        tools_container.pack(fill=tk.BOTH, expand=True)

        for idx, tool in enumerate(self.tools):
            row = idx // 2
            col = idx % 2

            card = self.create_tool_card(tools_container, tool)
            card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

        # Configure grid weights
        tools_container.grid_columnconfigure(0, weight=1)
        tools_container.grid_columnconfigure(1, weight=1)
        for i in range((len(self.tools) + 1) // 2):
            tools_container.grid_rowconfigure(i, weight=1)

        # Footer
        footer = tk.Frame(self.root, bg='#34495e', pady=15)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(
            footer,
            text="TL Linux is committed to universal accessibility • All tools are free and open source",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6'
        ).pack()

    def create_tool_card(self, parent, tool):
        """Create tool card"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=2)

        # Header with color and icon
        card_header = tk.Frame(card, bg=tool['color'], height=80)
        card_header.pack(fill=tk.X)
        card_header.pack_propagate(False)

        header_content = tk.Frame(card_header, bg=tool['color'])
        header_content.pack(expand=True)

        tk.Label(
            header_content,
            text=tool['icon'],
            font=('Arial', 36),
            bg=tool['color'],
            fg='white'
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            header_content,
            text=tool['name'],
            font=('Arial', 16, 'bold'),
            bg=tool['color'],
            fg='white'
        ).pack(side=tk.LEFT, padx=10)

        # Category badge
        tk.Label(
            card_header,
            text=tool['category'],
            font=('Arial', 8, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            padx=8,
            pady=2
        ).place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

        # Content
        content = tk.Frame(card, bg='white', padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            content,
            text=tool['description'],
            font=('Arial', 11),
            bg='white',
            fg='#2c3e50',
            wraplength=380,
            justify='left'
        ).pack(anchor='w', pady=(0, 20))

        # Launch button
        btn = tk.Button(
            content,
            text="Launch Tool",
            command=lambda t=tool: self.launch_tool(t),
            bg=tool['color'],
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        btn.pack(fill=tk.X)

        # Hover effect
        def on_enter(e):
            btn.configure(bg=self.darken_color(tool['color']))

        def on_leave(e):
            btn.configure(bg=tool['color'])

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return card

    def darken_color(self, hex_color):
        """Darken hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'

    def launch_tool(self, tool):
        """Launch accessibility tool"""
        script_path = self.base_path / tool['script']

        if not script_path.exists():
            tk.messagebox.showerror(
                "Tool Not Found",
                f"Could not find tool script:\n{script_path}\n\n"
                "Please ensure all accessibility tools are properly installed."
            )
            return

        try:
            subprocess.Popen([sys.executable, str(script_path)])
        except Exception as e:
            tk.messagebox.showerror("Launch Error", f"Could not launch tool:\n{e}")

    def run(self):
        """Run hub"""
        self.root.mainloop()

if __name__ == '__main__':
    hub = AccessibilityHub()
    hub.run()
