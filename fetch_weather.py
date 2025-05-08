import requests
import json
import time
import csv
import os
import argparse
from datetime import datetime
import configparser

# Default settings
API_KEY = "0267276dcdc78ea5568eb0db1d52d5cd"
CITY = "London"
OUTPUT_FILE = "weather.csv"
DEFAULT_INTERVAL = 120  # Default update interval in seconds (2 minutes)
CONFIG_FILE = "config.ini"

def load_config():
    """Load configuration from config file if it exists"""
    config = configparser.ConfigParser()
    config_data = {
        'api_key': API_KEY,
        'city': CITY,
        'update_interval': DEFAULT_INTERVAL
    }
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'Settings' in config:
            if 'city' in config['Settings']:
                config_data['city'] = config['Settings']['city']
            if 'update_interval' in config['Settings']:
                try:
                    config_data['update_interval'] = int(config['Settings']['update_interval'])
                except ValueError:
                    pass  # Use default if value is invalid
    
    return config_data

def fetch_weather(city, api_key):
    """Fetch weather data and save to CSV"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON.")
        return

    # Check for API error response
    if response.status_code != 200 or "weather" not in data:
        print("API Error:", data.get("message", "Unknown error"))
        return

    # Save the data to CSV file
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
            with open(OUTPUT_FILE, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass
        
        # Write to CSV file
        with open(OUTPUT_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=weather_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(weather_data)
        
        # Print weather info
        print(f"Weather updated at {datetime.now().strftime('%H:%M:%S')}")
        print(f"City: {data['name']}")
        print(f"Temperature: {data['main']['temp']:.1f}°C, {data['weather'][0]['description']}")
        print(f"Wind: {data['wind']['speed']} m/s from {data['wind'].get('deg', 'unknown')}°")
        print(f"Humidity: {data['main']['humidity']}%, Pressure: {data['main']['pressure']} hPa")
        print("-" * 40)
        
    except Exception as e:
        print(f"Error saving weather data: {e}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Fetch weather data and save to CSV')
    parser.add_argument('--city', help='City to fetch weather for')
    parser.add_argument('--interval', type=int, help='Update interval in minutes (1-60)')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Override with command-line arguments if provided
    city = args.city if args.city else config['city']
    update_interval = args.interval * 60 if args.interval else config['update_interval']
    
    print(f"NOTCH Weather Controller (CLI)")
    print(f"City: {city}")
    print(f"Update interval: {update_interval // 60} minutes")
    print("-" * 40)
    
    # Main loop
    try:
        while True:
            fetch_weather(city, config['api_key'])
            print(f"Next update in {update_interval // 60} minute(s)...")
            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("\nExiting weather monitoring.")
