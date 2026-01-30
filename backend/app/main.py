from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.models.database import init_db
from app.api import chat, projects, knowledge
from app.utils.startup_check import check_environment
import logging
import sys

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动前检查
    logger.info("Running startup checks...")
    if not check_environment():
        logger.error("Startup checks failed. Please fix the errors above.")
        sys.exit(1)
    
    # 启动时
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # 关闭时
    logger.info("Application shutdown")


app = FastAPI(
    title="Meta-Agent Development System",
    description="AI-powered multi-persona development assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(projects.router)
app.include_router(knowledge.router)


@app.get("/")
async def root():
    return {
        "message": "Meta-Agent Development System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
