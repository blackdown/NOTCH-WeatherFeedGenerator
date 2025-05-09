# NOTCH Weather Feed Generator

A Python application that fetches and monitors weather data using the OpenWeatherMap (free) API with a simple GUI.

## Version 0.1 Pre-release Notes (May 8, 2025)

The first pre-release version of the NOTCH Weather Controller! This initial release includes all core functionality.

### What's Included

- **Complete Weather Monitoring**: Fetch and display current weather conditions including temperature, weather description, and detailed metrics
- **Dual Interface Options**: Choose between a GUI application or command-line interface
- **Data Persistence**: Automatic CSV logging for reading with NOTCH
- **Customizable Settings**: Set your preferred city, update frequency, and securely store your API key
- **Encrypted API key storage**: Config files stores an encrypted version of your API key.

### Known Limitations

- Limited to current weather data only
- Single city monitoring at a time
- Basic data visualisation only

### Installation

Pre-built executable available in the releases section, or follow the setup instructions below for development use.

## Features

- Retrieves current weather conditions including temperature, weather description, and wind information
- Updates data automatically with customizable time intervals
- Saves weather data to a local CSV file for historical tracking
- Allows users to securely store their own API key
- Enables users to select different cities for weather data
- Displays weather information in a clean, modern interface

## Command Line Options

The NOTCH Weather Controller can be run from the command line with the following options:

### Executable (Windows)

```bash
# Basic usage with settings from config.ini
NOTCH-WeatherController.exe

# Run in command-line mode with options
NOTCH-WeatherController.exe --city="Paris" --interval=5
```

### Python Script

```bash
# Basic usage with settings from config.ini
python fetch_weather.py

# Specify city and update interval
python fetch_weather.py --city="Berlin" --interval=10
```

#### Available Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--city` | City to fetch weather for | Value from config.ini (or "London") |
| `--interval` | Update interval in minutes (1-60) | Value from config.ini (or 2 minutes) |

## Files

- `weather_app.py` - Main GUI application
- `fetch_weather.py` - Command-line script version
- `build.py` - Script to build executable
- `weather.csv` - CSV file containing the weather data history
- `config.ini` - Created on first run to store settings (API key, city, update interval)

## Setup and Running

### Using Python (Development)

1. Clone this repository:
```bash
git clone https://github.com/yourusername/NOTCH-WeatherController.git
cd NOTCH-WeatherController
```

2. Install required dependencies:
```bash
pip install requests
```

3. Run the GUI application:
```bash
python weather_app.py
```

4. Run the command-line version (optional):
```bash
# Basic usage with settings from config.ini
python fetch_weather.py

# Specify city and update interval
python fetch_weather.py --city="New York" --interval=5
```

### Creating an Executable (Distribution)

1. Run the build script to create a standalone executable:
```bash
python build.py
```

2. Find the executable in the `dist` folder and run it.

## First Run

1. When you first run the application, you'll be prompted to enter your OpenWeatherMap API key
2. If you don't have an API key, you can get one for free at [OpenWeatherMap](https://openweathermap.org/api)
3. The app will securely store your API key and selected city for future use

## Configuration

Your settings are securely stored in a `config.ini` file and include:
- API key (stored with basic encoding)
- City preference
- Update interval (in seconds)

You can change these settings any time through the application interface:
- Use the city input field and "Set City" button to change location
- Click "Set Interval" to customize how often the weather data updates (1-60 minutes)
- Click "API Settings" to update your API key

## Weather Data

The application retrieves and displays the following weather information:
- Current temperature (°C)
- Weather description
- Wind speed (m/s) and direction (degrees)
- Humidity, pressure, and "feels like" temperature

All data is stored chronologically in the CSV file, allowing you to track weather changes over time.

## License

Attribution-ShareAlike 4.0 International
https://creativecommons.org/licenses/by-sa/4.0/
