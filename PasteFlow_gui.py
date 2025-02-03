# folder_analyzer_gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PasteFlow_core import FolderAnalyzer
import os
import pyperclip  # For clipboard operations

class FolderAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PasteFlow - Folder Analysis Tool")
        self.root.geometry("800x600")
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Folder selection section
        self.folder_frame = ttk.LabelFrame(self.main_frame, text="Select Folder", padding="5")
        self.folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_path)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        self.browse_button = ttk.Button(self.folder_frame, text="Browse...", command=self.browse_folder)
        self.browse_button.grid(row=0, column=1, padx=5)

        # File selection tree
        self.tree_frame = ttk.LabelFrame(self.main_frame, text="Target Files for Analysis", padding="5")
        self.tree_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Button frame
        self.button_frame = ttk.Frame(self.tree_frame)
        self.button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        self.select_all_button = ttk.Button(
            self.button_frame,
            text="Select All",
            command=lambda: self.toggle_all_files(True)
        )
        self.select_all_button.grid(row=0, column=0, padx=2)
        
        self.deselect_all_button = ttk.Button(
            self.button_frame,
            text="Deselect All",
            command=lambda: self.toggle_all_files(False)
        )
        self.deselect_all_button.grid(row=0, column=1, padx=2)

        # File tree
        self.tree = ttk.Treeview(self.tree_frame, height=20, selectmode="extended")
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Tree scrollbar
        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Tree column settings
        self.tree["columns"] = ("select",)
        self.tree.column("#0", width=400, stretch=tk.YES)  # For file path
        self.tree.column("select", width=50, anchor=tk.CENTER)  # For checkbox
        
        self.tree.heading("#0", text="File Path")
        self.tree.heading("select", text="Select")

        # Dictionary to store file selection states
        self.file_selections = {}

        # Other options
        self.option_frame = ttk.LabelFrame(self.main_frame, text="Options", padding="5")
        self.option_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.show_content = tk.BooleanVar(value=True)
        self.content_check = ttk.Checkbutton(
            self.option_frame, 
            text="Show File Contents",
            variable=self.show_content
        )
        self.content_check.grid(row=0, column=0, padx=5)
        
        # Analyze button
        self.analyze_button = ttk.Button(
            self.main_frame,
            text="Analyze Folder and Copy to Clipboard",
            command=self.analyze_folder
        )
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode='determinate',
            length=300
        )
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.folder_frame.columnconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(1, weight=1)

        # Set up tree click events
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_release)
        self.tree.bind('<space>', self.on_space_key)  # Bind space key
        self.clicked_item = None  # Track clicked item

        # Bind Enter key
        self.root.bind('<Return>', self.analyze_folder)

    def browse_folder(self):
        """Display folder selection dialog"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path.set(folder_path)
            self.update_file_tree()

    def update_file_tree(self):
        """Update file tree"""
        # Clear tree
        self.tree.delete(*self.tree.get_children())
        self.file_selections.clear()

        folder_path = self.folder_path.get()
        if not folder_path:
            return

        # Default exclusion patterns
        default_ignore = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "node_modules",
            "dist",
            "build"
        }

        try:
            # Add folder structure recursively
            for root_dir, dirs, files in os.walk(folder_path):
                # Skip excluded folders
                dirs[:] = [d for d in dirs if d not in default_ignore]
                
                # Get relative path from root folder
                rel_path = os.path.relpath(root_dir, folder_path)
                if rel_path == ".":
                    rel_path = ""

                # Add folder to tree
                if rel_path:
                    folder_parts = rel_path.split(os.sep)
                    parent = ""
                    for i, part in enumerate(folder_parts):
                        current_path = os.sep.join(folder_parts[:i+1])
                        parent_path = os.sep.join(folder_parts[:i]) if i > 0 else ""
                        if not self.tree.exists(current_path):
                            self.tree.insert(parent_path, 'end', current_path, text=part, values=(""))

                # Add files
                parent_path = rel_path if rel_path else ""
                for file in sorted(files):
                    if any(ignore in file for ignore in default_ignore):
                        continue
                    file_path = os.sep.join([rel_path, file]) if rel_path else file
                    self.file_selections[file_path] = tk.BooleanVar(value=True)
                    self.tree.insert(parent_path, 'end', file_path, text=file, 
                                   values=("☑" if self.file_selections[file_path].get() else "☐"))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating the file tree:\n{str(e)}")

    def on_tree_click(self, event):
        """Handle click start event"""
        x, y = event.x, event.y
        self.clicked_item = None

        # Identify clicked location
        item = self.tree.identify('item', x, y)
        column = self.tree.identify_column(x)
        
        if item and item in self.file_selections and column == "#1":
            self.clicked_item = item

    def on_tree_release(self, event):
        """Handle click release event"""
        if not self.clicked_item:
            return

        x, y = event.x, event.y
        item = self.tree.identify('item', x, y)
        column = self.tree.identify_column(x)
        
        # Process only if released on same item and column
        if item == self.clicked_item and column == "#1":
            current_state = self.file_selections[item].get()
            self.file_selections[item].set(not current_state)
            self.tree.set(item, "select", "☑" if not current_state else "☐")

    def on_tree_double_click(self, event):
        """Handle double click event"""
        x, y = event.x, event.y
        item = self.tree.identify('item', x, y)
        column = self.tree.identify_column(x)
        
        if item and item in self.file_selections and column == "#1":
            current_state = self.file_selections[item].get()
            self.file_selections[item].set(not current_state)
            self.tree.set(item, "select", "☑" if not current_state else "☐")

    def on_space_key(self, event):
        """Toggle checkbox of selected items when space key is pressed"""
        selected_items = self.tree.selection()
        for item in selected_items:
            if item in self.file_selections:
                current_state = self.file_selections[item].get()
                self.file_selections[item].set(not current_state)
                self.tree.set(item, "select", "☑" if not current_state else "☐")
        return "break"  # Cancel default space key behavior

    def analyze_folder(self, event=None):
        """Execute folder analysis"""
        folder_path = self.folder_path.get()
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder")
            return

        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showerror("Error", "Please select files for analysis")
            return

        # Update UI
        self.analyze_button.state(['disabled'])
        self.progress["value"] = 0

        # Run analysis in separate thread
        thread = threading.Thread(target=self._analyze_thread, args=(selected_files,))
        thread.start()

    def _analyze_thread(self, selected_files):
        """Run analysis process in separate thread"""
        try:
            analyzer = FolderAnalyzer(self.folder_path.get(), selected_files)
            stats = analyzer.analyze()
            
            # Update progress bar (100% complete)
            self.root.after(0, self._update_progress, 100)
            
            # Generate report
            report = analyzer.generate_report(show_content=self.show_content.get())
            
            # Copy to clipboard
            self.root.after(0, self._copy_to_clipboard, report)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._cleanup)

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress["value"] = value

    def _copy_to_clipboard(self, text):
        """Copy results to clipboard"""
        pyperclip.copy(text)
        messagebox.showinfo("Success", "Analysis results copied to clipboard")

    def _show_error(self, error_msg):
        """Display error message"""
        messagebox.showerror("Error", f"An error occurred during analysis:\n{error_msg}")

    def _cleanup(self):
        """Restore UI elements"""
        self.analyze_button.state(['!disabled'])
        self.progress["value"] = 0

    def toggle_all_files(self, state: bool):
        """Toggle selection state of all files"""
        for file_path, var in self.file_selections.items():
            var.set(state)
            self.tree.set(file_path, "select", "☑" if state else "☐")

    def get_selected_files(self):
        """Get paths of selected files"""
        return [path for path, var in self.file_selections.items() if var.get()]

def main():
    root = tk.Tk()
    app = FolderAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
