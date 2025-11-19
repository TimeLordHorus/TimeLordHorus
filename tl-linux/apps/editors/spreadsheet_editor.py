#!/usr/bin/env python3
"""
TL Linux - Spreadsheet Editor
Simple spreadsheet with formulas and CSV import/export
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from pathlib import Path

class SpreadsheetEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📊 TL Spreadsheet")
        self.root.geometry("1000x600")

        self.current_file = None
        self.rows = 50
        self.cols = 26  # A-Z

        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_spreadsheet)
        file_menu.add_command(label="Open CSV", command=self.open_csv)
        file_menu.add_command(label="Save CSV", command=self.save_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Sheet", command=self.clear_sheet)
        edit_menu.add_command(label="Clear Selection", command=self.clear_selection)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#f0f0f0', pady=5)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="📄 New", command=self.new_spreadsheet, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="📁 Open CSV", command=self.open_csv, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 Save CSV", command=self.save_csv, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        tk.Label(toolbar, text="Functions: SUM(), AVG(), MIN(), MAX(), COUNT()", bg='#f0f0f0', font=('Arial', 9)).pack(side=tk.LEFT, padx=10)

        # Spreadsheet frame
        sheet_frame = tk.Frame(self.root)
        sheet_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview for spreadsheet
        columns = [chr(65 + i) for i in range(self.cols)]  # A-Z
        self.tree = ttk.Treeview(sheet_frame, columns=columns, show='tree headings', height=20)

        # Column headings
        self.tree.heading('#0', text='#')
        self.tree.column('#0', width=40, anchor='center')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='w')

        # Add rows
        for i in range(1, self.rows + 1):
            values = [''] * self.cols
            self.tree.insert('', 'end', text=str(i), values=values)

        # Scrollbars
        vsb = ttk.Scrollbar(sheet_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(sheet_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        sheet_frame.grid_rowconfigure(0, weight=1)
        sheet_frame.grid_columnconfigure(0, weight=1)

        # Cell editor
        editor_frame = tk.Frame(self.root, bg='#f0f0f0', pady=10)
        editor_frame.pack(fill=tk.X, padx=5)

        tk.Label(editor_frame, text="Cell:", bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.cell_label = tk.Label(editor_frame, text="A1", bg='white', width=5, relief=tk.SUNKEN, anchor='w')
        self.cell_label.pack(side=tk.LEFT, padx=5)

        tk.Label(editor_frame, text="Value:", bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.cell_entry = tk.Entry(editor_frame, font=('Arial', 10), width=50)
        self.cell_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cell_entry.bind('<Return>', self.update_cell)

        tk.Button(editor_frame, text="✓ Update", command=self.update_cell, bg='#4CAF50', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_cell_select)
        self.tree.bind('<Double-1>', self.on_double_click)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_cell_select(self, event):
        """Handle cell selection"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            col = self.tree.identify_column(self.tree.winfo_pointerx() - self.tree.winfo_rootx())
            if col:
                col_index = int(col.replace('#', '')) - 1
                if col_index >= 0:
                    col_letter = chr(65 + col_index)
                    row_num = self.tree.item(item, 'text')
                    self.cell_label.config(text=f"{col_letter}{row_num}")

                    # Get current value
                    values = self.tree.item(item, 'values')
                    if values and col_index < len(values):
                        self.cell_entry.delete(0, tk.END)
                        self.cell_entry.insert(0, values[col_index])

    def on_double_click(self, event):
        """Handle double click"""
        self.cell_entry.focus()

    def update_cell(self, event=None):
        """Update selected cell"""
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        col = self.tree.identify_column(self.tree.winfo_pointerx() - self.tree.winfo_rootx())

        if col:
            col_index = int(col.replace('#', '')) - 1
            if col_index >= 0:
                values = list(self.tree.item(item, 'values'))
                new_value = self.cell_entry.get()

                # Handle formulas
                if new_value.startswith('='):
                    try:
                        result = self.evaluate_formula(new_value[1:])
                        values[col_index] = str(result)
                        self.status_bar.config(text=f"Formula evaluated: {result}")
                    except Exception as e:
                        messagebox.showerror("Formula Error", f"Invalid formula:\n{e}")
                        return
                else:
                    values[col_index] = new_value

                self.tree.item(item, values=values)

    def evaluate_formula(self, formula):
        """Evaluate simple formulas"""
        formula = formula.upper().strip()

        # Simple function evaluation
        if formula.startswith('SUM('):
            range_str = formula[4:-1]
            values = self.get_range_values(range_str)
            return sum(float(v) for v in values if v)

        elif formula.startswith('AVG('):
            range_str = formula[4:-1]
            values = [float(v) for v in self.get_range_values(range_str) if v]
            return sum(values) / len(values) if values else 0

        elif formula.startswith('MIN('):
            range_str = formula[4:-1]
            values = [float(v) for v in self.get_range_values(range_str) if v]
            return min(values) if values else 0

        elif formula.startswith('MAX('):
            range_str = formula[4:-1]
            values = [float(v) for v in self.get_range_values(range_str) if v]
            return max(values) if values else 0

        elif formula.startswith('COUNT('):
            range_str = formula[6:-1]
            values = self.get_range_values(range_str)
            return len([v for v in values if v])

        else:
            # Simple arithmetic
            return eval(formula)

    def get_range_values(self, range_str):
        """Get values from range like A1:A10"""
        if ':' in range_str:
            start, end = range_str.split(':')
            # Simple implementation for column ranges
            start_col = ord(start[0]) - 65
            start_row = int(start[1:]) - 1

            end_col = ord(end[0]) - 65
            end_row = int(end[1:]) - 1

            values = []
            for row_idx in range(start_row, end_row + 1):
                item = self.tree.get_children()[row_idx]
                row_values = self.tree.item(item, 'values')
                for col_idx in range(start_col, end_col + 1):
                    if col_idx < len(row_values) and row_values[col_idx]:
                        values.append(row_values[col_idx])

            return values
        else:
            # Single cell
            col = ord(range_str[0]) - 65
            row = int(range_str[1:]) - 1
            item = self.tree.get_children()[row]
            row_values = self.tree.item(item, 'values')
            return [row_values[col]] if col < len(row_values) else []

    def new_spreadsheet(self):
        """New spreadsheet"""
        if messagebox.askyesno("New", "Clear all data?"):
            self.clear_sheet()
            self.current_file = None
            self.status_bar.config(text="New spreadsheet")

    def clear_sheet(self):
        """Clear all data"""
        for item in self.tree.get_children():
            self.tree.item(item, values=[''] * self.cols)

    def clear_selection(self):
        """Clear selected cells"""
        selected = self.tree.selection()
        for item in selected:
            self.tree.item(item, values=[''] * self.cols)

    def open_csv(self):
        """Open CSV file"""
        file_path = filedialog.askopenfilename(
            title="Open CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)

                # Clear sheet
                self.clear_sheet()

                # Load data
                for row_idx, row_data in enumerate(rows[:self.rows]):
                    if row_idx < len(self.tree.get_children()):
                        item = self.tree.get_children()[row_idx]
                        values = row_data + [''] * (self.cols - len(row_data))
                        self.tree.item(item, values=values[:self.cols])

                self.current_file = Path(file_path)
                self.status_bar.config(text=f"Opened: {self.current_file.name}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open CSV:\n{e}")

    def save_csv(self):
        """Save as CSV"""
        file_path = filedialog.asksaveasfilename(
            title="Save CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)

                    for item in self.tree.get_children():
                        values = self.tree.item(item, 'values')
                        # Remove trailing empty cells
                        while values and not values[-1]:
                            values = values[:-1]
                        if values:  # Only write non-empty rows
                            writer.writerow(values)

                self.current_file = Path(file_path)
                self.status_bar.config(text=f"Saved: {self.current_file.name}")
                messagebox.showinfo("Saved", "CSV saved successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Could not save CSV:\n{e}")

    def run(self):
        """Run editor"""
        self.root.mainloop()

if __name__ == '__main__':
    editor = SpreadsheetEditor()
    editor.run()
