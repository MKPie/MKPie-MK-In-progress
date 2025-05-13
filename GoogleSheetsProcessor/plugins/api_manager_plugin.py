#!/usr/bin/env python3
# Minimal API Manager plugin with fix for duplicate buttons

import os
import json
import traceback
from PyQt5.QtWidgets import QPushButton, QMessageBox

class Plugin:
    """Minimal plugin for API manager functionality with fix for duplicate buttons"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.name = "API Manager"
        self.version = "1.0.0"
        self.description = "Manage API integrations for product data retrieval"
        self.button = None
        
    def initialize(self):
        """Called when the plugin is loaded - with fix for duplicate buttons"""
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
            if isinstance(widget, QPushButton) and widget.text() == "API Manager":
                button_exists = True
                self.button = widget  # Remember this button
                try:
                    self.button.clicked.disconnect()  # Disconnect any existing connections
                except:
                    pass  # No problem if it wasn't connected
                self.button.clicked.connect(self.on_button_clicked)
                print("Found existing API Manager button and reconnected")
                break
        
        # Only create a new button if one doesn't exist
        if not button_exists:
            self.button = QPushButton("API Manager", self.main_window)
            self.button.setObjectName("secondaryButton")
            self.button.clicked.connect(self.on_button_clicked)
            button_layout.addWidget(self.button)
            print("Added new API Manager button")
    
    def on_button_clicked(self):
        """Handle the button click event"""
        QMessageBox.information(self.main_window, "API Manager", 
                               "API Manager functionality is under development.")
        
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
