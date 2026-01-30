from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ChatRequest, ChatResponse
from app.models.database import get_db
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.core.workflow_engine import WorkflowEngine
from app.core.code_modifier import CodeModifier
from app.core.security_reviewer import SecurityReviewer

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 全局实例
workflow_engine = WorkflowEngine()
llm_service = LLMService()
rag_service = RAGService()
code_modifier = CodeModifier()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """发送消息并获取AI响应"""
    
    try:
        # 1. 获取或创建对话
        conversation_id = request.conversation_id
        if not conversation_id:
            if not request.project_id:
                raise HTTPException(status_code=400, detail="project_id is required for new conversation")
            
            conversation = await ConversationService.create_conversation(
                db,
                project_id=request.project_id,
                title=request.message[:50]
            )
            conversation_id = conversation.id
        
        # 2. 保存用户消息
        await ConversationService.add_message(
            db,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        # 3. 获取对话历史
        history = await ConversationService.get_conversation_history(db, conversation_id)
        
        # 4. RAG检索（如果指定了上下文文件）
        context_docs = []
        if request.context_files and request.project_id:
            context_docs = await rag_service.retrieve_context(
                query=request.message,
                project_id=request.project_id,
                top_k=5
            )
        
        # 5. 构建提示词
        system_prompt = workflow_engine.build_system_prompt()
        context_prompt = workflow_engine.build_context_prompt(
            user_message=request.message,
            conversation_history=history[:-1],
            context_files=[
                {
                    "filename": doc["metadata"]["filename"],
                    "file_type": doc["metadata"]["file_type"],
                    "content": doc["text"]
                }
                for doc in context_docs
            ] if context_docs else None
        )
        
        # 6. 调用LLM
        llm_response = await llm_service.generate_response(
            system_prompt=system_prompt,
            user_message=context_prompt,
            conversation_history=None,
            temperature=0.7,
            max_tokens=4000
        )
        
        if not llm_response["success"]:
            raise HTTPException(status_code=500, detail=llm_response.get("error", "LLM service error"))
        
        assistant_content = llm_response["content"]
        
        # 7. 解析代码修改
        code_modifications = workflow_engine.parse_code_modifications(assistant_content)
        
        # 8. 安全审查
        security_warnings = workflow_engine.extract_security_warnings(assistant_content)
        
        for mod in code_modifications:
            issues = SecurityReviewer.review_code(mod["content"])
            if issues:
                security_report = SecurityReviewer.generate_security_report(issues)
                security_warnings.append(security_report)
        
        # 9. 保存助手消息
        assistant_message = await ConversationService.add_message(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_content,
            metadata={
                "workflow_phase": workflow_engine.current_state.current_phase.value,
                "code_modifications": code_modifications,
                "security_warnings": security_warnings,
                "usage": llm_response.get("usage", {})
            }
        )
        
        # 10. 构建响应
        return ChatResponse(
            message_id=assistant_message.id,
            content=assistant_content,
            conversation_id=conversation_id,
            workflow_state=workflow_engine.current_state,
            code_modifications=code_modifications if code_modifications else None,
            suggestions=security_warnings if security_warnings else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-modifications")
async def apply_code_modifications(modifications: list[dict]):
    """应用代码修改"""
    
    results = []
    for mod in modifications:
        result = code_modifier.apply_modification(mod)
        results.append(result)
    
    return {
        "success": all(r["success"] for r in results),
        "results": results
    }
