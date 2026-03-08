import { Bot } from 'lucide-react';
import { motion } from 'framer-motion';

const Header = ({ isTyping }) => {
    return (
        <header className="bg-wa-teal p-4 flex items-center gap-3 z-10 shrink-0">
            <div className="w-11 h-11 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
                <Bot size={24} className="text-white" />
            </div>
            <div className="min-w-0 flex-1">
                <h1 className="text-base font-semibold text-white truncate">KisaanVaani Advisor</h1>
                {isTyping ? (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-1 text-xs text-white/90"
                    >
                        <span>typing</span>
                        <motion.span
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ repeat: Infinity, duration: 1.5 }}
                        >
                            ...
                        </motion.span>
                    </motion.div>
                ) : (
                    <p className="text-xs text-white/80">Online</p>
                )}
            </div>
        </header>
    );
};

export default Header;
