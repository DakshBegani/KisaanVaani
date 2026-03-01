import { Send, Image as ImageIcon, MapPin, Mic, Square, Plus, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

/**
 * Component for message input, location sharing, and voice/image uploads.
 * 
 * @param {Object} props
 * @param {string} props.inputText - Current text in the input field.
 * @param {Function} props.setInputText - Setter for input text.
 * @param {Function} props.onSendText - Callback for sending text.
 * @param {Function} props.onLocation - Callback for sharing location.
 * @param {Function} props.onUploadClick - Callback for initiating file upload.
 * @param {boolean} props.isRecording - Whether audio recording is active.
 * @param {Function} props.onStartRecording - Callback to start recording.
 * @param {Function} props.onStopRecording - Callback to stop recording.
 */
const ChatInput = ({
    inputText,
    setInputText,
    onSendText,
    onLocation,
    onUploadClick,
    isRecording,
    onStartRecording,
    onStopRecording
}) => {
    const [showAttachMenu, setShowAttachMenu] = useState(false);
    const [recordingDuration, setRecordingDuration] = useState(0);

    useEffect(() => {
        let interval;
        if (isRecording) {
            setRecordingDuration(0);
            interval = setInterval(() => {
                setRecordingDuration(prev => prev + 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isRecording]);

    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    /**
     * Handles keyboard shortcuts for the input field.
     * @param {Event} e - Keyboard event.
     */
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onSendText();
        }
    };

    return (
        <footer className="p-3 px-3 flex items-end gap-2 bg-[#f0f2f5] z-10 shrink-0 safe-area-bottom">
            {/* Attachment Menu */}
            <div className="relative">
                <motion.button
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowAttachMenu(!showAttachMenu)}
                    className={`text-wa-text-secondary p-3 active:bg-white rounded-full transition-all ${showAttachMenu ? 'bg-white rotate-45' : ''}`}
                >
                    {showAttachMenu ? <X size={24} /> : <Plus size={24} />}
                </motion.button>

                <AnimatePresence>
                    {showAttachMenu && (
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.9 }}
                            className="absolute bottom-14 left-0 bg-white rounded-xl shadow-2xl p-3 flex flex-col gap-2 min-w-[160px] border border-black/5"
                        >
                            <button
                                onClick={() => {
                                    onUploadClick('image');
                                    setShowAttachMenu(false);
                                }}
                                className="flex items-center gap-3 p-2.5 hover:bg-gray-50 rounded-lg transition-all text-left"
                            >
                                <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                                    <ImageIcon size={18} className="text-white" />
                                </div>
                                <span className="text-sm font-medium text-gray-700">Photos</span>
                            </button>
                            <button
                                onClick={() => {
                                    onLocation();
                                    setShowAttachMenu(false);
                                }}
                                className="flex items-center gap-3 p-2.5 hover:bg-gray-50 rounded-lg transition-all text-left"
                            >
                                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                                    <MapPin size={18} className="text-white" />
                                </div>
                                <span className="text-sm font-medium text-gray-700">Location</span>
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <div className="grow relative flex items-center min-w-0">
                {isRecording ? (
                    <motion.div
                        initial={{ scale: 0.95 }}
                        animate={{ scale: 1 }}
                        className="bg-white w-full rounded-3xl py-3.5 px-4 flex items-center justify-between shadow-sm"
                    >
                        <div className="flex items-center gap-3 text-red-500">
                            <motion.div
                                animate={{ scale: [1, 1.3, 1] }}
                                transition={{ repeat: Infinity, duration: 1.5 }}
                                className="w-3 h-3 bg-red-500 rounded-full"
                            />
                            <span className="text-sm font-semibold">{formatDuration(recordingDuration)}</span>
                        </div>
                        <span className="text-xs text-wa-text-secondary">Slide to cancel</span>
                    </motion.div>
                ) : (
                    <input
                        type="text"
                        placeholder="Message"
                        className="bg-white border-none outline-none w-full text-[15px] py-3.5 px-4 rounded-3xl shadow-sm transition-all focus:shadow-md placeholder:text-gray-400"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />
                )}
            </div>

            <div className="flex shrink-0">
                <AnimatePresence mode="wait">
                    {inputText.trim() ? (
                        <motion.button
                            key="send"
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            exit={{ scale: 0, rotate: 180 }}
                            transition={{ type: "spring", stiffness: 200, damping: 15 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={onSendText}
                            className="w-12 h-12 bg-wa-teal rounded-full flex items-center justify-center text-white shadow-md hover:bg-green-600 transition-colors"
                        >
                            <Send size={18} className="translate-x-0.5" />
                        </motion.button>
                    ) : (
                        <motion.button
                            key="voice"
                            initial={{ scale: 0.8 }}
                            animate={{ scale: 1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={isRecording ? onStopRecording : onStartRecording}
                            className={`w-12 h-12 rounded-full flex items-center justify-center shadow-md transition-all ${isRecording ? 'bg-red-500 text-white' : 'bg-wa-teal text-white hover:bg-green-600'
                                }`}
                        >
                            {isRecording ? <Square size={18} fill="currentColor" /> : <Mic size={20} />}
                        </motion.button>
                    )}
                </AnimatePresence>
            </div>
        </footer>
    );
};

export default ChatInput;
