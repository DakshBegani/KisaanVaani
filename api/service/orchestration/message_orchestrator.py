import json

from api.service import data
from api.service.llm import BedrockModel
from api.service.speech import AWSVoiceService


def handle_message(user_id, input_type, text=None, image_bytes=None, audio_bytes=None, media_uri=None):
    conv_id, user = data.get_or_create_conversation(user_id)
    history = data.fetch_recent_messages(conv_id, limit=20)

    if audio_bytes:
        voice_service = AWSVoiceService()
        text = voice_service.transcribe(audio_bytes)
        data.put_message(conv_id, user_id, "user", text, media_type="audio")
    else:
        data.put_message(conv_id, user_id, "user", text, media_type=input_type)

    weather = None
    if user and user.get("lat") and user.get("lon"):
        weather = {"summary": "..."}

    context = {
        "user_profile": user,
        "history": history,
        "weather": weather,
    }

    reply_json = BedrockModel().generate_response(text, context)
    reply_text = json.dumps(reply_json)

    data.put_message(
        conv_id,
        user_id,
        "user",
        text or "",
        media_type=input_type,
        media_uri=media_uri,
    )
    data.put_message(conv_id, user_id, "assistant", reply_text)

    tts_uri = AWSVoiceService().synthesize(reply_text)
    return conv_id, reply_text, tts_uri
