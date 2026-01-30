from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.vector_service import VectorService
from app.services.rag_service import RAGService
from pydantic import BaseModel

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])
vector_service = VectorService()
rag_service = RAGService()


class SearchRequest(BaseModel):
    query: str
    project_id: int
    top_k: int = 5


@router.post("/search")
async def search_knowledge(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    """搜索知识库"""
    
    results = await rag_service.retrieve_context(
        query=request.query,
        project_id=request.project_id,
        top_k=request.top_k
    )
    
    return {
        "query": request.query,
        "results": results
    }


@router.get("/collection-info")
async def get_collection_info():
    """获取向量数据库信息"""
    
    info = vector_service.get_collection_info()
    return info
