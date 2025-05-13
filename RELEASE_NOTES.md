# NOTCH Data Tool v1.0.0 Release Notes

**Release Date:** May 13, 2025

## Overview

This is the first stable release of the NOTCH Data Tool (formerly NOTCH Weather Feed Generator). The application has been completely redesigned and expanded beyond its original weather monitoring functionality to include MIDI control capabilities, making it a versatile data tool for NOTCH and other compatible applications.

## Major Changes

### Application Renaming and Rebranding
- Renamed from "NOTCH Weather Feed Generator" to "NOTCH Data Tool"
- Updated all references in code and documentation
- Prepared for repository rename from "NOTCH-WeatherController" to "NOTCH-Data-Tool"

### New MIDI Functionality
- Added full MIDI device integration
- Implemented MIDI note message functionality with customizable parameters:
  - Note number selection (0-127)
  - Velocity control (0-127)
  - Channel selection (1-16)
- Implemented MIDI CC message functionality:
  - CC number selection (0-127)
  - CC value control (0-127)
  - Channel selection (1-16)
- Added MIDI preset system for saving and loading frequently used configurations
- Created dedicated MIDI device connection management

### Architecture Improvements
- Transitioned from monolithic script to modular architecture
- Organized code into specialized modules:
  - `weather_tab.py` - Weather data handling and display
  - `midi_tab.py` - MIDI control interface
  - `settings_tab.py` - Application settings management
  - `app.py` - Core application framework
  - `midi.py` - MIDI helper functions
  - `config.py` - Configuration management
- Improved error handling and user feedback
- Enhanced settings management

### User Interface Enhancements
- Implemented tabbed interface for better organization:
  - Weather tab for monitoring weather data
  - MIDI tab for controlling MIDI devices
  - Settings tab for application configuration
- Modernized UI elements and layout
- Added real-time status indicators for all connected services

### Build System Improvements
- Updated build scripts for the renamed application
- Created new spec files for PyInstaller
- Removed Chocolatey packaging support
- Changed executable name from "NOTCH Data Tool.exe" to "NOTCH-Data-Tool.exe" for better command-line compatibility

## Bug Fixes
- Fixed weather data caching issues
- Improved API key storage security
- Enhanced error handling for network failures
- Resolved city name validation issues
- Fixed CSV data logging consistency problems

## Known Limitations
- Limited to current weather data only (no forecast)
- Single city monitoring at a time
- Basic data visualization
- MIDI output only (no MIDI input capability)

## Dependencies
- Added `python-rtmidi` for MIDI functionality
- Maintained existing dependencies:
  - `requests` for API communication
  - `tkinter` for GUI components

## Migrating from Previous Versions
Users of previous versions should:
1. Uninstall any old versions
2. Download and install the new NOTCH Data Tool
3. Launch the application - existing configurations will be automatically migrated

---

Thank you for using NOTCH Data Tool! For support, please submit issues on our GitHub repository.