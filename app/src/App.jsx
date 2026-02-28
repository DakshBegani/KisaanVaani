import { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';
import * as chatApi from './api/chatApi';
import { getCurrentPosition } from './utils/geoUtils';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);
  const warningTimerRef = useRef(null);
  const autoSubmitTimerRef = useRef(null);

  /**
   * Automatically scroll the chat to the bottom when new messages arrive.
   */
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  /**
   * Manages inactivity timers for auto-submission.
   */
  const resetInactivityTimer = () => {
    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
    if (autoSubmitTimerRef.current) clearTimeout(autoSubmitTimerRef.current);

    if (!sessionId) return;

    // 30s Warning
    warningTimerRef.current = setTimeout(() => {
      addMessage('bot', '⚠️ Information will be submitted in 30 seconds for processing unless more information is sent.');
    }, 30000);

    // 60s Auto-End
    autoSubmitTimerRef.current = setTimeout(() => {
      handleEndSession(true); // pass true to indicate it was automatic
    }, 60000);
  };

  /**
   * Reset timer whenever session ID changes (session start).
   */
  useEffect(() => {
    if (sessionId) {
      resetInactivityTimer();
    }
    return () => {
      if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
      if (autoSubmitTimerRef.current) clearTimeout(autoSubmitTimerRef.current);
    };
  }, [sessionId]);

  /**
   * Appends a new message to the chat state.
   * @param {string} sender - 'user' or 'bot'.
   * @param {string} text - Message content.
   */
  const addMessage = (sender, text) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'sent'
    }]);
  };

  /**
   * Ensures a valid session exists, creating one if necessary.
   * @returns {Promise<string>} - The active session ID.
   */
  const ensureSession = async () => {
    if (sessionId) return sessionId;
    try {
      const data = await chatApi.startSession();
      setSessionId(data.session_id);
      return data.session_id;
    } catch (err) {
      console.error('Failed to start session implicitly', err);
      addMessage('bot', 'Connection error: Could not initialize session.');
      throw err;
    }
  };

  /**
   * Handles sending a text message from the input field.
   */
  const handleSendText = async () => {
    if (!inputText.trim()) return;

    const text = inputText;
    setInputText('');
    addMessage('user', text);

    try {
      const currentSessionId = await ensureSession();
      resetInactivityTimer();
      await chatApi.sendText(currentSessionId, text);
    } catch (err) {
      console.error('Failed to send text', err);
    }
  };

  /**
   * Handles capturing and sending the current geolocation.
   */
  const handleLocation = async () => {
    try {
      const coords = await getCurrentPosition();
      const { latitude, longitude } = coords;
      addMessage('user', `📍 My location: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);

      const currentSessionId = await ensureSession();
      resetInactivityTimer();
      await chatApi.sendLocation(currentSessionId, latitude, longitude);
    } catch (err) {
      console.error('Location error', err);
      addMessage('bot', err.message || 'Failed to get location.');
    }
  };

  /**
   * Starts audio recording using the MediaRecorder API.
   */
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Temporary placeholder message
        const tempId = Date.now();
        setMessages(prev => [...prev, {
          id: tempId,
          sender: 'user',
          text: '🎤 Sending voice message...',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          status: 'sending'
        }]);

        try {
          const currentSessionId = await ensureSession();
          resetInactivityTimer();
          setIsLoading(true);
          const data = await chatApi.uploadVoice(currentSessionId, audioBlob);

          // Update with transcribed text AND audio URL
          setMessages(prev => prev.map(m =>
            m.id === tempId
              ? {
                ...m,
                text: data.transcription,
                voiceUrl: data.voice_url,
                status: 'sent'
              }
              : m
          ));
        } catch (err) {
          console.error('Voice upload failed', err);
          setMessages(prev => prev.map(m =>
            m.id === tempId
              ? { ...m, text: 'Failed to process voice message.', status: 'error' }
              : m
          ));
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Recording start fail', err);
      addMessage('bot', 'Microphone access denied.');
    }
  };

  /**
   * Stops the active audio recording.
   */
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  /**
   * Ends the current session and displays the summary.
   * @param {boolean} isAuto - Whether the session end was triggered automatically.
   */
  const handleEndSession = async (isAuto = false) => {
    if (!sessionId) {
      if (!isAuto) addMessage('bot', 'No active session to summarize.');
      return;
    }
    setIsLoading(true);
    if (!isAuto) {
      addMessage('user', '🛑 End session and summarize.');
    } else {
      addMessage('bot', '🕒 Inactivity detected. Automatically processing your information...');
    }

    try {
      const data = await chatApi.endSession(sessionId);
      addMessage('bot', data.response);
      setSessionId(null);
    } catch (err) {
      console.error('Failed to end session', err);
      addMessage('bot', 'Failed to generate session summary.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Triggers the hidden file input for image selection.
   */
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  /**
   * Handles single or multiple image uploads.
   * @param {Event} event - File input change event.
   */
  const handleImageUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    for (const file of files) {
      const tempId = Date.now() + Math.random();
      setMessages(prev => [...prev, {
        id: tempId,
        sender: 'user',
        text: `Uploading ${file.name}...`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        status: 'sending'
      }]);

      try {
        const currentSessionId = await ensureSession();
        resetInactivityTimer();
        setIsLoading(true);
        const data = await chatApi.uploadImage(currentSessionId, file);

        setMessages(prev => prev.map(m =>
          m.id === tempId
            ? { ...m, text: '', imageUrl: data.image_url, status: 'sent' }
            : m
        ));
      } catch (err) {
        console.error('Image upload failed', err);
        setMessages(prev => prev.map(m =>
          m.id === tempId
            ? { ...m, text: `Failed to upload ${file.name}`, status: 'error' }
            : m
        ));
      } finally {
        setIsLoading(false);
      }
    }
    event.target.value = '';
  };

  return (
    <div className="flex flex-col h-screen relative overflow-hidden bg-white chat-shadow">
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept="image/*"
        multiple
        onChange={handleImageUpload}
      />
      <Header onEndSession={handleEndSession} />

      <MessageList
        messages={messages}
        isLoading={isLoading}
        scrollRef={scrollRef}
      />

      <ChatInput
        inputText={inputText}
        setInputText={setInputText}
        onSendText={handleSendText}
        onLocation={handleLocation}
        onUploadClick={handleUploadClick}
        isRecording={isRecording}
        onStartRecording={startRecording}
        onStopRecording={stopRecording}
      />
    </div>
  );
}

export default App;
