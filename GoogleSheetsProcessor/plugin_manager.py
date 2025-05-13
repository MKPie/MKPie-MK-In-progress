#!/usr/bin/env python3
# Minimal plugin manager with fix for duplicate buttons

import os
import json
import importlib.util
import traceback

class PluginManager:
    """Minimal plugin manager with fix for duplicate buttons"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins = {}
        self.plugin_info = {}
        self.plugin_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugin_config.json")
        self.initialized_plugins = set()  # Track which plugins have been initialized
        
        # Create plugin directory if it doesn't exist
        if not os.path.exists(self.plugin_directory):
            os.makedirs(self.plugin_directory)
        
        # Load plugin configuration
        self.load_plugin_config()
        
        # Discover and load enabled plugins
        self.discover_plugins()
    
    def load_plugin_config(self):
        """Load plugin configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.plugin_info = json.load(f)
                print(f"Plugin configuration loaded from {self.config_file}")
            else:
                self.plugin_info = {}
                self.save_plugin_config()
                print(f"Created new plugin configuration at {self.config_file}")
        except Exception as e:
            print(f"Error loading plugin configuration: {e}")
            print(traceback.format_exc())
            self.plugin_info = {}
    
    def save_plugin_config(self):
        """Save plugin configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.plugin_info, f, indent=4)
            print(f"Plugin configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving plugin configuration: {e}")
            print(traceback.format_exc())
            return False
    
    def discover_plugins(self):
        """Scan the plugins directory and load all valid plugins"""
        print(f"Scanning for plugins in: {self.plugin_directory}")
        
        # Clear existing loaded plugins (but keep configuration)
        self.plugins = {}
        self.initialized_plugins = set()  # Reset initialized plugins
        
        # Only scan the proper plugins directory, not disabled_plugins
        if not os.path.exists(self.plugin_directory):
            print(f"Plugin directory does not exist: {self.plugin_directory}")
            return
            
        # Scan plugin directory for all potential plugins
        for filename in os.listdir(self.plugin_directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_path = os.path.join(self.plugin_directory, filename)
                plugin_name = os.path.splitext(filename)[0]
                
                # Skip any plugin that starts with "x-" (explicitly disabled)
                if plugin_name.startswith("x-"):
                    print(f"Skipping explicitly disabled plugin: {plugin_name}")
                    continue
                
                # Check plugin info in configuration
                if plugin_name not in self.plugin_info:
                    # New plugin found, add default configuration
                    self.plugin_info[plugin_name] = {
                        "enabled": True,  # Enable by default
                        "show_in_ui": True,  # Show in UI by default
                        "name": plugin_name,  # Default name
                        "description": "",  # Empty description initially
                        "version": ""  # Empty version initially
                    }
                
                # Load plugin metadata even if disabled
                self.load_plugin_metadata(plugin_name, plugin_path)
                
                # Load the plugin only if enabled
                if self.plugin_info[plugin_name]["enabled"]:
                    try:
                        self.load_plugin(plugin_name, plugin_path)
                    except Exception as e:
                        print(f"Error loading plugin {plugin_name}: {e}")
                        print(traceback.format_exc())
        
        # Save updated configuration
        self.save_plugin_config()
    
    def load_plugin_metadata(self, name, path):
        """Load plugin metadata without initializing it"""
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if it has the required Plugin class
            if hasattr(module, "Plugin"):
                plugin_class = getattr(module, "Plugin")
                
                # Create a temporary instance to get metadata
                temp_instance = plugin_class(None)
                
                # Update metadata in plugin_info
                if hasattr(temp_instance, "name"):
                    self.plugin_info[name]["name"] = temp_instance.name
                
                if hasattr(temp_instance, "description"):
                    self.plugin_info[name]["description"] = temp_instance.description
                
                if hasattr(temp_instance, "version"):
                    self.plugin_info[name]["version"] = temp_instance.version
                
                return True
            else:
                print(f"Plugin {name} does not have a Plugin class")
                return False
                
        except Exception as e:
            print(f"Failed to load plugin metadata for {name}: {e}")
            print(traceback.format_exc())
            return False
    
    def load_plugin(self, name, path):
        """Load and initialize a single plugin from path"""
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if it has the required Plugin class
            if hasattr(module, "Plugin"):
                plugin_class = getattr(module, "Plugin")
                plugin = plugin_class(self.main_window)
                
                # Store plugin instance
                self.plugins[name] = plugin
                print(f"Successfully loaded plugin: {name}")
                
                # Initialize the plugin if it should be shown in UI and hasn't been initialized yet
                if self.plugin_info[name]["show_in_ui"] and hasattr(plugin, "initialize") and name not in self.initialized_plugins:
                    plugin.initialize()
                    self.initialized_plugins.add(name)  # Mark as initialized
                
                return True
            else:
                print(f"Plugin {name} does not have a Plugin class")
                return False
                
        except Exception as e:
            print(f"Failed to load plugin {name}: {e}")
            print(traceback.format_exc())
            return False
    
    def execute_hook(self, hook_name, *args, **kwargs):
        """Execute a specific hook across all plugins"""
        results = {}
        
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, hook_name):
                try:
                    hook_method = getattr(plugin, hook_name)
                    results[plugin_name] = hook_method(*args, **kwargs)
                except Exception as e:
                    print(f"Error executing {hook_name} in plugin {plugin_name}: {e}")
                    print(traceback.format_exc())
        
        return results
