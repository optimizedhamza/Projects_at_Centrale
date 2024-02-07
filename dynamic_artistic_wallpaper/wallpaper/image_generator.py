from datetime import datetime
import requests
import json
import os
from weather.weather_service import kelvin_to_celsius, get_time_of_day_description, get_weather_narrative

def generate_prompt(city_name, timestamp, temperature_k, weather_description):
    """Generates a creative and detailed prompt for image generation based on weather data."""
    
    temperature_c = kelvin_to_celsius(temperature_k)
    temperature_formatted = f"{temperature_c:.2f}°C"
    hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
    time_of_day_description = get_time_of_day_description(hour)
    weather_narrative = get_weather_narrative(weather_description)
    
    prompt = (f"Create an artistic, numbers-and-writings-free image suitable for a PC wallpaper, with specific dimensions of 1024x1024 pixels, that captures {city_name} {weather_narrative}. "
              f"The scene unfolds {time_of_day_description}, enhancing the city's unique charm. "
              f"The temperature is a comfortable {temperature_formatted}, suggesting a gentle breeze that adds life to the scene. "
              f"Elements reflecting the city's culture and the natural beauty of its surroundings are subtly integrated, "
              f"enhancing the sense of place. The mood is one of reflection and beauty, capturing the essence of the moment. "
              f"The artistic style is rich and evocative, blending realism with imaginative touches to highlight the magical interplay between the landscape and the weather. "
              f"Please ensure the image is devoid of any textual elements, focusing solely on the visual storytelling.")
    
    return prompt

def generate_image_from_prompt(prompt, api_img_key, save_path="generated.png"):
    """Generates an image based on the given prompt using the Eden AI API"""

    url = "https://api.edenai.run/v2/image/generation"

    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_original_response": False,
        "settings": "{\"openai\":\"dall-e-3\",\"amazon\":\"titan-image-generator-v1_premium\"}",
        "resolution": "1024x1024",
        "num_images": 1,
        "providers": "openai",
        "text": prompt,
        "fallback_providers": "amazon"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": api_img_key
    }

    response = requests.post(url, json=payload, headers=headers)

    # Parse the JSON response
    response_data = json.loads(response.text)

    # Extract the image_resource_url
    image_url = response_data["openai"]["items"][0]["image_resource_url"]

    # Download and save the image
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Image successfully downloaded to {save_path}")
    else:
        print("Failed to download the image.")
    return os.path.abspath(save_path)