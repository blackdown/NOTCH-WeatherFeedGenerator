#!/usr/bin/env python3
# NOTCH Data Tool - Main Application
import tkinter as tk
from modules.app import NOTCHDataTool

if __name__ == "__main__":
    root = tk.Tk()
    app = NOTCHDataTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()