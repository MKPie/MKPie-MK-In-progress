#!/usr/bin/env python3
# Field Selector plugin for enhanced scraping capabilities

import os
import json
import traceback
from PyQt5.QtWidgets import (
    QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QDialog, QLabel, 
    QListWidget, QListWidgetItem, QCheckBox, QGroupBox, QScrollArea,
    QWidget, QFormLayout, QLineEdit, QComboBox, QGridLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QSplitter,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

class FieldGroup:
    """Grouping of related fields for the selector"""
    def __init__(self, name, fields=None):
        self.name = name
        self.fields = fields or []
        self.enabled = True

class FieldSelectorDialog(QDialog):
    """Dialog for selecting which fields to extract from web pages"""
    
    field_selection_changed = pyqtSignal(dict)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.field_groups = []
        self.selected_fields = {}
        
        self.setWindowTitle("Field Selector")
        self.resize(800, 600)
        
        # Init field groups
        self.init_field_groups()
        
        # Set up UI
        self.setup_ui()
        
        # Load saved field selections
        self.load_saved_selections()
    
    def init_field_groups(self):
        """Initialize field groups with default selections"""
        # Basic product info
        basic_info = FieldGroup("Basic Product Information")
        basic_info.fields = [
            "title", "description", "sku", "upc", "mpn", "gtin", "brand", "manufacturer",
            "model", "price", "sale_price", "cost", "weight", "dimensions"
        ]
        
        # Specifications
        specs = FieldGroup("Specifications")
        specs.fields = [
            "food_type", "frypot_style", "heat", "hertz", "nema", "number_of_fry_pots",
            "oil_capacity", "phase", "product_type", "rating", "special_features",
            "voltage", "warranty", "material", "color", "size", "capacity"
        ]
        
        # Media
        media = FieldGroup("Media")
        media.fields = [
            "main_image", "additional_images", "video_links", "360_view",
            "pdf_manuals", "cad_drawings", "spec_sheets"
        ]
        
        # Inventory & Shipping
        inventory = FieldGroup("Inventory & Shipping")
        inventory.fields = [
            "stock_status", "availability", "lead_time", "minimum_order_quantity",
            "shipping_weight", "shipping_dimensions", "freight_class",
            "harmonized_code", "country_of_origin"
        ]
        
        # SEO & Marketing
        seo = FieldGroup("SEO & Marketing")
        seo.fields = [
            "meta_title", "meta_description", "meta_keywords", "search_terms",
            "features", "benefits", "awards", "certifications"
        ]
        
        # Add groups to the list
        self.field_groups = [basic_info, specs, media, inventory, seo]
        
        # Add custom fields from config if available
        if "custom_fields" in self.config:
            custom = FieldGroup("Custom Fields")
            custom.fields = self.config.get("custom_fields", [])
            self.field_groups.append(custom)
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tabs widget
        self.tabs = QTabWidget()
        self.selection_tab = QWidget()
        self.custom_tab = QWidget()
        self.preview_tab = QWidget()
        
        self.tabs.addTab(self.selection_tab, "Field Selection")
        self.tabs.addTab(self.custom_tab, "Custom Fields")
        self.tabs.addTab(self.preview_tab, "Preview")
        
        # Set up each tab
        self.setup_selection_tab()
        self.setup_custom_tab()
        self.setup_preview_tab()
        
        # Add tabs to layout
        layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Selections")
        self.save_btn.clicked.connect(self.save_selections)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def setup_selection_tab(self):
        """Set up the field selection tab"""
        layout = QVBoxLayout(self.selection_tab)
        
        # Intro text
        intro = QLabel("Select the fields you want to extract from web pages:")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        
        # Create scrollable area for field groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Container for field groups
        container = QWidget()
        self.groups_layout = QVBoxLayout(container)
        
        # Create a group box for each field group
        for group in self.field_groups:
            group_box = QGroupBox(group.name)
            group_layout = QVBoxLayout(group_box)
            
            # Group enable checkbox
            group_checkbox = QCheckBox(f"Enable all {group.name} fields")
            group_checkbox.setChecked(group.enabled)
            group_checkbox.stateChanged.connect(lambda state, g=group: self.toggle_group(g, state == Qt.Checked))
            group_layout.addWidget(group_checkbox)
            
            # Field grid - 2 columns of checkboxes
            fields_layout = QGridLayout()
            
            # Add field checkboxes to the grid
            for i, field in enumerate(group.fields):
                row, col = divmod(i, 2)  # 2 columns
                
                # Format field name for display (underscores to spaces, title case)
                display_name = field.replace('_', ' ').title()
                
                checkbox = QCheckBox(display_name)
                # Store the original field name as property
                checkbox.setProperty("field_name", field)
                checkbox.setProperty("group_name", group.name)
                
                # Pre-select basic essential fields
                if group.name == "Basic Product Information" and field in ["title", "description", "model", "manufacturer"]:
                    checkbox.setChecked(True)
                    self.selected_fields[field] = True
                
                checkbox.stateChanged.connect(self.update_field_selection)
                fields_layout.addWidget(checkbox, row, col)
            
            group_layout.addLayout(fields_layout)
            self.groups_layout.addWidget(group_box)
        
        # Add container to scroll area
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Quick select buttons
        select_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_fields)
        
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_no_fields)
        
        self.select_essential_btn = QPushButton("Select Essential")
        self.select_essential_btn.clicked.connect(self.select_essential_fields)
        
        select_layout.addWidget(self.select_essential_btn)
        select_layout.addWidget(self.select_all_btn)
        select_layout.addWidget(self.select_none_btn)
        
        layout.addLayout(select_layout)
    
    def setup_custom_tab(self):
        """Set up the custom fields tab"""
        layout = QVBoxLayout(self.custom_tab)
        
        # Intro text
        intro = QLabel("Define custom fields to extract from web pages:")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        
        # Custom fields table
        self.custom_fields_table = QTableWidget(0, 3)
        self.custom_fields_table.setHorizontalHeaderLabels(["Field Name", "CSS Selector", "Enabled"])
        self.custom_fields_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.custom_fields_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.custom_fields_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.custom_fields_table)
        
        # Add/Remove buttons
        buttons_layout = QHBoxLayout()
        
        self.add_custom_btn = QPushButton("Add Custom Field")
        self.add_custom_btn.clicked.connect(self.add_custom_field)
        
        self.remove_custom_btn = QPushButton("Remove Custom Field")
        self.remove_custom_btn.clicked.connect(self.remove_custom_field)
        
        buttons_layout.addWidget(self.add_custom_btn)
        buttons_layout.addWidget(self.remove_custom_btn)
        
        layout.addLayout(buttons_layout)
        
        # Import/Export area
        import_export = QGroupBox("Import/Export Custom Fields")
        import_export_layout = QHBoxLayout(import_export)
        
        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self.import_custom_fields)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_custom_fields)
        
        import_export_layout.addWidget(self.import_btn)
        import_export_layout.addWidget(self.export_btn)
        
        layout.addWidget(import_export)
    
    def setup_preview_tab(self):
        """Set up the preview tab"""
        layout = QVBoxLayout(self.preview_tab)
        
        # Intro text
        intro = QLabel("Preview selected fields that will be extracted:")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        
        # Split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Selected fields list
        fields_group = QGroupBox("Selected Fields")
        fields_layout = QVBoxLayout(fields_group)
        
        self.fields_list = QListWidget()
        fields_layout.addWidget(self.fields_list)
        
        # Output preview
        preview_group = QGroupBox("Output Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        preview_text = QLabel("This is how the extracted data will look:")
        preview_text.setWordWrap(True)
        preview_layout.addWidget(preview_text)
        
        self.preview_table = QTableWidget(0, 2)
        self.preview_table.setHorizontalHeaderLabels(["Field", "Example Value"])
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        preview_layout.addWidget(self.preview_table)
        
        # Add to splitter
        splitter.addWidget(fields_group)
        splitter.addWidget(preview_group)
        splitter.setSizes([200, 400])  # Initial sizes
        
        layout.addWidget(splitter)
        
        # Update preview button
        self.update_preview_btn = QPushButton("Update Preview")
        self.update_preview_btn.clicked.connect(self.update_preview)
        layout.addWidget(self.update_preview_btn)
    
    def load_saved_selections(self):
        """Load saved field selections from config"""
        if "selected_fields" in self.config:
            self.selected_fields = self.config.get("selected_fields", {})
            
            # Update checkboxes to match saved selections
            self.update_checkboxes_from_selection()
        
        # Load custom fields
        if "custom_fields" in self.config:
            custom_fields = self.config.get("custom_fields", [])
            
            # Update custom fields table
            self.custom_fields_table.setRowCount(0)
            
            for field in custom_fields:
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
        
        # Update preview tab
        self.update_preview()
    
    def update_checkboxes_from_selection(self):
        """Update all checkboxes to match saved selections"""
        # Iterate through all groups and fields in the UI
        for i in range(self.groups_layout.count()):
            group_box = self.groups_layout.itemAt(i).widget()
            if not isinstance(group_box, QGroupBox):
                continue
                
            # Get the group layout
            group_layout = group_box.layout()
            
            # Check for field checkboxes (they're in a grid inside the group layout)
            for j in range(group_layout.count()):
                if isinstance(group_layout.itemAt(j), QGridLayout):
                    grid_layout = group_layout.itemAt(j)
                    
                    # Iterate through grid layout items
                    for k in range(grid_layout.count()):
                        item = grid_layout.itemAt(k)
                        if item and item.widget() and isinstance(item.widget(), QCheckBox):
                            checkbox = item.widget()
                            field_name = checkbox.property("field_name")
                            
                            # Skip the group checkbox
                            if not field_name:
                                continue
                                
                            # Set checkbox state based on saved selection
                            checkbox.setChecked(self.selected_fields.get(field_name, False))
    
    def update_field_selection(self, state):
        """Update the selected fields when a checkbox state changes"""
        checkbox = self.sender()
        field_name = checkbox.property("field_name")
        
        if field_name:
            self.selected_fields[field_name] = (state == Qt.Checked)
    
    def toggle_group(self, group, enabled):
        """Toggle all fields in a group"""
        group.enabled = enabled
        
        # Find and update all checkboxes for this group
        for i in range(self.groups_layout.count()):
            group_box = self.groups_layout.itemAt(i).widget()
            if not isinstance(group_box, QGroupBox):
                continue
                
            if group_box.title() == group.name:
                # Get the group layout
                group_layout = group_box.layout()
                
                # Check for field checkboxes (they're in a grid inside the group layout)
                for j in range(group_layout.count()):
                    if isinstance(group_layout.itemAt(j), QGridLayout):
                        grid_layout = group_layout.itemAt(j)
                        
                        # Iterate through grid layout items
                        for k in range(grid_layout.count()):
                            item = grid_layout.itemAt(k)
                            if item and item.widget() and isinstance(item.widget(), QCheckBox):
                                checkbox = item.widget()
                                field_name = checkbox.property("field_name")
                                
                                # Skip the group checkbox
                                if not field_name:
                                    continue
                                    
                                # Update checkbox state
                                checkbox.setChecked(enabled)
                                
                                # Update selected fields
                                self.selected_fields[field_name] = enabled
    
    def select_all_fields(self):
        """Select all fields"""
        for group in self.field_groups:
            self.toggle_group(group, True)
    
    def select_no_fields(self):
        """Deselect all fields"""
        for group in self.field_groups:
            self.toggle_group(group, False)
    
    def select_essential_fields(self):
        """Select only essential fields"""
        # First deselect all
        self.select_no_fields()
        
        # Define essential fields
        essential_fields = [
            "title", "description", "model", "manufacturer", "weight", 
            "dimensions", "price", "sku", "main_image", "video_links"
        ]
        
        # Select only the essential fields
        for i in range(self.groups_layout.count()):
            group_box = self.groups_layout.itemAt(i).widget()
            if not isinstance(group_box, QGroupBox):
                continue
                
            # Get the group layout
            group_layout = group_box.layout()
            
            # Check for field checkboxes
            for j in range(group_layout.count()):
                if isinstance(group_layout.itemAt(j), QGridLayout):
                    grid_layout = group_layout.itemAt(j)
                    
                    # Iterate through grid layout items
                    for k in range(grid_layout.count()):
                        item = grid_layout.itemAt(k)
                        if item and item.widget() and isinstance(item.widget(), QCheckBox):
                            checkbox = item.widget()
                            field_name = checkbox.property("field_name")
                            
                            # Skip the group checkbox
                            if not field_name:
                                continue
                                
                            # Check if this is an essential field
                            if field_name in essential_fields:
                                checkbox.setChecked(True)
                                self.selected_fields[field_name] = True
    
    def add_custom_field(self):
        """Add a new custom field to the table"""
        row = self.custom_fields_table.rowCount()
        self.custom_fields_table.insertRow(row)
        
        # Field name
        self.custom_fields_table.setItem(row, 0, QTableWidgetItem("custom_field"))
        
        # CSS selector
        self.custom_fields_table.setItem(row, 1, QTableWidgetItem(".selector"))
        
        # Enabled checkbox
        enabled_checkbox = QCheckBox()
        enabled_checkbox.setChecked(True)
        
        # Create centered widget for checkbox
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(enabled_checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        
        self.custom_fields_table.setCellWidget(row, 2, checkbox_widget)
        
        # Start editing the field name
        self.custom_fields_table.editItem(self.custom_fields_table.item(row, 0))
    
    def remove_custom_field(self):
        """Remove the selected custom field"""
        selected_rows = self.custom_fields_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        self.custom_fields_table.removeRow(row)
    
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
