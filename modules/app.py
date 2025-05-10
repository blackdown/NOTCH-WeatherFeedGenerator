"""
Main application module for NOTCH Data Tool
"""
import tkinter as tk
from tkinter import ttk
import threading

from modules.config import CONFIG_FILE, DEFAULT_CITY, DEFAULT_INTERVAL, DEFAULT_WEATHER_FILE, DEFAULT_MIDI_CONFIG
from modules.weather_tab import WeatherTab
from modules.midi_tab import MidiTab
from modules.settings_tab import SettingsTab

class NOTCHDataTool:
    def __init__(self, root):
        self.root = root
        self.root.title("NOTCH Data Tool")
        self.root.geometry("450x650")
        self.root.resizable(False, False)
        
        # Config variables
        self.config = None
        self.api_key = ""
        self.city = DEFAULT_CITY
        self.update_interval = DEFAULT_INTERVAL
        self.weather_file = DEFAULT_WEATHER_FILE
        
        # MIDI variables
        self.midi_outputs = {}
        self.current_midi_port = None
        self.midi_presets = []
        self.midi_channel = 1
        
        # Load config and MIDI settings
        self.load_config()
        self.load_midi_config()
        self.init_midi()
        
        # Configure style
        self.setup_styles()
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create basic tab frames first
        self.weather_tab_frame = ttk.Frame(self.notebook, padding="20")
        self.midi_tab_frame = ttk.Frame(self.notebook, padding="20")
        self.settings_tab_frame = ttk.Frame(self.notebook, padding="20")
        
        # Add frames to notebook
        self.notebook.add(self.weather_tab_frame, text="Weather > CSV")
        self.notebook.add(self.midi_tab_frame, text="MIDI")
        self.notebook.add(self.settings_tab_frame, text="Settings")
        
        # Now set up scrollable content inside each tab
        self.weather_content = self.create_scrollable_area(self.weather_tab_frame)
        self.midi_content = self.create_scrollable_area(self.midi_tab_frame)
        self.settings_content = self.create_scrollable_area(self.settings_tab_frame)
        
        # Create status bar
        self.create_status_bar()
        
        # Initialize tab modules
        self.weather = WeatherTab(self)
        self.midi = MidiTab(self)
        self.settings = SettingsTab(self)
        
        # Check if we need to migrate CSV format
        self.weather.check_and_migrate_csv_format()
        
        # Start weather update thread if API key exists
        self.running = True
        if self.api_key:
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # Initial fetch
            self.weather.fetch_weather()
        else:
            self.status_label.config(text="Please set your API key to start")
            self.notebook.select(self.settings_tab_frame)  # Switch to settings tab

    def create_scrollable_area(self, parent):
        """Create a scrollable area inside the given parent frame"""
        # Create canvas
        canvas = tk.Canvas(parent, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar to frame but don't pack it yet
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        # Configure canvas
        canvas.configure(yscrollcommand=self._on_scrollbar_set(scrollbar))
        
        # Create frame inside canvas
        scrollable_frame = ttk.Frame(canvas)
        
        # Add frame to canvas window
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Update scroll region when frame size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Adjust width of frame to match canvas
            canvas.itemconfig(window_id, width=canvas.winfo_width())
            # Check if scrollbar is needed
            self._check_scrollbar_needed(canvas, scrollbar)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", lambda e: (canvas.itemconfig(window_id, width=e.width), 
                                              self._check_scrollbar_needed(canvas, scrollbar)))
        
        # Configure scrolling with mouse wheel - only when scrollbar is visible
        def _on_mousewheel(event):
            # Only scroll if scrollbar is visible (content overflows)
            if scrollbar.winfo_viewable():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        # Bind mousewheel to the canvas
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame
        
    def _on_scrollbar_set(self, scrollbar):
        """Custom scrollbar set function that shows/hides scrollbar as needed"""
        def wrapped(first, last):
            # Normal scrollbar behavior
            scrollbar.set(first, last)
            
            # Show scrollbar only when needed (when not seeing the full content)
            if float(first) <= 0.0 and float(last) >= 1.0:
                scrollbar.pack_forget()
            else:
                # Check if already packed to avoid error
                if not scrollbar.winfo_ismapped():
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    
        return wrapped
        
    def _check_scrollbar_needed(self, canvas, scrollbar):
        """Check if the scrollbar is needed based on content height vs canvas height"""
        # Get canvas dimensions
        canvas_height = canvas.winfo_height()
        
        # Get scroll region dimensions
        scrollregion = canvas.cget("scrollregion").split()
        if not scrollregion or len(scrollregion) < 4:
            return
            
        # Calculate content height
        try:
            content_height = int(float(scrollregion[3]) - float(scrollregion[1]))
            
            # Show/hide scrollbar based on content vs. canvas height
            if content_height <= canvas_height:
                scrollbar.pack_forget()
            else:
                if not scrollbar.winfo_ismapped():
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        except (ValueError, IndexError):
            pass

    def setup_styles(self):
        """Configure application styles"""
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", padding=[10, 5], font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Weather.TLabel", font=("Arial", 20))
        style.configure("Info.TLabel", font=("Arial", 12))
        style.configure("Link.TLabel", font=("Arial", 10), foreground="blue")
        style.configure("Path.TLabel", font=("Arial", 8), foreground="gray")
        style.configure("MIDI.TButton", background="#2E8B57", foreground="white")
        
        # Remove black outline on selection for various elements
        style.map('TCombobox', fieldbackground=[('readonly', '#f0f0f0')])
        style.map('TEntry', fieldbackground=[('focus', '#f0f0f0')])
        style.map('TCombobox', selectbackground=[('readonly', '#0078d7')])
        style.map('TEntry', selectbackground=[('focus', '#0078d7')])
        style.map('TCombobox', selectforeground=[('readonly', 'white')])
        style.map('TEntry', selectforeground=[('focus', 'white')])
        
        # Fix the outline for Treeview selection
        style.map('Treeview', 
                  background=[('selected', '#0078d7')],
                  foreground=[('selected', 'white')])
        
        # Fix Listbox selection
        self.root.option_add('*TCombobox*Listbox.background', '#f0f0f0')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#0078d7')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')

    def create_status_bar(self):
        """Create the status bar for the application"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Last updated: never", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.interval_label = ttk.Label(status_frame, text=f"Update: {self.update_interval//60} min", anchor=tk.CENTER)
        self.interval_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.refresh_button = ttk.Button(status_frame, text="Refresh", command=lambda: self.weather.fetch_weather())
        self.refresh_button.pack(side=tk.RIGHT, padx=10, pady=5)

    def update_loop(self):
        """Background thread to update weather periodically"""
        import os
        import time
        
        # Try to load existing data first
        if os.path.exists(self.weather_file):
            self.root.after(0, self.weather.load_weather_from_csv)
            
        while self.running:
            time.sleep(self.update_interval)  # Use the customizable interval
            if self.running:
                # Use after to schedule UI update on main thread
                self.root.after(0, self.weather.fetch_weather)

    def on_closing(self):
        """Cleanup when closing the application"""
        self.running = False
        
        # Close MIDI connection if open
        if self.midi:
            self.midi.close_connection()
        
        self.root.destroy()
    
    def load_config(self):
        """Load configuration from config file - stub method to be implemented in config module"""
        from modules.config import load_config
        config_data = load_config(CONFIG_FILE)
        if config_data:
            self.config = config_data['config_obj']
            self.api_key = config_data['api_key']
            self.city = config_data['city']
            self.update_interval = config_data['update_interval']
            self.weather_file = config_data['weather_file']

    def save_config(self):
        """Save configuration to config file - stub method to be implemented in config module"""
        from modules.config import save_config
        save_config(CONFIG_FILE, self.config, self.api_key, self.city, self.update_interval, self.weather_file)
    
    def load_midi_config(self):
        """Load MIDI configuration - stub method to be implemented in midi module"""
        from modules.midi import load_midi_config
        midi_data = load_midi_config(DEFAULT_MIDI_CONFIG)
        self.midi_presets = midi_data['presets']
        self.midi_channel = midi_data['channel']
    
    def save_midi_config(self):
        """Save MIDI configuration - stub method to be implemented in midi module"""
        from modules.midi import save_midi_config
        save_midi_config(DEFAULT_MIDI_CONFIG, self.midi_presets, self.midi_channel)
    
    def init_midi(self):
        """Initialize MIDI - stub method to be implemented in midi module"""
        from modules.midi import init_midi
        self.midi_outputs = init_midi()