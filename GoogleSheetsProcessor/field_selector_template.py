# Step 5: Create Field Selector plugin
field_selector_path = os.path.join(plugins_dir, "field_selector_plugin.py")
field_selector_template_path = os.path.join(current_dir, "field_selector_template.py")

# Check if template file exists, otherwise create it
if os.path.exists(field_selector_template_path):
    # Copy the template file to the plugins directory
    shutil.copy2(field_selector_template_path, field_selector_path)
    print(f"Created Field Selector plugin by copying template: {field_selector_path}")
else:
    print(f"Field Selector template file not found: {field_selector_template_path}")
    print("Please create it separately using the provided code.")
