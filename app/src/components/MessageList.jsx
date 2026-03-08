import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import MessageBubble from './MessageBubble';

const MessageList = ({ messages, isLoading, scrollRef }) => {
    const [showScrollButton, setShowScrollButton] = useState(false);

    // Check if user has scrolled up
    useEffect(() => {
        const scrollElement = scrollRef.current;
        if (!scrollElement) return;

        const handleScroll = () => {
            const { scrollTop, scrollHeight, clientHeight } = scrollElement;
            const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
            setShowScrollButton(!isNearBottom);
        };

        scrollElement.addEventListener('scroll', handleScroll);
        return () => scrollElement.removeEventListener('scroll', handleScroll);
    }, [scrollRef]);

    const scrollToBottom = () => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({
                top: scrollRef.current.scrollHeight,
                behavior: 'smooth'
            });
        }
    };

    return (
        <div
            ref={scrollRef}
            className="grow overflow-y-auto p-3 pb-2 flex flex-col gap-1 relative bg-[#efeae2]"
            style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d9d9d9' fill-opacity='0.15'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }}
        >
            <div className="flex flex-col gap-1.5 relative z-10">
                <AnimatePresence initial={false}>
                    {messages.map((msg) => (
                        <MessageBubble key={msg.id} msg={msg} />
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex justify-start mb-1"
                    >
                        <div className="bg-white p-3 px-4 rounded-lg rounded-tl-sm message-shadow">
                            <div className="flex gap-1">
                                <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0 }} className="w-2 h-2 bg-gray-400 rounded-full" />
                                <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.2 }} className="w-2 h-2 bg-gray-400 rounded-full" />
                                <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.4 }} className="w-2 h-2 bg-gray-400 rounded-full" />
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Scroll to bottom button */}
            <AnimatePresence>
                {showScrollButton && (
                    <motion.button
                        initial={{ opacity: 0, scale: 0.8, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 20 }}
                        onClick={scrollToBottom}
                        className="fixed bottom-20 right-4 w-11 h-11 bg-white rounded-full shadow-lg flex items-center justify-center text-wa-text-secondary active:bg-gray-50 transition-all z-20 border border-black/5"
                    >
                        <ChevronDown size={22} />
                    </motion.button>
                )}
            </AnimatePresence>
        </div>
    );
};

export default MessageList;
