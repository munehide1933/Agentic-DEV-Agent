from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "meta_agent_knowledge"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/sqlite/meta_agent.db"
    
    # Security
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # Application
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# 确保数据目录存在
os.makedirs("./data/qdrant", exist_ok=True)
os.makedirs("./data/sqlite", exist_ok=True)
os.makedirs("./data/uploads", exist_ok=True)