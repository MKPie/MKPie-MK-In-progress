#!/usr/bin/env python3
# Save as apply_fixes.py

import os
import shutil
import json
import sys

def apply_fixes():
    """Apply all fixes to the MK Processor application"""
    print("Starting application fixes...")
    
    # Get the current directory (where this script is located)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Remove the multi-prefix plugin files
    multi_prefix_files = [
        os.path.join(current_dir, "disabled_plugins/x-multi_prefix_plugin.py"),
        os.path.join(current_dir, "disabled_plugins/x-multi_prefix_config.json")
    ]
    
    for file_path in multi_prefix_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
    
    # Step 2: Update the plugin manager
    plugin_manager_path = os.path.join(current_dir, "plugin_manager.py")
    plugin_manager_backup = os.path.join(current_dir, "plugin_manager.py.bak")
    
    # Backup the original plugin manager
    if os.path.exists(plugin_manager_path):
        try:
            shutil.copy2(plugin_manager_path, plugin_manager_backup)
            print(f"Backed up plugin manager to: {plugin_manager_backup}")
        except Exception as e:
            print(f"Error backing up plugin manager: {e}")
    
    # Write the updated plugin manager
    with open("fixed-plugin-manager.py", "r") as f:
        plugin_manager_content = f.read()
    
    with open(plugin_manager_path, "w") as f:
        f.write(plugin_manager_content)
    
    print(f"Updated: {plugin_manager_path}")
    
    # Step 3: Update the API Manager plugin
    api_manager_path = os.path.join(current_dir, "plugins/api_manager_plugin.py")
    api_manager_backup = os.path.join(current_dir, "plugins/api_manager_plugin.py.bak")
    
    # Create plugins directory if it doesn't exist
    os.makedirs(os.path.dirname(api_manager_path), exist_ok=True)
    
    # Backup the original API Manager plugin
    if os.path.exists(api_manager_path):
        try:
            shutil.copy2(api_manager_path, api_manager_backup)
            print(f"Backed up API Manager plugin to: {api_manager_backup}")
        except Exception as e:
            print(f"Error backing up API Manager plugin: {e}")
    
    # Write the updated API Manager plugin
    with open("fixed-api-manager-plugin.py", "r") as f:
        api_manager_content = f.read()
    
    with open(api_manager_path, "w") as f:
        f.write(api_manager_content)
    
    print(f"Updated: {api_manager_path}")
    
    # Step 4: Update the plugin configuration
    plugin_config_path = os.path.join(current_dir, "plugin_config.json")
    plugin_config_backup = os.path.join(current_dir, "plugin_config.json.bak")
    
    # Backup the original plugin configuration
    if os.path.exists(plugin_config_path):
        try:
            shutil.copy2(plugin_config_path, plugin_config_backup)
            print(f"Backed up plugin config to: {plugin_config_backup}")
        except Exception as e:
            print(f"Error backing up plugin config: {e}")
    
    # Write the updated plugin configuration
    with open("updated-plugin-config.json", "r") as f:
        plugin_config_content = f.read()
    
    with open(plugin_config_path, "w") as f:
        f.write(plugin_config_content)
    
    print(f"Updated: {plugin_config_path}")
    
    # Step 5: Ensure the API Manager config file exists
    api_config_path = os.path.join(current_dir, "plugins/api_config.json")
    if not os.path.exists(api_config_path):
        with open(api_config_path, "w") as f:
            f.write("""
{
    "endpoints": [],
    "base_url": "",
    "auth_type": "None",
    "auth_config": {}
}
            """.strip())
        print(f"Created: {api_config_path}")
    
    # Final cleanup
    cleanup_files = [
        "fixed-plugin-manager.py",
        "fixed-api-manager-plugin.py",
        "updated-plugin-config.json"
    ]
    
    for file_path in cleanup_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                print(f"Error removing temporary file {file_path}: {e}")
    
    print("\nAll fixes have been applied successfully!")
    print("Please restart the application for the changes to take effect.")

if __name__ == "__main__":
    # Ask for confirmation before applying fixes
    confirm = input("This will apply fixes to the MK Processor application. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
        
    apply_fixes()
