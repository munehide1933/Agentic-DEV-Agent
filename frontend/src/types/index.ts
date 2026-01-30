export interface Project {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: number;
  project_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  meta_info?: {  // 重命名为 meta_info
    workflow_phase?: string;
    code_modifications?: CodeModification[];
    security_warnings?: string[];
    usage?: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  };
  created_at: string;
}

export interface CodeModification {
  file_path: string;
  modification_type: 'ADD' | 'MODIFY' | 'DELETE';
  content: string;
}

export interface KnowledgeFile {
  id: number;
  project_id: number;
  filename: string;
  file_type: string;
  semantic_tag?: string;
  chunk_count: number;
  vectorized: number;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
  project_id?: number;
  context_files?: number[];
}

export interface ChatResponse {
  message_id: number;
  content: string;
  conversation_id: number;
  workflow_state?: {
    current_phase: string;
    active_personas: string[];
    phase_outputs?: Record<string, any>;
    security_flags?: string[];
  };
  code_modifications?: CodeModification[];
  suggestions?: string[];
}

export interface ProjectCreate {
  name: string;
  description?: string;
}
