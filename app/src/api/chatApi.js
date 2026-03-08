/**
 * Utility for interacting with the KisaanVaani backend API.
 * In development the Vite proxy forwards /session/* to http://localhost:5001.
 */

const API_BASE = import.meta.env.VITE_API_BASE ?? '';

/**
 * Initiates a new user session.
 * @param {string} userId - Unique identifier for the user.
 * @returns {Promise<Object>} - The session initialization response.
 */
export const startSession = async (userId = 'farmer_123') => {
    const res = await fetch(`${API_BASE}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
    return res.json();
};

/**
 * Sends a text message to the current session.
 * @param {string} sessionId - The active session ID.
 * @param {string} text - Message content.
 * @returns {Promise<Object>} - Response with AI reply.
 */
export const sendText = async (sessionId, text) => {
    const res = await fetch(`${API_BASE}/session/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, text })
    });
    return res.json();
};

/**
 * Updates the user's location in the current session.
 * @param {string} sessionId - The active session ID.
 * @param {number} latitude - Latitude coordinate.
 * @param {number} longitude - Longitude coordinate.
 * @returns {Promise<Object>} - Response with weather summary.
 */
export const sendLocation = async (sessionId, latitude, longitude) => {
    const res = await fetch(`${API_BASE}/session/location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, latitude, longitude })
    });
    return res.json();
};

/**
 * Ends the current session and retrieves the final summary.
 * @param {string} sessionId - The active session ID.
 * @returns {Promise<Object>} - The summary and ending status.
 */
export const endSession = async (sessionId) => {
    const res = await fetch(`${API_BASE}/session/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    return res.json();
};

/**
 * Uploads a voice recorded blob to the session.
 * @param {string} sessionId - The active session ID.
 * @param {Blob} audioBlob - The recorded audio data.
 * @returns {Promise<Object>} - Transcription result.
 */
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

/**
 * Uploads an image file to the session.
 * @param {string} sessionId - The active session ID.
 * @param {File} imageFile - The selected image file.
 * @returns {Promise<Object>} - Upload status and image URL.
 */
export const uploadImage = async (sessionId, imageFile) => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('image', imageFile);

    const res = await fetch(`${API_BASE}/session/image`, {
        method: 'POST',
        body: formData
    });
    return res.json();
};
