# MIDI Alternatives Documentation

This document describes potential alternatives for MIDI functionality in case `python-rtmidi` cannot be installed.

## MIDI Library Options

1. **python-rtmidi** (preferred)
   - Comprehensive MIDI functionality
   - Requires C++ compiler for installation
   - Best performance and feature set

2. **mido**
   - Pure Python implementation
   - No compilation required
   - May use python-rtmidi as backend if available

3. **pygame.midi**
   - Part of PyGame library
   - Doesn't require separate C++ compiler
   - More limited feature set

## Installation Instructions

### If python-rtmidi fails to install:

1. **Install Visual C++ Build Tools**
   - Download Visual Studio Build Tools from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Select "Desktop development with C++"
   - This allows python-rtmidi to compile properly

2. **Use a pre-built wheel**
   - Try installing a specific version: `pip install python-rtmidi==1.4.9`
   - May avoid compilation issues on some systems

3. **Switch to mido**
   - Install with: `pip install mido`
   - Update imports in code from `import rtmidi` to `import mido`

### Code Change Required for mido:

```python
# If using mido instead of rtmidi
midi_out = mido.open_output(port_name)
message = mido.Message('note_on', note=60, velocity=64, channel=0)
midi_out.send(message)
```

vs. rtmidi:

```python
# Original rtmidi approach
midi_out = rtmidi.MidiOut()
midi_out.open_port(port_index)
midi_out.send_message([0x90, note, velocity])  # Note on message
```

For most users, the automatic fallback in the build script should handle this transition seamlessly.
