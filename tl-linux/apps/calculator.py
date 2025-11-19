#!/usr/bin/env python3
"""
TL Linux Calculator
Advanced calculator with scientific functions
"""

import tkinter as tk
from tkinter import ttk
import math

class TLCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TL Calculator")
        self.root.geometry("400x550")
        self.root.resizable(False, False)

        self.expression = ""
        self.result_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """Setup calculator UI"""
        # Display
        display_frame = tk.Frame(self.root, bg='#1a1a1a', padx=10, pady=10)
        display_frame.pack(fill=tk.BOTH)

        display = tk.Entry(
            display_frame,
            textvariable=self.result_var,
            font=('Monospace', 24),
            bg='#000000',
            fg='#00FF00',
            bd=0,
            justify=tk.RIGHT,
            state='readonly'
        )
        display.pack(fill=tk.BOTH, ipady=20)

        # Expression display
        self.expr_label = tk.Label(
            display_frame,
            text="",
            font=('Monospace', 10),
            bg='#1a1a1a',
            fg='#888888',
            anchor='e'
        )
        self.expr_label.pack(fill=tk.X, pady=(5, 0))

        # Buttons
        button_frame = tk.Frame(self.root, bg='#0a0a0a')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button layout
        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', ''],
        ]

        scientific = [
            ['sin', 'cos', 'tan', 'π'],
            ['√', 'x²', 'xʸ', 'log'],
        ]

        # Create main buttons
        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                if btn_text:
                    self.create_button(button_frame, btn_text, i, j)

        # Scientific buttons (smaller)
        sci_frame = tk.Frame(self.root, bg='#0a0a0a')
        sci_frame.pack(fill=tk.X, padx=5, pady=5)

        for i, row in enumerate(scientific):
            for j, btn_text in enumerate(row):
                self.create_sci_button(sci_frame, btn_text, i, j)

    def create_button(self, parent, text, row, col):
        """Create calculator button"""
        # Button colors
        if text in ['C', '⌫']:
            bg_color = '#FF3333'
            fg_color = '#FFFFFF'
        elif text in ['/', '*', '-', '+', '=', '%']:
            bg_color = '#FF00FF'
            fg_color = '#000000'
        else:
            bg_color = '#1a1a1a'
            fg_color = '#00FF00'

        btn = tk.Button(
            parent,
            text=text,
            font=('Sans', 16, 'bold'),
            bg=bg_color,
            fg=fg_color,
            activebackground='#333333',
            activeforeground='#FFFFFF',
            bd=0,
            command=lambda: self.on_button_click(text),
            cursor='hand2'
        )

        btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

    def create_sci_button(self, parent, text, row, col):
        """Create scientific function button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Sans', 10),
            bg='#333333',
            fg='#00FFFF',
            activebackground='#444444',
            bd=0,
            command=lambda: self.on_sci_button_click(text),
            cursor='hand2',
            width=8
        )
        btn.grid(row=row, column=col, padx=2, pady=2)

    def on_button_click(self, char):
        """Handle button click"""
        if char == 'C':
            self.expression = ""
            self.result_var.set("")
            self.expr_label.config(text="")

        elif char == '⌫':
            self.expression = self.expression[:-1]
            self.result_var.set(self.expression)

        elif char == '=':
            try:
                # Replace symbols for evaluation
                expr = self.expression.replace('×', '*').replace('÷', '/')
                result = eval(expr)
                self.expr_label.config(text=self.expression + " =")
                self.result_var.set(str(result))
                self.expression = str(result)
            except:
                self.result_var.set("Error")
                self.expression = ""

        else:
            self.expression += str(char)
            self.result_var.set(self.expression)

    def on_sci_button_click(self, func):
        """Handle scientific function button"""
        try:
            current = float(self.expression) if self.expression else 0

            if func == 'sin':
                result = math.sin(math.radians(current))
            elif func == 'cos':
                result = math.cos(math.radians(current))
            elif func == 'tan':
                result = math.tan(math.radians(current))
            elif func == 'π':
                self.expression += str(math.pi)
                self.result_var.set(self.expression)
                return
            elif func == '√':
                result = math.sqrt(current)
            elif func == 'x²':
                result = current ** 2
            elif func == 'log':
                result = math.log10(current)
            else:
                return

            self.expression = str(result)
            self.result_var.set(self.expression)

        except:
            self.result_var.set("Error")
            self.expression = ""

    def run(self):
        """Run calculator"""
        self.root.mainloop()

if __name__ == '__main__':
    calc = TLCalculator()
    calc.run()
