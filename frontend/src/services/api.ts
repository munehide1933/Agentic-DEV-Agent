import axios from 'axios';
import type {
  Project,
  ProjectCreate,
  Conversation,
  Message,
  ChatRequest,
  ChatResponse,
  KnowledgeFile,
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const projectsApi = {
  list: () => api.get<Project[]>('/projects/'),
  create: (data: ProjectCreate) => api.post<Project>('/projects/', data),
  get: (id: number) => api.get<Project>(`/projects/${id}`),
  delete: (id: number) => api.delete(`/projects/${id}`),
  listConversations: (projectId: number) =>
    api.get<Conversation[]>(`/projects/${projectId}/conversations`),
  listFiles: (projectId: number) =>
    api.get<KnowledgeFile[]>(`/projects/${projectId}/files`),
  uploadFile: (projectId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/projects/${projectId}/upload-file`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Conversations API
export const conversationsApi = {
  get: (conversationId: number) =>
    api.get<Conversation>(`/projects/conversations/${conversationId}`),
};

// Chat API
export const chatApi = {
  sendMessage: (data: ChatRequest) =>
    api.post<ChatResponse>('/chat/message', data),
  applyModifications: (modifications: any[]) =>
    api.post('/chat/apply-modifications', modifications),
};

// Knowledge API
export const knowledgeApi = {
  search: (query: string, projectId: number, topK: number = 5) =>
    api.post('/knowledge/search', { query, project_id: projectId, top_k: topK }),
  getCollectionInfo: () => api.get('/knowledge/collection-info'),
};

export default api;
