import json
import re

import boto3


class BedrockModel:
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name="ap-south-1")
        self.model_id = "apac.amazon.nova-pro-v1:0"

    def _format_messages(self, history, user_input):
        messages = []

        for msg in history[-10:]:
            messages.append(
                {
                    "role": msg["role"],
                    "content": [{"text": msg["text"]}],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": [{"text": user_input}],
            }
        )

        return messages

    def _build_system_prompt(self, context):
        return f"""
            You are KisaanVaani — an AI farming advisor for rural India.

            User Profile:
            {context.get('user_profile')}

            Weather:
            {context.get('weather')}

            Respond ONLY in valid JSON format:

            {{
            "immediate_action": "",
            "what_to_avoid": "",
            "what_to_monitor": "",
            "risk_level": "Low/Medium/High"
            }}
        """

    def generate_response(self, user_input, context):
        history = context.get("history") or []
        messages = self._format_messages(history, user_input)

        response = self.client.converse(
            modelId=self.model_id,
            system=[{"text": self._build_system_prompt(context)}],
            messages=messages,
            inferenceConfig={"temperature": 0.3, "maxTokens": 800},
        )

        text_output = response["output"]["message"]["content"][0]["text"]

        match = re.search(r"\{.*\}", text_output, re.DOTALL)
        if match:
            return json.loads(match.group())

        return {"error": "Invalid JSON from model", "raw": text_output}


if __name__ == "__main__":
    model = BedrockModel()

    context = {
        "history": [],
        "user_profile": "Wheat farmer in Punjab, 5 acres, uses drip irrigation",
        "weather": "Sunny, 28°C, humidity 40%, no rain expected for 7 days",
    }

    user_input = "My wheat leaves are turning yellow, what should I do?"
    print(f"User: {user_input}\n")

    result = model.generate_response(user_input, context)
    print("Response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

