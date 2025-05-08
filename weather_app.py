import requests
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import os
import csv
from datetime import datetime
import configparser
import base64
import webbrowser

# Configuration setup
CONFIG_FILE = "config.ini"
DEFAULT_CITY = "London"
DEFAULT_INTERVAL = 120  # Default update interval in seconds (2 minutes)
WEATHER_FILE = "weather.csv"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NOTCH Weather Controller")
        self.root.geometry("450x600")  # Slightly taller to accommodate tabs
        self.root.resizable(False, False)
        
        # Load config (API key, city, and update interval)
        self.config = configparser.ConfigParser()
        self.api_key = ""
        self.city = DEFAULT_CITY
        self.update_interval = DEFAULT_INTERVAL
        self.load_config()
        
        # Configure style
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", padding=[10, 5], font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Weather.TLabel", font=("Arial", 20))
        style.configure("Info.TLabel", font=("Arial", 12))
        style.configure("Link.TLabel", font=("Arial", 10), foreground="blue")
        style.configure("Path.TLabel", font=("Arial", 8), foreground="gray")
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Weather Tab
        self.weather_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.weather_tab, text="Weather")
        
        # Settings Tab
        self.settings_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Create the UI for each tab
        self.create_weather_tab()
        self.create_settings_tab()
        
        # Status bar with update interval display
        status_frame = ttk.Frame(root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Last updated: never", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.interval_label = ttk.Label(status_frame, text=f"Update: {self.update_interval//60} min", anchor=tk.CENTER)
        self.interval_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.refresh_button = ttk.Button(status_frame, text="Refresh", command=self.fetch_weather)
        self.refresh_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Check if we need to migrate CSV format
        self.check_and_migrate_csv_format()
        
        # Start weather update thread if API key exists
        self.running = True
        if self.api_key:
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # Initial fetch
            self.fetch_weather()
        else:
            self.status_label.config(text="Please set your API key to start")
            self.notebook.select(self.settings_tab)  # Switch to settings tab

    def create_weather_tab(self):
        """Create the weather tab UI"""
        # City and Location Controls
        loc_frame = ttk.Frame(self.weather_tab)
        loc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.city_entry = ttk.Entry(loc_frame, width=15)
        self.city_entry.insert(0, self.city)
        self.city_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.set_city_btn = ttk.Button(loc_frame, text="Set City", command=self.update_city)
        self.set_city_btn.pack(side=tk.LEFT, padx=5)
        
        self.geolocate_btn = ttk.Button(loc_frame, text="Geolocate", command=self.geolocate_location)
        self.geolocate_btn.pack(side=tk.LEFT, padx=5)
        
        # City label - increased top padding from 0 to 15
        self.city_label = ttk.Label(self.weather_tab, text=f"Weather for {self.city}", style="Header.TLabel")
        self.city_label.pack(pady=(15, 10))
        
        # Weather info
        self.weather_frame = ttk.Frame(self.weather_tab)
        self.weather_frame.pack(fill=tk.X, pady=10)
        
        self.temp_label = ttk.Label(self.weather_frame, text="-- °C", style="Weather.TLabel")
        self.temp_label.pack()
        
        self.desc_label = ttk.Label(self.weather_frame, text="--", style="Info.TLabel")
        self.desc_label.pack(pady=5)
        
        # Details frame
        details_frame = ttk.Frame(self.weather_tab)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Wind info
        wind_frame = ttk.LabelFrame(details_frame, text="Wind")
        wind_frame.pack(fill=tk.X, pady=5)
        
        self.wind_label = ttk.Label(wind_frame, text="-- m/s, --°")
        self.wind_label.pack(pady=5)
        
        # Coordinates info
        coords_frame = ttk.LabelFrame(details_frame, text="Coordinates")
        coords_frame.pack(fill=tk.X, pady=5)
        
        self.coords_label = ttk.Label(coords_frame, text="Longitude: --, Latitude: --")
        self.coords_label.pack(pady=5)
        
        # Additional info
        info_frame = ttk.LabelFrame(details_frame, text="Additional Information")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.humidity_label = ttk.Label(info_frame, text="Humidity: --%")
        self.humidity_label.pack(anchor="w", pady=2)
        
        self.pressure_label = ttk.Label(info_frame, text="Pressure: -- hPa")
        self.pressure_label.pack(anchor="w", pady=2)
        
        self.feels_like_label = ttk.Label(info_frame, text="Feels like: -- °C")
        self.feels_like_label.pack(anchor="w", pady=2)
        
        # CSV link frame
        csv_frame = ttk.Frame(self.weather_tab)
        csv_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.csv_link = ttk.Label(
            csv_frame, 
            text=f"Open weather data file", 
            style="Link.TLabel",
            cursor="hand2"
        )
        self.csv_link.pack(anchor="w")
        self.csv_link.bind("<Button-1>", self.open_csv_file)
        
        # Full path display beneath the link
        self.csv_path = ttk.Label(
            csv_frame,
            text=f"{os.path.abspath(WEATHER_FILE)}",
            style="Path.TLabel"
        )
        self.csv_path.pack(anchor="w")
    
    def create_settings_tab(self):
        """Create the settings tab UI"""
        # API Settings Section
        api_frame = ttk.LabelFrame(self.settings_tab, text="API Settings")
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="Enter your OpenWeatherMap API Key:").pack(anchor="w", pady=(10, 5), padx=10)
        
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.api_key_entry = ttk.Entry(api_key_frame, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        
        self.show_key_btn = ttk.Button(api_key_frame, text="Show", width=5, command=self.toggle_api_key_visibility)
        self.show_key_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save API key button
        save_api_frame = ttk.Frame(api_frame)
        save_api_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.save_api_btn = ttk.Button(save_api_frame, text="Save API Key", command=self.save_api_key, width=15)
        self.save_api_btn.pack(side=tk.RIGHT)
        
        # Get API key info
        ttk.Label(api_frame, text="Don't have an API key?").pack(anchor="w", pady=(5, 2), padx=10)
        
        api_link = ttk.Label(
            api_frame,
            text="Get one for free at OpenWeatherMap.org",
            foreground="blue",
            cursor="hand2"
        )
        api_link.pack(anchor="w", padx=10, pady=(0, 10))
        api_link.bind("<Button-1>", lambda e: webbrowser.open("https://openweathermap.org/api"))
        
        # Update Interval Section
        interval_frame = ttk.LabelFrame(self.settings_tab, text="Update Interval")
        interval_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(interval_frame, text="Set how often to fetch new weather data:").pack(anchor="w", pady=(10, 5), padx=10)
        
        interval_setting_frame = ttk.Frame(interval_frame)
        interval_setting_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        current_interval = self.update_interval // 60  # Convert to minutes
        
        self.interval_var = tk.IntVar(value=current_interval)
        interval_scale = ttk.Scale(
            interval_setting_frame, 
            from_=1, 
            to=60, 
            variable=self.interval_var,
            orient="horizontal",
            command=self.update_interval_display
        )
        interval_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.interval_display = ttk.Label(interval_setting_frame, text=f"{current_interval} min")
        self.interval_display.pack(side=tk.LEFT, padx=(10, 0))
        
        self.save_interval_btn = ttk.Button(interval_frame, text="Save Interval", command=self.save_interval, width=15)
        self.save_interval_btn.pack(side=tk.RIGHT, padx=10, pady=(0, 10))
        
        # About section
        about_frame = ttk.LabelFrame(self.settings_tab, text="About")
        about_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(about_frame, text="NOTCH Weather Controller").pack(anchor="w", padx=10, pady=(10, 2))
        ttk.Label(about_frame, text="A simple weather app for desktop.").pack(anchor="w", padx=10, pady=(0, 2))
        ttk.Label(about_frame, text="Data provided by OpenWeatherMap.org").pack(anchor="w", padx=10, pady=(0, 10))
        
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_entry['show'] == '*':
            self.api_key_entry.config(show="")
            self.show_key_btn.config(text="Hide")
        else:
            self.api_key_entry.config(show="*")
            self.show_key_btn.config(text="Show")
    
    def update_interval_display(self, value):
        """Update the interval display when the scale is moved"""
        # Round to integer
        minutes = int(float(value))
        if minutes < 1:
            minutes = 1
        self.interval_display.config(text=f"{minutes} min")
    
    def save_interval(self):
        """Save the selected update interval"""
        minutes = self.interval_var.get()
        if minutes < 1:
            minutes = 1
            
        # Convert to seconds
        self.update_interval = minutes * 60
        self.interval_label.config(text=f"Update: {minutes} min")
        self.save_config()
        
        # Restart the update thread with new interval
        self.running = False
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            time.sleep(0.5)  # Give thread time to stop
            
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        messagebox.showinfo("Success", f"Update interval set to {minutes} minutes")
        
    def save_api_key(self):
        """Save the API key from the settings tab"""
        new_key = self.api_key_entry.get().strip()
        if not new_key:
            messagebox.showerror("Error", "API Key cannot be empty")
            return
        
        self.api_key = new_key
        self.save_config()
        
        # Start the update thread if it doesn't exist
        if not hasattr(self, 'update_thread') or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
        
        # Switch to weather tab and fetch data
        self.notebook.select(self.weather_tab)
        self.fetch_weather()
        messagebox.showinfo("Success", "API key saved successfully")

    def geolocate_location(self):
        """Get the user's location based on IP address"""
        try:
            self.status_label.config(text="Detecting location...")
            self.root.update()  # Force GUI update
            
            # Use a free IP geolocation service
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    # Update city entry with detected city
                    detected_city = data.get("city", "")
                    if detected_city:
                        self.city_entry.delete(0, tk.END)
                        self.city_entry.insert(0, detected_city)
                        self.update_city()
                        self.status_label.config(text=f"Location detected: {detected_city}")
                    else:
                        self.status_label.config(text="Could not determine your city")
                else:
                    self.status_label.config(text="Geolocation failed")
            else:
                self.status_label.config(text=f"Geolocation error: {response.status_code}")
        except Exception as e:
            self.status_label.config(text=f"Geolocation error: {str(e)}")
    
    def check_and_migrate_csv_format(self):
        """Check if CSV needs migration and perform it if necessary"""
        try:
            if os.path.exists(WEATHER_FILE):
                with open(WEATHER_FILE, 'r') as f:
                    # Read first line to check header format
                    first_line = f.readline().strip()
                    
                    # Check if the CSV format needs migration
                    if first_line.startswith('timestamp,') and 'longitude' not in first_line:
                        self.status_label.config(text="Migrating CSV format...")
                        self.root.update()  # Force GUI update to show status
                        self.migrate_csv_format()
                        self.status_label.config(text="CSV migration completed")
        except Exception as e:
            self.status_label.config(text=f"Error checking CSV format: {str(e)}")
    
    def migrate_csv_format(self):
        """Migrate existing CSV to new format with separate date/time columns and coordinates"""
        try:
            # Create a backup of the current file
            backup_file = f"{WEATHER_FILE}.bak"
            if os.path.exists(WEATHER_FILE):
                with open(WEATHER_FILE, 'r', newline='') as src, open(backup_file, 'w', newline='') as dst:
                    dst.write(src.read())
                
                # Read the old format
                rows = []
                with open(WEATHER_FILE, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    for row in reader:
                        rows.append(row)
                
                # Create the new format file
                if rows:
                    with open(WEATHER_FILE, 'w', newline='') as f:
                        # Define new fieldnames
                        new_fieldnames = ['date', 'time', 'city', 'description', 'temperature', 
                                        'feels_like', 'humidity', 'pressure', 'wind_speed', 
                                        'wind_deg', 'visibility', 'longitude', 'latitude']
                        
                        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
                        writer.writeheader()
                        
                        # Convert each row
                        for row in rows:
                            # Split timestamp into date and time if available
                            date_str = ""
                            time_str = ""
                            if 'timestamp' in row:
                                parts = row['timestamp'].split(' ')
                                if len(parts) >= 2:
                                    date_str = parts[0]
                                    time_str = parts[1]
                            
                            # Create new row
                            new_row = {
                                'date': date_str,
                                'time': time_str,
                                'city': row.get('city', ''),
                                'description': row.get('description', ''),
                                'temperature': row.get('temperature', ''),
                                'feels_like': row.get('feels_like', ''),
                                'humidity': row.get('humidity', ''),
                                'pressure': row.get('pressure', ''),
                                'wind_speed': row.get('wind_speed', ''),
                                'wind_deg': row.get('wind_deg', ''),
                                'visibility': row.get('visibility', ''),
                                'longitude': '',  # No coordinates in old format
                                'latitude': ''    # No coordinates in old format
                            }
                            writer.writerow(new_row)
        except Exception as e:
            messagebox.showerror("Migration Error", f"Error migrating CSV format: {str(e)}")
            # If there was an error, try to restore from backup
            if os.path.exists(backup_file):
                try:
                    os.replace(backup_file, WEATHER_FILE)
                    self.status_label.config(text="Restored from backup due to error.")
                except Exception:
                    self.status_label.config(text="Failed to restore from backup.")
    
    def open_csv_file(self, event=None):
        """Open the CSV file with the default application"""
        try:
            import subprocess
            import os
            # Use the appropriate command based on the operating system
            if os.name == 'nt':  # Windows
                os.startfile(os.path.abspath(WEATHER_FILE))
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(('open', os.path.abspath(WEATHER_FILE)) if os.uname().sysname == 'Darwin' 
                               else ('xdg-open', os.path.abspath(WEATHER_FILE)))
            self.status_label.config(text="Opening CSV file...")
        except Exception as e:
            self.status_label.config(text=f"Error opening CSV: {str(e)}")
    
    def load_config(self):
        """Load configuration from config file"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
            if 'Settings' in self.config:
                if 'api_key' in self.config['Settings']:
                    # Decode the API key
                    encoded_key = self.config['Settings']['api_key']
                    try:
                        self.api_key = base64.b64decode(encoded_key).decode('utf-8')
                    except:
                        self.api_key = ""
                
                if 'city' in self.config['Settings']:
                    self.city = self.config['Settings']['city']
                    
                if 'update_interval' in self.config['Settings']:
                    try:
                        self.update_interval = int(self.config['Settings']['update_interval'])
                    except:
                        self.update_interval = DEFAULT_INTERVAL
    
    def save_config(self):
        """Save configuration to config file"""
        if 'Settings' not in self.config:
            self.config['Settings'] = {}
            
        # Encode the API key
        if self.api_key:
            encoded_key = base64.b64encode(self.api_key.encode('utf-8')).decode('utf-8')
            self.config['Settings']['api_key'] = encoded_key
            
        self.config['Settings']['city'] = self.city
        self.config['Settings']['update_interval'] = str(self.update_interval)
        
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)
            
    def set_update_interval(self):
        """Allow the user to set a custom update interval"""
        # Switch to settings tab
        self.notebook.select(self.settings_tab)
        
    def show_api_settings(self):
        """Show API settings tab"""
        self.notebook.select(self.settings_tab)
        
    def update_city(self):
        """Update the city and refresh weather"""
        new_city = self.city_entry.get().strip()
        if not new_city:
            return
            
        self.city = new_city
        self.city_label.config(text=f"Weather for {self.city}")
        self.save_config()
        
        # Refresh weather data
        if self.api_key:
            self.fetch_weather()
        
    def fetch_weather(self):
        """Fetch weather data from API"""
        if not self.api_key:
            self.status_label.config(text="API Key not set")
            self.notebook.select(self.settings_tab)  # Switch to settings tab
            return
            
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code}"
                data = response.json()
                if "message" in data:
                    error_msg += f" - {data['message']}"
                self.status_label.config(text=error_msg)
                return
                
            data = response.json()
            
            # Save the data to CSV
            try:
                # Get current date and time separately
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                
                # Extract the most important weather data
                weather_data = {
                    'date': date_str,
                    'time': time_str,
                    'city': data['name'],
                    'description': data['weather'][0]['description'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'wind_deg': data['wind'].get('deg', ''),
                    'visibility': data.get('visibility', ''),
                    'longitude': data['coord']['lon'],
                    'latitude': data['coord']['lat']
                }
                
                # Check if file exists and handle CSV format migration if needed
                file_exists = False
                existing_rows = []
                fieldnames = list(weather_data.keys())
                
                try:
                    with open(WEATHER_FILE, 'r', newline='') as f:
                        # Read first line to check header format
                        first_line = f.readline().strip()
                        file_exists = True
                        
                        # Check if the CSV format needs migration
                        if first_line.startswith('timestamp,') and 'longitude' not in first_line:
                            self.status_label.config(text="Migrating CSV format...")
                            self.root.update()  # Force GUI update to show status
                            self.migrate_csv_format()
                            self.status_label.config(text="CSV migration completed")
                        else:
                            # If no migration needed, read existing data
                            f.seek(0)  # Go back to beginning of file
                            reader = csv.DictReader(f)
                            existing_rows = list(reader)
                            
                except FileNotFoundError:
                    pass
                
                # Write to CSV file with newest entry at the top
                with open(WEATHER_FILE, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Write the new row first (at the top)
                    writer.writerow(weather_data)
                    
                    # Write all existing rows after
                    for row in existing_rows:
                        # Ensure all rows have the same fieldnames
                        cleaned_row = {field: row.get(field, '') for field in fieldnames}
                        writer.writerow(cleaned_row)
                
                # Update UI with weather information
                self.update_weather_ui(data)
                
                # Update status
                self.status_label.config(text=f"Last updated: {time_str}")
                
            except Exception as e:
                self.status_label.config(text=f"Error saving weather data: {str(e)}")
                
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def update_weather_ui(self, data):
        """Update UI with weather data"""
        # Main weather info
        self.temp_label.config(text=f"{data['main']['temp']:.1f} °C")
        self.desc_label.config(text=data['weather'][0]['description'].capitalize())
        
        # Wind info
        if 'wind' in data:
            wind_text = f"{data['wind']['speed']} m/s"
            if 'deg' in data['wind']:
                wind_text += f", {data['wind']['deg']}°"
            self.wind_label.config(text=wind_text)
        
        # Coordinates info
        if 'coord' in data:
            lon = data['coord']['lon']
            lat = data['coord']['lat']
            self.coords_label.config(text=f"Longitude: {lon}, Latitude: {lat}")
            
            # Also update the city label but without coordinates now
            self.city_label.config(text=f"Weather for {data['name']}")
        
        # Additional info
        if 'main' in data:
            if 'humidity' in data['main']:
                self.humidity_label.config(text=f"Humidity: {data['main']['humidity']}%")
            if 'pressure' in data['main']:
                self.pressure_label.config(text=f"Pressure: {data['main']['pressure']} hPa")
            if 'feels_like' in data['main']:
                self.feels_like_label.config(text=f"Feels like: {data['main']['feels_like']:.1f} °C")
    
    def load_weather_from_csv(self):
        """Load the most recent weather data from CSV file"""
        try:
            if not os.path.exists(WEATHER_FILE):
                return False
                
            with open(WEATHER_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            if not rows:
                return False
                
            # Get the most recent entry
            latest = rows[-1]
            
            # Update UI with this data - safely handle potential data type issues
            try:
                temp = float(latest.get('temperature', 0))
                self.temp_label.config(text=f"{temp:.1f} °C")
            except (ValueError, TypeError):
                self.temp_label.config(text="-- °C")
                
            self.desc_label.config(text=latest.get('description', '--').capitalize())
            
            # Wind info
            wind_text = f"{latest.get('wind_speed', '--')} m/s"
            wind_deg = latest.get('wind_deg', '')
            if wind_deg:
                wind_text += f", {wind_deg}°"
            self.wind_label.config(text=wind_text)
            
            # Coordinates info
            lon = latest.get('longitude', '--')
            lat = latest.get('latitude', '--')
            self.coords_label.config(text=f"Longitude: {lon}, Latitude: {lat}")
            
            # Additional info
            self.humidity_label.config(text=f"Humidity: {latest.get('humidity', '--')}%")
            self.pressure_label.config(text=f"Pressure: {latest.get('pressure', '--')} hPa")
            
            # Handle feels_like with potential type conversion issues
            try:
                feels_like = float(latest.get('feels_like', 0))
                self.feels_like_label.config(text=f"Feels like: {feels_like:.1f} °C")
            except (ValueError, TypeError):
                self.feels_like_label.config(text="Feels like: -- °C")
            
            # Update city label (without coordinates now)
            self.city_label.config(text=f"Weather for {latest.get('city', '--')}")
            
            # Update status with time from the file
            time_display = latest.get('time', '')
            if not time_display and 'timestamp' in latest:
                # Handle legacy CSV format with combined timestamp
                time_parts = latest['timestamp'].split(' ')
                if len(time_parts) > 1:
                    time_display = time_parts[1]
            
            self.status_label.config(text=f"Last updated: {time_display}")
            
            return True
            
        except Exception as e:
            self.status_label.config(text=f"Error loading weather data: {str(e)}")
            return False
        
    def update_loop(self):
        """Background thread to update weather periodically"""
        # Try to load existing data first
        if os.path.exists(WEATHER_FILE):
            self.root.after(0, self.load_weather_from_csv)
            
        while self.running:
            time.sleep(self.update_interval)  # Use the customizable interval
            if self.running:
                # Use after to schedule UI update on main thread
                self.root.after(0, self.fetch_weather)
    
    def on_closing(self):
        """Cleanup when closing the application"""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()