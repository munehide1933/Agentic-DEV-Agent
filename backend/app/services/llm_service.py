from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.config import settings
from typing import List, Dict, Optional
import tiktoken

class LLMService:
    """LangChain集成的Azure OpenAI服务"""
    
    def __init__(self):
        # 初始化聊天模型
        self.chat_model = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0.7,
            max_tokens=4000,
        )
        
        # 初始化嵌入模型
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )
        
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def generate_response(self,
                               system_prompt: str,
                               user_message: str,
                               conversation_history: Optional[List[Dict[str, str]]] = None,
                               #temperature: float = 0.7,
                               max_tokens: int = 4000) -> Dict[str, any]:
        """使用LangChain生成响应"""
        
        try:
            # 构建消息列表
            messages = [SystemMessage(content=system_prompt)]
            
            # 添加历史消息（控制token数量）
            if conversation_history:
                total_tokens = self.count_tokens(system_prompt)
                for msg in reversed(conversation_history):
                    msg_tokens = self.count_tokens(msg["content"])
                    if total_tokens + msg_tokens > 16000:
                        break
                    
                    if msg["role"] == "user":
                        messages.insert(1, HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.insert(1, AIMessage(content=msg["content"]))
                    
                    total_tokens += msg_tokens
            
            # 添加当前用户消息
            messages.append(HumanMessage(content=user_message))
            
            # 调用模型
            response = await self.chat_model.ainvoke(
                messages,
                config={"max_tokens": max_tokens, "temperature": temperature}
            )
            
            # 计算token使用（LangChain可能不直接提供，需要手动计算）
            prompt_tokens = sum(self.count_tokens(msg.content) for msg in messages)
            completion_tokens = self.count_tokens(response.content)
            
            return {
                "success": True,
                "content": response.content,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                "model": settings.AZURE_OPENAI_DEPLOYMENT_NAME
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        return len(self.encoding.encode(text))
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """使用LangChain生成文本嵌入"""
        try:
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return None
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入"""
        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return []