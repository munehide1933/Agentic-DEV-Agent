from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ChatRequest, ChatResponse
from app.models.database import get_db
from app.services.conversation_service import ConversationService
from app.core.langgraph_workflow import LangGraphWorkflow
from app.core.workflow_engine import WorkflowEngine
from app.core.code_modifier import CodeModifier

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 全局实例 - 使用LangGraph
langgraph_workflow = LangGraphWorkflow()
workflow_engine = WorkflowEngine()  # 保留用于prompt生成
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
        
        # 5. 构建系统提示词
        system_prompt = workflow_engine.build_system_prompt()
        
        # 6. 使用LangGraph执行完整工作流
        workflow_result = await langgraph_workflow.run(
            user_input=request.message,
            system_prompt=system_prompt,
            conversation_history=history[:-1],
            project_id=request.project_id
        )
        
        if not workflow_result["success"]:
            raise HTTPException(status_code=500, detail=workflow_result.get("error", "Workflow execution error"))
        
        assistant_content = workflow_result["content"]
        code_modifications = workflow_result.get("code_modifications", [])
        security_warnings = workflow_result.get("security_warnings", [])
        
        # 7. 保存助手消息
        assistant_message = await ConversationService.add_message(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_content,
            meta_info={
                "workflow_state": workflow_result.get("workflow_state", {}),
                "code_modifications": code_modifications,
                "security_warnings": security_warnings,
            }
        )
        
        # 8. 构建响应
        workflow_state_data = workflow_result.get("workflow_state", {})
        
        return ChatResponse(
            message_id=assistant_message.id,
            content=assistant_content,
            conversation_id=conversation_id,
            workflow_state={
                "current_phase": workflow_state_data.get("current_phase", ""),
                "active_personas": workflow_state_data.get("active_personas", []),
                "phase_outputs": {},
                "security_flags": security_warnings
            } if workflow_state_data else None,
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
