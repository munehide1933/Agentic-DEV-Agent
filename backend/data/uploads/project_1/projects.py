from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ProjectCreate, ProjectResponse, ConversationResponse, FileResponse
from app.models.database import get_db
from app.services.conversation_service import ConversationService
from app.services.rag_service import RAGService
from app.services.vector_service import VectorService
from typing import List
import os
import aiofiles

router = APIRouter(prefix="/api/projects", tags=["projects"])
rag_service = RAGService()
vector_service = VectorService()

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """创建新项目"""
    new_project = await ConversationService.create_project(db, project)
    return new_project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """获取所有项目"""
    projects = await ConversationService.get_projects(db)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """获取项目详情"""
    project = await ConversationService.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """删除项目"""
    # 删除向量数据
    await vector_service.delete_by_project(project_id)
    
    # 删除数据库记录
    success = await ConversationService.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(project_id: int, db: AsyncSession = Depends(get_db)):
    """获取项目的所有对话"""
    conversations = await ConversationService.get_conversations(db, project_id)
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """获取对话详情"""
    conversation = await ConversationService.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/{project_id}/upload-file")
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传文件到项目"""
    
    # 验证项目存在
    project = await ConversationService.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 保存文件
    upload_dir = f"./data/uploads/project_{project_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # 检测文件类型
    file_extension = os.path.splitext(file.filename)[1]
    file_type_map = {
        ".py": "code", ".js": "code", ".ts": "code", ".tsx": "code",
        ".java": "code", ".go": "code", ".cpp": "code", ".c": "code",
        ".md": "documentation", ".txt": "documentation",
        ".json": "config", ".yaml": "config", ".yml": "config",
        ".xml": "config", ".toml": "config"
    }
    file_type = file_type_map.get(file_extension, "other")
    
    # 读取文件内容用于分析
    content_str = content.decode('utf-8', errors='ignore')
    
    # 自动分析文件
    analysis = await rag_service.summarize_file(content_str, file.filename)
    
    # 保存文件记录
    db_file = await ConversationService.add_file(
        db,
        project_id=project_id,
        filename=file.filename,
        filepath=file_path,
        file_type=file_type,
        semantic_tag=analysis["semantic_tag"]
    )
    
    # 向量化文件内容
    vectorization_result = await rag_service.vectorize_file(
        file_id=db_file.id,
        project_id=project_id,
        filename=file.filename,
        content=content_str,
        file_type=file_type,
        semantic_tag=analysis["semantic_tag"]
    )
    
    # 更新向量化状态
    if vectorization_result["success"]:
        await ConversationService.update_file_vectorization(
            db,
            db_file.id,
            vectorization_result["chunks_count"]
        )
    
    return {
        "file_id": db_file.id,
        "filename": file.filename,
        "analysis": analysis,
        "vectorization": vectorization_result
    }


@router.get("/{project_id}/files", response_model=List[FileResponse])
async def list_files(project_id: int, db: AsyncSession = Depends(get_db)):
    """获取项目的所有文件"""
    files = await ConversationService.get_project_files(db, project_id)
    return files
