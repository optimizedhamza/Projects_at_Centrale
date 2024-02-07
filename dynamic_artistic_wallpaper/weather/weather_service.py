import requests
from datetime import datetime

def fetch_weather(base_url, api_key, city_name):
    """Fetches current weather data for the specified city"""
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name

    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        weather_data = response.json()

        # Check if the city is found
        if weather_data["cod"] != "404":
            print("City Found\n")
            main_data = weather_data["main"]
            weather_description = weather_data["weather"][0]["description"]

            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            current_temperature = main_data["temp"]

            return city_name, time_now, current_temperature, weather_description
        else:
            print("City Not Found\n")
            return None
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def kelvin_to_celsius(kelvin_temp):
    """Converts temperature from Kelvin to Celsius."""
    return kelvin_temp - 273.15

def get_time_of_day_description(hour):
    """Returns a descriptive narrative based on the hour of the day, changing every 4 hours."""
    if hour < 4:
        return "in the deep silence of late night, where stars peek through the dark canvas of the sky"
    elif hour < 8:
        return "in the quiet of early morning, as the first rays of sun gently brighten the horizon"
    elif hour < 12:
        return "in the freshness of the morning, where the world awakens to the promise of a new day"
    elif hour < 16:
        return "under the high sun of midday, casting short shadows and highlighting the vibrancy of life"
    elif hour < 20:
        return "in the soft glow of the afternoon, as the day slowly transitions, casting long shadows and a golden hue"
    else:
        return "under the cloak of evening, where the sky dims into twilight, welcoming the mystery of the night"

def get_weather_narrative(weather_description):
    """Generates a narrative based on the general weather condition."""
    if "thunderstorm" in weather_description:
        if "light" in weather_description or "drizzle" in weather_description:
            return "as a light thunderstorm rumbles in the distance, bringing with it a gentle, refreshing drizzle"
        elif "heavy" in weather_description:
            return "under the fury of a heavy thunderstorm, where the sky roars and lightning carves bright paths through the clouds"
        else:
            return "as the thunderstorm unfolds, its energy electrifying the air, and lightning illuminates the scene in dramatic flashes"

    elif "drizzle" in weather_description or "rain" in weather_description:
        if "light" in weather_description:
            return "under a gentle rain that caresses the landscape, adding a layer of tranquility and refreshment"
        elif "heavy" in weather_description or "extreme" in weather_description:
            return "under the onslaught of heavy rain, transforming the environment into a dramatic and compelling scene"
        else:
            return "during a steady rain that nourishes the earth, invigorating the colors of nature"

    elif "snow" in weather_description or "sleet" in weather_description:
        if "light" in weather_description:
            return "in a light snowfall, where the world becomes a quiet, enchanting wonderland"
        elif "heavy" in weather_description:
            return "under a heavy snowfall, the landscape transforms into a serene, white blanket, muffling sounds and softening shapes"
        else:
            return "as snowflakes gently fall, covering the world in a pristine layer of snow, bringing peace and quiet"

    elif "mist" in weather_description or "fog" in weather_description:
        return "enveloped in a mystical fog, the world around becomes a canvas for the imagination, blurring lines and softening the landscape"

    elif "clouds" in weather_description:
        if "few" in weather_description:
            return "beneath a sky playfully dotted with a few clouds, casting gentle shadows and adding depth to the landscape"
        elif "scattered" in weather_description or "broken" in weather_description:
            return "under a sky of scattered clouds, creating a dynamic and ever-changing tapestry of light and shadow"
        else:
            return "under a blanket of clouds, where the light diffuses softly, casting a gentle glow over everything"

    elif "clear" in weather_description:
        return "under a vast, clear sky that stretches infinitely, offering a sense of openness and clarity"

    else:  # For other conditions like smoke, haze, dust, etc.
        return "in a unique atmosphere, where the specific elements of the weather add a distinct character to the scene, painting a story unique to this moment"