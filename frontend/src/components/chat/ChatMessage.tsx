import React from 'react';
import { ChatMessage as ChatMessageType } from '../../hooks/useChat';
import { IntentBadge } from './IntentBadge';
import { User, Bot } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-2`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-blue-600' : 'bg-indigo-600'}`}>
          {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
        </div>
        
        {/* Message Bubble */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          {!isUser && message.intent && <IntentBadge intent={message.intent} />}
          
          <div className={`px-4 py-3 rounded-2xl ${
            isUser 
              ? 'bg-blue-600 text-white rounded-br-none' 
              : message.intent === 'CRISIS'
                ? 'bg-red-50 text-red-900 border border-red-200 rounded-bl-none'
                : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-bl-none'
          }`}>
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
          
          <span className="text-[10px] text-gray-400 mt-1">
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        
      </div>
    </div>
  );
};
