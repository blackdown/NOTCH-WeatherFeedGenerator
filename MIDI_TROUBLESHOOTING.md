# MIDI Troubleshooting Guide

This guide will help you resolve common MIDI connectivity issues with the NOTCH Data Tool.

## Common MIDI Issues

### DLL Errors

If you receive an error related to "portmidi.dll" or "cannot find specified module", this is typically caused by missing MIDI libraries on your system. Here are some solutions:

1. **Install loopMIDI**:
   - Download and install loopMIDI from [here](https://www.tobias-erichsen.de/software/loopmidi.html)
   - Once installed, open loopMIDI and create at least one virtual MIDI port
   - In the NOTCH Data Tool, click "Refresh Devices" to detect the virtual port

2. **Install Audio Interface Drivers**:
   - If you're using an audio interface with MIDI capabilities, ensure you have the latest drivers installed
   - Some audio interfaces require specific software to enable MIDI functionality

### No MIDI Devices Detected

If the application doesn't find any MIDI devices, try these steps:

1. **Use Audio Interface Compatibility Mode**:
   - If no MIDI devices are found, the application will automatically offer to try the audio interface compatibility mode
   - This mode uses alternative methods to detect certain types of audio interfaces

2. **Manual MIDI Port Entry**:
   - Right-click on the MIDI port dropdown and select "Force Manual Port"
   - Enter the exact name of your MIDI port (e.g., "MIDI Out 1" or "Audio Interface MIDI")

3. **Check USB Connections**:
   - Make sure your MIDI device or audio interface is properly connected
   - Try a different USB port or cable

## Using Virtual MIDI with loopMIDI

loopMIDI creates virtual MIDI ports that allow different music applications to communicate with each other. This is particularly useful if:

1. You want to route MIDI data from one application to another
2. You want to test MIDI functionality without physical hardware
3. Your hardware MIDI devices aren't being detected properly

**Steps to set up loopMIDI:**

1. **Install and Run loopMIDI**:
   - Download and install from [Tobias Erichsen's website](https://www.tobias-erichsen.de/software/loopmidi.html)
   - Run loopMIDI as administrator

2. **Create a Virtual Port**:
   - In the loopMIDI application, enter a name for your virtual port (e.g., "NOTCH MIDI")
   - Click the "+" button to create the virtual port

3. **Connect in NOTCH Data Tool**:
   - Open the NOTCH Data Tool
   - Go to the MIDI tab
   - Click "Refresh Devices"
   - Select your virtual port from the dropdown menu

4. **Routing MIDI Data**:
   - Use other applications like MIDI-OX or DAWs to connect to the same virtual port
   - All MIDI data sent from NOTCH Data Tool will now be available to these applications

## Advanced Audio Interface Detection

Some audio interfaces have MIDI capabilities but aren't detected by standard MIDI libraries. The Audio Interface Compatibility Mode helps with this:

1. **When to Use**:
   - Your audio interface has MIDI ports but isn't showing in the MIDI device list
   - You get DLL errors but know your device supports MIDI

2. **How to Activate**:
   - Click "Refresh Devices" in the MIDI tab
   - If no devices are found, click "Yes" when prompted to try audio interface compatibility mode
   - Alternatively, right-click the port dropdown and select "Audio Interface Mode"

## Contact Support

If you continue to experience MIDI issues after trying these solutions, please contact support with:

1. The exact error message you're receiving
2. The name and model of your audio interface or MIDI device
3. A list of steps you've already tried
4. Information on whether virtual MIDI with loopMIDI works for you

This information will help us diagnose and resolve your specific issue more quickly.
