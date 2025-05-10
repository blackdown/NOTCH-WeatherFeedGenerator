"""
MIDI tab functionality for NOTCH Data Tool
"""
import tkinter as tk
from tkinter import ttk, messagebox

class MidiTab:
    def __init__(self, app):
        """Initialize the MIDI tab with the main application reference"""
        self.app = app
        self.tab = app.midi_tab_frame
        
        # Create the MIDI Tab UI
        self.create_midi_tab()
        
    def create_midi_tab(self):
        """Create the MIDI tab UI"""
        # Title
        title_label = ttk.Label(self.tab, text="MIDI Controller", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # MIDI Port Selection
        port_frame = ttk.LabelFrame(self.tab, text="MIDI Output")
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
        
        self.channel_var = tk.IntVar(value=self.app.midi_channel)
        channel_dropdown = ttk.Combobox(port_subframe, textvariable=self.channel_var, state="readonly",
                                        values=list(range(1, 17)))
        channel_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        channel_dropdown.bind("<<ComboboxSelected>>", self.on_channel_selected)
        
        port_subframe.grid_columnconfigure(1, weight=1)
        
        # MIDI Controls frame
        controls_frame = ttk.LabelFrame(self.tab, text="MIDI Controls")
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
        preset_frame = ttk.LabelFrame(self.tab, text="Presets")
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
        self.midi_status = ttk.Label(self.tab, text="MIDI Status: Not connected", foreground="red")
        self.midi_status.pack(pady=10)
        
        # Populate with available MIDI ports
        self.refresh_midi_ports()
        self.refresh_preset_list()

    def refresh_midi_ports(self):
        """Refresh the list of available MIDI ports"""
        from modules.midi import get_midi_ports
        
        ports = get_midi_ports()
        
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
        from modules.midi import MIDI_LIBRARY
        
        selected_port = self.port_var.get()
        
        if selected_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: No ports available", foreground="red")
            return
            
        try:
            if MIDI_LIBRARY == "rtmidi":
                # Close existing connection if any
                if self.app.current_midi_port is not None:
                    from modules.midi import close_midi_port
                    close_midi_port(self.app.midi_outputs, self.app.current_midi_port)
                
                # Open the selected port
                port_index = self.port_dropdown['values'].index(selected_port)
                self.app.midi_outputs["rtmidi"].open_port(port_index)
                self.app.current_midi_port = port_index
                self.midi_status.config(text=f"MIDI Status: Connected to {selected_port}", foreground="green")
                
            elif MIDI_LIBRARY == "mido":
                self.app.current_midi_port = selected_port
                self.midi_status.config(text=f"MIDI Status: Ready to use {selected_port}", foreground="green")
                
        except Exception as e:
            self.midi_status.config(text=f"MIDI Error: {str(e)}", foreground="red")
            
    def on_channel_selected(self, event=None):
        """Handle MIDI channel selection"""
        self.app.midi_channel = self.channel_var.get()
            
    def send_note_on(self):
        """Send MIDI Note On message"""
        from modules.midi import send_midi_message
        
        if not self.app.current_midi_port or self.app.current_midi_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: Not connected", foreground="red")
            return
            
        note = self.note_var.get()
        velocity = self.velocity_var.get()
        
        success = send_midi_message(
            self.app.midi_outputs, 
            self.app.current_midi_port, 
            "note_on", 
            self.app.midi_channel, 
            note, 
            velocity
        )
        
        if success:
            self.midi_status.config(text=f"MIDI Status: Sent Note On {note} with velocity {velocity}", foreground="green")
        else:
            self.midi_status.config(text="MIDI Error: Failed to send Note On message", foreground="red")
            
    def send_note_off(self):
        """Send MIDI Note Off message"""
        from modules.midi import send_midi_message
        
        if not self.app.current_midi_port or self.app.current_midi_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: Not connected", foreground="red")
            return
            
        note = self.note_var.get()
        
        success = send_midi_message(
            self.app.midi_outputs, 
            self.app.current_midi_port, 
            "note_off", 
            self.app.midi_channel, 
            note, 
            0
        )
        
        if success:
            self.midi_status.config(text=f"MIDI Status: Sent Note Off {note}", foreground="green")
        else:
            self.midi_status.config(text="MIDI Error: Failed to send Note Off message", foreground="red")
            
    def send_cc(self):
        """Send MIDI CC message"""
        from modules.midi import send_midi_message
        
        if not self.app.current_midi_port or self.app.current_midi_port == "No MIDI ports available":
            self.midi_status.config(text="MIDI Status: Not connected", foreground="red")
            return
            
        cc_num = self.cc_var.get()
        cc_val = self.cc_value_var.get()
        
        success = send_midi_message(
            self.app.midi_outputs,
            self.app.current_midi_port,
            "control_change",
            self.app.midi_channel,
            cc_num,
            cc_val
        )
        
        if success:
            self.midi_status.config(text=f"MIDI Status: Sent CC {cc_num} with value {cc_val}", foreground="green")
        else:
            self.midi_status.config(text="MIDI Error: Failed to send CC message", foreground="red")

    def save_preset(self):
        """Save current MIDI settings as a preset"""
        name = self.preset_name_var.get()
        if not name:
            # Generate a default name if none provided
            name = f"Preset {len(self.app.midi_presets) + 1}"
            self.preset_name_var.set(name)
            
        preset = {
            'name': name,
            'channel': self.app.midi_channel,
            'note': self.note_var.get(),
            'velocity': self.velocity_var.get(),
            'cc': self.cc_var.get(),
            'cc_value': self.cc_value_var.get()
        }
        
        # Check if preset with this name exists and update it, or add new
        for i, p in enumerate(self.app.midi_presets):
            if p['name'] == name:
                self.app.midi_presets[i] = preset
                break
        else:
            self.app.midi_presets.append(preset)
            
        self.app.save_midi_config()
        self.refresh_preset_list()
        self.midi_status.config(text=f"MIDI Status: Preset '{name}' saved", foreground="green")

    def load_preset(self):
        """Load selected preset"""
        selected = self.preset_listbox.curselection()
        if not selected:
            return
            
        index = selected[0]
        if 0 <= index < len(self.app.midi_presets):
            self._apply_preset(self.app.midi_presets[index])
            
    def load_selected_preset(self, event=None):
        """Load preset when double-clicked in the listbox"""
        self.load_preset()
            
    def _apply_preset(self, preset):
        """Apply preset values to the UI"""
        self.preset_name_var.set(preset['name'])
        self.channel_var.set(preset['channel'])
        self.app.midi_channel = preset['channel']
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
        if 0 <= index < len(self.app.midi_presets):
            preset_name = self.app.midi_presets[index]['name']
            del self.app.midi_presets[index]
            self.app.save_midi_config()
            self.refresh_preset_list()
            self.midi_status.config(text=f"MIDI Status: Preset '{preset_name}' deleted", foreground="green")
            
    def refresh_preset_list(self):
        """Update the preset listbox"""
        self.preset_listbox.delete(0, tk.END)
        for preset in self.app.midi_presets:
            self.preset_listbox.insert(tk.END, preset['name'])
            
    def close_connection(self):
        """Close MIDI connection if open"""
        from modules.midi import MIDI_LIBRARY, close_midi_port
        
        if MIDI_LIBRARY == "rtmidi" and self.app.current_midi_port is not None:
            close_midi_port(self.app.midi_outputs, self.app.current_midi_port)