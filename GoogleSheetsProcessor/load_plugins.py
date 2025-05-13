#!/usr/bin/env python3
# Simple plugin loader that can be added to main.py

import os
import sys
import traceback

def load_plugins(main_window):
    """Load plugins for MK Processor without modifying main.py"""
    try:
        # Try to import the plugin manager
        from plugin_manager import PluginManager
        
        # Create plugin manager and attach it to main window
        plugin_manager = PluginManager(main_window)
        main_window.plugin_manager = plugin_manager
        
        print("Plugins loaded successfully")
        return plugin_manager
    except Exception as e:
        print(f"Error loading plugins: {e}")
        print(traceback.format_exc())
        return None
