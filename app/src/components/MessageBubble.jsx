import { motion } from 'framer-motion';
import { CheckCheck } from 'lucide-react';

/**
 * Component for rendering individual chat messages.
 * Supports text, images, and status indicators.
 * 
 * @param {Object} props
 * @param {Object} props.msg - Message data object.
 */
const MessageBubble = ({ msg }) => {
    const isUser = msg.sender === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            <div
                className={`max-w-[85%] p-2 px-3 rounded-lg relative shadow-sm border border-black/5 ${isUser
                    ? 'bg-wa-bubble-out rounded-tr-none'
                    : 'bg-wa-bubble-in rounded-tl-none'
                    }`}
            >
                {msg.imageUrl && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="mb-2 rounded-md overflow-hidden bg-gray-100 max-w-[300px] max-h-[400px] flex items-center justify-center"
                    >
                        <img
                            src={msg.imageUrl}
                            alt="Uploaded content"
                            className="max-w-full max-h-full object-contain"
                            onLoad={() => {
                                if (window.scrollToBottom) window.scrollToBottom();
                            }}
                        />
                    </motion.div>
                )}

                {msg.voiceUrl && (
                    <div className="mb-2 w-full max-w-[240px]">
                        <audio
                            controls
                            className="w-full h-8 scale-90 origin-left"
                            src={msg.voiceUrl}
                        >
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                )}
                <p className="text-[14.5px] leading-relaxed text-[#111b21]">
                    {msg.text}
                </p>
                <div className="flex items-center justify-end gap-1 mt-1">
                    <span className="text-[10px] text-wa-text-secondary uppercase select-none">
                        {msg.timestamp}
                    </span>
                    {isUser && (
                        <CheckCheck size={14} className="text-wa-teal" />
                    )}
                </div>

                <div className={`absolute top-0 w-2 h-2 ${isUser
                    ? 'right-[-8px] border-l-[8px] border-l-wa-bubble-out border-b-[8px] border-b-transparent'
                    : 'left-[-8px] border-r-[8px] border-r-wa-bubble-in border-b-[8px] border-b-transparent'
                    }`} />
            </div>
        </motion.div>
    );
};

export default MessageBubble;
