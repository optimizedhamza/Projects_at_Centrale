import json
import os

def save_configuration(self):
    """Saves the current settings to a configuration file in the application's directory."""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    config = {
        'city_name': self.city_name_var.get(),
        'weather_api_key': self.weather_api_key_var.get(),
        'img_api_key': self.img_api_key_var.get(),
        'update_frequency': self.update_frequency_var.get(),
    }
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    print("Configuration saved.")
    
def load_configuration(self):
    """Loads settings from a configuration file in the application's directory."""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        self.city_name_var.set(config.get('city_name', ''))
        self.weather_api_key_var.set(config.get('weather_api_key', 'insert your API Key here!'))
        self.img_api_key_var.set(config.get('img_api_key', 'insert your API Key here!'))
        self.update_frequency_var.set(config.get('update_frequency', '3600'))  # Default to 3600 seconds
        print("Configuration loaded.")
    except FileNotFoundError:
        print("Configuration file not found. Using default settings.")
