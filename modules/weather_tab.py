"""
Weather tab functionality for NOTCH Data Tool
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv
import requests
from datetime import datetime
import webbrowser
import shutil

class WeatherTab:
    def __init__(self, app):
        """Initialize the Weather tab with the main application reference"""
        self.app = app
        self.tab = app.weather_tab_frame
        
        # Create the Weather Tab UI
        self.create_weather_tab()
        
    def create_weather_tab(self):
        """Create the weather tab UI"""
        # City and Location Controls
        loc_frame = ttk.Frame(self.tab)
        loc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.city_entry = ttk.Entry(loc_frame, width=15)
        self.city_entry.insert(0, self.app.city)
        self.city_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.set_city_btn = ttk.Button(loc_frame, text="Set City", command=self.update_city)
        self.set_city_btn.pack(side=tk.LEFT, padx=5)
        
        self.geolocate_btn = ttk.Button(loc_frame, text="Geolocate", command=self.geolocate_location)
        self.geolocate_btn.pack(side=tk.LEFT, padx=5)
        
        # City label - increased top padding from 0 to 15
        self.city_label = ttk.Label(self.tab, text=f"Weather for {self.app.city}", style="Header.TLabel")
        self.city_label.pack(pady=(15, 10))
        
        # Weather info
        self.weather_frame = ttk.Frame(self.tab)
        self.weather_frame.pack(fill=tk.X, pady=10)
        
        self.temp_label = ttk.Label(self.weather_frame, text="-- °C", style="Weather.TLabel")
        self.temp_label.pack()
        
        self.desc_label = ttk.Label(self.weather_frame, text="--", style="Info.TLabel")
        self.desc_label.pack(pady=5)
        
        # Details frame
        details_frame = ttk.Frame(self.tab)
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
        csv_frame = ttk.Frame(self.tab)
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
            text=f"{os.path.abspath(self.app.weather_file)}",
            style="Path.TLabel"
        )
        self.csv_path.pack(anchor="w")

    def update_city(self):
        """Update the city and refresh weather"""
        new_city = self.city_entry.get().strip()
        if not new_city:
            return
            
        self.app.city = new_city
        self.city_label.config(text=f"Weather for {self.app.city}")
        self.app.save_config()
        
        # Refresh weather data
        if self.app.api_key:
            self.fetch_weather()

    def geolocate_location(self):
        """Get the user's location based on IP address"""
        try:
            self.app.status_label.config(text="Detecting location...")
            self.app.root.update()  # Force GUI update
            
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
                        self.app.status_label.config(text=f"Location detected: {detected_city}")
                    else:
                        self.app.status_label.config(text="Could not determine your city")
                else:
                    self.app.status_label.config(text="Geolocation failed")
            else:
                self.app.status_label.config(text=f"Geolocation error: {response.status_code}")
        except Exception as e:
            self.app.status_label.config(text=f"Geolocation error: {str(e)}")

    def fetch_weather(self):
        """Fetch weather data from API"""
        if not self.app.api_key:
            self.app.status_label.config(text="API Key not set")
            self.app.notebook.select(self.app.settings_tab_frame)  # Switch to settings tab
            return
            
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={self.app.city}&appid={self.app.api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code}"
                data = response.json()
                if "message" in data:
                    error_msg += f" - {data['message']}"
                self.app.status_label.config(text=error_msg)
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
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(os.path.abspath(self.app.weather_file)), exist_ok=True)
                
                # Check if file exists and handle CSV format migration if needed
                file_exists = False
                existing_rows = []
                fieldnames = list(weather_data.keys())
                
                try:
                    with open(self.app.weather_file, 'r', newline='') as f:
                        # Read first line to check header format
                        first_line = f.readline().strip()
                        file_exists = True
                        
                        # Check if the CSV format needs migration
                        if first_line.startswith('timestamp,') and 'longitude' not in first_line:
                            self.app.status_label.config(text="Migrating CSV format...")
                            self.app.root.update()  # Force GUI update to show status
                            self.migrate_csv_format()
                            self.app.status_label.config(text="CSV migration completed")
                        else:
                            # If no migration needed, read existing data
                            f.seek(0)  # Go back to beginning of file
                            reader = csv.DictReader(f)
                            existing_rows = list(reader)
                            
                except FileNotFoundError:
                    pass
                
                # Write to CSV file with newest entry at the top
                with open(self.app.weather_file, 'w', newline='') as f:
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
                self.app.status_label.config(text=f"Last updated: {time_str}")
                
            except Exception as e:
                self.app.status_label.config(text=f"Error saving weather data: {str(e)}")
                
        except Exception as e:
            self.app.status_label.config(text=f"Error: {str(e)}")
    
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
            if not os.path.exists(self.app.weather_file):
                return False
                
            with open(self.app.weather_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            if not rows:
                return False
                
            # Get the first entry (since we now add new entries at the top)
            latest = rows[0]
            
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
            
            self.app.status_label.config(text=f"Last updated: {time_display}")
            
            return True
            
        except Exception as e:
            self.app.status_label.config(text=f"Error loading weather data: {str(e)}")
            return False

    def check_and_migrate_csv_format(self):
        """Check if CSV needs migration and perform it if necessary"""
        try:
            if os.path.exists(self.app.weather_file):
                with open(self.app.weather_file, 'r') as f:
                    # Read first line to check header format
                    first_line = f.readline().strip()
                    
                    # Check if the CSV format needs migration
                    if first_line.startswith('timestamp,') and 'longitude' not in first_line:
                        self.app.status_label.config(text="Migrating CSV format...")
                        self.app.root.update()  # Force GUI update to show status
                        self.migrate_csv_format()
                        self.app.status_label.config(text="CSV migration completed")
        except Exception as e:
            self.app.status_label.config(text=f"Error checking CSV format: {str(e)}")
    
    def migrate_csv_format(self):
        """Migrate existing CSV to new format with separate date/time columns and coordinates"""
        try:
            # Create a backup of the current file
            backup_file = f"{self.app.weather_file}.bak"
            if os.path.exists(self.app.weather_file):
                with open(self.app.weather_file, 'r', newline='') as src, open(backup_file, 'w', newline='') as dst:
                    dst.write(src.read())
                
                # Read the old format
                rows = []
                with open(self.app.weather_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    for row in reader:
                        rows.append(row)
                
                # Create the new format file
                if rows:
                    with open(self.app.weather_file, 'w', newline='') as f:
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
                    os.replace(backup_file, self.app.weather_file)
                    self.app.status_label.config(text="Restored from backup due to error.")
                except Exception:
                    self.app.status_label.config(text="Failed to restore from backup.")
    
    def open_csv_file(self, event=None):
        """Open the CSV file with the default application"""
        try:
            import subprocess
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.app.weather_file)), exist_ok=True)
            
            # Create the file if it doesn't exist
            if not os.path.exists(self.app.weather_file):
                with open(self.app.weather_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['date', 'time', 'city', 'description', 'temperature', 
                                   'feels_like', 'humidity', 'pressure', 'wind_speed', 
                                   'wind_deg', 'visibility', 'longitude', 'latitude'])
            
            # Use the appropriate command based on the operating system
            if os.name == 'nt':  # Windows
                os.startfile(os.path.abspath(self.app.weather_file))
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(('open', os.path.abspath(self.app.weather_file)) if os.uname().sysname == 'Darwin' 
                               else ('xdg-open', os.path.abspath(self.app.weather_file)))
            self.app.status_label.config(text="Opening CSV file...")
        except Exception as e:
            self.app.status_label.config(text=f"Error opening CSV: {str(e)}")