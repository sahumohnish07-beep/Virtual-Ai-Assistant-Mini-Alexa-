"""
Weather Skill for Mini-Alexa.

Retrieves real-time weather reports for specified or default cities using the
OpenWeatherMap REST API with metric unit formatting.
"""

import re
import requests
import config

def get_weather(command: str) -> str:
    """
    Extract a city name from the voice command and query the OpenWeatherMap API.

    Parameters:
        command (str): The spoken instruction (e.g. 'what is the weather in Pune').

    Returns:
        str: A natural spoken summary of the current temperature and conditions.
    """
    api_key = getattr(config, "WEATHER_API_KEY", "")
    default_city = getattr(config, "DEFAULT_CITY", "Pune")

    # Verify that the user has configured an actual API key
    if not api_key or api_key == "YOUR_WEATHER_API_KEY_HERE":
        return "Please configure your OpenWeatherMap API key in the .env file first."

    city = ""
    if command:
        # Match natural prepositional city patterns: 'weather in Pune', 'temperature for London'
        match = re.search(r"(?:weather|temperature|forecast)\s+(?:in|at|of|for)\s+([a-zA-Z\s]+)", command, re.IGNORECASE)
        if not match:
            match = re.search(r"(?:in|at|for|of)\s+([a-zA-Z\s]+)", command, re.IGNORECASE)

        if match:
            city = match.group(1).strip()
        else:
            # Clean common filler words when the format is 'Pune weather'
            cleaned = re.sub(
                r"\b(weather|temperature|forecast|what|is|the|how|like|today|please|tell|me)\b",
                "",
                command,
                flags=re.IGNORECASE,
            ).strip()
            if cleaned:
                city = cleaned

    # Fall back to default configured city if no specific location was extracted
    if not city:
        city = default_city

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code == 200:
            temp = round(data["main"]["temp"])
            description = data["weather"][0]["description"]
            city_name = data.get("name", city.title())
            return f"The weather in {city_name} is currently {description} with a temperature of {temp} degrees Celsius."
        elif response.status_code == 404:
            return f"Sorry, I couldn't find weather data for {city.title()}."
        elif response.status_code == 401:
            return "The OpenWeatherMap API key is invalid. Please check your .env file."
        else:
            return f"Unable to fetch weather: {data.get('message', 'Please try again later.')}"

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return "I could not connect to the weather service. Please check your internet connection."
    except Exception as err:
        return f"An error occurred while fetching the weather: {err}"
