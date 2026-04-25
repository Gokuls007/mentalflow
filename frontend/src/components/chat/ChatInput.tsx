import React, { useState, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4 rounded-b-xl">
      <div className="relative flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={isLoading}
          className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="absolute right-2 p-2 rounded-full text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
        >
          {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </div>
      <p className="text-center text-[10px] text-gray-400 mt-2">
        Clinical AI can make mistakes. In a crisis, please call 988.
      </p>
    </div>
  );
};
