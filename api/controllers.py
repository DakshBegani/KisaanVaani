import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from api.service.text import GPTModel
from api.service.image import VisionModel
from api.service.voice import AWSVoiceService

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# In-memory storage for simplicity, as requested for a "thin backend"
# Format: {session_id: {"text": [], "images": [], "voice": [], "location": None}}
sessions = {}

class SessionManager:
    @staticmethod
    def create_session(user_id):
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
        return sessions.get(session_id)

    @staticmethod
    def delete_session(session_id):
        sessions.pop(session_id, None)

# Initialize Services
text_service = GPTModel()
image_service = VisionModel()
voice_service = AWSVoiceService()

@app.route('/session/start', methods=['POST'])
def start_session():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    session_id = SessionManager.create_session(user_id)
    return jsonify({"session_id": session_id, "status": "started"}), 201

@app.route('/session/text', methods=['POST'])
def post_text():
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
    # Assuming base64 or bytes for simplicity in this thin backend
    session_id = request.form.get('session_id')
    image_file = request.files.get('image')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    if image_file:
        image_data = image_file.read()
        analysis = image_service.analyze_image(image_data)
        session['images'].append(analysis)
        return jsonify({"status": "image processed", "analysis": analysis}), 200
    
    return jsonify({"error": "No image provided"}), 400

@app.route('/session/voice', methods=['POST'])
def post_voice():
    session_id = request.form.get('session_id')
    voice_file = request.files.get('voice')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    if voice_file:
        audio_data = voice_file.read()
        transcription = voice_service.transcribe(audio_data)
        session['voice'].append(transcription)
        return jsonify({"status": "voice transcribed", "transcription": transcription}), 200
    
    return jsonify({"error": "No voice message provided"}), 400

@app.route('/session/location', methods=['POST'])
def post_location():
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
    data = request.json
    session_id = data.get('session_id')
    
    session = SessionManager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 404
    
    # Aggregate context for LLM
    context = {
        "user_id": session["user_id"],
        "location": session["location"],
        "inputs": {
            "text": session["text"],
            "image_analyses": session["images"],
            "voice_transcriptions": session["voice"]
        }
    }
    
    # Generate final response
    query = "Summarize the session and provide agricultural advice based on all inputs provided."
    response_text = text_service.generate_response(query, context)
    
    # Cleanup session
    SessionManager.delete_session(session_id)
    
    return jsonify({
        "status": "completed",
        "response": response_text,
        "summary_context": context
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
