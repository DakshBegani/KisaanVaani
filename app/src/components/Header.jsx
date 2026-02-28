import { Bot, Power, MoreVertical } from 'lucide-react';

const Header = ({ onEndSession }) => {
    return (
        <header className="glass p-4 flex items-center justify-between z-10 shrink-0">
            <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-full bg-wa-teal flex items-center justify-center">
                    <Bot size={24} className="text-white" />
                </div>
                <div>
                    <h1 className="text-sm font-medium">KisaanVaani Advisor</h1>
                    <p className="text-xs text-wa-teal">Online</p>
                </div>
            </div>
            <div className="flex items-center gap-4">
                <button
                    onClick={onEndSession}
                    className="p-2 transition-all hover:bg-wa-input-bg rounded-full text-wa-teal"
                    title="End Session"
                >
                    <Power size={20} />
                </button>
                <MoreVertical size={20} className="text-wa-text-secondary" />
            </div>
        </header>
    );
};

export default Header;
