# NOTCH Data Tool v1.1.0 Release Notes

**Release Date:** May 13, 2025

## Overview

This release focuses on improving MIDI functionality with enhanced error handling, virtual MIDI support, and better compatibility with audio interfaces. These improvements address common issues users experienced with MIDI connectivity in the previous version.

## Major Changes

### Enhanced MIDI Functionality
- Added robust error handling for DLL issues, particularly with portmidi.dll
- Implemented virtual MIDI support with loopMIDI integration
- Created audio interface compatibility mode for better MIDI device detection
- Added manual MIDI port entry option for troubleshooting
- Improved UI feedback during MIDI connection processes
- Added right-click context menu for advanced MIDI options

### New Documentation
- Added comprehensive [MIDI Troubleshooting Guide](MIDI_TROUBLESHOOTING.md)
- Created step-by-step [loopMIDI Setup Guide](LOOPMIDI_SETUP.md)
- Updated README with MIDI connectivity information

### Architecture Improvements
- Created `midi_wrapper.py` module for better error handling
- Added `midi_helper.py` to assist with MIDI troubleshooting
- Improved MIDI backend selection to avoid problematic dependencies
- Fixed indentation and structural issues in `midi_tab.py`

### Bug Fixes
- Fixed portmidi.dll errors preventing MIDI functionality
- Resolved issues with audio interface MIDI detection
- Fixed syntax errors in the MIDI tab module

## Upgrading from v1.0.0

This is a direct upgrade that maintains full compatibility with the previous version. No configuration changes are required.

If you experienced MIDI connectivity issues in v1.0.0, please refer to the new [MIDI Troubleshooting Guide](MIDI_TROUBLESHOOTING.md) after upgrading.

## Known Issues

- Some specialized audio interfaces with non-standard MIDI implementations may still require manual port entry
- The "Send All Weather Data as CC" function may behave unexpectedly with some software synthesizers
