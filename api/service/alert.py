from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from service.weather import WeatherAPI
from service.text import TextModel


class Alert:
    def __init__(self, user_id: str, alert_type: str, message: str, condition: str, timestamp: Optional[datetime] = None):
        self.user_id = user_id
        self.alert_type = alert_type
        self.message = message
        self.condition = condition
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "condition": self.condition,
            "timestamp": self.timestamp.isoformat()
        }


class AlertDatabase(ABC):
    @abstractmethod
    def save_alert(self, alert: Alert) -> bool:
        """
        Persist the alert to the database.
        """
        pass

    @abstractmethod
    def get_user_alerts(self, user_id: str) -> list[Alert]:
        """
        Retrieve all alerts for a specific user.
        """
        pass


class DynamoAlertDB(AlertDatabase):
    def save_alert(self, alert: Alert) -> bool:
        """
        Placeholder for AWS DynamoDB integration.
        """
        # TODO: Implement DynamoDB put_item logic
        print(f"[DynamoAlertDB] Saving alert for user {alert.user_id}: {alert.alert_type}")
        return True

    def get_user_alerts(self, user_id: str) -> list[Alert]:
        """
        Placeholder for AWS DynamoDB query logic.
        """
        # TODO: Implement DynamoDB query logic
        print(f"[DynamoAlertDB] Fetching alerts for user {user_id}")
        return []


class AlertService:
    def __init__(self, db: AlertDatabase, weather_api: WeatherAPI, text_model: TextModel):
        self.db = db
        self.weather_api = weather_api
        self.text_model = text_model

    def set_alert(self, user_id: str, alert_type: str, message: str, condition: str) -> bool:
        """
        Registers a new alert for a user and stores it in the database.
        """
        alert = Alert(user_id=user_id, alert_type=alert_type, message=message, condition=condition)
        return self.db.save_alert(alert)

    def generate_weather_alerts(self, users: List[dict]) -> List[dict]:
        """
        Generate weather alerts for multiple users based on their location and weather conditions.
        Uses LLM to analyze weather data and determine if conditions are abnormal.
        
        Args:
            users: List of user dictionaries with keys: user_id, latitude, longitude, crop_type, farming_method
            
        Returns:
            List of alert dictionaries with user_id, alert_type, message, condition
        """
        alerts = []
        
        for user in users:
            user_id = user.get('user_id')
            latitude = user.get('latitude')
            longitude = user.get('longitude')
            crop_type = user.get('crop_type', 'general crops')
            farming_method = user.get('farming_method', 'conventional')
            
            if not user_id or latitude is None or longitude is None:
                continue
            
            # Fetch weather data
            weather_data = self.weather_api.get_weather(latitude, longitude)
            
            if 'error' in weather_data:
                continue
            
            # Let LLM analyze weather and generate alert if needed
            alert_response = self._analyze_and_generate_alert(
                weather_data=weather_data,
                crop_type=crop_type,
                farming_method=farming_method
            )
            
            # Only create alert if LLM determined conditions are abnormal
            if alert_response and alert_response.get('should_alert'):
                alert_message = alert_response.get('message')
                condition = alert_response.get('condition')
                
                alert_data = {
                    "user_id": user_id,
                    "alert_type": "weather",
                    "message": alert_message,
                    "condition": condition
                }
                
                # Save to database
                self.set_alert(
                    user_id=user_id,
                    alert_type="weather",
                    message=alert_message,
                    condition=condition
                )
                
                alerts.append(alert_data)
        
        return alerts

    def _analyze_and_generate_alert(self, weather_data: dict, crop_type: str, farming_method: str) -> Optional[dict]:
        """
        Use LLM to analyze weather data and generate alert if conditions are abnormal.
        
        Args:
            weather_data: Weather information from API
            crop_type: Type of crop the farmer is growing
            farming_method: Organic or conventional farming
            
        Returns:
            Dictionary with keys: should_alert (bool), message (str), condition (str)
            Returns None if weather data is invalid
        """
        if 'main' not in weather_data or 'weather' not in weather_data:
            return None
        
        # Extract weather parameters
        temp = weather_data['main'].get('temp')
        humidity = weather_data['main'].get('humidity')
        pressure = weather_data['main'].get('pressure')
        wind_speed = weather_data.get('wind', {}).get('speed')
        weather_main = weather_data['weather'][0].get('main', '')
        weather_desc = weather_data['weather'][0].get('description', '')
        
        # Build context for LLM
        context = {
            "weather_data": weather_data,
            "crop_type": crop_type,
            "farming_method": farming_method
        }
        
        query = f"""Analyze the following weather conditions for a farmer growing {crop_type} using {farming_method} farming method:

Temperature: {temp}°C
Humidity: {humidity}%
Pressure: {pressure} hPa
Wind Speed: {wind_speed} m/s
Weather: {weather_main} - {weather_desc}

Task:
1. Determine if these weather conditions are ABNORMAL or pose a risk to the crops
2. If abnormal, provide:
   - A brief condition label (e.g., "extreme_heat", "heavy_rain", "high_humidity")
   - A short alert message (1 sentence)
   - One actionable suggestion to protect crops (1-2 sentences)
3. If conditions are NORMAL, respond with "NO_ALERT"

Format your response as:
CONDITION: [condition_label or NORMAL]
ALERT: [alert message or NO_ALERT]
SUGGESTION: [suggestion or NONE]

Keep language simple and practical for farmers."""
        
        # Get LLM response
        llm_response = self.text_model.generate_response(query, context)
        
        # Parse LLM response
        return self._parse_llm_alert_response(llm_response)
    
    def _parse_llm_alert_response(self, llm_response: str) -> Optional[dict]:
        """
        Parse the LLM response to extract alert information.
        
        Args:
            llm_response: Raw response from LLM
            
        Returns:
            Dictionary with should_alert, message, and condition
        """
        # Simple parsing logic - can be enhanced based on actual LLM output format
        lines = llm_response.strip().split('\n')
        
        condition = None
        alert = None
        suggestion = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('CONDITION:'):
                condition = line.replace('CONDITION:', '').strip()
            elif line.startswith('ALERT:'):
                alert = line.replace('ALERT:', '').strip()
            elif line.startswith('SUGGESTION:'):
                suggestion = line.replace('SUGGESTION:', '').strip()
        
        # Check if alert is needed
        if condition and condition.upper() != 'NORMAL' and alert and alert.upper() != 'NO_ALERT':
            message = alert
            if suggestion and suggestion.upper() != 'NONE':
                message += f" {suggestion}"
            
            return {
                "should_alert": True,
                "message": message,
                "condition": condition
            }
        
        return {
            "should_alert": False,
            "message": None,
            "condition": "normal"
        }
