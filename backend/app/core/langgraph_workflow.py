from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.core.security_reviewer import SecurityReviewer
from app.models.schemas import WorkflowPhase
import operator

class WorkflowState(TypedDict):
    """工作流状态定义"""
    messages: Annotated[List[Dict[str, str]], operator.add]
    current_phase: str
    user_input: str
    system_prompt: str
    context_files: Optional[List[Dict[str, Any]]]
    project_id: Optional[int]
    
    # 各阶段输出
    requirement_analysis: Optional[str]
    architecture_design: Optional[str]
    rag_plan: Optional[str]
    implementation: Optional[str]
    security_review: Optional[str]
    final_output: Optional[str]
    
    # 元数据
    code_modifications: List[Dict[str, Any]]
    security_warnings: List[str]
    active_personas: List[str]

class LangGraphWorkflow:
    """基于LangGraph的6阶段工作流"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建工作流图"""
        
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("requirement_understanding", self.requirement_understanding)
        workflow.add_node("architecture_design", self.architecture_design)
        workflow.add_node("rag_planning", self.rag_planning)
        workflow.add_node("implementation", self.implementation)
        workflow.add_node("security_review", self.security_review_node)
        workflow.add_node("delivery", self.delivery)
        
        # 定义边
        workflow.set_entry_point("requirement_understanding")
        workflow.add_edge("requirement_understanding", "architecture_design")
        workflow.add_edge("architecture_design", "rag_planning")
        workflow.add_edge("rag_planning", "implementation")
        workflow.add_edge("implementation", "security_review")
        workflow.add_edge("security_review", "delivery")
        workflow.add_edge("delivery", END)
        
        return workflow.compile()
    
    async def requirement_understanding(self, state: WorkflowState) -> WorkflowState:
        """阶段1: 需求理解"""
        
        prompt = f"""You are in the REQUIREMENT UNDERSTANDING phase.

Active Personas: Documentation & PM, Architect

Your task:
1. Extract key points from the user's request
2. Identify any unclear or missing requirements
3. Output a structured understanding of the task

User Input: {state['user_input']}

Provide your analysis in this format:
**Requirement Analysis:**
[Your analysis here]

**Clarification Needed:** (if any)
[List questions or mark as "None"]
"""
        
        response = await self.llm_service.generate_response(
            system_prompt=state['system_prompt'],
            user_message=prompt,
            conversation_history=state.get('messages', []),
            temperature=0.5
        )
        
        state['requirement_analysis'] = response['content'] if response['success'] else "Error in analysis"
        state['current_phase'] = WorkflowPhase.REQUIREMENT.value
        state['active_personas'] = ["documentation_pm", "architect"]
        
        return state
    
    async def architecture_design(self, state: WorkflowState) -> WorkflowState:
        """阶段2: 架构设计"""
        
        prompt = f"""You are in the ARCHITECTURE DESIGN phase.

Active Personas: Architect, Backend Lead

Based on the requirement analysis:
{state.get('requirement_analysis', '')}

Your task:
1. Design system architecture and module division
2. Define key data structures and interfaces
3. Consider scalability and maintainability

Provide your design.
"""
        
        response = await self.llm_service.generate_response(
            system_prompt=state['system_prompt'],
            user_message=prompt,
            conversation_history=state.get('messages', []),
            temperature=0.6
        )
        
        state['architecture_design'] = response['content'] if response['success'] else "Error in design"
        state['current_phase'] = WorkflowPhase.ARCHITECTURE.value
        state['active_personas'] = ["architect", "backend_lead"]
        
        return state
    
    async def rag_planning(self, state: WorkflowState) -> WorkflowState:
        """阶段3: RAG规划"""
        
        context_info = ""
        if state.get('project_id'):
            try:
                results = await self.rag_service.retrieve_context(
                    query=state['user_input'],
                    project_id=state['project_id'],
                    top_k=5
                )
                
                if results:
                    context_info = "\n\nRetrieved Context:\n"
                    for idx, result in enumerate(results, 1):
                        context_info += f"\n{idx}. {result['metadata']['filename']}\n"
            except Exception as e:
                context_info = f"\n\nRAG Error: {str(e)}"
        
        prompt = f"""You are in the RAG PLANNING phase.

Architecture Design:
{state.get('architecture_design', '')}

{context_info}

Your task:
1. Determine if additional file context is needed
2. Specify embedding/chunking strategy if applicable

Provide your plan.
"""
        
        response = await self.llm_service.generate_response(
            system_prompt=state['system_prompt'],
            user_message=prompt,
            conversation_history=state.get('messages', []),
            temperature=0.5
        )
        
        state['rag_plan'] = response['content'] if response['success'] else "Error in RAG planning"
        state['current_phase'] = WorkflowPhase.RAG_PLANNING.value
        state['active_personas'] = ["ai_rag_engineer", "architect"]
        
        return state
    
    async def implementation(self, state: WorkflowState) -> WorkflowState:
        """阶段4: 实现"""
        
        prompt = f"""You are in the IMPLEMENTATION phase.

Previous phases summary:
- Requirement: {state.get('requirement_analysis', '')[:200]}
- Architecture: {state.get('architecture_design', '')[:200]}

Your task:
1. Generate complete, runnable code
2. Follow the Code Modification Protocol

Provide your implementation with clear code blocks.
"""
        
        response = await self.llm_service.generate_response(
            system_prompt=state['system_prompt'],
            user_message=prompt,
            conversation_history=state.get('messages', []),
            temperature=0.7,
            max_tokens=4000
        )
        
        state['implementation'] = response['content'] if response['success'] else "Error in implementation"
        state['current_phase'] = WorkflowPhase.IMPLEMENTATION.value
        state['active_personas'] = ["backend_lead", "frontend_engineer"]
        
        # 解析代码修改
        from app.core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        modifications = engine.parse_code_modifications(state['implementation'])
        state['code_modifications'] = modifications
        
        return state
    
    async def security_review_node(self, state: WorkflowState) -> WorkflowState:
        """阶段5: 安全审查"""
        
        security_issues = []
        for mod in state.get('code_modifications', []):
            issues = SecurityReviewer.review_code(mod.get('content', ''))
            if issues:
                report = SecurityReviewer.generate_security_report(issues)
                security_issues.append(f"File: {mod['file_path']}\n{report}")
        
        prompt = f"""You are in the SECURITY REVIEW phase.

Implementation to review:
{state.get('implementation', '')[:1000]}

Automated Security Scan:
{chr(10).join(security_issues) if security_issues else "No issues detected"}

Your task:
1. Identify potential security vulnerabilities
2. Provide remediation suggestions

Provide your security review.
"""
        
        response = await self.llm_service.generate_response(
            system_prompt=state['system_prompt'],
            user_message=prompt,
            conversation_history=state.get('messages', []),
            temperature=0.3
        )
        
        state['security_review'] = response['content'] if response['success'] else "Error in security review"
        state['current_phase'] = WorkflowPhase.SECURITY_REVIEW.value
        state['active_personas'] = ["security_reviewer"]
        state['security_warnings'] = security_issues
        
        return state
    
    async def delivery(self, state: WorkflowState) -> WorkflowState:
        """阶段6: 交付"""
        
        final_output = f"""# Meta-Agent Development Result

## Summary
{state.get('requirement_analysis', '')}

## Architecture Design
{state.get('architecture_design', '')}

## Implementation
{state.get('implementation', '')}

## Security Review
{state.get('security_review', '')}

## Next Steps
1. Review the generated code
2. Address security warnings if any
3. Test the implementation
"""
        
        state['final_output'] = final_output
        state['current_phase'] = WorkflowPhase.DELIVERY.value
        state['active_personas'] = ["documentation_pm"]
        
        return state
    
    async def run(self, 
                  user_input: str,
                  system_prompt: str,
                  conversation_history: Optional[List[Dict[str, str]]] = None,
                  project_id: Optional[int] = None) -> Dict[str, Any]:
        """运行完整工作流"""
        
        initial_state: WorkflowState = {
            "messages": conversation_history or [],
            "current_phase": "",
            "user_input": user_input,
            "system_prompt": system_prompt,
            "context_files": None,
            "project_id": project_id,
            "requirement_analysis": None,
            "architecture_design": None,
            "rag_plan": None,
            "implementation": None,
            "security_review": None,
            "final_output": None,
            "code_modifications": [],
            "security_warnings": [],
            "active_personas": [],
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "success": True,
                "content": final_state['final_output'],
                "workflow_state": {
                    "current_phase": final_state['current_phase'],
                    "active_personas": final_state['active_personas'],
                },
                "code_modifications": final_state['code_modifications'],
                "security_warnings": final_state['security_warnings'],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }