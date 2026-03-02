import logging
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from weather_api import OpenWeather
from alert_generator import AlertGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'weather-alert-service-secret-key'

socketio = SocketIO(app, cors_allowed_origins="*")

weather_service = OpenWeather()
alert_generator = AlertGenerator()


@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('get_alert')
def handle_get_alert(data):
    try:
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        user_id = data.get('user_id', 'anonymous')
        
        if latitude is None or longitude is None:
            emit('alert_error', {'message': 'Missing latitude or longitude'})
            return

        logger.info(f"Fetching weather for location: {latitude}, {longitude}")
        weather_data = weather_service.get_weather(latitude, longitude)
        
        logger.info(f"Generating alert for user: {user_id}")
        alert = alert_generator.generate_alert(
            weather_data,
            {"latitude": latitude, "longitude": longitude}
        )

        alert["user_id"] = user_id
        alert["latitude"] = latitude
        alert["longitude"] = longitude
        
        logger.info(f"Alert generated for user {user_id}")
        emit('weather_alert', alert)

    except Exception as e:
        logger.error(f"Error: {e}")
        emit('alert_error', {'message': str(e)})


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5002, allow_unsafe_werkzeug=True)
