"""
MIDI module wrapper that handles module errors gracefully
"""
import os
import sys
import importlib
import traceback

# Available MIDI libraries to try
midi_libraries = [
    {
        "name": "rtmidi",
        "module": "rtmidi",
        "backends": []  # rtmidi manages its own backends
    },
    {
        "name": "mido",
        "module": "mido", 
        "backends": [
            "mido.backends.rtmidi",  # Preferred backend
            None  # Default backend
        ]
    }
]

# Global tracking variables
MIDI_AVAILABLE = False
MIDI_MODULE = None
MIDI_BACKEND = None
MIDI_ERROR = None

def safe_import(module_name):
    """Safely import a module without crashing"""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        return None
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        return None

def init_midi():
    """Initialize MIDI support and return the best available library"""
    global MIDI_AVAILABLE, MIDI_MODULE, MIDI_BACKEND, MIDI_ERROR
    
    print("Initializing MIDI support...")
    dll_errors = []
    
    for lib in midi_libraries:
        module = safe_import(lib["module"])
        if not module:
            continue
            
        print(f"Found {lib['name']} library")
        
        # If rtmidi, use directly
        if lib["name"] == "rtmidi":
            try:
                # Test if we can actually use it
                midi_out = module.MidiOut()
                MIDI_AVAILABLE = True
                MIDI_MODULE = module
                return {"library": "rtmidi", "module": module}
            except Exception as e:
                error_msg = str(e)
                print(f"rtmidi error: {error_msg}")
                # Check for common DLL errors
                if "cannot find" in error_msg.lower() and ".dll" in error_msg.lower():
                    dll_errors.append(f"rtmidi: {error_msg}")
                continue
                
        # If mido, try backends
        elif lib["name"] == "mido":
            # Handle mido backends
            working_backend = None
            
            for backend in lib["backends"]:
                try:
                    if backend:
                        module.set_backend(backend)
                        print(f"Set mido backend to {backend}")
                    
                    # Test if the backend works
                    ports = module.get_output_names()
                    print(f"Mido detected {len(ports)} ports")
                    
                    # Backend works
                    working_backend = backend
                    MIDI_AVAILABLE = True
                    MIDI_MODULE = module
                    MIDI_BACKEND = backend
                    return {"library": "mido", "module": module, "backend": backend}
                except Exception as e:
                    error_msg = str(e)
                    if "portmidi.dll" in error_msg.lower():
                        # Specific portmidi.dll error
                        print(f"PortMidi DLL error, skipping this backend")
                        dll_errors.append(f"mido: {error_msg}")
                    elif ".dll" in error_msg.lower() and ("cannot find" in error_msg.lower() or "not found" in error_msg.lower()):
                        print(f"DLL error detected: {error_msg}")
                        dll_errors.append(f"mido: {error_msg}")
                    else:
                        print(f"Mido backend {backend} error: {e}")
            
            # If no backend worked but mido is available, return mido with blank backend
            if working_backend is None:
                try:
                    # Try one more time with rtmidi backend explicitly
                    try:
                        module.set_backend('mido.backends.rtmidi')
                        ports = module.get_output_names()
                        MIDI_AVAILABLE = True
                        MIDI_MODULE = module
                        MIDI_BACKEND = 'mido.backends.rtmidi'
                        return {"library": "mido", "module": module, "backend": 'mido.backends.rtmidi'}
                    except Exception as e:
                        if ".dll" in str(e).lower():
                            dll_errors.append(f"mido rtmidi: {e}")
                        pass
                        
                    # Last resort - just return mido with default backend even if ports can't be detected
                    try:
                        # Don't try to enumerate ports - just return the module
                        MIDI_AVAILABLE = True
                        MIDI_MODULE = module
                        return {"library": "mido", "module": module}
                    except Exception as e:
                        print(f"Mido final attempt error: {e}")
                except Exception as e:
                    print(f"Mido final attempt error: {e}")
    
    # No working MIDI library found - capture specific DLL errors
    if dll_errors:
        MIDI_ERROR = "DLL issues detected: " + "; ".join(dll_errors)
        print(f"MIDI DLL errors: {MIDI_ERROR}")
    else:
        MIDI_ERROR = "No working MIDI library found"
    
    return None

# Export results to a simple API
midi_support = init_midi()
