import { create } from 'zustand';
import type { Message, ChatRequest, Conversation } from '@/types';
import { chatApi, conversationsApi } from '@/services/api';

interface ChatState {
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  
  setCurrentConversation: (conversation: Conversation | null) => void;
  loadConversation: (conversationId: number) => Promise<void>;
  sendMessage: (request: ChatRequest) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentConversation: null,
  messages: [],
  isLoading: false,
  error: null,

  setCurrentConversation: (conversation) => {
    set({ 
      currentConversation: conversation,
      messages: conversation?.messages || []
    });
  },

  loadConversation: async (conversationId: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await conversationsApi.get(conversationId);
      set({
        currentConversation: response.data,
        messages: response.data.messages || [],
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load conversation',
        isLoading: false,
      });
    }
  },

  sendMessage: async (request: ChatRequest) => {
    set({ isLoading: true, error: null });
    
    // 添加用户消息到UI
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: request.message,
      created_at: new Date().toISOString(),
    };
    
    set((state) => ({
      messages: [...state.messages, userMessage],
    }));

    try {
      const response = await chatApi.sendMessage(request);
      
      // 添加助手消息
      const assistantMessage: Message = {
        id: response.data.message_id,
        role: 'assistant',
        content: response.data.content,
        metadata: {
          workflow_phase: response.data.workflow_state?.current_phase,
          code_modifications: response.data.code_modifications,
          security_warnings: response.data.suggestions,
        },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        currentConversation: state.currentConversation
          ? {
              ...state.currentConversation,
              id: response.data.conversation_id,
            }
          : null,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to send message',
        isLoading: false,
      });
    }
  },

  clearMessages: () => {
    set({ messages: [], currentConversation: null });
  },
}));
