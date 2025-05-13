#!/usr/bin/env python3
# Manually add Field Selector button if plugins aren't working

def add_field_selector_button(main_window):
    """Manually add a Field Selector button to the main window"""
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
