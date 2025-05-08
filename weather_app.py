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

# Configuration setup
CONFIG_FILE = "config.ini"
DEFAULT_CITY = "London"
DEFAULT_INTERVAL = 120  # Default update interval in seconds (2 minutes)
WEATHER_FILE = "weather.csv"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NOTCH Weather Controller")
        self.root.geometry("450x500")
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
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Weather.TLabel", font=("Arial", 20))
        style.configure("Info.TLabel", font=("Arial", 12))
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # City and Settings
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.city_entry = ttk.Entry(settings_frame, width=15)
        self.city_entry.insert(0, self.city)
        self.city_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.set_city_btn = ttk.Button(settings_frame, text="Set City", command=self.update_city)
        self.set_city_btn.pack(side=tk.LEFT, padx=5)
        
        self.interval_btn = ttk.Button(settings_frame, text="Set Interval", command=self.set_update_interval)
        self.interval_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = ttk.Button(settings_frame, text="API Settings", command=self.show_api_settings)
        self.settings_btn.pack(side=tk.RIGHT)
        
        # City label
        self.city_label = ttk.Label(main_frame, text=f"Weather for {self.city}", style="Header.TLabel")
        self.city_label.pack(pady=(0, 10))
        
        # Weather info
        self.weather_frame = ttk.Frame(main_frame)
        self.weather_frame.pack(fill=tk.X, pady=10)
        
        self.temp_label = ttk.Label(self.weather_frame, text="-- °C", style="Weather.TLabel")
        self.temp_label.pack()
        
        self.desc_label = ttk.Label(self.weather_frame, text="--", style="Info.TLabel")
        self.desc_label.pack(pady=5)
        
        # Details frame
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Wind info
        wind_frame = ttk.LabelFrame(details_frame, text="Wind")
        wind_frame.pack(fill=tk.X, pady=5)
        
        self.wind_label = ttk.Label(wind_frame, text="-- m/s, --°")
        self.wind_label.pack(pady=5)
        
        # Additional info
        info_frame = ttk.LabelFrame(details_frame, text="Additional Information")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.humidity_label = ttk.Label(info_frame, text="Humidity: --%")
        self.humidity_label.pack(anchor="w", pady=2)
        
        self.pressure_label = ttk.Label(info_frame, text="Pressure: -- hPa")
        self.pressure_label.pack(anchor="w", pady=2)
        
        self.feels_like_label = ttk.Label(info_frame, text="Feels like: -- °C")
        self.feels_like_label.pack(anchor="w", pady=2)
        
        # Status bar with update interval display
        status_frame = ttk.Frame(root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Last updated: never", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.interval_label = ttk.Label(status_frame, text=f"Update: {self.update_interval//60} min", anchor=tk.CENTER)
        self.interval_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.refresh_button = ttk.Button(status_frame, text="Refresh", command=self.fetch_weather)
        self.refresh_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
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
            self.show_api_settings()
    
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
        interval_min = simpledialog.askinteger(
            "Update Interval", 
            "Enter update interval in minutes (1-60):",
            minvalue=1,
            maxvalue=60,
            initialvalue=self.update_interval // 60
        )
        
        if interval_min is not None:
            # Convert to seconds and update
            self.update_interval = interval_min * 60
            self.interval_label.config(text=f"Update: {interval_min} min")
            self.save_config()
            
            # Restart the update thread with new interval
            self.running = False
            if hasattr(self, 'update_thread') and self.update_thread.is_alive():
                time.sleep(0.5)  # Give thread time to stop
                
            self.running = True
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def show_api_settings(self):
        """Show API settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("API Settings")
        settings_window.geometry("400x200")  # Made taller to fit the Save button
        settings_window.resizable(False, False)
        settings_window.grab_set()  # Make it modal
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key entry
        ttk.Label(frame, text="Enter your OpenWeatherMap API Key:").pack(anchor="w", pady=(0, 5))
        
        api_frame = ttk.Frame(frame)
        api_frame.pack(fill=tk.X, pady=5)
        
        api_entry = ttk.Entry(api_frame, width=40, show="*")
        api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        show_btn = ttk.Button(api_frame, text="Show", width=5)
        show_btn.pack(side=tk.RIGHT, padx=5)
        
        def toggle_show():
            if api_entry['show'] == '*':
                api_entry.config(show="")
                show_btn.config(text="Hide")
            else:
                api_entry.config(show="*")
                show_btn.config(text="Show")
                
        show_btn.config(command=toggle_show)
        
        if self.api_key:
            api_entry.insert(0, self.api_key)
            
        # Get free API key link
        ttk.Label(frame, text="Don't have an API key?").pack(anchor="w", pady=(10, 0))
        
        def open_api_page():
            import webbrowser
            webbrowser.open("https://openweathermap.org/api")
            
        link_label = ttk.Label(frame, text="Get one for free at OpenWeatherMap.org", foreground="blue", cursor="hand2")
        link_label.pack(anchor="w")
        link_label.bind("<Button-1>", lambda e: open_api_page())
        
        # Save button - Updated to be more visible
        def save_api_key():
            new_key = api_entry.get().strip()
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
                
            self.fetch_weather()
            settings_window.destroy()
        
        # Button frame to ensure the save button is visible
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_button = ttk.Button(
            button_frame, 
            text="Save API Key", 
            command=save_api_key,
            width=15  # Make the button wider
        )
        save_button.pack(side=tk.RIGHT)
        
        # Add Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=settings_window.destroy,
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Set focus to the entry field and bind Enter key to save
        api_entry.focus_set()
        api_entry.bind("<Return>", lambda event: save_api_key())
        settings_window.bind("<Escape>", lambda event: settings_window.destroy())
        
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
                # Extract the most important weather data
                weather_data = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'city': data['name'],
                    'description': data['weather'][0]['description'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'wind_deg': data['wind'].get('deg', ''),
                    'visibility': data.get('visibility', '')
                }
                
                # Check if file exists to determine if we need headers
                file_exists = False
                try:
                    with open(WEATHER_FILE, 'r'):
                        file_exists = True
                except FileNotFoundError:
                    pass
                
                # Write to CSV file
                with open(WEATHER_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=weather_data.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(weather_data)
                
                # Update UI with weather information
                self.update_weather_ui(data)
                
                # Update status
                current_time = datetime.now().strftime("%H:%M:%S")
                self.status_label.config(text=f"Last updated: {current_time}")
                
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
            
            # Update UI with this data
            self.temp_label.config(text=f"{float(latest['temperature']):.1f} °C")
            self.desc_label.config(text=latest['description'].capitalize())
            
            # Wind info
            wind_text = f"{latest['wind_speed']} m/s"
            if latest['wind_deg']:
                wind_text += f", {latest['wind_deg']}°"
            self.wind_label.config(text=wind_text)
            
            # Additional info
            self.humidity_label.config(text=f"Humidity: {latest['humidity']}%")
            self.pressure_label.config(text=f"Pressure: {latest['pressure']} hPa")
            self.feels_like_label.config(text=f"Feels like: {float(latest['feels_like']):.1f} °C")
            
            # Update city label
            self.city_label.config(text=f"Weather for {latest['city']}")
            
            # Update status with timestamp from the file
            self.status_label.config(text=f"Last updated: {latest['timestamp']}")
            
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