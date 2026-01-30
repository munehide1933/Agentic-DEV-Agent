from openai import AzureOpenAI
from app.config import settings
from typing import List, Dict, Optional
import tiktoken
import asyncio

class LLMService:
    """Azure OpenAI 集成服务"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def generate_response(self,
                               system_prompt: str,
                               user_message: str,
                               conversation_history: Optional[List[Dict[str, str]]] = None,
                               #temperature: float = 0.7,
                               max_tokens: int = 4000) -> Dict[str, any]:
        """生成响应"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息（控制token数量）
        if conversation_history:
            total_tokens = self.count_tokens(system_prompt)
            for msg in reversed(conversation_history):
                msg_tokens = self.count_tokens(msg["content"])
                if total_tokens + msg_tokens > 16000:
                    break
                messages.insert(1, msg)
                total_tokens += msg_tokens
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model
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
        """生成文本嵌入"""
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                model=self.embedding_deployment,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return None
