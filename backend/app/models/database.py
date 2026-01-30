from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime
from app.config import settings

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="project", cascade="all, delete-orphan")
    files = relationship("KnowledgeFile", back_populates="project", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(50))
    content = Column(Text)
    meta_info = Column(JSON, nullable=True)  # 使用 meta_info 代替 metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeFile(Base):
    __tablename__ = "knowledge_files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String(255))
    filepath = Column(String(512))
    file_type = Column(String(50))
    semantic_tag = Column(String(100), nullable=True)
    chunk_count = Column(Integer, default=0)
    vectorized = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="files")

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖注入
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 初始化数据库
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)