import os
import sys
import subprocess
import pkg_resources
import platform

required_packages = {'pyinstaller', 'requests', 'python-rtmidi'}

def install_requirements():
    """Install required packages if they're not already installed"""
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required_packages - installed
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print("Installation completed.")
        except Exception as e:
            print(f"Error installing packages: {e}")
            return False
    return True

def find_pyinstaller():
    """Find the PyInstaller executable in the Python scripts directory"""
    # Check if PyInstaller is directly accessible in PATH
    try:
        subprocess.run(['pyinstaller', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'pyinstaller'
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
        
    # Try to find it in the Scripts directory
    if platform.system() == 'Windows':
        # First check the common locations
        possible_paths = [
            os.path.join(sys.prefix, 'Scripts', 'pyinstaller.exe'),
            os.path.join(sys.prefix, 'Scripts', 'pyinstaller'),
            # For Windows Store Python
            os.path.join(os.path.dirname(sys.executable), 'Scripts', 'pyinstaller.exe')
        ]
        
        # Add the warning path we received
        warning_path = r'C:\Users\ab\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\pyinstaller.exe'
        possible_paths.append(warning_path)
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found PyInstaller at: {path}")
                return path
    
    print("Warning: PyInstaller not found in PATH or Scripts directory.")
    print("Falling back to module execution method.")
    return [sys.executable, '-m', 'PyInstaller']

def build_executable():
    """Build the executable using PyInstaller"""
    try:
        print("Building executable with PyInstaller...")
        
        # Create icon if it doesn't exist (simple placeholder)
        if not os.path.exists('weather.ico'):
            try:
                from PIL import Image, ImageDraw
                
                # Create a simple weather icon
                img = Image.new('RGBA', (256, 256), color=(73, 109, 137, 255))
                d = ImageDraw.Draw(img)
                
                # Draw a sun
                d.ellipse((50, 50, 206, 206), fill=(255, 200, 0))
                
                # Draw a cloud
                cloud_color = (240, 240, 240)
                d.ellipse((100, 120, 200, 220), fill=cloud_color)
                d.ellipse((80, 150, 180, 250), fill=cloud_color)
                d.ellipse((150, 150, 250, 250), fill=cloud_color)
                d.rectangle((80, 180, 250, 250), fill=cloud_color)
                
                img.save('weather.ico')
                print("Created weather.ico icon")
            except ImportError:
                print("Pillow not installed, skipping icon creation")
                pass  # Skip icon creation if Pillow is not installed
        
        # Find PyInstaller executable
        pyinstaller_cmd = find_pyinstaller()
        
        # Build command arguments
        if isinstance(pyinstaller_cmd, list):            command = pyinstaller_cmd + [
                '--onefile',
                '--windowed',
                '--name=NOTCH-Data-Tool',  # Updated name to remove spaces
                '--add-data=readme.md;.',
            ]
        else:
            command = [
                pyinstaller_cmd,
                '--onefile',
                '--windowed',
                '--name=NOTCH-Data-Tool',  # Updated name to remove spaces
                '--add-data=readme.md;.',
            ]
            
        # Add modules directory
        if os.path.exists('modules'):
            if platform.system() == 'Windows':
                command.append('--add-data=modules/*.py;modules')
            else:
                command.append('--add-data=modules/*.py:modules')
        
        # Add icon if it exists
        if os.path.exists('weather.ico'):
            command.append('--icon=weather.ico')
            
        # Include weather.csv if it exists
        if os.path.exists('weather.csv'):
            if platform.system() == 'Windows':
                command.append('--add-data=weather.csv;.')
            else:
                command.append('--add-data=weather.csv:.')
                
        # Add hidden imports
        command.extend([
            '--hidden-import=modules.app', 
            '--hidden-import=modules.config',
            '--hidden-import=modules.midi',
            '--hidden-import=modules.weather_tab',
            '--hidden-import=modules.settings_tab',
            '--hidden-import=modules.midi_tab'
        ])
        
        # Update to use the new main file
        command.append('notch_data_tool.py')  # Using the new entry point
        
        print(f"Running command: {' '.join(command)}")
        subprocess.check_call(command)
        print("\nBuild completed successfully!")
        print("Executable can be found in the 'dist' folder.")
        
        return True
    except Exception as e:
        print(f"Error building executable: {e}")
        return False

if __name__ == "__main__":
    print("===== NOTCH-Data-Tool Builder =====")  # Updated name without spaces
    
    if install_requirements():
        build_executable()
    else:
        print("Failed to install required packages. Build aborted.")