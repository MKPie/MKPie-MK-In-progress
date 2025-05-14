import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal

class FieldSelectorPlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "Field Selector"
        self.config_path = os.path.join(os.path.dirname(__file__), "field_selector_config.json")
        self.config = self.load_config()
        self.widget = None

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                "selected_fields": {
                    "title": True,
                    "description": True,
                    "main_image": True,
                    "additional_images": True,
                    "manufacturer": True,
                    "food_type": True,
                    "frypot_style": True,
                    "heat": True,
                    "hertz": True,
                    "nema": True,
                    "number_of_fry_pots": True,
                    "oil_capacity_fryer_lb": True,
                    "phase": True,
                    "product": True,
                    "product_type": True,
                    "rating": True,
                    "special_features": True,
                    "type": True,
                    "voltage": True,
                    "warranty": True,
                    "weight": True
                },
                "custom_fields": [
                    {"name": "shipping_weight", "enabled": True, "process": "add_10"}
                ],
                "output_settings": {
                    "path": "~/GoogleDriveMount/Web/Output/",
                    "prefix": "processed_"
                }
            }

    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_widget(self):
        if not self.widget:
            self.widget = QWidget()
            layout = QVBoxLayout()
            self.checkboxes = {}
            for field, enabled in self.config["selected_fields"].items():
                cb = QCheckBox(field.replace('_', ' ').title())
                cb.setChecked(enabled)
                cb.stateChanged.connect(lambda state, f=field: self.update_field(f, state))
                self.checkboxes[field] = cb
                layout.addWidget(cb)
            for custom_field in self.config["custom_fields"]:
                field_name = custom_field.get("name", "")
                enabled = custom_field.get("enabled", True)
                cb = QCheckBox(field_name.replace('_', ' ').title())
                cb.setChecked(enabled)
                cb.stateChanged.connect(lambda state, f=field_name: self.update_custom_field(f, state))
                self.checkboxes[field_name] = cb
                layout.addWidget(cb)
            save_button = QPushButton("Save Configuration")
            save_button.clicked.connect(self.save_config)
            layout.addWidget(save_button)
            self.widget.setLayout(layout)
        return self.widget

    def update_field(self, field, state):
        self.config["selected_fields"][field] = bool(state)
        self.save_config()

    def update_custom_field(self, field_name, state):
        for custom_field in self.config["custom_fields"]:
            if custom_field["name"] == field_name:
                custom_field["enabled"] = bool(state)
                break
        self.save_config()

    def initialize(self):
        print(f"Initializing {self.name} plugin")
        self.parent.plugin_manager.plugins[self.name] = {"plugin": self, "config": self.config}
