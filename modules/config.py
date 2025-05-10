"""
Configuration module for NOTCH Data Tool
"""
import configparser
import os
import base64

# Configuration constants
CONFIG_FILE = "config.ini"
DEFAULT_CITY = "London"
DEFAULT_INTERVAL = 120  # Default update interval in seconds (2 minutes)
DEFAULT_WEATHER_FILE = "weather.csv"
DEFAULT_MIDI_CONFIG = "midi_presets.json"

def load_config(config_file):
    """
    Load configuration from config file
    Returns a dictionary with config object and settings
    """
    config = configparser.ConfigParser()
    api_key = ""
    city = DEFAULT_CITY
    update_interval = DEFAULT_INTERVAL
    weather_file = DEFAULT_WEATHER_FILE
    
    if os.path.exists(config_file):
        config.read(config_file)
        if 'Settings' in config:
            if 'api_key' in config['Settings']:
                # Decode the API key
                encoded_key = config['Settings']['api_key']
                try:
                    api_key = base64.b64decode(encoded_key).decode('utf-8')
                except:
                    api_key = ""
            
            if 'city' in config['Settings']:
                city = config['Settings']['city']
                
            if 'update_interval' in config['Settings']:
                try:
                    update_interval = int(config['Settings']['update_interval'])
                except:
                    update_interval = DEFAULT_INTERVAL
            
            if 'weather_file' in config['Settings']:
                weather_file = config['Settings']['weather_file']
    
    return {
        'config_obj': config,
        'api_key': api_key,
        'city': city,
        'update_interval': update_interval,
        'weather_file': weather_file
    }

def save_config(config_file, config, api_key, city, update_interval, weather_file):
    """
    Save configuration to config file
    """
    if config is None:
        config = configparser.ConfigParser()
    
    if 'Settings' not in config:
        config['Settings'] = {}
        
    # Encode the API key
    if api_key:
        encoded_key = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
        config['Settings']['api_key'] = encoded_key
        
    config['Settings']['city'] = city
    config['Settings']['update_interval'] = str(update_interval)
    config['Settings']['weather_file'] = weather_file
    
    with open(config_file, 'w') as f:
        config.write(f)