from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.database import Project, Conversation, Message, KnowledgeFile
from app.models.schemas import ProjectCreate
from typing import List, Optional
from datetime import datetime

class ConversationService:
    """对话管理服务"""
    
    @staticmethod
    async def create_project(db: AsyncSession, project_data: ProjectCreate) -> Project:
        """创建新项目"""
        project = Project(
            name=project_data.name,
            description=project_data.description
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project
    
    @staticmethod
    async def get_projects(db: AsyncSession) -> List[Project]:
        """获取所有项目"""
        result = await db.execute(select(Project).order_by(desc(Project.updated_at)))
        return result.scalars().all()
    
    @staticmethod
    async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
        """获取单个项目"""
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int) -> bool:
        """删除项目"""
        project = await db.get(Project, project_id)
        if project:
            await db.delete(project)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def create_conversation(db: AsyncSession, project_id: int, title: str) -> Conversation:
        """创建新对话"""
        conversation = Conversation(
            project_id=project_id,
            title=title
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation
    
    @staticmethod
    async def get_conversations(db: AsyncSession, project_id: int) -> List[Conversation]:
        """获取项目的所有对话"""
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(Conversation)
            .where(Conversation.project_id == project_id)
            .options(selectinload(Conversation.messages))
            .order_by(desc(Conversation.updated_at))
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_conversation(db: AsyncSession, conversation_id: int) -> Optional[Conversation]:
        """获取单个对话及其消息"""
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_message(db: AsyncSession,
                        conversation_id: int,
                        role: str,
                        content: str,
                        meta_info: Optional[dict] = None) -> Message:
        """添加消息到对话"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            meta_info=meta_info
        )
        
        db.add(message)
        
        # 更新对话的 updated_at
        conversation = await db.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(message)  # 🔑 关键：刷新对象以重新附加到会话
        
        return message
    
    @staticmethod
    async def get_conversation_history(db: AsyncSession, conversation_id: int) -> List[dict]:
        """获取对话历史（格式化为LLM输入）"""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    @staticmethod
    async def add_file(db: AsyncSession,
                      project_id: int,
                      filename: str,
                      filepath: str,
                      file_type: str,
                      semantic_tag: Optional[str] = None) -> KnowledgeFile:
        """添加文件到项目"""
        file = KnowledgeFile(
            project_id=project_id,
            filename=filename,
            filepath=filepath,
            file_type=file_type,
            semantic_tag=semantic_tag
        )
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file
    
    @staticmethod
    async def get_project_files(db: AsyncSession, project_id: int) -> List[KnowledgeFile]:
        """获取项目的所有文件"""
        result = await db.execute(
            select(KnowledgeFile)
            .where(KnowledgeFile.project_id == project_id)
            .order_by(desc(KnowledgeFile.created_at))
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_file(db: AsyncSession, file_id: int) -> Optional[KnowledgeFile]:
        """获取单个文件"""
        return await db.get(KnowledgeFile, file_id)
    
    @staticmethod
    async def update_file_vectorization(db: AsyncSession, file_id: int, chunk_count: int):
        """更新文件向量化状态"""
        file = await db.get(KnowledgeFile, file_id)
        if file:
            file.vectorized = 1
            file.chunk_count = chunk_count
            await db.commit()
