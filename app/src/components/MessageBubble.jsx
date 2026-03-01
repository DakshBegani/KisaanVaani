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
            transition={{ duration: 0.3, ease: "easeOut" }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-1`}
        >
            <div
                className={`max-w-[80%] p-2.5 px-3 rounded-lg relative message-shadow ${isUser
                    ? 'bg-wa-bubble-out rounded-tr-sm'
                    : 'bg-wa-bubble-in rounded-tl-sm'
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
                <p className="text-[14.5px] leading-relaxed text-[#111b21] break-words">
                    {msg.text}
                </p>
                <div className="flex items-center justify-end gap-1 mt-1">
                    <span className="text-[11px] text-wa-text-secondary select-none">
                        {msg.timestamp}
                    </span>
                    {isUser && (
                        <CheckCheck size={16} className="text-[#53bdeb] flex-shrink-0" />
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default MessageBubble;
