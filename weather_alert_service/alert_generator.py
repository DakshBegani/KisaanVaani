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
                    "alert_type": "warning",
                    "message": "Unable to fetch weather data. Please try again.",
                    "risk_level": "Medium",
                    "advice": "Check your internet connection and location settings.",
                }

            context = {
                "user_profile": "",
                "weather": json.dumps(weather_data, ensure_ascii=False),
                "history": []
            }

            user_input = f"""
            Based on the weather data provided, generate a simple weather alert for a farmer.
            
            Location: Latitude {location_context.get('latitude')}, Longitude {location_context.get('longitude')}
            
            If weather is abnormal or risky (high wind, extreme temp, heavy rain, frost), generate a warning.
            If weather is normal, generate an info message.
            
            Respond ONLY in JSON format:
            {{
                "alert_type": "warning|info",
                "message": "Brief alert (1-2 sentences)",
                "risk_level": "Low|Medium|High",
                "advice": "Specific farming advice"
            }}
            """

            result = self.model.generate_response(user_input, context)
            
            if isinstance(result, dict) and "error" not in result:
                return {
                    "alert_type": result.get("alert_type", "info"),
                    "message": result.get("message", "Weather data received."),
                    "risk_level": result.get("risk_level", "Low"),
                    "advice": result.get("advice", "Continue with regular farming activities.")
                }
            
            return {
                "alert_type": "info",
                "message": "Weather data received. Conditions appear normal.",
                "risk_level": "Low",
                "advice": "Continue with regular farming activities."
            }

        except Exception as e:
            return {
                "alert_type": "warning",
                "message": f"Error generating alert: {str(e)}",
                "risk_level": "Medium",
                "advice": "Please try again later."
            }
