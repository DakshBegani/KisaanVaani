const API_BASE = 'http://localhost:5000';

export const startSession = async (userId = 'farmer_123') => {
    const res = await fetch(`${API_BASE}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
    return res.json();
};

export const sendText = async (sessionId, text) => {
    await fetch(`${API_BASE}/session/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, text })
    });
};

export const sendLocation = async (sessionId, latitude, longitude) => {
    await fetch(`${API_BASE}/session/location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, latitude, longitude })
    });
};

export const endSession = async (sessionId) => {
    const res = await fetch(`${API_BASE}/session/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    return res.json();
};

export const uploadVoice = async (sessionId, audioBlob) => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('voice', audioBlob, 'voice.webm');

    const res = await fetch(`${API_BASE}/session/voice`, {
        method: 'POST',
        body: formData
    });
    return res.json();
};
