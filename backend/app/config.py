from pydantic_settings import BaseSettings
from typing import List
import os
import json
from pathlib import Path

# 找到项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large"
    
    # Qdrant
    QDRANT_COLLECTION_NAME: str = "meta_agent_knowledge"
    QDRANT_PATH: str = "./data/qdrant"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/sqlite/meta_agent.db"
    
    # Security
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Application
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 解析 CORS_ORIGINS（如果是字符串）
        if isinstance(self.CORS_ORIGINS, str):
            try:
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except:
                self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

# 打印配置文件位置（用于调试）
print(f"📁 Looking for .env file at: {ENV_FILE}")
if not ENV_FILE.exists():
    print(f"⚠️  WARNING: .env file not found!")
    print(f"   Please create it by copying .env.example:")
    print(f"   copy {BASE_DIR}\\.env.example {ENV_FILE}")
else:
    print(f"✅ .env file found")

settings = Settings()

# 确保数据目录存在
data_dir = BASE_DIR / "data"
os.makedirs(data_dir / "qdrant", exist_ok=True)
os.makedirs(data_dir / "sqlite", exist_ok=True)
os.makedirs(data_dir / "uploads", exist_ok=True)