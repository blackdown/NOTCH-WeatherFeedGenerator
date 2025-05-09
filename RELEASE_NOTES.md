# NOTCH Weather Feed Generator v1.0.0 - Release Notes

*Released: May 9, 2025*

## Overview

This is the first stable release of the NOTCH Weather Feed Generator, following the v0.1 pre-release. It includes all core functionality with improved stability, performance optimizations, and bug fixes.

## Technical Improvements

- **Error Handling**: Improved exception handling for network failures and API request timeouts.
- **Memory Management**: Reduced application memory footprint with optimized data structures.
- **API Request Optimization**: Implemented request caching to minimize redundant API calls.
- **UI Thread Management**: Fixed UI thread locking during data retrieval operations.
- **Configuration File Handling**: More robust `config.ini` read/write operations with error recovery.

## Core Features

- **Weather Data Retrieval**: Fetches real-time weather conditions via the OpenWeatherMap API.
- **Dual Interface**: Provides both GUI and command-line interfaces.
- **Data Logging**: Automatically logs weather data to a CSV file for historical tracking.
- **Customizable Settings**: Allows users to configure the city, update frequency, and API key.
- **API Key Security**: Stores the OpenWeatherMap API key securely using basic encryption.

## Installation

Download the executable from the releases section of the repository. No installation is required. The application is portable and will create necessary configuration files on the first run.

## Command Line Usage

The application can be run from the command line with the following options:

### Executable (Windows)

```bash
# Basic usage with settings from config.ini
NOTCH-WeatherController.exe

# Run with custom parameters
NOTCH-WeatherController.exe --city="Paris" --interval=5
```

### Python Script (Development)

```bash
# Basic usage with settings from config.ini
python fetch_weather.py

# Specify city and update interval
python fetch_weather.py --city="Berlin" --interval=10
```

#### Available Command Line Arguments

| Argument     | Description                          | Default                     |
|--------------|--------------------------------------|-----------------------------|
| `--city`     | City to fetch weather for            | Value from config.ini (or "London") |
| `--interval` | Update interval in minutes (1-60)    | Value from config.ini (or 2 minutes) |

## Bug Fixes

- Fixed CSV data logging interruptions during extended operation.
- Resolved city name encoding issues with non-ASCII characters.
- Corrected temperature unit conversion logic.
- Fixed UI rendering issues on high-DPI displays.
- Addressed thread-safety issues in the data update cycle.
- Improved error messages for API key validation failures.

## Technical Requirements

- **Operating System**: Windows 10/11 (64-bit).
- **Dependencies**: No additional dependencies required for the executable version.
- **Development Requirements**: Python 3.9+ with the `requests` library.

## Distribution Files

- `NOTCH-WeatherController.exe`: Main executable.
- `weather.csv`: Generated on the first run, stores historical weather data.
- `config.ini`: Generated on the first run, stores encrypted configuration settings.

## Upgrading

Users of v0.1 can simply replace the existing executable with the new version. Configuration settings and historical data will be preserved.
