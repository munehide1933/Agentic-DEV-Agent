import { create } from 'zustand';
import type { Project, Conversation, KnowledgeFile } from '@/types';
import { projectsApi } from '@/services/api';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  conversations: Conversation[];
  files: KnowledgeFile[];
  isLoading: boolean;
  error: string | null;

  loadProjects: () => Promise<void>;
  createProject: (name: string, description?: string) => Promise<Project | null>;
  setCurrentProject: (project: Project | null) => Promise<void>;
  deleteProject: (projectId: number) => Promise<void>;
  loadConversations: (projectId: number) => Promise<void>;
  loadFiles: (projectId: number) => Promise<void>;
  uploadFile: (projectId: number, file: File) => Promise<void>;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,
  conversations: [],
  files: [],
  isLoading: false,
  error: null,

  loadProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await projectsApi.list();
      set({ projects: response.data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load projects',
        isLoading: false,
      });
    }
  },

  createProject: async (name: string, description?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await projectsApi.create({ name, description });
      set((state) => ({
        projects: [response.data, ...state.projects],
        isLoading: false,
      }));
      return response.data;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create project',
        isLoading: false,
      });
      return null;
    }
  },

  setCurrentProject: async (project: Project | null) => {
    set({ currentProject: project });
    if (project) {
      await get().loadConversations(project.id);
      await get().loadFiles(project.id);
    }
  },

  deleteProject: async (projectId: number) => {
    set({ isLoading: true, error: null });
    try {
      await projectsApi.delete(projectId);
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== projectId),
        currentProject: state.currentProject?.id === projectId ? null : state.currentProject,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete project',
        isLoading: false,
      });
    }
  },

  loadConversations: async (projectId: number) => {
    try {
      const response = await projectsApi.listConversations(projectId);
      set({ conversations: response.data });
    } catch (error: any) {
      console.error('Failed to load conversations:', error);
    }
  },

  loadFiles: async (projectId: number) => {
    try {
      const response = await projectsApi.listFiles(projectId);
      set({ files: response.data });
    } catch (error: any) {
      console.error('Failed to load files:', error);
    }
  },

  uploadFile: async (projectId: number, file: File) => {
    set({ isLoading: true, error: null });
    try {
      await projectsApi.uploadFile(projectId, file);
      await get().loadFiles(projectId);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to upload file',
        isLoading: false,
      });
    }
  },
}));
