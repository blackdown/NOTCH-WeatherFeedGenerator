import os
import sys
import subprocess
import pkg_resources

required_packages = {'pyinstaller', 'requests'}

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
        
        # Run PyInstaller
        command = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name=NOTCH-WeatherController',
            '--add-data=readme.md;.',
        ]
        
        # Add icon if it exists
        if os.path.exists('weather.ico'):
            command.append('--icon=weather.ico')
            
        # Include weather.csv if it exists
        if os.path.exists('weather.csv'):
            command.append('--add-data=weather.csv;.')
        
        command.append('weather_app.py')
        
        subprocess.check_call(command)
        print("\nBuild completed successfully!")
        print("Executable can be found in the 'dist' folder.")
        
        return True
    except Exception as e:
        print(f"Error building executable: {e}")
        return False

if __name__ == "__main__":
    print("===== NOTCH Weather Controller Builder =====")
    
    if install_requirements():
        build_executable()
    else:
        print("Failed to install required packages. Build aborted.")