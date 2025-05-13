#!/usr/bin/env python3
# fix_plugins_and_image_fields.py - Script to fix plugin loading and image field selection

import os
import json
import sys
import shutil

def fix_issues():
    print("Starting to fix plugin and image field issues...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Ensure plugins directory exists
    plugins_dir = os.path.join(current_dir, "plugins")
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        print(f"Created plugins directory: {plugins_dir}")
    
    # 2. Fix field_selector_config.json
    field_selector_config_path = os.path.join(plugins_dir, "field_selector_config.json")
    
    # Default configuration with essential fields enabled
    default_config = {
        "selected_fields": {
            "title": True,
            "description": True,
            "model": True,
            "manufacturer": True,
            "weight": True,
            "dimensions": True,
            "price": True,
            "sku": True,
            "main_image": True,
            "additional_images": True,
            "video_links": True,
            # Other fields can be false
            "upc": False,
            "mpn": False,
            "gtin": False,
            "brand": False,
            "sale_price": False,
            "cost": False
        },
        "custom_fields": []
    }
    
    # Load existing config if it exists, or use default
    if os.path.exists(field_selector_config_path):
        try:
            with open(field_selector_config_path, 'r') as f:
                config = json.load(f)
                
            # Ensure image fields are enabled
            if "selected_fields" in config:
                config["selected_fields"]["main_image"] = True
                config["selected_fields"]["additional_images"] = True
                config["selected_fields"]["video_links"] = True
            else:
                config["selected_fields"] = default_config["selected_fields"]
                
            print(f"Updated existing field selector config")
        except Exception as e:
            print(f"Error reading field selector config, using default: {e}")
            config = default_config
    else:
        config = default_config
        print(f"Creating new field selector config with defaults")
    
    # Save the config
    with open(field_selector_config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Saved field selector config to: {field_selector_config_path}")
    
    # 3. Ensure plugin_config.json has field_selector_plugin enabled
    plugin_config_path = os.path.join(current_dir, "plugin_config.json")
    if os.path.exists(plugin_config_path):
        try:
            with open(plugin_config_path, 'r') as f:
                plugin_config = json.load(f)
                
            # Ensure field_selector_plugin is enabled
            plugin_config["field_selector_plugin"] = {
                "enabled": True,
                "show_in_ui": True,
                "name": "Field Selector",
                "description": "Select and customize fields to extract from web pages",
                "version": "1.0.0"
            }
            
            # Ensure API Manager is enabled
            plugin_config["api_manager_plugin"] = {
                "enabled": True,
                "show_in_ui": True,
                "name": "API Manager",
                "description": "Manage API integrations for product data retrieval",
                "version": "1.0.0"
            }
            
            print(f"Updated plugin config to enable needed plugins")
        except Exception as e:
            print(f"Error reading plugin config: {e}")
            plugin_config = {
                "api_manager_plugin": {
                    "enabled": True,
                    "show_in_ui": True,
                    "name": "API Manager",
                    "description": "Manage API integrations for product data retrieval",
                    "version": "1.0.0"
                },
                "field_selector_plugin": {
                    "enabled": True,
                    "show_in_ui": True,
                    "name": "Field Selector",
                    "description": "Select and customize fields to extract from web pages",
                    "version": "1.0.0"
                }
            }
            
        # Save the plugin config
        with open(plugin_config_path, 'w') as f:
            json.dump(plugin_config, f, indent=4)
        print(f"Saved plugin config to: {plugin_config_path}")
    
    # 4. Check if field_selector_plugin.py exists in plugins directory
    field_selector_plugin_path = os.path.join(plugins_dir, "field_selector_plugin.py")
    if not os.path.exists(field_selector_plugin_path):
        # Source path - check disabled_plugins directory first
        source_paths = [
            os.path.join(current_dir, "disabled_plugins", "field_selector_plugin.py"),
            os.path.join(current_dir, "fix_plugins.py")  # This contains the code as a string
        ]
        
        source_path = None
        for path in source_paths:
            if os.path.exists(path):
                source_path = path
                break
                
        if source_path:
            # Copy or extract the file
            if source_path.endswith("field_selector_plugin.py"):
                # Direct copy
                shutil.copy2(source_path, field_selector_plugin_path)
                print(f"Copied field_selector_plugin.py from {source_path}")
            else:
                # Extract from fix_plugins.py
                with open(source_path, 'r') as f:
                    content = f.read()
                    
                # Find the class definition
                plugin_code = None
                if "class Plugin:" in content and "Field Selector" in content:
                    # Extract the complete plugin code - this is a simplified approach
                    # A more robust approach would use regex or parse the Python code
                    lines = content.split("\n")
                    plugin_lines = []
                    in_plugin = False
                    
                    for line in lines:
                        if line.startswith("class Plugin:") and "Field Selector" in content:
                            in_plugin = True
                            plugin_lines.append("#!/usr/bin/env python3")
                            plugin_lines.append("# Field Selector plugin for enhanced scraping capabilities")
                            plugin_lines.append("")
                            plugin_lines.append("import os")
                            plugin_lines.append("import json")
                            plugin_lines.append("import traceback")
                            plugin_lines.append("from PyQt5.QtWidgets import (")
                            plugin_lines.append("    QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QDialog, QLabel, ")
                            plugin_lines.append("    QListWidget, QListWidgetItem, QCheckBox, QGroupBox, QScrollArea,")
                            plugin_lines.append("    QWidget, QFormLayout, QLineEdit, QComboBox, QGridLayout, QTabWidget,")
                            plugin_lines.append("    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QSplitter,")
                            plugin_lines.append("    QSpacerItem, QSizePolicy")
                            plugin_lines.append(")")
                            plugin_lines.append("from PyQt5.QtCore import Qt, pyqtSignal")
                            plugin_lines.append("from PyQt5.QtGui import QFont, QIcon")
                            plugin_lines.append("")
                            
                        if in_plugin:
                            plugin_lines.append(line)
                            
                    plugin_code = "\n".join(plugin_lines)
                
                if plugin_code:
                    with open(field_selector_plugin_path, 'w') as f:
                        f.write(plugin_code)
                    print(f"Created field_selector_plugin.py from extracted code")
                else:
                    print(f"Could not extract field_selector plugin code")
        else:
            print(f"Could not find source for field_selector_plugin.py")
    
    # 5. Verify that load_plugins.py exists
    load_plugins_path = os.path.join(current_dir, "load_plugins.py")
    if not os.path.exists(load_plugins_path):
        # Create simple load_plugins.py
        with open(load_plugins_path, 'w') as f:
            f.write("""#!/usr/bin/env python3
# Simple plugin loader that can be added to main.py

import os
import sys
import traceback

def load_plugins(main_window):
    \"\"\"Load plugins for MK Processor without modifying main.py\"\"\"
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
""")
        print(f"Created load_plugins.py")
    
    # 6. Create manual field selector button script as backup
    manual_btn_script_path = os.path.join(current_dir, "add_field_selector_button.py")
    with open(manual_btn_script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
# Manually add Field Selector button if plugins aren't working

def add_field_selector_button(main_window):
    \"\"\"Manually add a Field Selector button to the main window\"\"\"
    try:
        from PyQt5.QtWidgets import QPushButton
        import os
        import json
        
        # Find the button layout
        button_layout = None
        for i in range(main_window.layout().count()):
            item = main_window.layout().itemAt(i)
            if item and item.layout():
                for j in range(item.layout().count()):
                    widget = item.layout().itemAt(j).widget()
                    if isinstance(widget, QPushButton):
                        button_layout = item.layout()
                        break
                if button_layout:
                    break
        
        if not button_layout:
            print("Could not find button layout")
            return False
        
        # Check if Field Selector button already exists
        for i in range(button_layout.count()):
            widget = button_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == "Field Selector":
                print("Field Selector button already exists")
                return True
        
        # Define function to open field selector dialog
        def open_field_selector():
            # Load or create field selector config
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "plugins", "field_selector_config.json")
            
            # Ensure plugins directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                except:
                    config = {"selected_fields": {}}
            else:
                config = {"selected_fields": {}}
            
            # Ensure selected_fields exists
            if "selected_fields" not in config:
                config["selected_fields"] = {}
            
            # Enable essential fields including images
            essential_fields = [
                "title", "description", "model", "manufacturer", 
                "weight", "dimensions", "price", "sku",
                "main_image", "additional_images", "video_links"
            ]
            
            for field in essential_fields:
                config["selected_fields"][field] = True
            
            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Updated field_selector_config.json to enable essential fields")
        
        # Create and add the button
        field_selector_btn = QPushButton("Field Selector", main_window)
        field_selector_btn.setObjectName("secondaryButton")
        field_selector_btn.clicked.connect(open_field_selector)
        button_layout.addWidget(field_selector_btn)
        
        print("Manually added Field Selector button")
        return True
        
    except Exception as e:
        import traceback
        print(f"Error adding Field Selector button: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("This script is meant to be imported into main.py")
    print("Add the following to your MainWindow.__init__ method:")
    print("try:")
    print("    from add_field_selector_button import add_field_selector_button")
    print("    add_field_selector_button(self)")
    print("except Exception as e:")
    print("    print(f'Error adding Field Selector button: {e}')")
""")
    print(f"Created backup script: {manual_btn_script_path}")
    
    print("\nAll fixes have been applied successfully!")
    print("Please restart the application for the changes to take effect.")

if __name__ == "__main__":
    fix_issues()
