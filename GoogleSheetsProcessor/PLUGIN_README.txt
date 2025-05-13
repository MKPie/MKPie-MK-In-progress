PLUGIN SYSTEM FIXES

The plugin system has been fixed to resolve the following issues:
1. Removed the problematic multi-prefix plugin
2. Fixed the duplicate API Manager button issue

To use the fixed plugin system:

1. You don't need to modify your main.py file!

2. Simply add these 3 lines to your MainWindow.__init__ method, after self.setup_ui():

   # Load plugins (optional)
   from load_plugins import load_plugins
   load_plugins(self)

3. That's it! Your main.py script will continue to work with all its core
   functionality, but now with properly managed plugins.

All the necessary files have been created:
- plugin_manager.py - Fixed plugin manager
- plugins/api_manager_plugin.py - Fixed API Manager plugin
- plugin_config.json - Clean configuration without multi-prefix plugin
- load_plugins.py - Helper to load plugins without modifying main.py

Files created on: 2025-05-13 11:27:46
