import tkinter as tk
from tkinter import ttk
import threading
import os
from PIL import Image, ImageTk
import json
import time
import webbrowser
from datetime import datetime
from config.config_manager import load_configuration, save_configuration
from weather.weather_service import fetch_weather, kelvin_to_celsius
from wallpaper.image_generator import generate_prompt, generate_image_from_prompt
from wallpaper.wallpaper_manager import cut_generated_image, cleanup_old_images, set_wallpaper_windows

class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Artistic Weather Wallpaper")
        self.update_thread = None  # Holds the update thread
        self.update_stop = threading.Event()  # Signal to stop the update thread
        self.update_pause = threading.Event()  # Signal to pause/resume the update thread
        self.create_widgets()
        self.load_configuration()  # Load saved configuration
        self.apply_theme()  # Apply custom theme
        self.make_responsive()  # Make the design responsive
        self.set_large_icon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'winter_school.jpeg'))

    def set_large_icon(self, icon_path):
        img = Image.open(icon_path)
        icon_image = ImageTk.PhotoImage(img)
        self.root.iconphoto(True, icon_image)

    def create_widgets(self):
        # Input Frame for User Inputs
        input_frame = ttk.Frame(self.root)
        input_frame.grid(column=0, row=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        input_frame.columnconfigure(1, weight=1)  # Allow the second column to expand

        # City Name
        ttk.Label(input_frame, text="City Name:").grid(column=0, row=0, sticky=tk.W)
        self.city_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.city_name_var).grid(column=1, row=0, sticky=(tk.W, tk.E))

        # Weather Information Frame
        weather_info_frame = ttk.Frame(self.root)
        weather_info_frame.grid(column=0, row=3, sticky=(tk.W, tk.E), padx=10, pady=10)
        weather_info_frame.columnconfigure(1, weight=1)  # Allow labels to expand

        # City Name Display
        ttk.Label(weather_info_frame, text="City:").grid(column=0, row=0, sticky=tk.W)
        self.display_city_name_var = tk.StringVar()
        self.display_city_name_var.set("N/A")
        ttk.Label(weather_info_frame, textvariable=self.display_city_name_var).grid(column=1, row=0, sticky=(tk.W, tk.E))

        # Temperature Display
        ttk.Label(weather_info_frame, text="Temperature:").grid(column=0, row=1, sticky=tk.W)
        self.display_temperature_var = tk.StringVar()
        self.display_temperature_var.set("N/A")
        ttk.Label(weather_info_frame, textvariable=self.display_temperature_var).grid(column=1, row=1, sticky=(tk.W, tk.E))

        # Weather Condition Display
        ttk.Label(weather_info_frame, text="Condition:").grid(column=0, row=2, sticky=tk.W)
        self.display_weather_condition_var = tk.StringVar()
        self.display_weather_condition_var.set("N/A")
        ttk.Label(weather_info_frame, textvariable=self.display_weather_condition_var).grid(column=1, row=2, sticky=(tk.W, tk.E))

        # Weather API Key
        ttk.Label(input_frame, text="Weather API Key:").grid(column=0, row=1, sticky=tk.W)
        self.weather_api_key_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.weather_api_key_var).grid(column=1, row=1, sticky=(tk.W, tk.E))

        # Image Generation API Key
        ttk.Label(input_frame, text="Eden AI API Key:").grid(column=0, row=2, sticky=tk.W)
        self.img_api_key_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.img_api_key_var).grid(column=1, row=2, sticky=(tk.W, tk.E))

        # Update Frequency
        ttk.Label(input_frame, text="Update Frequency (seconds):").grid(column=0, row=3, sticky=tk.W)
        self.update_frequency_var = tk.StringVar()
        self.update_frequency_var.set("3600")  # Default to 1 hour
        ttk.Entry(input_frame, textvariable=self.update_frequency_var).grid(column=1, row=3, sticky=(tk.W, tk.E))

        # Control Frame for Buttons
        control_frame = ttk.Frame(self.root)
        control_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Save button
        self.save_button = ttk.Button(control_frame, text="Save Settings", command=self.save_configuration)
        self.save_button.grid(column=4, row=0, sticky=tk.E, padx=5)


        # Start Button
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_update_process)
        self.start_button.grid(column=1, row=0, sticky=tk.E)

        # Pause Button
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_update_process)
        self.pause_button.grid(column=2, row=0, sticky=tk.E, padx=5)
        self.pause_button["state"] = "disabled"  # Disabled until update starts

        # Stop Button
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_update_process)
        self.stop_button.grid(column=3, row=0, sticky=tk.E, padx=5)
        self.stop_button["state"] = "disabled"  # Disabled until update starts

        # Create a new frame for the additional buttons
        link_buttons_frame = ttk.Frame(self.root)
        link_buttons_frame.grid(column=0, row=4, sticky=(tk.W, tk.E), padx=10, pady=5)
        link_buttons_frame.columnconfigure(0, weight=1)  # This centers the content of the frame

        # Button that redirects to the weather API
        self.link_button1 = ttk.Button(link_buttons_frame, text="Get Weather API", command=lambda: webbrowser.open('https://openweathermap.org/price'))
        self.link_button1.grid(column=0, row=0, sticky=tk.EW) 
        self.link_button1["style"] = "LinkButton1.TButton" 

        # Button that redirects to the Eden AI API
        self.link_button2 = ttk.Button(link_buttons_frame, text="Get Eden AI API", command=lambda: webbrowser.open('https://www.edenai.co/pricing'))
        self.link_button2.grid(column=1, row=0, sticky=tk.EW)  
        self.link_button2["style"] = "LinkButton2.TButton"

        # Ensure the main window's grid columns can expand
        self.root.columnconfigure(0, weight=1)

        # Status Frame for Updates and Messages
        status_frame = ttk.Frame(self.root)
        status_frame.grid(column=0, row=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        status_frame.columnconfigure(0, weight=1)  # Allow the status label to expand

        # Status Message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(status_frame, textvariable=self.status_var).grid(column=0, row=0, sticky=(tk.W, tk.E))

        # Ensure the main window's grid columns can expand
        self.root.columnconfigure(0, weight=1)
        for widget in [input_frame, control_frame, status_frame]:
            widget.columnconfigure(0, weight=1)

    def apply_theme(self):
        style = ttk.Style(self.root)
        
        # Optionally set a base theme
        style.theme_use('clam')
        
        # General style configurations
        style.configure('.', font=('Helvetica', 10), background='#F0F0F0', foreground='#505050')
        style.configure('TFrame', background='#F0F0F0')
        
        # Button style
        style.configure('TButton', font=('Helvetica', 10), foreground='#F0F0F0', background='#0078D7', borderwidth=1)
        style.map('TButton',
                foreground=[('pressed', '#F0F0F0'), ('active', '#F0F0F0')],
                background=[('pressed', '!disabled', '#005EA6'), ('active', '#005EA6')],
                bordercolor=[('active', '#005EA6')],
                lightcolor=[('pressed', '#005EA6'), ('active', '#005EA6')],
                darkcolor=[('pressed', '#005EA6'), ('active', '#005EA6')])
        
        # Entry style
        style.configure('TEntry', fieldbackground='#FFFFFF', foreground='#505050', bordercolor='#BEBEBE')
        
        # Label style
        style.configure('TLabel', background='#F0F0F0', foreground='#505050')

        # Style for the first link button
        style.configure('LinkButton1.TButton', font=('Helvetica', 8), foreground='white', background='green')
        # Style for the second link button
        style.configure('LinkButton2.TButton', font=('Helvetica', 8), foreground='white', background='green')

    def make_responsive(self):
        self.root.columnconfigure(0, weight=1)
        for i in range(4):  # Adjust the range based on your grid
            self.root.rowconfigure(i, weight=1)
            for j in range(2):  # Adjust based on the number of columns in your grid
                self.root.columnconfigure(j, weight=1)
    
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

    def start_update_process(self):
        # Retrieve inputs from the GUI elements
        city_name = self.city_name_var.get()
        weather_api_key = self.weather_api_key_var.get()
        img_api_key = self.img_api_key_var.get()
        update_frequency = int(self.update_frequency_var.get())

        # Now, with the variables properly defined, proceed to start the update thread
        self.start_button["state"] = "disabled"
        self.pause_button["state"] = "normal"
        self.stop_button["state"] = "normal"
        self.pause_button["text"] = "Pause"
        self.status_var.set("Starting...")

        self.update_stop.clear()  # Ensure stop signal is not set
        self.update_pause.clear()  # Ensure pause signal is not set

        # Start the update process in a separate thread
        self.update_thread = threading.Thread(target=self.update_process, args=(city_name, weather_api_key, img_api_key, update_frequency), daemon=True)
        self.update_thread.start()


    def pause_update_process(self):
        if self.update_pause.is_set():
            self.update_pause.clear()  # Clear pause signal to resume
            self.status_var.set("Resumed. Updating...")
            self.pause_button["text"] = "Pause"
        else:
            self.update_pause.set()  # Set pause signal
            self.status_var.set("Paused. Click Resume to continue.")
            self.pause_button["text"] = "Resume"

    def stop_update_process(self):
        self.update_stop.set()  # Signal the thread to stop
        self.status_var.set("Stopped. Click Start to begin again.")
        self.start_button["state"] = "normal"
        self.pause_button["state"] = "disabled"
        self.stop_button["state"] = "disabled"


    def update_process(self, city_name, weather_api_key, img_api_key, update_frequency):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        image_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), city_name + "_" + datetime.now().strftime("%Y-%m-%d") + ".png") 
        image_pattern = "*.png"  # Pattern to match the images for cleanup
        max_images_to_keep = 5  # Adjust based on how many images you want to keep

        while not self.update_stop.is_set():
            if self.update_pause.is_set():
                self.status_var.set("Paused. Waiting to resume...")
                self.root.update_idletasks()  # Ensure UI updates are reflected
                self.update_pause.wait()  # Wait here until pause is cleared
                self.status_var.set("Resumed. Continuing updates...")
                self.root.update_idletasks()  # Ensure UI updates are reflected

            try:
                self.status_var.set("Fetching weather data...")
                self.root.update_idletasks()  # Update UI
                
                # Fetch updated weather data
                weather_data = fetch_weather(base_url, weather_api_key, city_name)
                if weather_data is not None:
                    city_name, timestamp, temperature_k, weather_description = weather_data

                    # Update the UI with the fetched weather information
                    self.display_city_name_var.set(city_name)
                    temperature_c = kelvin_to_celsius(temperature_k)
                    self.display_temperature_var.set(f"{temperature_c:.2f}°C")
                    self.display_weather_condition_var.set(weather_description)

                    prompt = generate_prompt(city_name, timestamp, temperature_k, weather_description)

                    self.status_var.set("Generating image...")
                    self.root.update_idletasks()  # Update UI

                    image_path = generate_image_from_prompt(prompt, img_api_key, save_path=image_directory)

                    # Now cut and resize the generated image to fit the background
                    self.status_var.set("Setting wallpaper...")
                    self.root.update_idletasks()  # Update UI

                    resized_image_path = cut_generated_image(image_path, image_directory)
                    set_wallpaper_windows(resized_image_path)

                    # Cleanup old images to free up space
                    cleanup_old_images(image_directory, image_pattern, max_images_to_keep)

                    self.status_var.set("Wallpaper updated. Waiting for next cycle...")
                else:
                    self.status_var.set("Failed to fetch weather data. Trying again in next cycle...")

                self.root.update_idletasks()  # Ensure UI updates are reflected
                time.sleep(update_frequency)  # Wait for the next update cycle
                
            except Exception as e:
                self.status_var.set(f"Error occurred: {str(e)}")
                break  # Exit the loop in case of error

            if self.update_stop.is_set():
                break  # Exit the loop if stop signal is received

        # Cleanup and reset after the loop is exited
        self.start_button["state"] = "normal"  # Re-enable the start button
        self.pause_button["state"] = "disabled"
        self.stop_button["state"] = "disabled"
        self.status_var.set("Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperApp(root)
    root.mainloop()