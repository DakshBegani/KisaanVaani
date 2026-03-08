import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv


class WeatherAPI(ABC):
    @abstractmethod
    def get_weather(self, latitude: float, longitude: float) -> dict:
        raise NotImplementedError


class OpenWeather(WeatherAPI):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPEN_WEATHER_API_KEY")
        self.url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, latitude: float, longitude: float) -> dict:
        if not self.api_key:
            raise ValueError(
                "OpenWeather API key not found. Please set OPEN_WEATHER_API_KEY in your .env file."
            )

        try:
            response = requests.get(
                self.url,
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            status_code = getattr(getattr(http_err, "response", None), "status_code", None)
            return {"error": f"HTTP error occurred: {http_err}", "status_code": status_code}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error occurred. Please check your internet connection."}
        except requests.exceptions.Timeout:
            return {"error": "The request timed out."}
        except requests.exceptions.RequestException as err:
            return {"error": f"An error occurred: {err}"}
        except Exception as err:
            return {"error": f"Unexpected error: {err}"}
