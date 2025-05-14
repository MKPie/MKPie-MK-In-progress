from plugins.field_selector_plugin import FieldSelectorPlugin

def load_plugins(parent):
    plugins = {}
    plugins["Field Selector"] = FieldSelectorPlugin(parent)
    return type('PluginManager', (), {'plugins': plugins})()
