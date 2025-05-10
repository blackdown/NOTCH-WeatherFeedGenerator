"""
Settings tab functionality for NOTCH Data Tool
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import webbrowser

class SettingsTab:
    def __init__(self, app):
        """Initialize the Settings tab with the main application reference"""
        self.app = app
        self.tab = app.settings_content  # Use the scrollable content area instead of the direct frame
        
        # Create the Settings Tab UI
        self.create_settings_tab()
        
    def create_settings_tab(self):
        """Create the settings tab UI"""
        # API Settings Section
        api_frame = ttk.LabelFrame(self.tab, text="API Settings")
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="Enter your OpenWeatherMap API Key:").pack(anchor="w", pady=(10, 5), padx=10)
        
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.api_key_entry = ttk.Entry(api_key_frame, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.app.api_key:
            self.api_key_entry.insert(0, self.app.api_key)
        
        self.show_key_btn = ttk.Button(api_key_frame, text="Show", width=5, command=self.toggle_api_key_visibility)
        self.show_key_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save API key button
        save_api_frame = ttk.Frame(api_frame)
        save_api_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.save_api_btn = ttk.Button(save_api_frame, text="Save API Key", command=self.save_api_key, width=15)
        self.save_api_btn.pack(side=tk.RIGHT)
        
        # Get API key info
        ttk.Label(api_frame, text="Don't have an API key?").pack(anchor="w", pady=(5, 2), padx=10)
        
        api_link = ttk.Label(
            api_frame,
            text="Get one for free at OpenWeatherMap.org",
            foreground="blue",
            cursor="hand2"
        )
        api_link.pack(anchor="w", padx=10, pady=(0, 10))
        api_link.bind("<Button-1>", lambda e: webbrowser.open("https://openweathermap.org/api"))
        
        # Update Interval Section
        interval_frame = ttk.LabelFrame(self.tab, text="Update Interval")
        interval_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(interval_frame, text="Set how often to fetch new weather data:").pack(anchor="w", pady=(10, 5), padx=10)
        
        interval_setting_frame = ttk.Frame(interval_frame)
        interval_setting_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        current_interval = self.app.update_interval // 60  # Convert to minutes
        
        self.interval_var = tk.IntVar(value=current_interval)
        interval_scale = ttk.Scale(
            interval_setting_frame, 
            from_=1, 
            to=60, 
            variable=self.interval_var,
            orient="horizontal",
            command=self.update_interval_display
        )
        interval_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.interval_display = ttk.Label(interval_setting_frame, text=f"{current_interval} min")
        self.interval_display.pack(side=tk.LEFT, padx=(10, 0))
        
        self.save_interval_btn = ttk.Button(interval_frame, text="Save Interval", command=self.save_interval, width=15)
        self.save_interval_btn.pack(side=tk.RIGHT, padx=10, pady=(0, 10))
        
        # File Settings Section
        file_frame = ttk.LabelFrame(self.tab, text="Data File Settings")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Choose where to save weather data:").pack(anchor="w", pady=(10, 5), padx=10)
        
        # File location info
        file_info_frame = ttk.Frame(file_frame)
        file_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_path_label = ttk.Label(file_info_frame, text=os.path.abspath(self.app.weather_file), style="Path.TLabel")
        self.file_path_label.pack(fill=tk.X, expand=True, anchor="w", pady=5)
        
        # Migration option
        migration_frame = ttk.Frame(file_frame)
        migration_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.migrate_var = tk.BooleanVar(value=True)
        migrate_check = ttk.Checkbutton(
            migration_frame, 
            text="Copy existing data to the new file location", 
            variable=self.migrate_var
        )
        migrate_check.pack(side=tk.LEFT)
        
        # Save file settings button
        file_buttons_frame = ttk.Frame(file_frame)
        file_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        browse_btn = ttk.Button(file_buttons_frame, text="Browse...", command=self.browse_file, width=10)
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_file_btn = ttk.Button(file_buttons_frame, text="Save", command=self.save_file_settings, width=10)
        self.save_file_btn.pack(side=tk.LEFT)

    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_entry['show'] == '*':
            self.api_key_entry.config(show="")
            self.show_key_btn.config(text="Hide")
        else:
            self.api_key_entry.config(show="*")
            self.show_key_btn.config(text="Show")

    def update_interval_display(self, value):
        """Update the interval display when the scale is moved"""
        # Round to integer
        minutes = int(float(value))
        if minutes < 1:
            minutes = 1
        self.interval_display.config(text=f"{minutes} min")

    def save_interval(self):
        """Save the selected update interval"""
        import time
        
        minutes = self.interval_var.get()
        if minutes < 1:
            minutes = 1
            
        # Convert to seconds
        self.app.update_interval = minutes * 60
        self.app.interval_label.config(text=f"Update: {minutes} min")
        self.app.save_config()
        
        # Restart the update thread with new interval
        self.app.running = False
        if hasattr(self.app, 'update_thread') and self.app.update_thread.is_alive():
            time.sleep(0.5)  # Give thread time to stop
            
        self.app.running = True
        self.app.update_thread = self.app.threading.Thread(target=self.app.update_loop)
        self.app.update_thread.daemon = True
        self.app.update_thread.start()
        
        messagebox.showinfo("Success", f"Update interval set to {minutes} minutes")

    def save_api_key(self):
        """Save the API key from the settings tab"""
        new_key = self.api_key_entry.get().strip()
        if not new_key:
            messagebox.showerror("Error", "API Key cannot be empty")
            return
        
        self.app.api_key = new_key
        self.app.save_config()
        
        # Start the update thread if it doesn't exist
        if not hasattr(self.app, 'update_thread') or not self.app.update_thread.is_alive():
            self.app.update_thread = self.app.threading.Thread(target=self.app.update_loop)
            self.app.update_thread.daemon = True
            self.app.update_thread.start()
        
        # Switch to weather tab and fetch data
        self.app.notebook.select(self.app.weather_tab_frame)
        self.app.weather.fetch_weather()
        messagebox.showinfo("Success", "API key saved successfully")

    def browse_file(self):
        """Open a dialog to choose where to save the CSV file, including filename"""
        # Get the current directory and filename
        current_dir = os.path.dirname(os.path.abspath(self.app.weather_file))
        current_filename = os.path.basename(self.app.weather_file)
        
        # Ask for file path with dialog
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        new_file_path = filedialog.asksaveasfilename(
            initialdir=current_dir,
            initialfile=current_filename,
            title="Select CSV file location",
            filetypes=filetypes,
            defaultextension=".csv"
        )
        
        # If user cancels, new_path will be empty
        if new_file_path:
            # Normalize the path and ensure it has .csv extension
            new_file_path = os.path.normpath(new_file_path)
            if not new_file_path.lower().endswith('.csv'):
                new_file_path += '.csv'
                
            # Update the file path label
            self.file_path_label.config(text=new_file_path)

    def save_file_settings(self):
        """Save the file path settings"""
        import shutil
        
        # Get the full file path from the label
        new_file_path = self.file_path_label.cget("text")
        
        # Ensure it's a CSV file
        if not new_file_path.lower().endswith('.csv'):
            messagebox.showerror("Error", "File must be a CSV file")
            return
        
        # Check if it's different from the current path
        if new_file_path != os.path.abspath(self.app.weather_file):
            # Check if should migrate data
            migrate = self.migrate_var.get()
            
            # Remember the old file path
            old_file_path = self.app.weather_file
            
            # Update the file path
            self.app.weather_file = new_file_path
            
            # Update config
            self.app.save_config()
            
            # If migration is requested and the old file exists, copy the data
            if migrate and os.path.exists(old_file_path):
                try:
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(old_file_path, new_file_path)
                    messagebox.showinfo("Success", f"Weather data file location updated and data migrated.\nNew location: {new_file_path}")
                    self.app.status_label.config(text="Data file location updated with migration")
                except Exception as e:
                    messagebox.showerror("Migration Error", f"Error copying data: {str(e)}\nData file location updated but data was not transferred.")
                    self.app.status_label.config(text="Data file location updated but migration failed")
            else:
                messagebox.showinfo("Success", f"Weather data file location updated.\nNew location: {new_file_path}")
                self.app.status_label.config(text="Data file location updated")
            
            # Update the CSV path in the weather tab
            if hasattr(self.app.weather, 'csv_path'):
                self.app.weather.csv_path.config(text=os.path.abspath(new_file_path))
        else:
            messagebox.showinfo("Info", "File location is unchanged")