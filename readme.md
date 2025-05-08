# NOTCH Weather Controller

A Python application that fetches and monitors weather data using the OpenWeatherMap API with a user-friendly GUI.

## Features

- Retrieves current weather conditions including temperature, weather description, and wind information
- Updates data automatically with customizable time intervals
- Saves weather data to a local CSV file for historical tracking
- Allows users to securely store their own API key
- Enables users to select different cities for weather data
- Displays weather information in a clean, modern interface

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

[Add your preferred license here]