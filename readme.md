# NOTCH Data Tool

A Python application that fetches weather data and generates MIDI control data for integration with NOTCH and other MIDI-compatible applications.

## Version 1.1.0

This release includes complete weather monitoring functionality, an enhanced MIDI control interface with improved error handling, and virtual MIDI support for integration with NOTCH and other MIDI-compatible applications.

### What's Included

- **Weather Data Integration**: Fetch and display current weather conditions including temperature, weather description, and detailed metrics
- **Enhanced MIDI Control Interface**: Send MIDI notes and CC messages to control external applications
- **Improved MIDI Error Handling**: Better handling of DLL errors and missing drivers
- **Virtual MIDI Support**: Integration with loopMIDI for reliable MIDI connectivity
- **Audio Interface Compatibility Mode**: Better detection of MIDI-capable audio interfaces
- **Preset Management**: Save and recall your favorite MIDI settings
- **Dual Interface Options**: Choose between a GUI application or command-line interface
- **Data Persistence**: Automatic CSV logging for integration with NOTCH
- **Customizable Settings**: Set your preferred city, update frequency, and securely store your API key
- **Encrypted API key storage**: Config file stores an encrypted version of your API key

### Known Limitations

- Limited to current weather data only
- Single city monitoring at a time
- Basic data visualization only

### Installation

Pre-built executable available in the releases section, or follow the setup instructions below for development use.

## Features

### MIDI Connectivity

The NOTCH Data Tool provides robust MIDI connectivity options:

- **Hardware MIDI devices**: Connect to MIDI interfaces and controllers
- **Audio interfaces**: Better detection of MIDI capabilities in audio interfaces
- **Virtual MIDI**: Support for loopMIDI virtual MIDI ports
- **Troubleshooting tools**: Advanced options for resolving MIDI connectivity issues

For MIDI connection troubleshooting, see:
- [MIDI Troubleshooting Guide](MIDI_TROUBLESHOOTING.md)
- [Setting up loopMIDI](LOOPMIDI_SETUP.md)

### Weather Monitoring
- Retrieves current weather conditions including temperature, weather description, and wind information
- Updates data automatically with customizable time intervals
- Saves weather data to a local CSV file for historical tracking
- Allows users to securely store their own API key
- Enables users to select different cities for weather data

### MIDI Control
- Connect to available MIDI output devices
- Send MIDI note messages with customizable note, velocity, and channel
- Send MIDI CC messages with adjustable CC number and value
- Save and recall MIDI presets for quick access to common settings

### Interface
- Clean, modern tab-based interface
- Real-time weather display with auto-updates
- MIDI control panel with interactive controls
- Settings management for all application features

## Command Line Options

The NOTCH Data Tool can be run from the command line with the following options:

### Executable (Windows)

```bash
# Basic usage with settings from config.ini
NOTCH-Data-Tool.exe

# Run in command-line mode with options
NOTCH-Data-Tool.exe --city="Paris" --interval=5
```

### Python Script

```bash
# Basic usage with settings from config.ini
python notch_data_tool.py

# Specify city and update interval
python notch_data_tool.py --city="Berlin" --interval=10
```

#### Available Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--city` | City to fetch weather for | Value from config.ini (or "London") |
| `--interval` | Update interval in minutes (1-60) | Value from config.ini (or 2 minutes) |

## Files

- `notch_data_tool.py` - Main application entry point
- `modules/weather_tab.py` - Weather monitoring module
- `modules/midi_tab.py` - MIDI control interface module
- `modules/settings_tab.py` - Application settings module
- `modules/app.py` - Core application framework
- `modules/midi.py` - MIDI helper functions
- `modules/config.py` - Configuration management
- `build.py` - Script to build executable
- `weather.csv` - CSV file containing weather data history
- `config.ini` - Created on first run to store settings

## Setup and Running

### Using Python (Development)

1. Clone this repository:
```bash
git clone https://github.com/blackdown/NOTCH-Data-Tool.git
cd NOTCH-Data-Tool
```

2. Install required dependencies:
```bash
pip install requests python-rtmidi
```

3. Run the application:
```bash
python notch_data_tool.py
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
4. You'll need to select a MIDI output device to send MIDI messages

## Configuration

Your settings are securely stored in a `config.ini` file and include:
- API key (stored with basic encryption)
- City preference
- Update interval (in minutes)
- Last used MIDI device

You can change these settings any time through the application interface:
- Use the Settings tab to update weather and API settings
- Use the MIDI tab to configure MIDI output devices and message parameters

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
