def import_custom_fields(self):
        """Import custom fields from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Custom Fields", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            # Read fields from file
            with open(file_path, "r") as f:
                imported_fields = json.load(f)
                
            if not isinstance(imported_fields, list):
                raise ValueError("Invalid format: Expected a list of custom fields")
                
            # Update custom fields table
            self.custom_fields_table.setRowCount(0)
            
            for field in imported_fields:
                row = self.custom_fields_table.rowCount()
                self.custom_fields_table.insertRow(row)
                
                # Field name
                name_item = QTableWidgetItem(field.get("name", ""))
                self.custom_fields_table.setItem(row, 0, name_item)
                
                # CSS selector
                selector_item = QTableWidgetItem(field.get("selector", ""))
                self.custom_fields_table.setItem(row, 1, selector_item)
                
                # Enabled checkbox
                enabled_checkbox = QCheckBox()
                enabled_checkbox.setChecked(field.get("enabled", True))
                
                # Create centered widget for checkbox
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(enabled_checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                self.custom_fields_table.setCellWidget(row, 2, checkbox_widget)
            
            QMessageBox.information(self, "Import Successful", f"Imported {len(imported_fields)} custom fields")
            
        except Exception as e:
            print(f"Error importing custom fields: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Import Failed", f"Failed to import custom fields: {str(e)}")
    
    def export_custom_fields(self):
        """Export custom fields to a JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Custom Fields", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            # Collect custom fields
            custom_fields = []
            
            for row in range(self.custom_fields_table.rowCount()):
                name = self.custom_fields_table.item(row, 0).text()
                selector = self.custom_fields_table.item(row, 1).text()
                
                # Get checkbox state
                checkbox_widget = self.custom_fields_table.cellWidget(row, 2)
                checkbox = checkbox_widget.findChild(QCheckBox)
                enabled = checkbox.isChecked() if checkbox else True
                
                custom_fields.append({
                    "name": name,
                    "selector": selector,
                    "enabled": enabled
                })
            
            # Write to file
            with open(file_path, "w") as f:
                json.dump(custom_fields, f, indent=4)
                
            QMessageBox.information(self, "Export Successful", f"Exported {len(custom_fields)} custom fields to {file_path}")
            
        except Exception as e:
            print(f"Error exporting custom fields: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Export Failed", f"Failed to export custom fields: {str(e)}")
    
    def update_preview(self):
        """Update the preview tab with current selections"""
        # Clear previous preview
        self.fields_list.clear()
        self.preview_table.setRowCount(0)
        
        # Get all selected fields
        selected_field_names = [field for field, selected in self.selected_fields.items() if selected]
        
        # Add selected fields to the list
        for field in selected_field_names:
            # Format field name for display
            display_name = field.replace('_', ' ').title()
            self.fields_list.addItem(display_name)
        
        # Get custom fields
        custom_fields = []
        for row in range(self.custom_fields_table.rowCount()):
            name = self.custom_fields_table.item(row, 0).text()
            
            # Get checkbox state
            checkbox_widget = self.custom_fields_table.cellWidget(row, 2)
            checkbox = checkbox_widget.findChild(QCheckBox)
            enabled = checkbox.isChecked() if checkbox else True
            
            if enabled:
                custom_fields.append(name)
                # Add to the fields list
                display_name = name.replace('_', ' ').title() + " (Custom)"
                self.fields_list.addItem(display_name)
        
        # Create preview table with example values
        example_values = {
            "title": "Professional Deep Fryer XL-5000",
            "description": "Commercial-grade deep fryer with 50lb oil capacity...",
            "sku": "FR-XL5000",
            "upc": "123456789012",
            "mpn": "XL5000-FR",
            "gtin": "00123456789012",
            "brand": "FryMaster",
            "manufacturer": "Kitchen Equipment Inc.",
            "model": "XL-5000",
            "price": "$2,499.99",
            "sale_price": "$2,199.99",
            "cost": "$1,875.00",
            "weight": "105 lbs",
            "dimensions": "36\" L x 24\" W x 48\" H",
            "food_type": "Commercial",
            "frypot_style": "Open",
            "heat": "Electric",
            "hertz": "60 Hz",
            "nema": "NEMA 5-15P",
            "number_of_fry_pots": "2",
            "oil_capacity": "50 lbs",
            "phase": "Single",
            "product_type": "Deep Fryer",
            "rating": "208V/240V",
            "special_features": "Automatic Filtration",
            "voltage": "208V",
            "warranty": "2 Year Parts & Labor",
            "material": "Stainless Steel",
            "color": "Silver",
            "size": "XL",
            "capacity": "50 lbs",
            "main_image": "https://example.com/images/fryer.jpg",
            "additional_images": "3 additional images",
            "video_links": "2 video links",
            "360_view": "Available",
            "pdf_manuals": "Installation Guide, User Manual",
            "cad_drawings": "Front, Side, Top views",
            "spec_sheets": "Technical Specifications Sheet",
            "stock_status": "In Stock",
            "availability": "Ships in 2-3 business days",
            "lead_time": "5-7 business days",
            "minimum_order_quantity": "1",
            "shipping_weight": "125 lbs",
            "shipping_dimensions": "40\" x 28\" x 52\"",
            "freight_class": "85",
            "harmonized_code": "8419.81.5000",
            "country_of_origin": "USA",
            "meta_title": "Professional Deep Fryer XL-5000 | Kitchen Equipment Inc.",
            "meta_description": "Commercial-grade electric deep fryer with 50lb oil capacity...",
            "meta_keywords": "deep fryer, commercial fryer, electric fryer",
            "search_terms": "restaurant equipment, kitchen fryer, commercial deep fryer",
            "features": "Automatic oil filtration, Fast heat recovery",
            "benefits": "Energy efficient, Easy to clean",
            "awards": "Kitchen Innovation Award 2024",
            "certifications": "NSF, UL, Energy Star"
        }
        
        # Add selected fields to the preview table
        for field in selected_field_names:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            
            # Field name
            display_name = field.replace('_', ' ').title()
            name_item = QTableWidgetItem(display_name)
            self.preview_table.setItem(row, 0, name_item)
            
            # Example value
            value = example_values.get(field, "Example value would appear here")
            value_item = QTableWidgetItem(value)
            self.preview_table.setItem(row, 1, value_item)
        
        # Add custom fields to the preview table
        for field in custom_fields:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            
            # Field name
            display_name = field.replace('_', ' ').title() + " (Custom)"
            name_item = QTableWidgetItem(display_name)
            self.preview_table.setItem(row, 0, name_item)
            
            # Example value for custom field
            value_item = QTableWidgetItem("Custom extracted value")
            self.preview_table.setItem(row, 1, value_item)
    
    def save_selections(self):
        """Save the current field selections to config"""
        try:
            # Save selected fields
            self.config["selected_fields"] = self.selected_fields
            
            # Save custom fields
            custom_fields = []
            
            for row in range(self.custom_fields_table.rowCount()):
                name = self.custom_fields_table.item(row, 0).text()
                selector = self.custom_fields_table.item(row, 1).text()
                
                # Get checkbox state
                checkbox_widget = self.custom_fields_table.cellWidget(row, 2)
                checkbox = checkbox_widget.findChild(QCheckBox)
                enabled = checkbox.isChecked() if checkbox else True
                
                custom_fields.append({
                    "name": name,
                    "selector": selector,
                    "enabled": enabled
                })
            
            self.config["custom_fields"] = custom_fields
            
            # Emit signal for parent to react to changes
            self.field_selection_changed.emit(self.config)
            
            QMessageBox.information(self, "Saved", "Field selections have been saved.")
            
        except Exception as e:
            print(f"Error saving field selections: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Save Failed", f"Failed to save field selections: {str(e)}")


class Plugin:
    """Field Selector plugin for enhanced scraping capabilities"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.name = "Field Selector"
        self.version = "1.0.0"
        self.description = "Select and customize fields to extract from web pages"
        self.button = None
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'field_selector_config.json')
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                # Return default config if file exists but has invalid JSON
                return self.get_default_config()
        else:
            # Return default config if file doesn't exist
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration for Field Selector"""
        return {
            "selected_fields": {
                "title": True,
                "description": True,
                "model": True,
                "manufacturer": True,
                "weight": True,
                "dimensions": True
            },
            "custom_fields": []
        }
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Field Selector configuration saved to {self.config_file}")
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving Field Selector configuration: {e}")
            print(traceback.format_exc())
            return False
    
    def initialize(self):
        """Called when the plugin is loaded"""
        print(f"Initializing {self.name} v{self.version}")
        
        # Check if button already exists before creating a new one
        if self.button is not None:
            print(f"Button already exists for {self.name}, not creating a new one")
            return
            
        # Find button layout
        button_layout = None
        for i in range(self.main_window.layout().count()):
            item = self.main_window.layout().itemAt(i)
            if item and item.layout():
                # Look for a layout with buttons
                if item.layout().count() > 0:
                    for j in range(item.layout().count()):
                        widget = item.layout().itemAt(j).widget()
                        if isinstance(widget, QPushButton):
                            button_layout = item.layout()
                            break
                if button_layout:
                    break
        
        if not button_layout:
            print("Could not find button layout")
            return
        
        # Check if this plugin's button already exists in the layout
        button_exists = False
        for i in range(button_layout.count()):
            widget = button_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == "Field Selector":
                button_exists = True
                self.button = widget  # Remember this button
                try:
                    self.button.clicked.disconnect()  # Disconnect any existing connections
                except:
                    pass  # No problem if it wasn't connected
                self.button.clicked.connect(self.on_button_clicked)
                print("Found existing Field Selector button and reconnected")
                break
        
        # Only create a new button if one doesn't exist
        if not button_exists:
            self.button = QPushButton("Field Selector", self.main_window)
            self.button.setObjectName("secondaryButton")
            self.button.clicked.connect(self.on_button_clicked)
            button_layout.addWidget(self.button)
            print("Added new Field Selector button")
            
            # Register with WebScraperFacade if available
            self.register_with_web_scraper()
    
    def on_button_clicked(self):
        """Handle the button click event"""
        try:
            dialog = FieldSelectorDialog(self.config, self.main_window)
            dialog.field_selection_changed.connect(self.save_config)
            dialog.exec_()
        except Exception as e:
            print(f"Error in Field Selector button click handler: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Field Selector: {str(e)}")
    
    def register_with_web_scraper(self):
        """Register with WebScraperFacade to enhance scraping capabilities"""
        try:
            # Try to import the WebScraperFacade
            from webscraper_facade import WebScraperFacade
            
            # Check if main_window has a scraper instance
            if hasattr(self.main_window, "scraper"):
                scraper = self.main_window.scraper
                
                # Register our config with the scraper
                if isinstance(scraper, WebScraperFacade):
                    scraper.field_selector_config = self.config
                    print("Registered Field Selector with WebScraperFacade")
            else:
                print("WebScraperFacade not found in main_window")
        except ImportError:
            print("WebScraperFacade not available, skipping registration")
        except Exception as e:
            print(f"Error registering with WebScraperFacade: {e}")
            print(traceback.format_exc())
    
    def hide_ui(self):
        """Hide UI elements when plugin is set to not show in UI"""
        if self.button:
            self.button.setVisible(False)
    
    def cleanup(self):
        """Called when the plugin is disabled or unloaded"""
        if self.button and self.button.parent():
            parent_layout = self.button.parent().layout()
            if parent_layout:
                parent_layout.removeWidget(self.button)
                self.button.deleteLater()
                self.button = None
'''
    
    # Write the Field Selector plugin
    with open(field_selector_path, "w") as f:
        f.write(field_selector)
    
    print(f"Created Field Selector plugin: {field_selector_path}")
    
    # Step 6: Create WebScraper Facade to enhance scraping
    webscraper_facade_path = os.path.join(current_dir, "webscraper_facade.py")
    webscraper_wrapper_path = os.path.join(current_dir, "webscraper_wrapper.py")
    
    # Only create if they don't exist (they seem to be already present)
    if not os.path.exists(webscraper_facade_path):
        # Create enhanced WebScraper Facade code if needed
        pass
    else:
        print(f"WebScraper Facade already exists at {webscraper_facade_path}")
    
    if not os.path.exists(webscraper_wrapper_path):
        # Create WebScraper Wrapper code if needed
        pass
    else:
        print(f"WebScraper Wrapper already exists at {webscraper_wrapper_path}")
    
    # Step 7: Create a clean API config file if it doesn't exist
    api_config_path = os.path.join(plugins_dir, "api_config.json")
    
    if not os.path.exists(api_config_path):
        # Create default API config
        default_api_config = {
            "shopify": {
                "enabled": False,
                "base_url": "",
                "api_key": "",
                "api_secret": "",
                "store_id": "",
                "admin_api": False,
                "webhook_url": ""
            },
            "sellercloud": {
                "enabled": False,
                "base_url": "",
                "api_key": "",
                "api_secret": "",
                "store_id": "",
                "company_id": "",
                "warehouse_id": ""
            },
            "ebay": {
                "enabled": False,
                "base_url": "",
                "api_key": "",
                "api_secret": "",
                "store_id": "",
                "marketplace_id": "EBAY_US",
                "sandbox_mode": False
            },
            "amazon": {
                "enabled": False,
                "base_url": "",
                "api_key": "",
                "api_secret": "",
                "store_id": "",
                "marketplace_id": "US",
                "seller_id": "",
                "mws_auth_token": ""
            },
            "settings": {
                "auto_sync": False,
                "sync_interval": "On Demand"
            },
            "field_mappings": []
        }
        
        with open(api_config_path, "w") as f:
            json.dump(default_api_config, f, indent=4)
        
        print(f"Created default API config: {api_config_path}")
    else:
        print(f"API config already exists at {api_config_path}")
    
    # Step 8: Create a README file with instructions
    readme_path = os.path.join(current_dir, "ENHANCED_PLUGINS_README.txt")
    
    readme = f"""ENHANCED PLUGIN SYSTEM

The plugin system has been enhanced with the following features:

1. Fixed API Manager with support for multiple platforms:
   - Shopify
   - SellerCloud
   - eBay
   - Amazon

2. Added Field Selector for customizing what data is extracted from web pages
   without modifying the core functionality

To use the enhanced plugin system:

1. Add these 3 lines to your MainWindow.__init__ method (after self.setup_ui()):

   # Load plugins
   from load_plugins import load_plugins
   load_plugins(self)

2. To enhance the web scraping capabilities to use the Field Selector,
   add these lines after creating each SheetRow instance:

   # Enhance SheetRow with customizable field extraction
   from webscraper_wrapper import create_webscraper_wrapper
   row = create_webscraper_wrapper(row)

3. That's it! The enhanced API Manager and Field Selector buttons will
   appear in your application's UI.

All the necessary files have been created:
- plugin_manager.py - Enhanced plugin manager
- plugins/api_manager_plugin.py - Enhanced API Manager plugin
- plugins/field_selector_plugin.py - New Field Selector plugin
- plugin_config.json - Clean configuration
- load_plugins.py - Helper to load plugins

Files created on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(readme_path, "w") as f:
        f.write(readme)
    
    print(f"Created README with instructions: {readme_path}")
    
    print("\nEnhanced plugin system has been successfully applied!")
    print("Follow the instructions in ENHANCED_PLUGINS_README.txt to complete the integration.")


if __name__ == "__main__":
    # Ask for confirmation before applying fixes
    confirm = input("This will apply enhanced plugin fixes to add API Manager and Field Selector. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
        
    apply_plugin_fixes()
