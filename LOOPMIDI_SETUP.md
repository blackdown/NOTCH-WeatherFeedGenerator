# Setting up loopMIDI for NOTCH Data Tool

loopMIDI is a free virtual MIDI port driver for Windows that can help resolve MIDI connectivity issues with the NOTCH Data Tool, particularly when facing DLL errors or hardware compatibility problems.

## Why Use loopMIDI?

1. **Solves DLL errors** - Provides a reliable MIDI interface that doesn't depend on problematic system libraries
2. **Works without hardware** - Test and use MIDI features without physical MIDI devices
3. **Connect applications** - Route MIDI data between NOTCH Data Tool and other music applications
4. **Avoid compatibility issues** - Works reliably even when hardware interfaces have driver problems

## Installation Instructions

### Step 1: Download loopMIDI

1. Visit the official website: [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Click the "download" link for loopMIDI
3. Save the installer to your computer

### Step 2: Install loopMIDI

1. Run the downloaded installer
2. Follow the installation prompts (accept the default settings)
3. Complete the installation

### Step 3: Create a Virtual MIDI Port

1. Launch loopMIDI from your Start menu
2. In the text field at the bottom, enter a name for your virtual port (e.g., "NOTCH MIDI")
3. Click the "+" button to create the port
4. You should now see your port in the list

![loopMIDI Interface](https://www.tobias-erichsen.de/wp-content/uploads/2020/01/loopmidi.png)

### Step 4: Connect NOTCH Data Tool

1. Launch the NOTCH Data Tool
2. Go to the MIDI tab
3. Click the "Refresh Devices" button
4. Select your loopMIDI virtual port from the dropdown menu
5. The status should change to "Connected" with a green indicator

## Troubleshooting

### If loopMIDI Ports Don't Appear

1. Make sure loopMIDI is running (check your system tray)
2. Try creating a new port with a different name
3. Restart the NOTCH Data Tool
4. Try running loopMIDI as administrator

### If You Can't Install loopMIDI

1. Make sure you have administrator privileges on your computer
2. Temporarily disable antivirus software during installation
3. Try the portable version if available

## Using loopMIDI with Other Applications

One advantage of loopMIDI is that it allows you to connect the NOTCH Data Tool to other MIDI software:

1. **With DAWs**: Set your DAW to receive MIDI from the same virtual port
2. **With MIDI monitoring tools**: Connect MIDI-OX or similar tools to inspect the MIDI data
3. **With hardware**: Some MIDI interfaces can route virtual ports to physical MIDI outputs

## Need Help?

If you continue to have issues setting up loopMIDI with the NOTCH Data Tool, please refer to the complete [MIDI Troubleshooting Guide](MIDI_TROUBLESHOOTING.md) or contact support.
