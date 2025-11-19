#!/usr/bin/env python3
"""
TL Linux - Data Format Editor
JSON, XML, CSV, and YAML editor with validation and formatting
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import csv
from pathlib import Path

class DataEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📊 TL Data Editor")
        self.root.geometry("1100x750")

        self.current_file = None
        self.current_format = 'json'  # json, xml, csv, yaml

        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Format/Pretty Print", command=self.format_data, accelerator="Ctrl+F")
        tools_menu.add_command(label="Validate", command=self.validate_data, accelerator="Ctrl+V")
        tools_menu.add_command(label="Minify (JSON/XML)", command=self.minify_data)
        tools_menu.add_separator()
        tools_menu.add_command(label="Convert JSON ↔ XML", command=self.convert_format)

        # Toolbar
        toolbar = tk.Frame(self.root, bg='#f0f0f0', pady=8)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="📁 Open", command=self.open_file, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 Save", command=self.save_file, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        tk.Label(toolbar, text="Format:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.format_var = tk.StringVar(value='JSON')
        format_combo = ttk.Combobox(toolbar, textvariable=self.format_var, values=['JSON', 'XML', 'CSV', 'YAML'], state='readonly', width=10)
        format_combo.pack(side=tk.LEFT, padx=5)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)

        tk.Button(toolbar, text="✨ Format", command=self.format_data, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="✓ Validate", command=self.validate_data, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🔄 Convert", command=self.convert_format, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        # Main content
        content = tk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Editor
        self.editor = scrolledtext.ScrolledText(
            content,
            wrap=tk.NONE,
            font=('Courier New', 11),
            padx=10,
            pady=10,
            undo=True
        )
        self.editor.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Keybindings
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.format_data())
        self.root.bind('<Control-v>', lambda e: self.validate_data())

        # Sample data
        self.load_sample_json()

    def load_sample_json(self):
        """Load sample JSON"""
        sample = {
            "name": "TL Linux",
            "version": "1.0.0",
            "features": ["CBT Tools", "ACT Tools", "DBT Tools", "ADHD Support", "Autism Support"],
            "config": {
                "theme": "retro",
                "autostart": True
            }
        }
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', json.dumps(sample, indent=2))
        self.status_bar.config(text="Sample JSON loaded")

    def open_file(self):
        """Open file"""
        file_path = filedialog.askopenfilename(
            title="Open Data File",
            filetypes=[
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("CSV files", "*.csv"),
                ("YAML files", "*.yaml;*.yml"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', content)
                self.current_file = Path(file_path)

                # Detect format
                if file_path.endswith('.json'):
                    self.current_format = 'json'
                    self.format_var.set('JSON')
                elif file_path.endswith('.xml'):
                    self.current_format = 'xml'
                    self.format_var.set('XML')
                elif file_path.endswith('.csv'):
                    self.current_format = 'csv'
                    self.format_var.set('CSV')
                elif file_path.endswith(('.yaml', '.yml')):
                    self.current_format = 'yaml'
                    self.format_var.set('YAML')

                self.status_bar.config(text=f"Opened: {self.current_file.name}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        """Save file"""
        if self.current_file:
            self.write_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save as"""
        file_types = {
            'json': ("JSON files", "*.json"),
            'xml': ("XML files", "*.xml"),
            'csv': ("CSV files", "*.csv"),
            'yaml': ("YAML files", "*.yaml")
        }

        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=f".{self.current_format}",
            filetypes=[file_types.get(self.current_format, ("All files", "*.*")), ("All files", "*.*")]
        )

        if file_path:
            self.write_file(Path(file_path))

    def write_file(self, file_path):
        """Write to file"""
        try:
            content = self.editor.get('1.0', tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.current_file = file_path
            self.status_bar.config(text=f"Saved: {file_path.name}")
            messagebox.showinfo("Saved", f"File saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def on_format_change(self, event=None):
        """Handle format change"""
        format_str = self.format_var.get().lower()
        self.current_format = format_str
        self.status_bar.config(text=f"Format: {format_str.upper()}")

    def format_data(self):
        """Format/pretty print data"""
        content = self.editor.get('1.0', tk.END).strip()

        try:
            if self.current_format == 'json':
                # Parse and reformat JSON
                data = json.loads(content)
                formatted = json.dumps(data, indent=2, sort_keys=False)

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', formatted)
                self.status_bar.config(text="JSON formatted successfully")

            elif self.current_format == 'xml':
                # Parse and reformat XML
                root = ET.fromstring(content)
                dom = minidom.parseString(ET.tostring(root))
                formatted = dom.toprettyxml(indent="  ")

                # Remove extra blank lines
                formatted = '\n'.join([line for line in formatted.split('\n') if line.strip()])

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', formatted)
                self.status_bar.config(text="XML formatted successfully")

            elif self.current_format == 'csv':
                # CSV formatting
                lines = content.split('\n')
                # Simple CSV validation and reformatting
                formatted_lines = []
                for line in lines:
                    if line.strip():
                        formatted_lines.append(line.strip())

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', '\n'.join(formatted_lines))
                self.status_bar.config(text="CSV formatted")

            else:
                messagebox.showinfo("Format", f"Auto-formatting not available for {self.current_format.upper()}")

        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON:\n{e}")
        except ET.ParseError as e:
            messagebox.showerror("XML Error", f"Invalid XML:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Formatting failed:\n{e}")

    def validate_data(self):
        """Validate data"""
        content = self.editor.get('1.0', tk.END).strip()

        try:
            if self.current_format == 'json':
                json.loads(content)
                messagebox.showinfo("Valid", "✓ Valid JSON!")
                self.status_bar.config(text="JSON is valid")

            elif self.current_format == 'xml':
                ET.fromstring(content)
                messagebox.showinfo("Valid", "✓ Valid XML!")
                self.status_bar.config(text="XML is valid")

            elif self.current_format == 'csv':
                lines = content.split('\n')
                reader = csv.reader(lines)
                list(reader)  # Try to parse all rows
                messagebox.showinfo("Valid", "✓ CSV appears valid!")
                self.status_bar.config(text="CSV is valid")

            else:
                messagebox.showinfo("Validation", f"Validation not available for {self.current_format.upper()}")

        except json.JSONDecodeError as e:
            messagebox.showerror("Invalid JSON", f"JSON Error:\n{e}")
        except ET.ParseError as e:
            messagebox.showerror("Invalid XML", f"XML Error:\n{e}")
        except csv.Error as e:
            messagebox.showerror("Invalid CSV", f"CSV Error:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{e}")

    def minify_data(self):
        """Minify JSON/XML"""
        content = self.editor.get('1.0', tk.END).strip()

        try:
            if self.current_format == 'json':
                data = json.loads(content)
                minified = json.dumps(data, separators=(',', ':'))

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', minified)
                self.status_bar.config(text="JSON minified")

            elif self.current_format == 'xml':
                root = ET.fromstring(content)
                minified = ET.tostring(root, encoding='unicode')

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', minified)
                self.status_bar.config(text="XML minified")

            else:
                messagebox.showinfo("Minify", f"Minify not available for {self.current_format.upper()}")

        except Exception as e:
            messagebox.showerror("Error", f"Minify failed:\n{e}")

    def convert_format(self):
        """Convert between formats"""
        content = self.editor.get('1.0', tk.END).strip()

        if self.current_format == 'json':
            # JSON to XML
            try:
                data = json.loads(content)
                root = self.dict_to_xml(data, 'root')
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                formatted = dom.toprettyxml(indent="  ")

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', formatted)
                self.current_format = 'xml'
                self.format_var.set('XML')
                self.status_bar.config(text="Converted JSON → XML")

            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed:\n{e}")

        elif self.current_format == 'xml':
            # XML to JSON
            try:
                root = ET.fromstring(content)
                data = self.xml_to_dict(root)
                json_str = json.dumps(data, indent=2)

                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', json_str)
                self.current_format = 'json'
                self.format_var.set('JSON')
                self.status_bar.config(text="Converted XML → JSON")

            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed:\n{e}")

        else:
            messagebox.showinfo("Convert", "Conversion only available between JSON and XML")

    def dict_to_xml(self, data, root_name):
        """Convert dict to XML"""
        root = ET.Element(root_name)

        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(root, key)
                if isinstance(value, (dict, list)):
                    child.extend(self.dict_to_xml(value, 'item'))
                else:
                    child.text = str(value)

        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(root, 'item')
                if isinstance(item, (dict, list)):
                    child.extend(self.dict_to_xml(item, 'item'))
                else:
                    child.text = str(item)

        return root

    def xml_to_dict(self, element):
        """Convert XML to dict"""
        result = {}

        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # No children
                return element.text.strip()
            result['text'] = element.text.strip()

        # Add children
        for child in element:
            child_data = self.xml_to_dict(child)

            if child.tag in result:
                # Multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result if result else element.text

    def run(self):
        """Run editor"""
        self.root.mainloop()

if __name__ == '__main__':
    editor = DataEditor()
    editor.run()
