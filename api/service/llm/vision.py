import json
import re

import boto3


class VisionModel:
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name="ap-south-1")
        self.model_id = "apac.amazon.nova-pro-v1:0"

    def analyze_image(self, image_bytes: bytes, context: dict = None) -> dict:
        """
        Analyses a crop/farm image using Bedrock Vision and returns structured
        agricultural advice in the standard JSON format.

        Args:
            image_bytes: Raw bytes of the image (JPEG/PNG).
            context: Optional session context (weather, user_profile, etc.).

        Returns:
            dict with keys: immediate_action, what_to_avoid, what_to_monitor, risk_level
        """
        context = context or {}

        weather_info = ""
        weather = context.get("weather")
        if weather and "error" not in weather:
            temp = weather.get("main", {}).get("temp", "N/A")
            humidity = weather.get("main", {}).get("humidity", "N/A")
            desc = weather.get("weather", [{}])[0].get("description", "N/A")
            weather_info = f"Current weather: {temp}°C, {desc}, humidity {humidity}%."

        system_prompt = (
            "You are KisaanVaani — an expert AI farming advisor for rural India.\n"
            + (f"Weather context: {weather_info}\n" if weather_info else "")
            + "Analyse the crop or farm image provided and respond ONLY in valid JSON:\n"
            '{"immediate_action": "", "what_to_avoid": "", "what_to_monitor": "", "risk_level": "Low/Medium/High"}'
        )

        try:
            response = self.client.converse(
                modelId=self.model_id,
                system=[{"text": system_prompt}],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": "jpeg",
                                    "source": {"bytes": image_bytes},
                                }
                            },
                            {
                                "text": (
                                    "Analyse this farm or crop image. "
                                    "Identify any diseases, pests, nutrient deficiencies, "
                                    "or environmental stress. Provide specific, actionable advice."
                                )
                            },
                        ],
                    }
                ],
                inferenceConfig={"temperature": 0.3, "maxTokens": 600},
            )

            text_output = response["output"]["message"]["content"][0]["text"]
            match = re.search(r"\{.*\}", text_output, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"error": "Invalid JSON from model", "raw": text_output}

        except Exception as e:
            return {"error": str(e), "raw": "Image analysis failed."}
