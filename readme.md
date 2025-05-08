# NOTCH Weather Controller

A simple Python application that fetches and monitors weather data for London using the OpenWeatherMap API.

## Features

- Retrieves current weather conditions including temperature, weather description, and wind information
- Updates data automatically every 2 minutes
- Saves weather data to a local JSON file
- Displays weather information in the console

## Files

- `fetch_weather.py` - Main script that fetches weather data
- `weather.json` - JSON file containing the most recently fetched weather data

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/NOTCH-WeatherController.git
cd NOTCH-WeatherController
```

2. Install required dependencies:
```bash
pip install requests
```

3. Run the script:
```bash
python fetch_weather.py
```

## Configuration

You can modify the following variables in `fetch_weather.py` to customize the application:

- `API_KEY` - Your OpenWeatherMap API key
- `CITY` - The city to get weather data for (default: London)
- `OUTPUT_FILE` - The file path to save weather data (default: weather.json)
- Update frequency - Change the `time.sleep(120)` value to adjust how often the data is updated (in seconds)

## Weather Data

The application retrieves and stores the following weather information:
- Current temperature (°C)
- Weather description
- Wind speed (m/s) and direction (degrees)
- Humidity, pressure, and other meteorological data

## License

Copyright Antony Bailey 2025