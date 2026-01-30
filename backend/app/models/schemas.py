from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkflowPhase(str, Enum):
    REQUIREMENT = "requirement"
    ARCHITECTURE = "architecture"
    RAG_PLANNING = "rag_planning"
    IMPLEMENTATION = "implementation"
    SECURITY_REVIEW = "security_review"
    DELIVERY = "delivery"

class PersonaRole(str, Enum):
    ARCHITECT = "architect"
    BACKEND_LEAD = "backend_lead"
    FRONTEND_ENGINEER = "frontend_engineer"
    AI_RAG_ENGINEER = "ai_rag_engineer"
    SECURITY_REVIEWER = "security_reviewer"
    DOCUMENTATION_PM = "documentation_pm"

# Request Schemas
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    project_id: Optional[int] = None
    context_files: Optional[List[int]] = None

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class FileUpload(BaseModel):
    filename: str
    content: str
    file_type: str
    semantic_tag: Optional[str] = None

# Response Schemas
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    meta_info: Optional[Dict[str, Any]] = None  # 重命名为 meta_info
    created_at: datetime
    
    class Config:
        from_attributes = True
        # 允许字段别名（API 响应时仍显示为 metadata）
        populate_by_name = True

class ConversationResponse(BaseModel):
    id: int
    project_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FileResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    file_type: str
    semantic_tag: Optional[str] = None
    chunk_count: int
    vectorized: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowState(BaseModel):
    current_phase: WorkflowPhase
    active_personas: List[PersonaRole]
    phase_outputs: Dict[str, Any] = {}
    security_flags: List[str] = []

class ChatResponse(BaseModel):
    message_id: int
    content: str
    conversation_id: int
    workflow_state: Optional[WorkflowState] = None
    code_modifications: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
