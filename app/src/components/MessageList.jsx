import { motion, AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';

const MessageList = ({ messages, isLoading, scrollRef }) => {
    return (
        <div
            ref={scrollRef}
            className="grow overflow-y-auto p-4 flex flex-col gap-3 relative bg-[#f0f2f5]"
            style={{
                backgroundImage: `url("https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png")`,
                backgroundSize: '400px',
                backgroundBlendMode: 'overlay',
                backgroundColor: '#e5e7eb'
            }}
        >
            <div className="flex flex-col gap-2 relative z-10">
                <AnimatePresence initial={false}>
                    {messages.map((msg) => (
                        <MessageBubble key={msg.id} msg={msg} />
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex justify-start"
                    >
                        <div className="bg-white p-2 px-4 rounded-lg rounded-tl-none shadow-sm border border-black/5">
                            <div className="flex gap-1">
                                <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }} className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                                <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                                <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default MessageList;
