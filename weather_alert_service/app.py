import logging
import threading
import time
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from weather_api import OpenWeather
from alert_generator import AlertGenerator
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'weather-alert-service-secret-key'

socketio = SocketIO(app, cors_allowed_origins="*")

weather_service = OpenWeather()
alert_generator = AlertGenerator()

try:
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    users_tbl = dynamodb.Table("Users")
    DB_AVAILABLE = True
    logger.info("DynamoDB connected")
except Exception as e:
    logger.warning(f"DynamoDB not available: {e}")
    DB_AVAILABLE = False
    users_tbl = None

connected_users = {}


def get_all_users_with_location():
    if DB_AVAILABLE:
        try:
            response = users_tbl.scan(
                FilterExpression="attribute_exists(latitude) AND attribute_exists(longitude)"
            )
            users = response.get("Items", [])
            return [
                {
                    "user_id": user["user_id"],
                    "latitude": float(user.get("latitude", 0)),
                    "longitude": float(user.get("longitude", 0))
                }
                for user in users
                if user.get("latitude") and user.get("longitude")
            ]
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    else:
        logger.warning("DynamoDB not available, no users to process")
        return []


def check_and_send_alerts():
    while True:
        try:
            users = get_all_users_with_location()
            logger.info(f"Checking weather for {len(users)} users")
            
            for user in users:
                try:
                    user_id = user['user_id']
                    latitude = user['latitude']
                    longitude = user['longitude']
                    
                    weather_data = weather_service.get_weather(latitude, longitude)
                    
                    if "error" in weather_data:
                        logger.warning(f"Failed to fetch weather for {user_id}")
                        continue
                    
                    alert = alert_generator.generate_alert(
                        weather_data,
                        {"latitude": latitude, "longitude": longitude}
                    )
                    
                    alert["user_id"] = user_id
                    alert["latitude"] = latitude
                    alert["longitude"] = longitude
                    alert["timestamp"] = datetime.now().isoformat()
                    
                    socketio.emit('weather_alert', alert, room=user_id)
                    logger.info(f"Alert sent to {user_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing user {user.get('user_id')}: {e}")
            
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
        
        time.sleep(1800)


@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected")
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected")


@socketio.on('register')
def handle_register(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(user_id)
        connected_users[user_id] = True
        logger.info(f"User {user_id} registered and joined room")
        emit('registration_success', {'message': f'Registered as {user_id}'})
    else:
        emit('registration_error', {'message': 'Missing user_id'})


@app.route('/users', methods=['GET'])
def get_users():
    users = get_all_users_with_location()
    return jsonify({
        'total': len(users),
        'users': users
    })


if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=check_and_send_alerts, daemon=True)
    scheduler_thread.start()
    logger.info("Alert scheduler started (checking every 3 hours)")
    
    socketio.run(app, debug=True, port=5002, allow_unsafe_werkzeug=True)
