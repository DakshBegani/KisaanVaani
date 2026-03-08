import os
import sys
import traceback
import uuid

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image as PILImage

# Load .env before any AWS clients are initialised
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.service.llm.text import GPTModel
from api.service.llm.vision import VisionModel
from api.service.speech.aws_voice import AWSVoiceService
from api.service.weather.openweather import OpenWeather

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
VOICE_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'voice')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOICE_FOLDER, exist_ok=True)

# In-memory session store
sessions = {}


class SessionManager:
    """Manages user sessions and associated data."""

    @staticmethod
    def create_session(user_id):
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "user_id": user_id,
            "history": [],       # LLM conversation turns [{role, text}]
            "messages": [],      # Raw message log
            "location": None,
            "weather": None,
            "user_profile": f"Farmer (ID: {user_id})",
        }
        return session_id

    @staticmethod
    def get_session(session_id):
        return sessions.get(session_id)

    @staticmethod
    def delete_session(session_id):
        sessions.pop(session_id, None)


# --- Service singletons ---
text_service = GPTModel()
image_service = VisionModel()
voice_service = AWSVoiceService()
weather_service = OpenWeather()


def build_context(session):
    """Build the context dict expected by LLM services."""
    return {
        "history": session.get("history", []),
        "weather": session.get("weather"),
        "user_profile": session.get("user_profile"),
        "location": session.get("location"),
    }


def friendly_error(exc: Exception) -> str:
    """Map common AWS/network exceptions to plain user-facing messages."""
    msg = str(exc)
    if "AccessDeniedException" in msg or "INVALID_PAYMENT_INSTRUMENT" in msg:
        return (
            "⚠️ AI advisory is temporarily unavailable — the AWS account needs a "
            "valid payment method. Please add one at console.aws.amazon.com/billing "
            "and try again in a few minutes."
        )
    if "Unable to locate credentials" in msg or "NoCredentialProviders" in msg:
        return (
            "⚠️ AWS credentials are not configured. "
            "Please check your .env file and restart the server."
        )
    if "ResourceNotFoundException" in msg or "model" in msg.lower():
        return (
            "⚠️ The AI model is not available in this AWS region. "
            "Please enable Claude Sonnet in Bedrock Model Access (ap-south-1)."
        )
    if "ThrottlingException" in msg or "TooManyRequests" in msg:
        return "⚠️ Too many requests — please wait a moment and try again."
    if "Connection" in msg or "Timeout" in msg:
        return "⚠️ Could not reach the AI service. Please check your internet connection."
    return "⚠️ Something went wrong on our end. Please try again shortly."


def format_response(data):
    """Convert structured Bedrock JSON into readable chat text."""
    if not isinstance(data, dict):
        return str(data)

    if "error" in data and "raw" in data:
        return data.get("raw", "Unable to generate a response.")

    parts = []
    if data.get("immediate_action"):
        parts.append(f"✅ Immediate Action:\n{data['immediate_action']}")
    if data.get("what_to_avoid"):
        parts.append(f"⚠️ What to Avoid:\n{data['what_to_avoid']}")
    if data.get("what_to_monitor"):
        parts.append(f"👁️ What to Monitor:\n{data['what_to_monitor']}")
    if data.get("risk_level"):
        level = data["risk_level"]
        emoji = "🟢" if level == "Low" else "🟡" if level == "Medium" else "🔴"
        parts.append(f"{emoji} Risk Level: {level}")

    return "\n\n".join(parts) if parts else str(data)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/session/start', methods=['POST'])
def start_session():
    """Starts a new user session."""
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    session_id = SessionManager.create_session(user_id)
    return jsonify({"session_id": session_id, "status": "started"}), 201


@app.route('/session/text', methods=['POST'])
def post_text():
    """Receives text, stores it, and returns an immediate AI response."""
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    text = data.get('text', '').strip()

    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404

    session['messages'].append({"type": "text", "content": text})
    session['history'].append({"role": "user", "text": text})

    context = build_context(session)
    try:
        raw = text_service.generate_response(text, context)
        response_text = format_response(raw)
    except Exception as e:
        traceback.print_exc()
        response_text = friendly_error(e)

    session['history'].append({"role": "assistant", "text": response_text})

    return jsonify({"status": "text added", "response": response_text}), 200


@app.route('/session/image', methods=['POST'])
def upload_image():
    """Uploads an image, analyses it with Bedrock Vision, and returns the result."""
    session_id = request.form.get('session_id')
    image_file = request.files.get('image')

    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    if not image_file:
        return jsonify({"error": "No image provided"}), 400

    filename = f"{uuid.uuid4()}_{image_file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    img = PILImage.open(image_file.stream)
    img.thumbnail((800, 800))
    img.save(file_path, optimize=True, quality=85)

    base_url = request.host_url.rstrip('/')
    image_url = f"{base_url}/static/uploads/{filename}"

    context = build_context(session)
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        raw = image_service.analyze_image(image_data, context)
        analysis = format_response(raw)
    except Exception as e:
        analysis = f"📷 Image saved. {friendly_error(e)}"

    session['messages'].append({"type": "image", "url": image_url, "filename": filename})
    session['history'].append({"role": "user", "text": f"[Uploaded crop image: {filename}]"})
    session['history'].append({"role": "assistant", "text": analysis})

    return jsonify({"status": "image uploaded", "image_url": image_url, "analysis": analysis}), 200


@app.route('/session/voice', methods=['POST'])
def post_voice():
    """Transcribes a voice recording and returns transcription + AI response."""
    session_id = request.form.get('session_id')
    voice_file = request.files.get('voice')

    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    if not voice_file:
        return jsonify({"error": "No voice message provided"}), 400

    filename = f"{uuid.uuid4()}_{voice_file.filename}"
    file_path = os.path.join(VOICE_FOLDER, filename)
    voice_file.save(file_path)

    base_url = request.host_url.rstrip('/')
    voice_url = f"{base_url}/static/voice/{filename}"

    try:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        transcription = voice_service.transcribe(audio_data)
    except Exception as e:
        transcription = f"🎤 Voice message received (transcription unavailable)"

    session['messages'].append({"type": "voice", "url": voice_url, "transcription": transcription})
    session['history'].append({"role": "user", "text": transcription})

    context = build_context(session)
    try:
        raw = text_service.generate_response(transcription, context)
        response_text = format_response(raw)
    except Exception as e:
        response_text = friendly_error(e)

    session['history'].append({"role": "assistant", "text": response_text})

    return jsonify({
        "status": "voice uploaded",
        "voice_url": voice_url,
        "transcription": transcription,
        "response": response_text,
    }), 200


@app.route('/session/location', methods=['POST'])
def post_location():
    """Stores location and returns a formatted weather summary."""
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    lat = data.get('latitude')
    lon = data.get('longitude')

    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404

    session['location'] = {"lat": lat, "lon": lon}

    try:
        weather_data = weather_service.get_weather(lat, lon)
        session['weather'] = weather_data
    except Exception as e:
        weather_data = {"error": str(e)}
        session['weather'] = weather_data

    if 'error' not in weather_data:
        city = weather_data.get('name', 'your area')
        temp = weather_data.get('main', {}).get('temp', 'N/A')
        humidity = weather_data.get('main', {}).get('humidity', 'N/A')
        desc = weather_data.get('weather', [{}])[0].get('description', 'N/A').capitalize()
        wind = weather_data.get('wind', {}).get('speed', 'N/A')
        weather_summary = (
            f"📍 Location received! Current weather for {city}:\n\n"
            f"🌡️ Temperature: {temp}°C\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌤️ Conditions: {desc}\n"
            f"💨 Wind Speed: {wind} m/s\n\n"
            "Your location has been saved — I'll factor local conditions into all advice."
        )
    else:
        weather_summary = (
            "📍 Location received! "
            f"(Weather data temporarily unavailable: {weather_data.get('error')})"
        )

    return jsonify({
        "status": "location updated",
        "weather": weather_data,
        "weather_summary": weather_summary,
    }), 200


@app.route('/session/end', methods=['POST'])
def end_session():
    """Ends the session and generates a comprehensive agricultural advisory."""
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')

    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404

    context = build_context(session)
    query = (
        "Generate a comprehensive agricultural advisory report for this farmer "
        "based on everything shared in this session — including their location, "
        "weather conditions, crop images, and all messages. Be specific and actionable."
    )

    try:
        raw = text_service.generate_response(query, context)
        response_text = format_response(raw)
    except Exception as e:
        response_text = friendly_error(e)

    SessionManager.delete_session(session_id)

    return jsonify({"status": "completed", "response": response_text}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
