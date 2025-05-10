"""
MIDI functionality module for NOTCH Data Tool
"""
import os
import json

# Try importing MIDI libraries with fallbacks
try:
    import rtmidi
    MIDI_LIBRARY = "rtmidi"
except ImportError:
    try:
        import mido
        MIDI_LIBRARY = "mido"
    except ImportError:
        MIDI_LIBRARY = None


def init_midi():
    """Initialize MIDI output"""
    midi_outputs = {}
    
    if MIDI_LIBRARY == "rtmidi":
        try:
            midi_outputs["rtmidi"] = rtmidi.MidiOut()
        except Exception as e:
            print(f"Error initializing MIDI: {e}")
    elif MIDI_LIBRARY == "mido":
        # mido doesn't need initialization here
        pass
    
    return midi_outputs

def get_midi_ports():
    """Get available MIDI ports"""
    ports = []
    
    if MIDI_LIBRARY == "rtmidi":
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
        except Exception as e:
            print(f"Error getting MIDI ports: {e}")
    elif MIDI_LIBRARY == "mido":
        try:
            ports = mido.get_output_names()
        except Exception as e:
            print(f"Error getting MIDI ports: {e}")
    
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