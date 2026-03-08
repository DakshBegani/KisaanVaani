import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.service.llm.bedrock import BedrockModel


class AlertGenerator:
    def __init__(self):
        self.model = BedrockModel()

    def generate_alert(self, weather_data, location_context):
        try:
            if "error" in weather_data:
                return {
                    "alert": "Unable to fetch weather data. Please try again.",
                    "advice": "Check your internet connection and location settings."
                }

            context = {
                "user_profile": "",
                "weather": json.dumps(weather_data, ensure_ascii=False),
                "history": []
            }

            user_input = f"""
            Based on the weather data provided, generate a weather alert for a farmer.
            
            Location: Latitude {location_context.get('latitude')}, Longitude {location_context.get('longitude')}
            
            Format the response EXACTLY like this (no field labels, just the content):
            
            ⚠️ ALERT!
            [Write 1-2 sentences about the weather condition]
            
            [Write specific farming advice on what to do]
            
            Respond ONLY in JSON format:
            {{
                "alert": "Weather condition message (1-2 sentences)",
                "advice": "Specific farming advice"
            }}
            
            Example:
            {{
                "alert": "Heavy rainfall expected in your area today. Wind speed reaching 45 km/h.",
                "advice": "Postpone spraying pesticides until tomorrow. Cover harvested crops. Ensure proper drainage in fields."
            }}
            """

            result = self.model.generate_response(user_input, context)
            
            if isinstance(result, dict) and "error" not in result:
                return {
                    "alert": result.get("alert", "Weather data received."),
                    "advice": result.get("advice", "Continue with regular farming activities.")
                }
            
            return {
                "alert": "Weather data received. Conditions appear normal.",
                "advice": "Continue with regular farming activities."
            }

        except Exception as e:
            return {
                "alert": f"Error generating alert: {str(e)}",
                "advice": "Please try again later."
            }
