from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import settings
from typing import List, Dict, Optional, Any
import uuid
import os

# 全局单例
_qdrant_client = None

def get_qdrant_client():
    """获取Qdrant客户端单例"""
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_path = settings.QDRANT_PATH
        os.makedirs(qdrant_path, exist_ok=True)
        _qdrant_client = QdrantClient(path=qdrant_path)
    return _qdrant_client

class VectorService:
    """Qdrant 向量数据库服务"""
    
    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()
    
    def _ensure_collection(self):
        """确保集合存在"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=3072,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"⚠️  Qdrant collection check error: {e}")
    
    async def add_document(self,
                          text: str,
                          embedding: List[float],
                          metadata: Dict[str, Any]) -> str:
        """添加文档到向量数据库"""
        
        point_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": text,
                **metadata
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return point_id
    
    async def search(self,
                    query_embedding: List[float],
                    limit: int = 5,
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        
        search_params = {
            "collection_name": self.collection_name,
            "query_vector": query_embedding,
            "limit": limit
        }
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                filter_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            if filter_conditions:
                search_params["query_filter"] = Filter(must=filter_conditions)
        
        try:
            results = self.client.search(**search_params)
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                }
                for result in results
            ]
        except Exception as e:
            print(f"⚠️  Search error: {e}")
            return []
    
    async def delete_by_project(self, project_id: int):
        """删除项目相关的所有向量"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[FieldCondition(key="project_id", match=MatchValue(value=project_id))]
                )
            )
        except Exception as e:
            print(f"⚠️  Delete error: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            collection = self.client.get_collection(self.collection_name)
            return {
                "name": collection.name,
                "vectors_count": collection.vectors_count,
                "points_count": collection.points_count,
                "status": collection.status
            }
        except Exception as e:
            return {"error": str(e)}