import requests
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import os
import csv
from datetime import datetime
import configparser
import base64
import webbrowser
import shutil
import json
# Import MIDI libraries for MIDI message functionality
try:
    import rtmidi
    MIDI_LIBRARY = "rtmidi"
except ImportError:
    try:
        import mido
        MIDI_LIBRARY = "mido"
    except ImportError:
        MIDI_LIBRARY = None

# Configuration setup
CONFIG_FILE = "config.ini"
DEFAULT_CITY = "London"
DEFAULT_INTERVAL = 120  # Default update interval in seconds (2 minutes)
DEFAULT_WEATHER_FILE = "weather.csv"
DEFAULT_MIDI_CONFIG = "midi_presets.json"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NOTCH Weather Controller")
        self.root.geometry("450x650")  # Made taller to accommodate file settings
        self.root.resizable(False, False)
        
        # Load config (API key, city, and update interval)
        self.config = configparser.ConfigParser()
        self.api_key = ""
        self.city = DEFAULT_CITY
        self.update_interval = DEFAULT_INTERVAL
        self.weather_file = DEFAULT_WEATHER_FILE
        self.load_config()
        
        # MIDI setup
        self.midi_outputs = {}
        self.current_midi_port = None
        self.midi_presets = []
        self.midi_channel = 1
        self.load_midi_config()
        self.init_midi()
        
        # Configure style
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
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Weather Tab
        self.weather_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.weather_tab, text="Weather")
        
        # MIDI Tab
        self.midi_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.midi_tab, text="MIDI")
        
        # Settings Tab
        self.settings_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Create the UI for each tab
        self.create_weather_tab()
        self.create_midi_tab()
        self.create_settings_tab()
        
        # Status bar with update interval display - moved outside the notebook to always remain visible
        status_frame = ttk.Frame(root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Last updated: never", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.interval_label = ttk.Label(status_frame, text=f"Update: {self.update_interval//60} min", anchor=tk.CENTER)
        self.interval_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.refresh_button = ttk.Button(status_frame, text="Refresh", command=self.fetch_weather)
        self.refresh_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Check if we need to migrate CSV format
        self.check_and_migrate_csv_format()
        
        # Start weather update thread if API key exists
        self.running = True
        if self.api_key:
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # Initial fetch
            self.fetch_weather()
        else:
            self.status_label.config(text="Please set your API key to start")
            self.notebook.select(self.settings_tab)  # Switch to settings tab

    def create_weather_tab(self):
        """Create the weather tab UI"""
        # City and Location Controls
        loc_frame = ttk.Frame(self.weather_tab)
        loc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.city_entry = ttk.Entry(loc_frame, width=15)
        self.city_entry.insert(0, self.city)
        self.city_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.set_city_btn = ttk.Button(loc_frame, text="Set City", command=self.update_city)
        self.set_city_btn.pack(side=tk.LEFT, padx=5)
        
        self.geolocate_btn = ttk.Button(loc_frame, text="Geolocate", command=self.geolocate_location)
        self.geolocate_btn.pack(side=tk.LEFT, padx=5)
        
        # City label - increased top padding from 0 to 15
        self.city_label = ttk.Label(self.weather_tab, text=f"Weather for {self.city}", style="Header.TLabel")
        self.city_label.pack(pady=(15, 10))
        
        # Weather info
        self.weather_frame = ttk.Frame(self.weather_tab)
        self.weather_frame.pack(fill=tk.X, pady=10)
        
        self.temp_label = ttk.Label(self.weather_frame, text="-- °C", style="Weather.TLabel")
        self.temp_label.pack()
        
        self.desc_label = ttk.Label(self.weather_frame, text="--", style="Info.TLabel")
        self.desc_label.pack(pady=5)
        
        # Details frame
        details_frame = ttk.Frame(self.weather_tab)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Wind info
        wind_frame = ttk.LabelFrame(details_frame, text="Wind")
        wind_frame.pack(fill=tk.X, pady=5)
        
        self.wind_label = ttk.Label(wind_frame, text="-- m/s, --°")
        self.wind_label.pack(pady=5)
        
        # Coordinates info
        coords_frame = ttk.LabelFrame(details_frame, text="Coordinates")
        coords_frame.pack(fill=tk.X, pady=5)
        
        self.coords_label = ttk.Label(coords_frame, text="Longitude: --, Latitude: --")
        self.coords_label.pack(pady=5)
        
        # Additional info
        info_frame = ttk.LabelFrame(details_frame, text="Additional Information")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.humidity_label = ttk.Label(info_frame, text="Humidity: --%")
        self.humidity_label.pack(anchor="w", pady=2)
        
        self.pressure_label = ttk.Label(info_frame, text="Pressure: -- hPa")
        self.pressure_label.pack(anchor="w", pady=2)
        
        self.feels_like_label = ttk.Label(info_frame, text="Feels like: -- °C")
        self.feels_like_label.pack(anchor="w", pady=2)
        
        # CSV link frame
        csv_frame = ttk.Frame(self.weather_tab)
        csv_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.csv_link = ttk.Label(
            csv_frame, 
            text=f"Open weather data file", 
            style="Link.TLabel",
            cursor="hand2"
        )
        self.csv_link.pack(anchor="w")
        self.csv_link.bind("<Button-1>", self.open_csv_file)
        
        # Full path display beneath the link
        self.csv_path = ttk.Label(
            csv_frame,
            text=f"{os.path.abspath(self.weather_file)}",
            style="Path.TLabel"
        )
        self.csv_path.pack(anchor="w")
    
    def create_midi_tab(self):
        """Create the MIDI tab UI"""
        # Title
        title_label = ttk.Label(self.midi_tab, text="MIDI Controller", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # MIDI Port Selection
        port_frame = ttk.LabelFrame(self.midi_tab, text="MIDI Output")
        port_frame.pack(fill=tk.X, pady=10)
        
        port_subframe = ttk.Frame(port_frame)
        port_subframe.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(port_subframe, text="MIDI Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.port_var = tk.StringVar(value="No MIDI ports available")
        self.port_dropdown = ttk.Combobox(port_subframe, textvariable=self.port_var, state="readonly")
        self.port_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.port_dropdown.bind("<<ComboboxSelected>>", self.on_port_selected)
        
        self.refresh_ports_btn = ttk.Button(port_subframe, text="Refresh", command=self.refresh_midi_ports, width=10)
        self.refresh_ports_btn.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(port_subframe, text="MIDI Channel:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.channel_var = tk.IntVar(value=self.midi_channel)
        channel_dropdown = ttk.Combobox(port_subframe, textvariable=self.channel_var, state="readonly",
                                        values=list(range(1, 17)))
        channel_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        channel_dropdown.bind("<<ComboboxSelected>>", self.on_channel_selected)
        
        port_subframe.grid_columnconfigure(1, weight=1)
        
        # MIDI Controls frame
        controls_frame = ttk.LabelFrame(self.midi_tab, text="MIDI Controls")
        controls_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Note controls
        note_frame = ttk.Frame(controls_frame)
        note_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(note_frame, text="Note Controls", style="Info.TLabel").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        # Note Number Control
        ttk.Label(note_frame, text="Note Number:").grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.note_var = tk.IntVar(value=60)  # Middle C
        note_spin = ttk.Spinbox(note_frame, from_=0, to=127, textvariable=self.note_var, width=5)
        note_spin.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Note Velocity Control
        ttk.Label(note_frame, text="Velocity:").grid(row=1, column=2, sticky=tk.W, padx=5)
        
        self.velocity_var = tk.IntVar(value=100)
        velocity_spin = ttk.Spinbox(note_frame, from_=0, to=127, textvariable=self.velocity_var, width=5)
        velocity_spin.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Note Buttons
        note_buttons_frame = ttk.Frame(note_frame)
        note_buttons_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=10)
        
        send_note_on = ttk.Button(note_buttons_frame, text="Note On", command=self.send_note_on)
        send_note_on.pack(side=tk.LEFT, padx=(0, 5))
        
        send_note_off = ttk.Button(note_buttons_frame, text="Note Off", command=self.send_note_off)
        send_note_off.pack(side=tk.LEFT, padx=5)
        
        # CC Controls
        cc_frame = ttk.Frame(controls_frame)
        cc_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(cc_frame, text="CC Controls", style="Info.TLabel").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        # CC Number Control
        ttk.Label(cc_frame, text="CC Number:").grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.cc_var = tk.IntVar(value=1)
        cc_spin = ttk.Spinbox(cc_frame, from_=0, to=127, textvariable=self.cc_var, width=5)
        cc_spin.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # CC Value Control
        ttk.Label(cc_frame, text="CC Value:").grid(row=1, column=2, sticky=tk.W, padx=5)
        
        self.cc_value_var = tk.IntVar(value=64)
        cc_value_spin = ttk.Spinbox(cc_frame, from_=0, to=127, textvariable=self.cc_value_var, width=5)
        cc_value_spin.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Value Slider
        self.cc_slider = ttk.Scale(cc_frame, from_=0, to=127, orient="horizontal", variable=self.cc_value_var)
        self.cc_slider.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Send CC Button
        send_cc_btn = ttk.Button(cc_frame, text="Send CC", command=self.send_cc)
        send_cc_btn.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Preset management
        preset_frame = ttk.LabelFrame(self.midi_tab, text="Presets")
        preset_frame.pack(fill=tk.X, pady=10)
        
        preset_controls = ttk.Frame(preset_frame)
        preset_controls.pack(fill=tk.X, pady=10, padx=10)
        
        # Preset Name
        ttk.Label(preset_controls, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.preset_name_var = tk.StringVar()
        preset_name_entry = ttk.Entry(preset_controls, textvariable=self.preset_name_var)
        preset_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Preset buttons
        save_preset_btn = ttk.Button(preset_controls, text="Save Preset", command=self.save_preset)
        save_preset_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Preset list
        preset_list_frame = ttk.Frame(preset_frame)
        preset_list_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.preset_listbox = tk.Listbox(preset_list_frame, height=4)
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        preset_scrollbar = ttk.Scrollbar(preset_list_frame, orient="vertical", command=self.preset_listbox.yview)
        preset_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preset_listbox.config(yscrollcommand=preset_scrollbar.set)
        self.preset_listbox.bind("<Double-1>", self.load_selected_preset)
        
        # Load preset button
        preset_buttons_frame = ttk.Frame(preset_frame)
        preset_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        load_preset_btn = ttk.Button(preset_buttons_frame, text="Load Preset", command=self.load_preset)
        load_preset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_preset_btn = ttk.Button(preset_buttons_frame, text="Delete Preset", command=self.delete_preset)
        delete_preset_btn.pack(side=tk.LEFT)
        
        # MIDI Status
        self.midi_status = ttk.Label(self.midi_tab, text="MIDI Status: Not connected", foreground="red")
        self.midi_status.pack(pady=10)
        
        # Populate with available MIDI ports
        self.refresh_midi_ports()
        self.refresh_preset_list()

    def init_midi(self):
        """Initialize MIDI output"""
        if MIDI_LIBRARY == "rtmidi":
            try:
                self.midi_outputs["rtmidi"] = rtmidi.MidiOut()
                self.refresh_midi_ports()
            except Exception as e:
                print(f"Error initializing MIDI: {e}")
        elif MIDI_LIBRARY == "mido":
            try:
                self.refresh_midi_ports()
            except Exception as e:
                print(f"Error initializing MIDI: {e}")
            
    def refresh_midi_ports(self):
        """Refresh the list of available MIDI ports"""
        ports = []
        
        if MIDI_LIBRARY == "rtmidi":
            try:
                ports = self.midi_outputs["rtmidi"].get_ports()
            except Exception as e:
                print(f"Error getting MIDI ports: {e}")
        elif MIDI_LIBRARY == "mido":
            try:
                ports = mido.get_output_names()
            except Exception as e:
                print(f"Error getting MIDI ports: {e}")
        
        if ports:
            self.port_dropdown['values'] = ports
            self.port_var.set(ports[0] if ports else "No MIDI ports available")
            self.port_dropdown.config(state="readonly")
            self.on_port_selected()
        else:
            self.port_dropdown['values'] = ["No MIDI ports available"]
            self.port_var.set("No MIDI ports available")
            self.port_dropdown.config(state="disabled")
            self.midi_status.config(text="MIDI Status: No ports available", foreground="red")
            
    def on_port_selected(self, event=None):
        """Handle MIDI port selection"""
        selected_port = self.port_var.get()
        
        if selected_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: No ports available", foreground="red")
            return
            
        try:
            if MIDI_LIBRARY == "rtmidi":
                # Close existing connection if any
                if self.current_midi_port is not None:
                    self.midi_outputs["rtmidi"].close_port()
                
                # Open the selected port
                port_index = self.port_dropdown['values'].index(selected_port)
                self.midi_outputs["rtmidi"].open_port(port_index)
                self.current_midi_port = port_index
                self.midi_status.config(text=f"MIDI Status: Connected to {selected_port}", foreground="green")
                
            elif MIDI_LIBRARY == "mido":
                self.current_midi_port = selected_port
                self.midi_status.config(text=f"MIDI Status: Ready to use {selected_port}", foreground="green")
                
        except Exception as e:
            self.midi_status.config(text=f"MIDI Error: {str(e)}", foreground="red")
            
    def on_channel_selected(self, event=None):
        """Handle MIDI channel selection"""
        self.midi_channel = self.channel_var.get()
            
    def send_note_on(self):
        """Send MIDI Note On message"""
        if not self.current_midi_port or self.current_midi_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: Not connected", foreground="red")
            return
            
        note = self.note_var.get()
        velocity = self.velocity_var.get()
        channel = self.midi_channel - 1  # MIDI channels are 0-15 internally
        
        try:
            if MIDI_LIBRARY == "rtmidi":
                note_on = [0x90 + channel, note, velocity]  # Note On is 0x90 + channel
                self.midi_outputs["rtmidi"].send_message(note_on)
            elif MIDI_LIBRARY == "mido":
                with mido.open_output(self.current_midi_port) as port:
                    port.send(mido.Message('note_on', note=note, velocity=velocity, channel=channel))
                    
            self.midi_status.config(text=f"MIDI Status: Sent Note On {note} with velocity {velocity}", foreground="green")
        except Exception as e:
            self.midi_status.config(text=f"MIDI Error: {str(e)}", foreground="red")
            
    def send_note_off(self):
        """Send MIDI Note Off message"""
        if not self.current_midi_port or self.current_midi_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: Not connected", foreground="red")
            return
            
        note = self.note_var.get()
        channel = self.midi_channel - 1  # MIDI channels are 0-15 internally
        
        try:
            if MIDI_LIBRARY == "rtmidi":
                note_off = [0x80 + channel, note, 0]  # Note Off is 0x80 + channel
                self.midi_outputs["rtmidi"].send_message(note_off)
            elif MIDI_LIBRARY == "mido":
                with mido.open_output(self.current_midi_port) as port:
                    port.send(mido.Message('note_off', note=note, velocity=0, channel=channel))
                    
            self.midi_status.config(text=f"MIDI Status: Sent Note Off {note}", foreground="green")
        except Exception as e:
            self.midi_status.config(text=f"MIDI Error: {str(e)}", foreground="red")
            
    def send_cc(self):
        """Send MIDI CC message"""
        if not self.current_midi_port or self.current_midi_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: Not connected", foreground="red")
            return
            
        cc_num = self.cc_var.get()
        cc_val = self.cc_value_var.get()
        channel = self.midi_channel - 1  # MIDI channels are 0-15 internally
        
        try:
            if MIDI_LIBRARY == "rtmidi":
                cc_msg = [0xB0 + channel, cc_num, cc_val]  # CC is 0xB0 + channel
                self.midi_outputs["rtmidi"].send_message(cc_msg)
            elif MIDI_LIBRARY == "mido":
                with mido.open_output(self.current_midi_port) as port:
                    port.send(mido.Message('control_change', control=cc_num, value=cc_val, channel=channel))
                    
            self.midi_status.config(text=f"MIDI Status: Sent CC {cc_num} with value {cc_val}", foreground="green")
        except Exception as e:
            self.midi_status.config(text=f"MIDI Error: {str(e)}", foreground="red")

    def save_preset(self):
        """Save current MIDI settings as a preset"""
        name = self.preset_name_var.get()
        if not name:
            # Generate a default name if none provided
            name = f"Preset {len(self.midi_presets) + 1}"
            self.preset_name_var.set(name)
            
        preset = {
            'name': name,
            'channel': self.midi_channel,
            'note': self.note_var.get(),
            'velocity': self.velocity_var.get(),
            'cc': self.cc_var.get(),
            'cc_value': self.cc_value_var.get()
        }
        
        # Check if preset with this name exists and update it, or add new
        for i, p in enumerate(self.midi_presets):
            if p['name'] == name:
                self.midi_presets[i] = preset
                break
        else:
            self.midi_presets.append(preset)
            
        self.save_midi_config()
        self.refresh_preset_list()
        self.midi_status.config(text=f"MIDI Status: Preset '{name}' saved", foreground="green")

    def load_preset(self):
        """Load selected preset"""
        selected = self.preset_listbox.curselection()
        if not selected:
            return
            
        index = selected[0]
        if 0 <= index < len(self.midi_presets):
            self._apply_preset(self.midi_presets[index])
            
    def load_selected_preset(self, event=None):
        """Load preset when double-clicked in the listbox"""
        self.load_preset()
            
    def _apply_preset(self, preset):
        """Apply preset values to the UI"""
        self.preset_name_var.set(preset['name'])
        self.channel_var.set(preset['channel'])
        self.midi_channel = preset['channel']
        self.note_var.set(preset['note'])
        self.velocity_var.set(preset['velocity'])
        self.cc_var.set(preset['cc'])
        self.cc_value_var.set(preset['cc_value'])
        self.midi_status.config(text=f"MIDI Status: Loaded preset '{preset['name']}'", foreground="green")
            
    def delete_preset(self):
        """Delete selected preset"""
        selected = self.preset_listbox.curselection()
        if not selected:
            return
            
        index = selected[0]
        if 0 <= index < len(self.midi_presets):
            preset_name = self.midi_presets[index]['name']
            del self.midi_presets[index]
            self.save_midi_config()
            self.refresh_preset_list()
            self.midi_status.config(text=f"MIDI Status: Preset '{preset_name}' deleted", foreground="green")
            
    def refresh_preset_list(self):
        """Update the preset listbox"""
        self.preset_listbox.delete(0, tk.END)
        for preset in self.midi_presets:
            self.preset_listbox.insert(tk.END, preset['name'])
            
    def load_midi_config(self):
        """Load MIDI presets from JSON file"""
        try:
            if os.path.exists(DEFAULT_MIDI_CONFIG):
                with open(DEFAULT_MIDI_CONFIG, 'r') as f:
                    data = json.load(f)
                    self.midi_presets = data.get('presets', [])
                    self.midi_channel = data.get('last_channel', 1)
        except Exception as e:
            print(f"Error loading MIDI config: {e}")
            self.midi_presets = []
            
    def save_midi_config(self):
        """Save MIDI presets to JSON file"""
        try:
            data = {
                'presets': self.midi_presets,
                'last_channel': self.midi_channel
            }
            with open(DEFAULT_MIDI_CONFIG, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving MIDI config: {e}")
            
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
        minutes = self.interval_var.get()
        if minutes < 1:
            minutes = 1
            
        # Convert to seconds
        self.update_interval = minutes * 60
        self.interval_label.config(text=f"Update: {minutes} min")
        self.save_config()
        
        # Restart the update thread with new interval
        self.running = False
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            time.sleep(0.5)  # Give thread time to stop
            
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        messagebox.showinfo("Success", f"Update interval set to {minutes} minutes")
        
    def save_api_key(self):
        """Save the API key from the settings tab"""
        new_key = self.api_key_entry.get().strip()
        if not new_key:
            messagebox.showerror("Error", "API Key cannot be empty")
            return
        
        self.api_key = new_key
        self.save_config()
        
        # Start the update thread if it doesn't exist
        if not hasattr(self, 'update_thread') or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
        
        # Switch to weather tab and fetch data
        self.notebook.select(self.weather_tab)
        self.fetch_weather()
        messagebox.showinfo("Success", "API key saved successfully")

    def geolocate_location(self):
        """Get the user's location based on IP address"""
        try:
            self.status_label.config(text="Detecting location...")
            self.root.update()  # Force GUI update
            
            # Use a free IP geolocation service
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    # Update city entry with detected city
                    detected_city = data.get("city", "")
                    if detected_city:
                        self.city_entry.delete(0, tk.END)
                        self.city_entry.insert(0, detected_city)
                        self.update_city()
                        self.status_label.config(text=f"Location detected: {detected_city}")
                    else:
                        self.status_label.config(text="Could not determine your city")
                else:
                    self.status_label.config(text="Geolocation failed")
            else:
                self.status_label.config(text=f"Geolocation error: {response.status_code}")
        except Exception as e:
            self.status_label.config(text=f"Geolocation error: {str(e)}")
    
    def check_and_migrate_csv_format(self):
        """Check if CSV needs migration and perform it if necessary"""
        try:
            if os.path.exists(self.weather_file):
                with open(self.weather_file, 'r') as f:
                    # Read first line to check header format
                    first_line = f.readline().strip()
                    
                    # Check if the CSV format needs migration
                    if first_line.startswith('timestamp,') and 'longitude' not in first_line:
                        self.status_label.config(text="Migrating CSV format...")
                        self.root.update()  # Force GUI update to show status
                        self.migrate_csv_format()
                        self.status_label.config(text="CSV migration completed")
        except Exception as e:
            self.status_label.config(text=f"Error checking CSV format: {str(e)}")
    
    def migrate_csv_format(self):
        """Migrate existing CSV to new format with separate date/time columns and coordinates"""
        try:
            # Create a backup of the current file
            backup_file = f"{self.weather_file}.bak"
            if os.path.exists(self.weather_file):
                with open(self.weather_file, 'r', newline='') as src, open(backup_file, 'w', newline='') as dst:
                    dst.write(src.read())
                
                # Read the old format
                rows = []
                with open(self.weather_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    for row in reader:
                        rows.append(row)
                
                # Create the new format file
                if rows:
                    with open(self.weather_file, 'w', newline='') as f:
                        # Define new fieldnames
                        new_fieldnames = ['date', 'time', 'city', 'description', 'temperature', 
                                        'feels_like', 'humidity', 'pressure', 'wind_speed', 
                                        'wind_deg', 'visibility', 'longitude', 'latitude']
                        
                        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
                        writer.writeheader()
                        
                        # Convert each row
                        for row in rows:
                            # Split timestamp into date and time if available
                            date_str = ""
                            time_str = ""
                            if 'timestamp' in row:
                                parts = row['timestamp'].split(' ')
                                if len(parts) >= 2:
                                    date_str = parts[0]
                                    time_str = parts[1]
                            
                            # Create new row
                            new_row = {
                                'date': date_str,
                                'time': time_str,
                                'city': row.get('city', ''),
                                'description': row.get('description', ''),
                                'temperature': row.get('temperature', ''),
                                'feels_like': row.get('feels_like', ''),
                                'humidity': row.get('humidity', ''),
                                'pressure': row.get('pressure', ''),
                                'wind_speed': row.get('wind_speed', ''),
                                'wind_deg': row.get('wind_deg', ''),
                                'visibility': row.get('visibility', ''),
                                'longitude': '',  # No coordinates in old format
                                'latitude': ''    # No coordinates in old format
                            }
                            writer.writerow(new_row)
        except Exception as e:
            messagebox.showerror("Migration Error", f"Error migrating CSV format: {str(e)}")
            # If there was an error, try to restore from backup
            if os.path.exists(backup_file):
                try:
                    os.replace(backup_file, self.weather_file)
                    self.status_label.config(text="Restored from backup due to error.")
                except Exception:
                    self.status_label.config(text="Failed to restore from backup.")
    
    def open_csv_file(self, event=None):
        """Open the CSV file with the default application"""
        try:
            import subprocess
            import os
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.weather_file)), exist_ok=True)
            
            # Create the file if it doesn't exist
            if not os.path.exists(self.weather_file):
                with open(self.weather_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['date', 'time', 'city', 'description', 'temperature', 
                                   'feels_like', 'humidity', 'pressure', 'wind_speed', 
                                   'wind_deg', 'visibility', 'longitude', 'latitude'])
            
            # Use the appropriate command based on the operating system
            if os.name == 'nt':  # Windows
                os.startfile(os.path.abspath(self.weather_file))
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(('open', os.path.abspath(self.weather_file)) if os.uname().sysname == 'Darwin' 
                               else ('xdg-open', os.path.abspath(self.weather_file)))
            self.status_label.config(text="Opening CSV file...")
        except Exception as e:
            self.status_label.config(text=f"Error opening CSV: {str(e)}")
    
    def load_config(self):
        """Load configuration from config file"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
            if 'Settings' in self.config:
                if 'api_key' in self.config['Settings']:
                    # Decode the API key
                    encoded_key = self.config['Settings']['api_key']
                    try:
                        self.api_key = base64.b64decode(encoded_key).decode('utf-8')
                    except:
                        self.api_key = ""
                
                if 'city' in self.config['Settings']:
                    self.city = self.config['Settings']['city']
                    
                if 'update_interval' in self.config['Settings']:
                    try:
                        self.update_interval = int(self.config['Settings']['update_interval'])
                    except:
                        self.update_interval = DEFAULT_INTERVAL
                
                if 'weather_file' in self.config['Settings']:
                    self.weather_file = self.config['Settings']['weather_file']
    
    def save_config(self):
        """Save configuration to config file"""
        if 'Settings' not in self.config:
            self.config['Settings'] = {}
            
        # Encode the API key
        if self.api_key:
            encoded_key = base64.b64encode(self.api_key.encode('utf-8')).decode('utf-8')
            self.config['Settings']['api_key'] = encoded_key
            
        self.config['Settings']['city'] = self.city
        self.config['Settings']['update_interval'] = str(self.update_interval)
        self.config['Settings']['weather_file'] = self.weather_file
        
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)
    
    def set_update_interval(self):
        """Allow the user to set a custom update interval"""
        # Switch to settings tab
        self.notebook.select(self.settings_tab)
        
    def show_api_settings(self):
        """Show API settings tab"""
        self.notebook.select(self.settings_tab)
        
    def update_city(self):
        """Update the city and refresh weather"""
        new_city = self.city_entry.get().strip()
        if not new_city:
            return
            
        self.city = new_city
        self.city_label.config(text=f"Weather for {self.city}")
        self.save_config()
        
        # Refresh weather data
        if self.api_key:
            self.fetch_weather()
        
    def fetch_weather(self):
        """Fetch weather data from API"""
        if not self.api_key:
            self.status_label.config(text="API Key not set")
            self.notebook.select(self.settings_tab)  # Switch to settings tab
            return
            
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code}"
                data = response.json()
                if "message" in data:
                    error_msg += f" - {data['message']}"
                self.status_label.config(text=error_msg)
                return
                
            data = response.json()
            
            # Save the data to CSV
            try:
                # Get current date and time separately
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                
                # Extract the most important weather data
                weather_data = {
                    'date': date_str,
                    'time': time_str,
                    'city': data['name'],
                    'description': data['weather'][0]['description'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'wind_deg': data['wind'].get('deg', ''),
                    'visibility': data.get('visibility', ''),
                    'longitude': data['coord']['lon'],
                    'latitude': data['coord']['lat']
                }
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(os.path.abspath(self.weather_file)), exist_ok=True)
                
                # Check if file exists and handle CSV format migration if needed
                file_exists = False
                existing_rows = []
                fieldnames = list(weather_data.keys())
                
                try:
                    with open(self.weather_file, 'r', newline='') as f:
                        # Read first line to check header format
                        first_line = f.readline().strip()
                        file_exists = True
                        
                        # Check if the CSV format needs migration
                        if first_line.startswith('timestamp,') and 'longitude' not in first_line:
                            self.status_label.config(text="Migrating CSV format...")
                            self.root.update()  # Force GUI update to show status
                            self.migrate_csv_format()
                            self.status_label.config(text="CSV migration completed")
                        else:
                            # If no migration needed, read existing data
                            f.seek(0)  # Go back to beginning of file
                            reader = csv.DictReader(f)
                            existing_rows = list(reader)
                            
                except FileNotFoundError:
                    pass
                
                # Write to CSV file with newest entry at the top
                with open(self.weather_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Write the new row first (at the top)
                    writer.writerow(weather_data)
                    
                    # Write all existing rows after
                    for row in existing_rows:
                        # Ensure all rows have the same fieldnames
                        cleaned_row = {field: row.get(field, '') for field in fieldnames}
                        writer.writerow(cleaned_row)
                
                # Update UI with weather information
                self.update_weather_ui(data)
                
                # Update status
                self.status_label.config(text=f"Last updated: {time_str}")
                
            except Exception as e:
                self.status_label.config(text=f"Error saving weather data: {str(e)}")
                
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def update_weather_ui(self, data):
        """Update UI with weather data"""
        # Main weather info
        self.temp_label.config(text=f"{data['main']['temp']:.1f} °C")
        self.desc_label.config(text=data['weather'][0]['description'].capitalize())
        
        # Wind info
        if 'wind' in data:
            wind_text = f"{data['wind']['speed']} m/s"
            if 'deg' in data['wind']:
                wind_text += f", {data['wind']['deg']}°"
            self.wind_label.config(text=wind_text)
        
        # Coordinates info
        if 'coord' in data:
            lon = data['coord']['lon']
            lat = data['coord']['lat']
            self.coords_label.config(text=f"Longitude: {lon}, Latitude: {lat}")
            
            # Also update the city label but without coordinates now
            self.city_label.config(text=f"Weather for {data['name']}")
        
        # Additional info
        if 'main' in data:
            if 'humidity' in data['main']:
                self.humidity_label.config(text=f"Humidity: {data['main']['humidity']}%")
            if 'pressure' in data['main']:
                self.pressure_label.config(text=f"Pressure: {data['main']['pressure']} hPa")
            if 'feels_like' in data['main']:
                self.feels_like_label.config(text=f"Feels like: {data['main']['feels_like']:.1f} °C")
    
    def load_weather_from_csv(self):
        """Load the most recent weather data from CSV file"""
        try:
            if not os.path.exists(self.weather_file):
                return False
                
            with open(self.weather_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            if not rows:
                return False
                
            # Get the first entry (since we now add new entries at the top)
            latest = rows[0]
            
            # Update UI with this data - safely handle potential data type issues
            try:
                temp = float(latest.get('temperature', 0))
                self.temp_label.config(text=f"{temp:.1f} °C")
            except (ValueError, TypeError):
                self.temp_label.config(text="-- °C")
                
            self.desc_label.config(text=latest.get('description', '--').capitalize())
            
            # Wind info
            wind_text = f"{latest.get('wind_speed', '--')} m/s"
            wind_deg = latest.get('wind_deg', '')
            if wind_deg:
                wind_text += f", {wind_deg}°"
            self.wind_label.config(text=wind_text)
            
            # Coordinates info
            lon = latest.get('longitude', '--')
            lat = latest.get('latitude', '--')
            self.coords_label.config(text=f"Longitude: {lon}, Latitude: {lat}")
            
            # Additional info
            self.humidity_label.config(text=f"Humidity: {latest.get('humidity', '--')}%")
            self.pressure_label.config(text=f"Pressure: {latest.get('pressure', '--')} hPa")
            
            # Handle feels_like with potential type conversion issues
            try:
                feels_like = float(latest.get('feels_like', 0))
                self.feels_like_label.config(text=f"Feels like: {feels_like:.1f} °C")
            except (ValueError, TypeError):
                self.feels_like_label.config(text="Feels like: -- °C")
            
            # Update city label (without coordinates now)
            self.city_label.config(text=f"Weather for {latest.get('city', '--')}")
            
            # Update status with time from the file
            time_display = latest.get('time', '')
            if not time_display and 'timestamp' in latest:
                # Handle legacy CSV format with combined timestamp
                time_parts = latest['timestamp'].split(' ')
                if len(time_parts) > 1:
                    time_display = time_parts[1]
            
            self.status_label.config(text=f"Last updated: {time_display}")
            
            return True
            
        except Exception as e:
            self.status_label.config(text=f"Error loading weather data: {str(e)}")
            return False
        
    def update_loop(self):
        """Background thread to update weather periodically"""
        # Try to load existing data first
        if os.path.exists(self.weather_file):
            self.root.after(0, self.load_weather_from_csv)
            
        while self.running:
            time.sleep(self.update_interval)  # Use the customizable interval
            if self.running:
                # Use after to schedule UI update on main thread
                self.root.after(0, self.fetch_weather)
    
    def on_closing(self):
        """Cleanup when closing the application"""
        self.running = False
        
        # Close MIDI connection if open
        if MIDI_LIBRARY == "rtmidi" and self.current_midi_port is not None:
            try:
                self.midi_outputs["rtmidi"].close_port()
            except:
                pass
        
        self.root.destroy()

    def create_settings_tab(self):
        """Create the settings tab UI"""
        # API Settings Section
        api_frame = ttk.LabelFrame(self.settings_tab, text="API Settings")
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="Enter your OpenWeatherMap API Key:").pack(anchor="w", pady=(10, 5), padx=10)
        
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.api_key_entry = ttk.Entry(api_key_frame, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        
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
        interval_frame = ttk.LabelFrame(self.settings_tab, text="Update Interval")
        interval_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(interval_frame, text="Set how often to fetch new weather data:").pack(anchor="w", pady=(10, 5), padx=10)
        
        interval_setting_frame = ttk.Frame(interval_frame)
        interval_setting_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        current_interval = self.update_interval // 60  # Convert to minutes
        
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
        file_frame = ttk.LabelFrame(self.settings_tab, text="Data File Settings")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Choose where to save weather data:").pack(anchor="w", pady=(10, 5), padx=10)
        
        # File location info
        file_info_frame = ttk.Frame(file_frame)
        file_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_path_label = ttk.Label(file_info_frame, text=os.path.abspath(self.weather_file), style="Path.TLabel")
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