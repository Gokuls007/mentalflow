import { useState, useEffect, useRef } from 'react';
import { apiClient as api } from '../services/api';

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  created_at: string;
}

export function useChat(userId: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load history on mount
  useEffect(() => {
    if (!userId) return;
    
    const loadHistory = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/chat/history/${userId}`);
        setMessages(response.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load chat history');
      } finally {
        setLoading(false);
      }
    };
    
    loadHistory();
  }, [userId]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || !userId) return;
    
    // Add user message optimistically
    const tempId = Date.now();
    const newUserMsg: ChatMessage = {
      id: tempId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, newUserMsg]);
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/chat/message', { message: content });
      
      const newAssistantMsg: ChatMessage = {
        id: tempId + 1, // temporary ID until next refresh
        role: 'assistant',
        content: response.data.response,
        intent: response.data.intent,
        created_at: new Date().toISOString(),
      };
      
      setMessages(prev => {
        // Update user message with intent if possible, then add assistant message
        const updated = [...prev];
        const userMsgIndex = updated.findIndex(m => m.id === tempId);
        if (userMsgIndex !== -1) {
          updated[userMsgIndex].intent = response.data.intent;
        }
        return [...updated, newAssistantMsg];
      });
      
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      // Optionally remove optimistic message on failure
      setMessages(prev => prev.filter(m => m.id !== tempId));
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!userId) return;
    try {
      await api.delete(`/chat/history/${userId}`);
      setMessages([]);
    } catch (err: any) {
      setError(err.message || 'Failed to clear history');
    }
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory
  };
}
