"""
MIDI functionality module for NOTCH Data Tool
"""
import os
import json
import time
import sys

# Try importing MIDI libraries with fallbacks
try:
    import rtmidi
    MIDI_LIBRARY = "rtmidi"
    print(f"Using rtmidi library - version: {rtmidi.get_compiled_api()}")
except ImportError:
    try:
        import mido
        MIDI_LIBRARY = "mido"
        print(f"Using mido library")
    except ImportError:
        MIDI_LIBRARY = None
        print("Warning: No MIDI library found. Install python-rtmidi or mido to use MIDI features.")


def init_midi():
    """Initialize MIDI output"""
    midi_outputs = {}
    
    if MIDI_LIBRARY == "rtmidi":
        try:
            # Try to enumerate APIs first to ensure proper initialization
            apis = rtmidi.get_compiled_api()
            print(f"Available MIDI APIs: {apis}")
            
            # Initialize the MidiOut object with the first available API
            midi_outputs["rtmidi"] = rtmidi.MidiOut()
            
            # Check for ports immediately to ensure the interface is working
            ports = midi_outputs["rtmidi"].get_ports()
            print(f"MIDI ports detected during initialization: {len(ports)}")
            if len(ports) > 0:
                print(f"First port: {ports[0]}")
        except Exception as e:
            print(f"Error initializing MIDI: {e}")
            if hasattr(e, "__traceback__"):
                import traceback
                traceback.print_tb(e.__traceback__)
    elif MIDI_LIBRARY == "mido":
        try:
            # Check backends
            backends = mido.backend.get_api()
            print(f"Available MIDI backends: {backends}")
            
            # Initialize mido (no explicit initialization needed)
            ports = mido.get_output_names()
            print(f"MIDI ports detected during initialization: {len(ports)}")
            if len(ports) > 0:
                print(f"First port: {ports[0]}")
        except Exception as e:
            print(f"Error initializing MIDI with mido: {e}")
    
    return midi_outputs

def get_midi_ports():
    """Get available MIDI ports"""
    ports = []
    
    if MIDI_LIBRARY == "rtmidi":
        try:
            # Create a fresh instance to get the latest port list
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            print(f"rtmidi detected {len(ports)} ports: {ports}")
            
            # If no ports found, try reinitializing with different APIs
            if not ports:
                apis = rtmidi.get_compiled_api()
                for api in apis:
                    try:
                        alt_midi = rtmidi.MidiOut(api)
                        alt_ports = alt_midi.get_ports()
                        if alt_ports:
                            print(f"Found ports using alternate API {api}: {alt_ports}")
                            ports = alt_ports
                            break
                    except:
                        pass
        except Exception as e:
            print(f"Error getting MIDI ports with rtmidi: {e}")
    elif MIDI_LIBRARY == "mido":
        try:
            # Try multiple backends if available
            backends = mido.backend.get_api()
            for backend in backends:
                try:
                    mido.set_backend(backend)
                    ports = mido.get_output_names()
                    print(f"mido ({backend}) detected {len(ports)} ports: {ports}")
                    if ports:
                        break
                except:
                    pass
            
            # If still no ports, try the default backend again
            if not ports:
                mido.set_backend('mido.backends.rtmidi')  # Try explicit backend
                ports = mido.get_output_names()
        except Exception as e:
            print(f"Error getting MIDI ports with mido: {e}")
    
    # If still no ports but we have a MIDI library, try checking with system commands
    if not ports and MIDI_LIBRARY and os.name == 'nt':  # Windows
        try:
            print("Attempting system MIDI port detection...")
            import subprocess
            result = subprocess.run(['powershell', '-Command', "Get-WmiObject Win32_PnPEntity | Where-Object{$_.Name -match 'MIDI'} | Select-Object Name"], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith("Name"):
                    print(f"System detected MIDI device: {line.strip()}")
        except Exception as e:
            print(f"Error with system MIDI detection: {e}")
    
    return ports

def send_midi_message(midi_outputs, port, message_type, channel, data1, data2=0):
    """
    Send a MIDI message
    
    Args:
        midi_outputs: MIDI output object
        port: Port to send to
        message_type: Type of message (note_on, note_off, control_change)
        channel: MIDI channel (1-16)
        data1: First data byte (note number or CC number)
        data2: Second data byte (velocity or CC value)
    """
    channel = channel - 1  # Convert to 0-15 range for internal use
    
    if MIDI_LIBRARY == "rtmidi":
        try:
            if message_type == "note_on":
                msg = [0x90 + channel, data1, data2]
            elif message_type == "note_off":
                msg = [0x80 + channel, data1, data2]
            elif message_type == "control_change":
                msg = [0xB0 + channel, data1, data2]
            else:
                return False
                
            midi_outputs["rtmidi"].send_message(msg)
            return True
        except Exception as e:
            print(f"MIDI Error: {str(e)}")
            return False
            
    elif MIDI_LIBRARY == "mido":
        try:
            with mido.open_output(port) as mido_port:
                mido_msg = mido.Message(
                    message_type,
                    note=data1 if message_type in ["note_on", "note_off"] else None,
                    velocity=data2 if message_type in ["note_on", "note_off"] else None,
                    control=data1 if message_type == "control_change" else None,
                    value=data2 if message_type == "control_change" else None,
                    channel=channel
                )
                mido_port.send(mido_msg)
            return True
        except Exception as e:
            print(f"MIDI Error: {str(e)}")
            return False
    
    return False

def close_midi_port(midi_outputs, port_index=None):
    """Close a MIDI port connection"""
    if MIDI_LIBRARY == "rtmidi":
        try:
            if port_index is not None:
                midi_outputs["rtmidi"].close_port()
            return True
        except Exception as e:
            print(f"Error closing MIDI port: {e}")
            return False
    
    return True  # mido handles port closing in its context manager

def load_midi_config(config_file):
    """Load MIDI configuration from file"""
    presets = []
    channel = 1
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                data = json.load(f)
                presets = data.get('presets', [])
                channel = data.get('last_channel', 1)
    except Exception as e:
        print(f"Error loading MIDI config: {e}")
    
    return {
        'presets': presets,
        'channel': channel
    }

def save_midi_config(config_file, presets, channel):
    """Save MIDI configuration to file"""
    try:
        data = {
            'presets': presets,
            'last_channel': channel
        }
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving MIDI config: {e}")
        return False