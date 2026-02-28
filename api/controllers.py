import os
import uuid
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from PIL import Image as PILImage
import io
from service.text import GPTModel
from service.image import VisionModel
from service.voice import AWSVoiceService

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
VOICE_FOLDER = os.path.join('static', 'voice')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOICE_FOLDER, exist_ok=True)

# Session storage: {session_id: {"user_id": str, "text": [], "images": [], "voice": [], "location": dict}}
sessions = {}

class SessionManager:
    """Manages user sessions and associated data."""
    
    @staticmethod
    def create_session(user_id):
        """
        Creates a new session for a user.
        
        Args:
            user_id (str): The identifier for the user.
            
        Returns:
            str: The generated session ID.
        """
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "user_id": user_id,
            "text": [],
            "images": [],
            "voice": [],
            "location": None
        }
        return session_id

    @staticmethod
    def get_session(session_id):
        """
        Retrieves an existing session.
        
        Args:
            session_id (str): The ID of the session to retrieve.
            
        Returns:
            dict: The session data or None if not found.
        """
        return sessions.get(session_id)

    @staticmethod
    def delete_session(session_id):
        """
        Deletes a session and its data.
        
        Args:
            session_id (str): The ID of the session to delete.
        """
        sessions.pop(session_id, None)

# Service instance initialization
text_service = GPTModel()
image_service = VisionModel()
voice_service = AWSVoiceService()

@app.route('/session/start', methods=['POST'])
def start_session():
    """Starts a new user session."""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    session_id = SessionManager.create_session(user_id)
    return jsonify({"session_id": session_id, "status": "started"}), 201

@app.route('/session/text', methods=['POST'])
def post_text():
    """Adds a text message to the session context."""
    data = request.json
    session_id = data.get('session_id')
    text = data.get('text')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    session['text'].append(text)
    return jsonify({"status": "text added"}), 200

@app.route('/session/image', methods=['POST'])
def upload_image():
    """Uploads an image file and saves it to the local store."""
    session_id = request.form.get('session_id')
    image_file = request.files.get('image')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    if image_file:
        filename = f"{uuid.uuid4()}_{image_file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Use Pillow to resize
        img = PILImage.open(image_file)
        max_size = (800, 800)
        img.thumbnail(max_size)
        img.save(file_path, optimize=True, quality=85)
        
        image_url = f"http://localhost:5000/static/uploads/{filename}"
        
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            analysis = image_service.analyze_image(image_data)
        except Exception as e:
            analysis = f"Analysis failed: {str(e)}"
            
        image_info = {
            "url": image_url,
            "filename": filename,
            "analysis": analysis
        }
        session['images'].append(image_info)
        
        return jsonify({
            "status": "image uploaded",
            "image_url": image_url,
            "analysis": analysis
        }), 200
    
    return jsonify({"error": "No image provided"}), 400

@app.route('/session/voice', methods=['POST'])
def post_voice():
    """Uploads a voice recording, transcribes it, and saves the file."""
    session_id = request.form.get('session_id')
    voice_file = request.files.get('voice')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    if voice_file:
        # Save audio file
        filename = f"{uuid.uuid4()}_{voice_file.filename}"
        file_path = os.path.join(VOICE_FOLDER, filename)
        voice_file.save(file_path)
        
        voice_url = f"http://localhost:5000/static/voice/{filename}"
        
        # Transcribe
        try:
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            transcription = voice_service.transcribe(audio_data)
        except Exception as e:
            transcription = f"Transcription failed: {str(e)}"
            
        voice_info = {
            "url": voice_url,
            "filename": filename,
            "transcription": transcription
        }
        session['voice'].append(voice_info)
        
        return jsonify({
            "status": "voice uploaded",
            "voice_url": voice_url,
            "transcription": transcription
        }), 200
    
    return jsonify({"error": "No voice message provided"}), 400

@app.route('/session/location', methods=['POST'])
def post_location():
    """Updates the user location in the session context."""
    data = request.json
    session_id = data.get('session_id')
    lat = data.get('latitude')
    lon = data.get('longitude')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    session['location'] = {"lat": lat, "lon": lon}
    return jsonify({"status": "location updated"}), 200

@app.route('/session/end', methods=['POST'])
def end_session():
    """Ends the session and generates a summary based on aggregated context."""
    data = request.json
    session_id = data.get('session_id')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    context = {
        "user_id": session["user_id"],
        "location": session["location"],
        "inputs": {
            "text": session["text"],
            "images": session["images"],
            "voice_transcriptions": session["voice"]
        }
    }
    
    query = "Summarize the session and provide agricultural advice based on all inputs provided."
    response_text = text_service.generate_response(query, context)
    
    SessionManager.delete_session(session_id)
    
    return jsonify({
        "status": "completed",
        "response": response_text,
        "summary_context": context
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
