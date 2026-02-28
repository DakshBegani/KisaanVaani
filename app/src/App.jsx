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

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (sender, text) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'sent'
    }]);
  };

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

  const handleSendText = async () => {
    if (!inputText.trim()) return;

    const text = inputText;
    setInputText('');
    addMessage('user', text);

    try {
      const currentSessionId = await ensureSession();
      await chatApi.sendText(currentSessionId, text);
    } catch (err) {
      console.error('Failed to send text', err);
    }
  };

  const handleLocation = async () => {
    try {
      const coords = await getCurrentPosition();
      const { latitude, longitude } = coords;
      addMessage('user', `📍 My location: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);

      const currentSessionId = await ensureSession();
      await chatApi.sendLocation(currentSessionId, latitude, longitude);
    } catch (err) {
      console.error('Location error', err);
      addMessage('bot', err.message || 'Failed to get location.');
    }
  };

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
        addMessage('user', '🎤 Voice message sent');

        try {
          const currentSessionId = await ensureSession();
          setIsLoading(true);
          const data = await chatApi.uploadVoice(currentSessionId, audioBlob);
          addMessage('bot', `Transcribed: "${data.transcription}"`);
        } catch (err) {
          console.error('Voice upload failed', err);
          addMessage('bot', 'Failed to process voice message.');
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

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleEndSession = async () => {
    if (!sessionId) {
      addMessage('bot', 'No active session to summarize.');
      return;
    }
    setIsLoading(true);
    addMessage('user', '🛑 End session and summarize.');

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

  const handleUploadClick = (type) => {
    addMessage('bot', `Simulating ${type} upload... (Session will initiate if needed)`);
  };

  return (
    <div className="flex flex-col h-screen relative overflow-hidden bg-white chat-shadow">
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
