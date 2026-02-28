import { Send, Image as ImageIcon, MapPin, Mic, Square } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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
    /**
     * Handles keyboard shortcuts for the input field.
     * @param {Event} e - Keyboard event.
     */
    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            onSendText();
        }
    };

    return (
        <footer className="p-2 pb-4 px-4 flex items-center gap-3 bg-[#f0f2f5] z-10 shrink-0 border-t border-black/5">
            <div className="flex gap-1 shrink-0">
                <button
                    onClick={() => onUploadClick('image')}
                    className="text-wa-text-secondary p-2.5 hover:bg-white rounded-full transition-all"
                >
                    <ImageIcon size={22} />
                </button>
                <button
                    onClick={onLocation}
                    className="text-wa-text-secondary p-2.5 hover:bg-white rounded-full transition-all"
                >
                    <MapPin size={22} />
                </button>
            </div>

            <div className="grow relative flex items-center min-w-0">
                {isRecording ? (
                    <div className="bg-white w-full rounded-2xl py-2.5 px-4 flex items-center justify-between shadow-sm border border-black/5">
                        <div className="flex items-center gap-3 text-red-500">
                            <motion.div
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ repeat: Infinity, duration: 1 }}
                                className="w-2.5 h-2.5 bg-red-500 rounded-full"
                            />
                            <span className="text-sm font-medium animate-pulse">Recording...</span>
                        </div>
                        <span className="text-xs text-wa-text-secondary italic">Slide to cancel</span>
                    </div>
                ) : (
                    <input
                        type="text"
                        placeholder="Type a message"
                        className="bg-white border-none outline-none w-full text-[15px] py-2.5 px-5 rounded-2xl shadow-sm transition-all focus:ring-1 focus:ring-wa-teal/20"
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
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0, opacity: 0 }}
                            onClick={onSendText}
                            className="w-11 h-11 bg-wa-teal rounded-full flex items-center justify-center text-white shadow-md transform active:scale-90 transition-all"
                        >
                            <Send size={18} className="translate-x-0.5" />
                        </motion.button>
                    ) : (
                        <motion.button
                            key="voice"
                            initial={{ scale: 0.8 }}
                            animate={{ scale: 1 }}
                            onClick={isRecording ? onStopRecording : onStartRecording}
                            className={`w-11 h-11 rounded-full flex items-center justify-center shadow-md transform active:scale-90 transition-all ${isRecording ? 'bg-red-500 text-white' : 'bg-wa-teal text-white'
                                }`}
                        >
                            {isRecording ? <Square size={18} /> : <Mic size={18} />}
                        </motion.button>
                    )}
                </AnimatePresence>
            </div>
        </footer>
    );
};

export default ChatInput;
