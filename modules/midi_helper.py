"""
Simple MIDI compatibility module for audio interfaces
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

def check_loopmidi_installation():
    """
    Check if loopMIDI is installed on the system
    
    Returns:
        bool: True if loopMIDI appears to be installed
    """
    if os.name != 'nt':  # Only relevant on Windows
        return False
        
    try:
        # Check for loopMIDI in registry or program files
        result = subprocess.run(['powershell', '-Command', 
                               "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Where-Object {$_.DisplayName -like '*loopMIDI*'}"], 
                               capture_output=True, text=True, timeout=3)
                               
        if "DisplayName" in result.stdout and "loopMIDI" in result.stdout:
            print("loopMIDI appears to be installed")
            return True
            
        # Check in Program Files
        program_files = ["C:\\Program Files", "C:\\Program Files (x86)"]
        for path in program_files:
            if os.path.exists(os.path.join(path, "Tobias Erichsen", "loopMIDI")):
                print("loopMIDI found in Program Files")
                return True
                
        return False
    except Exception as e:
        print(f"Error checking for loopMIDI: {e}")
        return False

def check_midi_availability():
    """
    Check if MIDI devices are available in the system
    
    Returns:
        bool: True if MIDI devices are detected
    """
    if os.name == 'nt':  # Windows
        try:
            # Check both MIDI devices and loopMIDI
            has_loopmidi = check_loopmidi_installation()
            
            result = subprocess.run(['powershell', '-Command', 
                                   "Get-WmiObject Win32_PnPEntity | Where-Object{$_.Name -match 'MIDI|Audio'} | Select-Object Name"], 
                                   capture_output=True, text=True, timeout=3)
                                   
            lines = result.stdout.strip().split('\n')
            # Filter non-empty lines that don't start with "Name"
            devices = [line.strip() for line in lines if line.strip() and not line.startswith("Name")]
            
            # Check specifically for loopMIDI devices
            result_virtual = subprocess.run(['powershell', '-Command', 
                                          "Get-WmiObject Win32_PnPEntity | Where-Object{$_.Name -match 'loop|virtual|midi'} | Select-Object Name"], 
                                          capture_output=True, text=True, timeout=3)
                                          
            virtual_lines = result_virtual.stdout.strip().split('\n')
            virtual_devices = [line.strip() for line in virtual_lines if line.strip() and not line.startswith("Name")]
            
            for device in virtual_devices:
                if device not in devices:
                    devices.append(device)
            
            if devices:
                print(f"System detected potential MIDI devices: {devices}")
                return True
            elif has_loopmidi:
                print("loopMIDI installed but no active ports detected")
                return True
            else:
                print("No MIDI devices detected in system")
                return False
        except Exception as e:
            print(f"Error checking MIDI availability: {e}")
            return False
    else:  # Other OS
        # For macOS/Linux, we can't easily check - assume MIDI is available
        return True

def show_midi_troubleshooter(error_message=None, is_dll_error=False):
    """
    Show a MIDI troubleshooting dialog with common solutions
    
    Args:
        error_message (str): Specific error message to display
        is_dll_error (bool): Whether the error is DLL-related
    """
    # Get the state of loopMIDI installation
    has_loopmidi = check_loopmidi_installation()
    
    # Create the dialog window
    dialog = tk.Toplevel()
    dialog.title("MIDI Device Troubleshooter")
    dialog.geometry("600x550")
    dialog.resizable(True, True)
    
    # Add explanatory text
    header = tk.Label(dialog, text="MIDI Device Troubleshooter", font=("Arial", 16, "bold"))
    header.pack(pady=10)
    
    # Problem explanation
    problem_text = "The application is unable to connect to MIDI devices through standard methods.\n"
    
    if is_dll_error:
        problem_text += "A DLL (Dynamic Link Library) file is missing or cannot be loaded."
    else:
        problem_text += "This could be due to missing libraries or hardware connection issues."
        
    if error_message:
        problem_text += f"\n\nError details: {error_message}"
    
    problem = tk.Label(dialog, text=problem_text, justify=tk.LEFT, wraplength=550)
    problem.pack(pady=5, padx=20, anchor="w")
    
    # Create a frame for the solutions
    solutions_frame = tk.Frame(dialog)
    solutions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Add a text widget with scrollbar for solutions
    scrollbar = tk.Scrollbar(solutions_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    solutions_text = tk.Text(solutions_frame, wrap=tk.WORD, height=18, width=70)
    solutions_text.pack(fill=tk.BOTH, expand=True)
    
    # Connect scrollbar to text widget
    scrollbar.config(command=solutions_text.yview)
    solutions_text.config(yscrollcommand=scrollbar.set)
    
    # Add solution text
    solutions_text.insert(tk.END, "RECOMMENDED SOLUTIONS:\n\n")
    
    # Make virtual MIDI option the top recommendation for DLL errors
    if is_dll_error:
        solutions_text.insert(tk.END, "1. Install loopMIDI (Virtual MIDI Driver) - RECOMMENDED\n")
        solutions_text.insert(tk.END, "   • This is the fastest and most reliable solution\n")
        solutions_text.insert(tk.END, "   • Download from: https://www.tobias-erichsen.de/software/loopmidi.html\n")
        solutions_text.insert(tk.END, "   • After installation, open loopMIDI and click the + button to create a virtual port\n")
        if has_loopmidi:
            solutions_text.insert(tk.END, "   • loopMIDI appears to be installed, just create a port if you haven't already\n\n")
        else:
            solutions_text.insert(tk.END, "   • After installing, restart this application\n\n")
        
        solutions_text.insert(tk.END, "2. Fix the missing DLL issue\n")
        solutions_text.insert(tk.END, "   • Download and install the latest Visual C++ Redistributable from Microsoft\n")
        solutions_text.insert(tk.END, "   • URL: https://aka.ms/vs/17/release/vc_redist.x64.exe\n")
        solutions_text.insert(tk.END, "   • This resolves most DLL issues with MIDI libraries\n\n")
        
        solutions_text.insert(tk.END, "3. Switch MIDI backend\n")
        solutions_text.insert(tk.END, "   • The application will automatically try different backends\n")
        solutions_text.insert(tk.END, "   • You can manually install: pip install --only-binary :all: python-rtmidi\n\n")
    else:
        # Standard solutions for non-DLL issues
        solutions_text.insert(tk.END, "1. Install Visual C++ Redistributable\n")
        solutions_text.insert(tk.END, "   • Download and install the latest Visual C++ Redistributable from Microsoft\n")
        solutions_text.insert(tk.END, "   • URL: https://aka.ms/vs/17/release/vc_redist.x64.exe\n\n")
        
        solutions_text.insert(tk.END, "2. Try using the loopMIDI virtual MIDI driver\n")
        solutions_text.insert(tk.END, "   • Download from: https://www.tobias-erichsen.de/software/loopmidi.html\n")
        solutions_text.insert(tk.END, "   • Install and create a virtual MIDI port\n")
        if has_loopmidi:
            solutions_text.insert(tk.END, "   • loopMIDI appears to be installed, just create a port if you haven't already\n\n")
        else:
            solutions_text.insert(tk.END, "   • After installing, restart this application\n\n")
    
    # Common solutions for all issues
    solutions_text.insert(tk.END, f"{3 if is_dll_error else 3}. Install or reinstall the audio interface drivers\n")
    solutions_text.insert(tk.END, "   • Visit your audio interface manufacturer's website\n")
    solutions_text.insert(tk.END, "   • Download and install the latest drivers\n\n")
    
    solutions_text.insert(tk.END, f"{4 if is_dll_error else 4}. Check if another application is using the MIDI device\n")
    solutions_text.insert(tk.END, "   • Close any DAWs or MIDI applications that might be running\n")
    solutions_text.insert(tk.END, "   • Try disconnecting and reconnecting your MIDI device\n\n")
    
    solutions_text.insert(tk.END, f"{5 if is_dll_error else 5}. If you're using an audio interface with MIDI\n")
    solutions_text.insert(tk.END, "   • Make sure it's powered on before starting the application\n")
    solutions_text.insert(tk.END, "   • Check if MIDI functionality needs to be enabled in the interface's control panel\n\n")
    
    # Make the text widget read-only
    solutions_text.config(state=tk.DISABLED)
    
    # Button frame
    button_frame = tk.Frame(dialog)
    button_frame.pack(fill=tk.X, pady=10)
    
    # Download loopMIDI button
    if not has_loopmidi:
        download_button = tk.Button(
            button_frame, 
            text="Download loopMIDI", 
            command=lambda: os.startfile("https://www.tobias-erichsen.de/software/loopmidi.html"),
            width=15
        )
        download_button.pack(side=tk.LEFT, padx=20, pady=5)
    
    # Close button
    close_button = tk.Button(button_frame, text="Close", command=dialog.destroy, width=10)
    close_button.pack(side=tk.RIGHT, padx=20, pady=5)
    
    # Center the dialog on the screen
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    # Make the dialog modal
    dialog.transient()
    dialog.grab_set()
    dialog.focus_set()
    
    return dialog

if __name__ == "__main__":
    # Simple test if run directly
    has_midi = check_midi_availability()
    print(f"MIDI available: {has_midi}")
    
    # Create a test window and show the troubleshooter
    root = tk.Tk()
    root.withdraw()
    dialog = show_midi_troubleshooter()
    root.mainloop()
