from typing import Dict, Any, List, Optional
from app.models.schemas import WorkflowPhase, PersonaRole, WorkflowState
from app.core.personas import PersonaSystem
import re

class WorkflowEngine:
    """6阶段工作流引擎"""
    
    PHASE_ORDER = [
        WorkflowPhase.REQUIREMENT,
        WorkflowPhase.ARCHITECTURE,
        WorkflowPhase.RAG_PLANNING,
        WorkflowPhase.IMPLEMENTATION,
        WorkflowPhase.SECURITY_REVIEW,
        WorkflowPhase.DELIVERY
    ]
    
    def __init__(self):
        self.current_state = WorkflowState(
            current_phase=WorkflowPhase.REQUIREMENT,
            active_personas=[],
            phase_outputs={},
            security_flags=[]
        )
    
    def build_system_prompt(self) -> str:
        """构建完整的系统提示词"""
        return """You are a professional software development agent operating with a multi-persona architecture.

## Multi-Persona Architecture
You operate as a collaborative team of six specialized roles:

1. **Architect**: System design, module division, architecture evaluation
2. **Backend Lead**: Business logic, database modeling, API implementation
3. **Frontend Engineer**: UI structure, state management, frontend optimization
4. **AI/RAG Engineer**: Embedding strategies, vector databases, LangChain integration
5. **Security Reviewer**: Security risk assessment, vulnerability warnings
6. **Documentation & PM**: Requirement clarification, product logic, process modeling

## Development Workflow - 6 Mandatory Phases

### Phase 1: Requirement Understanding
- Extract key points from user's request
- If unclear, activate Requirement Clarification Mechanism
- Output task structure understanding

### Phase 2: Architecture/Design
- Architect + Backend Lead collaborate
- Output modules, data structures, interfaces
- Consider scalability and maintainability

### Phase 3: RAG Planning (if applicable)
- Determine if file context or retrieval needed
- Specify embedding/chunking strategy (300-1200 tokens)
- Recommend embedding model (text-embedding-3-large)
- Request additional files if needed

### Phase 4: Implementation
- Follow Code Modification Protocol
- Generate complete, runnable code
- Mark ADD / MODIFY / DELETE clearly

### Phase 5: Security Review
- Identify potential risks
- Provide remediation suggestions
- Flag security concerns

### Phase 6: Delivery
- Format output according to standard
- Provide next steps

## Code Modification Protocol

When modifying existing code:

```
[File to Modify]: path/to/file.py
[Modification Type]: MODIFY | ADD | DELETE

#--- ORIGINAL SNIPPET START ---
<original code>
#--- ORIGINAL SNIPPET END ---

#--- UPDATED SNIPPET START ---
<modified code>
#--- UPDATED SNIPPET END ---

```

## Output Format Standard

Structure ALL responses:

**Summary:** [Concise summary]

**Analysis:** [Multi-persona collaborative thinking]

**Proposed Workflow:** [Steps to execute]

**Implementation:** [Code in code blocks]

**Optional Enhancements:** [Improvement suggestions]

**Security Review:** [Risk warnings]

**Next Steps:** [Recommended actions]

## Security Constraints
- Never generate malicious code
- Warn about all potential risks
- Protect user-uploaded code confidentiality
- Add minimum necessary permissions

Always maintain professional, helpful, collaborative tone."""
    
    def build_context_prompt(self, 
                            user_message: str,
                            conversation_history: List[Dict[str, str]],
                            context_files: Optional[List[Dict[str, Any]]] = None) -> str:
        """构建上下文提示"""
        
        prompt_parts = []
        
        # 添加对话历史（最近5轮）
        if conversation_history:
            prompt_parts.append("## Recent Conversation History\n")
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"**{role.capitalize()}**: {content[:500]}\n")
        
        # 添加上下文文件
        if context_files:
            prompt_parts.append("\n## Context Files\n")
            for file in context_files:
                prompt_parts.append(f"### {file['filename']} ({file['file_type']})\n")
                prompt_parts.append(f"```\n{file['content'][:2000]}\n```\n")
        
        # 添加当前用户消息
        prompt_parts.append(f"\n## Current User Request\n{user_message}\n")
        
        # 添加工作流指导
        prompt_parts.append(f"\n## Current Workflow Phase\n")
        prompt_parts.append(f"You are currently in: **{self.current_state.current_phase.value.upper()}** phase\n")
        
        active_personas = PersonaSystem.get_active_personas_for_phase(
            self.current_state.current_phase.value
        )
        prompt_parts.append(f"Active Personas: {', '.join([p.value for p in active_personas])}\n")
        
        return "\n".join(prompt_parts)
    
    def advance_phase(self) -> WorkflowPhase:
        """推进到下一阶段"""
        current_idx = self.PHASE_ORDER.index(self.current_state.current_phase)
        if current_idx < len(self.PHASE_ORDER) - 1:
            self.current_state.current_phase = self.PHASE_ORDER[current_idx + 1]
        return self.current_state.current_phase
    
    def parse_code_modifications(self, response: str) -> List[Dict[str, Any]]:
        """解析代码修改块"""
        modifications = []
        
        pattern = r'\[File to Modify\]:\s*(.+?)\n\[Modification Type\]:\s*(.+?)\n(.*?)(?=\[File to Modify\]:|$)'
        matches = re.finditer(pattern, response, re.DOTALL)
                        
        for match in matches:
            file_path = match.group(1).strip()
            mod_type = match.group(2).strip()
            content = match.group(3).strip()
            
            modifications.append({
                "file_path": file_path,
                "modification_type": mod_type,
                "content": content
            })
        
        return modifications
    
    def extract_security_warnings(self, response: str) -> List[str]:
        """提取安全警告"""
        warnings = []
        
        security_section = re.search(
            r'\*\*Security Review:\*\*(.*?)(?=\*\*Next Steps:|\*\*Optional|$)',
            response,
            re.DOTALL
        )
        
        if security_section:
            content = security_section.group(1)
            warning_pattern = r'[-•]\s*[⚠️⚡🔒]?\s*\*\*(.+?)\*\*:?\s*(.+?)(?=\n[-•]|\n\n|$)'
            warning_matches = re.finditer(warning_pattern, content, re.DOTALL)
            
            for match in warning_matches:
                warnings.append(f"{match.group(1)}: {match.group(2).strip()}")
        
        return warnings
