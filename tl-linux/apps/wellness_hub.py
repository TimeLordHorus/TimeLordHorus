#!/usr/bin/env python3
"""
TL Linux - Wellness Hub
Central launcher for all therapeutic and support tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from pathlib import Path

class WellnessHub:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌟 TL Wellness Hub")
        self.root.geometry("900x700")
        self.root.configure(bg='#f5f5f5')

        self.apps_dir = Path(__file__).parent / 'wellness'

        self.setup_ui()

    def setup_ui(self):
        """Setup main UI"""
        # Header
        header = tk.Frame(self.root, bg='#673AB7', pady=25)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🌟 TL Wellness Hub",
            font=('Arial', 24, 'bold'),
            bg='#673AB7',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Mental Health & Neurodiversity Support Tools",
            font=('Arial', 12),
            bg='#673AB7',
            fg='white'
        ).pack(pady=(5, 0))

        # Main content area
        content = tk.Frame(self.root, bg='#f5f5f5')
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Therapeutic Tools Section
        tk.Label(
            content,
            text="🧠 Therapeutic Tools",
            font=('Arial', 16, 'bold'),
            bg='#f5f5f5',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 15))

        therapeutic_frame = tk.Frame(content, bg='#f5f5f5')
        therapeutic_frame.pack(fill=tk.X, pady=(0, 30))

        therapeutic_tools = [
            {
                'name': 'CBT Tools',
                'emoji': '🧠',
                'desc': 'Cognitive Behavioral Therapy\nThought records, mood tracking, cognitive distortions',
                'color': '#4A90E2',
                'script': 'cbt_tools.py'
            },
            {
                'name': 'ACT Tools',
                'emoji': '🌱',
                'desc': 'Acceptance & Commitment Therapy\nMindfulness, values, committed action',
                'color': '#66BB6A',
                'script': 'act_tools.py'
            },
            {
                'name': 'DBT Tools',
                'emoji': '⚖️',
                'desc': 'Dialectical Behavior Therapy\nEmotion regulation, distress tolerance, interpersonal skills',
                'color': '#9C27B0',
                'script': 'dbt_tools.py'
            }
        ]

        for i, tool in enumerate(therapeutic_tools):
            self.create_tool_card(therapeutic_frame, tool, row=0, col=i)

        # Neurodiversity Support Section
        tk.Label(
            content,
            text="🧩 Neurodiversity Support",
            font=('Arial', 16, 'bold'),
            bg='#f5f5f5',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(20, 15))

        neuro_frame = tk.Frame(content, bg='#f5f5f5')
        neuro_frame.pack(fill=tk.X, pady=(0, 30))

        neuro_tools = [
            {
                'name': 'ADHD Support',
                'emoji': '🎯',
                'desc': 'ADHD-specific tools\nFocus timer, task breakdown, routines, rewards',
                'color': '#FF9800',
                'script': 'adhd_support.py'
            },
            {
                'name': 'Autism Support',
                'emoji': '🧩',
                'desc': 'Autism-specific tools\nSocial scripts, sensory tracking, communication',
                'color': '#2196F3',
                'script': 'autism_support.py'
            }
        ]

        for i, tool in enumerate(neuro_tools):
            self.create_tool_card(neuro_frame, tool, row=0, col=i)

        # Info section
        info_frame = tk.Frame(self.root, bg='#E8EAF6', relief=tk.SOLID, borderwidth=1)
        info_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        info_text = """
        💜 About These Tools

        These evidence-based therapeutic tools are designed to support mental health and
        neurodivergent individuals. They complement (but don't replace) professional help.

        • CBT: Identify and change unhelpful thinking patterns
        • ACT: Live according to your values with psychological flexibility
        • DBT: Regulate emotions and improve relationships
        • ADHD: Executive function support and focus strategies
        • Autism: Social, sensory, and communication support

        All data is stored locally and privately on your device.
        """

        tk.Label(
            info_frame,
            text=info_text,
            font=('Arial', 9),
            bg='#E8EAF6',
            fg='#2c3e50',
            justify=tk.LEFT
        ).pack(padx=20, pady=15, anchor='w')

        # Bottom buttons
        bottom_frame = tk.Frame(self.root, bg='#f5f5f5')
        bottom_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        tk.Button(
            bottom_frame,
            text="ℹ️ About Mental Health Support",
            command=self.show_about,
            bg='#9E9E9E',
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT)

        tk.Button(
            bottom_frame,
            text="📞 Crisis Resources",
            command=self.show_crisis_resources,
            bg='#F44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.RIGHT)

    def create_tool_card(self, parent, tool, row, col):
        """Create a tool card"""
        card = tk.Frame(
            parent,
            bg='white',
            relief=tk.RAISED,
            borderwidth=2
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)

        # Header with emoji and color
        header = tk.Frame(card, bg=tool['color'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=tool['emoji'],
            font=('Arial', 36),
            bg=tool['color']
        ).pack(expand=True)

        # Tool name
        tk.Label(
            card,
            text=tool['name'],
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(15, 5))

        # Description
        tk.Label(
            card,
            text=tool['desc'],
            font=('Arial', 9),
            bg='white',
            fg='#666',
            justify=tk.CENTER,
            wraplength=200
        ).pack(pady=(0, 15), padx=15)

        # Launch button
        btn = tk.Button(
            card,
            text="Launch",
            command=lambda: self.launch_tool(tool['script']),
            bg=tool['color'],
            fg='white',
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2'
        )
        btn.pack(pady=(0, 15))

    def launch_tool(self, script_name):
        """Launch a therapeutic tool"""
        script_path = self.apps_dir / script_name

        if script_path.exists():
            try:
                subprocess.Popen([sys.executable, str(script_path)])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch tool:\n{e}")
        else:
            messagebox.showerror("Error", f"Tool not found:\n{script_path}")

    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About TL Wellness Hub")
        about_window.geometry("600x500")
        about_window.configure(bg='white')

        tk.Label(
            about_window,
            text="🌟 TL Wellness Hub",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#673AB7'
        ).pack(pady=20)

        about_text = """
        Evidence-Based Mental Health Tools

        These tools are based on established therapeutic approaches:

        CBT (Cognitive Behavioral Therapy)
        • Developed in the 1960s by Aaron Beck
        • Focuses on identifying and changing unhelpful thoughts
        • Effective for anxiety, depression, and many other conditions

        ACT (Acceptance & Commitment Therapy)
        • Developed by Steven Hayes in the 1980s
        • Focuses on psychological flexibility and values-based living
        • Emphasizes mindfulness and acceptance

        DBT (Dialectical Behavior Therapy)
        • Developed by Marsha Linehan in the 1990s
        • Originally for borderline personality disorder
        • Now used for emotion regulation challenges
        • Combines mindfulness, distress tolerance, emotion regulation,
          and interpersonal effectiveness

        ADHD & Autism Support
        • Based on neurodiversity-affirming approaches
        • Focuses on accommodation and support, not "fixing"
        • Recognizes neurodivergence as natural variation
        • Emphasizes self-advocacy and understanding

        Important Notes:
        • These tools complement professional help
        • They don't replace therapy or medication
        • If you're in crisis, please seek immediate help
        • All data is stored locally and privately

        Your mental health and wellbeing matter.
        You deserve support and care.
        """

        text_widget = tk.Text(
            about_window,
            font=('Arial', 10),
            wrap=tk.WORD,
            padx=20,
            pady=10
        )
        text_widget.insert('1.0', about_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def show_crisis_resources(self):
        """Show crisis resources"""
        crisis_window = tk.Toplevel(self.root)
        crisis_window.title("Crisis Resources")
        crisis_window.geometry("600x500")
        crisis_window.configure(bg='#FFEBEE')

        tk.Label(
            crisis_window,
            text="📞 Crisis Resources",
            font=('Arial', 18, 'bold'),
            bg='#FFEBEE',
            fg='#C62828'
        ).pack(pady=20)

        tk.Label(
            crisis_window,
            text="If you're in crisis, please reach out for help immediately.",
            font=('Arial', 12),
            bg='#FFEBEE',
            fg='#C62828'
        ).pack(pady=(0, 20))

        resources_text = """
        🆘 IMMEDIATE CRISIS HELP

        United States:
        • National Suicide Prevention Lifeline: 988
        • Crisis Text Line: Text HOME to 741741
        • SAMHSA National Helpline: 1-800-662-4357

        International:
        • International Association for Suicide Prevention:
          https://www.iasp.info/resources/Crisis_Centres/

        • Befrienders Worldwide:
          https://www.befrienders.org/


        📱 SPECIALIZED SUPPORT

        • Trevor Project (LGBTQ+ Youth): 1-866-488-7386
          Text START to 678678

        • Trans Lifeline: 1-877-565-8860

        • Veterans Crisis Line: 988 then press 1
          Text 838255

        • RAINN Sexual Assault Hotline: 1-800-656-4673

        • Domestic Violence Hotline: 1-800-799-7233


        🏥 WHEN TO SEEK EMERGENCY HELP

        Go to emergency room or call 911 if:
        • You have a plan to harm yourself or others
        • You've taken steps toward self-harm
        • You're hearing voices telling you to harm yourself
        • You feel you can't keep yourself safe


        💜 YOU MATTER

        Your life has value.
        This pain is temporary.
        Help is available.
        You are not alone.
        """

        text_widget = tk.Text(
            crisis_window,
            font=('Arial', 10),
            wrap=tk.WORD,
            padx=20,
            pady=10,
            bg='#FFEBEE'
        )
        text_widget.insert('1.0', resources_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def run(self):
        """Run the wellness hub"""
        self.root.mainloop()

if __name__ == '__main__':
    hub = WellnessHub()
    hub.run()
