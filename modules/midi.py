"""
MIDI functionality module for NOTCH Data Tool
"""
import os
import json
import time
import sys
import traceback

# Import the MIDI wrapper module - handles DLL issues and import errors gracefully
from modules.midi_wrapper import midi_support

# Set up global variables based on midi_wrapper results
if midi_support and 'library' in midi_support:
    MIDI_LIBRARY = midi_support['library']
    print(f"Using {MIDI_LIBRARY} for MIDI functionality")
    
    # Import the actual module dynamically
    if MIDI_LIBRARY == "rtmidi":
        import rtmidi
    elif MIDI_LIBRARY == "mido":
        import mido
        # Set backend if specified
        if 'backend' in midi_support and midi_support['backend']:
            try:
                mido.set_backend(midi_support['backend'])
                print(f"Using mido backend: {midi_support['backend']}")
            except Exception as e:
                print(f"Error setting mido backend: {e}")
else:
    MIDI_LIBRARY = None
    print("Warning: No MIDI library available. MIDI features will be disabled.")


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
            
            # Try to explicitly enumerate and reset the MIDI system first
            try:
                # Force re-enumeration of MIDI devices by creating and destroying instances
                temp_midi = rtmidi.MidiOut()
                temp_midi.delete()
                time.sleep(0.2)  # Short sleep to allow system to register changes
            except:
                pass
                
            # Try to get ports - do this twice as sometimes the first scan misses devices
            print("First scan for MIDI devices...")
            ports = midi_out.get_ports()
            
            # Second scan often catches more devices
            if not ports:
                print("No ports found on first scan, trying second scan...")
                time.sleep(0.5)  # Wait a bit longer before second scan
                midi_out = rtmidi.MidiOut()  # Create fresh instance
                ports = midi_out.get_ports()
            
            print(f"rtmidi detected {len(ports)} ports: {ports}")
            
            # If no ports found, try reinitializing with different APIs
            if not ports:
                print("Trying alternative APIs...")
                apis = rtmidi.get_compiled_api()
                for api in apis:
                    try:
                        print(f"Trying API: {api}")
                        alt_midi = rtmidi.MidiOut(api)
                        alt_ports = alt_midi.get_ports()
                        if alt_ports:
                            print(f"Found ports using alternate API {api}: {alt_ports}")
                            ports = alt_ports
                            break
                    except Exception as api_error:
                        print(f"Error with API {api}: {api_error}")
            
            # Special handling for common audio interfaces with MIDI
            if not ports:
                try:
                    print("Trying specialized audio interface detection...")
                    # Audio interfaces sometimes need a specific API or initialization
                    for api_name in rtmidi.get_compiled_api():
                        try:
                            # Create MIDI instance with specific API and try a different initialization
                            audio_midi = rtmidi.MidiOut(api_name)
                            audio_midi.open_virtual_port("TEMP_PORT")
                            time.sleep(0.3)
                            audio_midi.close_port()
                            
                            # Try getting ports again
                            audio_ports = audio_midi.get_ports()
                            if audio_ports:
                                print(f"Found ports after virtual port test: {audio_ports}")
                                ports = audio_ports
                                break
                        except Exception as virtual_error:
                            print(f"Virtual port method failed: {virtual_error}")
                except Exception as e:
                    print(f"Special audio interface detection failed: {e}")
                    
        except Exception as e:
            print(f"Error getting MIDI ports with rtmidi: {e}")
    elif MIDI_LIBRARY == "mido":
        # Create a list to track tried backends
        tried_backends = []
        
        try:
            # First try rtmidi backend which is more likely to work on Windows
            try:
                print("Trying preferred mido backend: mido.backends.rtmidi")
                mido.set_backend('mido.backends.rtmidi')
                tried_backends.append('mido.backends.rtmidi')
                ports = mido.get_output_names()
                print(f"mido (rtmidi) detected {len(ports)} ports: {ports}")
                if ports:
                    return {
                        'ports': ports,
                        'system_devices': []  # No need for system devices if we have ports
                    }
            except Exception as rtmidi_error:
                print(f"rtmidi backend failed: {rtmidi_error}")
            
            # Try to get available backends
            try:
                backends = mido.backend.get_api()
            except Exception as api_err:
                print(f"Error getting mido backends: {api_err}")
                backends = ['mido.backends.rtmidi']  # Default fallback
                
            # Try each backend, skipping portmidi on Windows
            for backend in backends:
                # Skip backends we've already tried
                if backend in tried_backends:
                    continue
                
                # Skip portmidi on Windows as it often has DLL issues
                if backend == 'mido.backends.portmidi' and os.name == 'nt':
                    print("Skipping portmidi backend on Windows due to common DLL issues")
                    continue
                    
                try:
                    print(f"Trying mido backend: {backend}")
                    mido.set_backend(backend)
                    tried_backends.append(backend)
                    ports = mido.get_output_names()
                    print(f"mido ({backend}) detected {len(ports)} ports: {ports}")
                    if ports:
                        break
                except Exception as backend_error:
                    print(f"Error with backend {backend}: {backend_error}")
        except Exception as e:
            print(f"Error getting MIDI ports with mido: {e}")
      # If still no ports but we have a MIDI library, try checking with system commands
    system_midi_info = []
    if not ports and MIDI_LIBRARY and os.name == 'nt':  # Windows
        try:
            print("Attempting system MIDI port detection...")
            import subprocess
            
            # Check for MIDI devices
            result = subprocess.run(['powershell', '-Command', "Get-WmiObject Win32_PnPEntity | Where-Object{$_.Name -match 'MIDI'} | Select-Object Name"], capture_output=True, text=True)
            midi_lines = result.stdout.strip().split('\n')
            for line in midi_lines:
                if line.strip() and not line.startswith("Name"):
                    device_name = line.strip()
                    print(f"System detected MIDI device: {device_name}")
                    system_midi_info.append(device_name)
            
            # Check audio interfaces that may have MIDI capabilities
            print("Checking for audio interfaces with possible MIDI functionality...")
            result = subprocess.run(['powershell', '-Command', "Get-WmiObject Win32_PnPEntity | Where-Object{$_.Name -match 'Audio|Sound|Interface'} | Select-Object Name"], capture_output=True, text=True)
            audio_lines = result.stdout.strip().split('\n')
            for line in audio_lines:
                if line.strip() and not line.startswith("Name"):
                    device_name = line.strip()
                    print(f"System detected audio device: {device_name}")
                    system_midi_info.append(f"Audio Interface: {device_name}")
                    
            # If we found some system devices, try once more with the main MIDI library
            if system_midi_info and MIDI_LIBRARY == "rtmidi":
                print("System found devices, attempting MIDI reconnection...")
                try:
                    # Force device re-enumeration 
                    midi_out = rtmidi.MidiOut()
                    midi_out.delete()
                    time.sleep(1.0)  # Longer wait
                    
                    # Try to open port 0 - sometimes audio interfaces default to this
                    try_midi = rtmidi.MidiOut()
                    if try_midi.get_port_count() > 0:
                        try_ports = try_midi.get_ports()
                        print(f"After forced reconnect, found ports: {try_ports}")
                        ports = try_ports
                except Exception as reconnect_error:
                    print(f"Reconnection attempt failed: {reconnect_error}")
                    
        except Exception as e:
            print(f"Error with system MIDI detection: {e}")
    
    # Return both the detected ports and system info for UI display
    return {
        'ports': ports,
        'system_devices': system_midi_info
    }

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

def detect_audio_interface_midi():
    """
    Specialized detection for audio interfaces with MIDI capabilities
    
    This function tries several approaches specifically tailored for audio interfaces
    that have MIDI ports which might not be detected by standard methods.
    
    Returns:
        list: List of detected MIDI ports
    """
    ports = []
    
    if MIDI_LIBRARY == "rtmidi":
        try:
            import rtmidi
            
            print("Attempting specialized audio interface MIDI detection...")
            
            # Approach 1: Create and destroy MIDI instance to force re-enumeration
            try:
                temp_midi = rtmidi.MidiOut()
                temp_midi.delete()
                time.sleep(1.0)  # Longer delay for hardware to respond
                
                midi_out = rtmidi.MidiOut()
                ports = midi_out.get_ports()
                if ports:
                    print(f"Audio interface detection found ports: {ports}")
                    return ports
            except Exception as e:
                print(f"Re-enumeration approach failed: {e}")
            
            # Approach 2: Try alternate APIs specifically
            apis = rtmidi.get_compiled_api()
            print(f"Trying alternate APIs for audio interface: {apis}")
            
            for api in apis:
                try:
                    midi_out = rtmidi.MidiOut(api)
                    api_ports = midi_out.get_ports()
                    if api_ports:
                        print(f"Found audio interface ports with API {api}: {api_ports}")
                        return api_ports
                except Exception as api_err:
                    print(f"API {api} failed: {api_err}")
            
            # Approach 3: Try to create a virtual port - sometimes triggers detection
            try:
                midi_out = rtmidi.MidiOut()
                midi_out.open_virtual_port("NOTCH_DATA_TOOL_DETECT")
                time.sleep(0.5)
                midi_out.close_port()
                time.sleep(0.5)
                
                # Check if this makes devices appear
                new_midi = rtmidi.MidiOut()
                new_ports = new_midi.get_ports()
                if new_ports:
                    print(f"Virtual port approach found ports: {new_ports}")
                    return new_ports
            except Exception as vp_err:
                print(f"Virtual port approach failed: {vp_err}")
                
            # Approach 4: Try direct port indices
            for i in range(4):  # Try first 4 port indices
                try:
                    midi_out = rtmidi.MidiOut()
                    port_count = midi_out.get_port_count()
                    
                    # If index exists
                    if i < port_count:
                        port_name = midi_out.get_port_name(i)
                        if port_name:
                            ports.append(port_name)
                    
                    # Try direct access
                    midi_out.open_port(i)
                    time.sleep(0.1)
                    midi_out.close_port()
                    
                    # Check if now available
                    new_midi = rtmidi.MidiOut()
                    new_ports = new_midi.get_ports()
                    if new_ports:
                        print(f"Direct port access found ports: {new_ports}")
                        return new_ports
                except Exception as idx_err:
                    print(f"Port index {i} approach failed: {idx_err}")
        
        except Exception as e:
            print(f"Audio interface detection error: {e}")
    
    elif MIDI_LIBRARY == "mido":
        try:
            import mido
            
            print("Attempting audio interface detection with mido...")
            
            # Try different backends with mido
            for backend_name in ['mido.backends.rtmidi', 'mido.backends.portmidi']:
                try:
                    mido.set_backend(backend_name)
                    ports = mido.get_output_names()
                    if ports:
                        print(f"Audio interface detection found ports with backend {backend_name}: {ports}")
                        return ports
                except Exception as backend_err:
                    print(f"Backend {backend_name} failed: {backend_err}")
        except Exception as e:
            print(f"Mido audio interface detection error: {e}")
    
    return ports

def force_open_midi_port(port_name):
    """
    Force open a MIDI port by name, useful for audio interfaces
    
    Args:
        port_name (str): Name of the MIDI port to open
        
    Returns:
        tuple: (success, port_index, message)
    """
    if not MIDI_LIBRARY:
        return (False, None, "No MIDI library installed")
        
    if MIDI_LIBRARY == "rtmidi":
        try:
            # Create a fresh instance
            from modules.midi import MIDI_LIBRARY
            
            if not hasattr(sys.modules[__name__], 'rtmidi'):
                print("rtmidi module not available for force_open_midi_port")
                return (False, None, "MIDI library not properly initialized")
                
            rtmidi_module = sys.modules[__name__].rtmidi
            midi_out = rtmidi_module.MidiOut()
            ports = midi_out.get_ports()
            
            # Check if the port name is in the list
            for i, p in enumerate(ports):
                if port_name in p:
                    try:
                        midi_out.open_port(i)
                        # Test with empty CC message
                        midi_out.send_message([0xB0, 0, 0])
                        return (True, i, f"Successfully connected to {p}")
                    except Exception as e:
                        return (False, None, f"Error opening port {p}: {e}")
            
            # If port not found by name, try direct index for the first few ports
            if not ports:
                for i in range(4):
                    try:
                        midi_out = rtmidi_module.MidiOut()
                        midi_out.open_port(i)
                        midi_out.send_message([0xB0, 0, 0])
                        actual_name = f"Port #{i}"
                        try:
                            actual_name = midi_out.get_port_name(i)
                        except:
                            pass
                        return (True, i, f"Connected to port index {i} ({actual_name})")
                    except:
                        pass
            
            return (False, None, f"Port '{port_name}' not found")
            
        except Exception as e:
            return (False, None, f"Error in force_open_midi_port: {e}")
    
    elif MIDI_LIBRARY == "mido":
        try:
            import mido
            
            # Try to open the named port
            ports = mido.get_output_names()
            for p in ports:
                if port_name in p:
                    try:
                        mido.open_output(p)
                        return (True, p, f"Successfully connected to {p}")
                    except Exception as e:
                        return (False, None, f"Error opening port {p}: {e}")
            
            return (False, None, f"Port '{port_name}' not found in {ports}")
            
        except Exception as e:
            return (False, None, f"Error in force_open_midi_port: {e}")
    
    return (False, None, "Unsupported MIDI library")