from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from typing import List, Dict, Optional, Any
import re
from langchain_qdrant import QdrantVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class RAGService:
    """RAG 检索增强生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.vector_service = VectorService()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """智能文本分块"""
        
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # 如果单个段落超过chunk_size，强制分割
            if len(para) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # 按句子分割长段落
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence
            else:
                if len(current_chunk) + len(para) > chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    current_chunk += "\n\n" + para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 添加重叠
        if overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    prev_overlap = chunks[i-1][-overlap:]
                    chunk = prev_overlap + " " + chunk
                overlapped_chunks.append(chunk)
            return overlapped_chunks
        
        return chunks
    
    async def vectorize_file(self,
                            file_id: int,
                            project_id: int,
                            filename: str,
                            content: str,
                            file_type: str,
                            semantic_tag: Optional[str] = None) -> Dict[str, Any]:
        """使用LangChain向量化文件内容"""
        
        try:
            # 使用LangChain的文本分割器
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # 创建文档
            doc = Document(
                page_content=content,
                metadata={
                    "file_id": file_id,
                    "project_id": project_id,
                    "filename": filename,
                    "file_type": file_type,
                    "semantic_tag": semantic_tag or "general",
                }
            )
            
            # 分割文档
            chunks = text_splitter.split_documents([doc])
            
            # 为每个chunk添加索引
            for idx, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = idx
            
            # 批量生成嵌入（使用LangChain）
            texts = [chunk.page_content for chunk in chunks]
            embeddings = await self.llm_service.generate_embeddings_batch(texts)
            
            # 存储到向量数据库
            stored_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                if embedding:
                    point_id = await self.vector_service.add_document(
                        text=chunk.page_content,
                        embedding=embedding,
                        metadata=chunk.metadata
                    )
                    stored_chunks.append(point_id)
            
            return {
                "success": True,
                "chunks_count": len(chunks),
                "stored_count": len(stored_chunks)
            }
        except Exception as e:
            print(f"Vectorization error: {e}")
            return {
                "success": False,
                "chunks_count": 0,
                "stored_count": 0,
                "error": str(e)
            }
    
    async def retrieve_context(self,
                              query: str,
                              project_id: int,
                              top_k: int = 5,
                              file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """检索相关上下文"""
        
        # 生成查询嵌入
        query_embedding = await self.llm_service.generate_embedding(query)
        
        if not query_embedding:
            return []
        
        # 构建过滤条件
        filters = {"project_id": project_id}
        
        # 检索
        results = await self.vector_service.search(
            query_embedding=query_embedding,
            limit=top_k,
            filters=filters
        )
        
        return results
    
    async def summarize_file(self, content: str, filename: str) -> Dict[str, Any]:
        """自动总结文件内容并确定语义标签"""
        
        prompt = f"""Analyze this file and provide:
1. A brief summary (2-3 sentences)
2. The file's purpose
3. A semantic tag (choose from: model, config, service, utils, router, schema, documentation, test, other)

Filename: {filename}

Content preview:
{content[:2000]}

Respond in this format:
Summary: [your summary]
Purpose: [file purpose]
Tag: [semantic tag]
"""
        
        response = await self.llm_service.generate_response(
            system_prompt="You are a code analyzer. Be concise and accurate.",
            user_message=prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        if response["success"]:
            content = response["content"]
            
            # 解析响应
            summary_match = re.search(r'Summary:\s*(.+)', content)
            purpose_match = re.search(r'Purpose:\s*(.+)', content)
            tag_match = re.search(r'Tag:\s*(\w+)', content)
            
            return {
                "summary": summary_match.group(1).strip() if summary_match else "",
                "purpose": purpose_match.group(1).strip() if purpose_match else "",
                "semantic_tag": tag_match.group(1).strip() if tag_match else "other"
            }
        
        return {
            "summary": "Analysis failed",
            "purpose": "Unknown",
            "semantic_tag": "other"
        }
