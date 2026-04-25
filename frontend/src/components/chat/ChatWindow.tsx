import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../../hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Bot, AlertCircle, Trash2, X, MessageCircle } from 'lucide-react';

interface ChatWindowProps {
  userId: number;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ userId }) => {
  const { messages, loading, error, sendMessage, clearHistory } = useChat(userId);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-blue-600 text-white rounded-full shadow-2xl hover:bg-blue-700 hover:scale-105 transition-all flex items-center justify-center z-50 group"
        title="Open Clinical AI Chat"
      >
        <MessageCircle size={32} className="group-hover:animate-pulse" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col h-[600px] w-full max-w-md bg-gray-50 rounded-2xl shadow-2xl border border-gray-200 overflow-hidden animate-in slide-in-from-bottom-5">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
            <Bot size={24} className="text-indigo-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-800">Clinical AI Assistant</h2>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <span className="text-xs text-gray-500">Always here to help 24/7</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button 
            onClick={clearHistory}
            className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
            title="Clear History"
          >
            <Trash2 size={18} />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
            title="Close Chat"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 p-3 flex items-center gap-2 border-b border-red-100 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-4 px-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-3xl">
              👋
            </div>
            <div>
              <h3 className="font-bold text-gray-800 text-lg">Welcome to MentalFlow AI</h3>
              <p className="text-gray-500 text-sm mt-1">Ask about mental health, log moods, get activity help, or just chat.</p>
            </div>
            <div className="bg-orange-50 border border-orange-200 text-orange-800 text-xs p-3 rounded-xl mt-4">
              <strong>⚠️ Crisis?</strong> Use 988 or Emergency Services.
            </div>
          </div>
        )}
        
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white z-10">
        <ChatInput onSend={sendMessage} isLoading={loading} />
      </div>
    </div>
  );
};

