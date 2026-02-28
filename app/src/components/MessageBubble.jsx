import { motion } from 'framer-motion';
import { CheckCheck } from 'lucide-react';

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

                {/* Tail integration (pseudo-visual) */}
                <div className={`absolute top-0 w-2 h-2 ${isUser
                        ? 'right-[-8px] border-l-[8px] border-l-wa-bubble-out border-b-[8px] border-b-transparent'
                        : 'left-[-8px] border-r-[8px] border-r-wa-bubble-in border-b-[8px] border-b-transparent'
                    }`} />
            </div>
        </motion.div>
    );
};

export default MessageBubble;
