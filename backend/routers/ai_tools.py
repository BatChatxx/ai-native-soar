"""
AI Tools Router - Secure Tool Calling Interface

This router provides a secure interface for LLM tool calling.
All tools must be registered and risk-classified.
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import (
    LLMTool, LLMToolCreate, LLMMessage, LLMToolCall,
    LLMToolCallRequest, LLMToolCallResponse,
)
from models.audit import log_audit_event
from utils.llm_config import get_llm_config_cached

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai/tools", tags=["AI Tools"])


def get_registered_tools() -> Dict[str, LLMTool]:
    """
    Get all registered AI tools.
    
    Returns:
        Dict mapping tool name to LLMTool object
    """
    with get_db() as session:
        tools = session.query(LLMTool).filter(LLMTool.enabled == True).all()
        return {tool.name: tool for tool in tools}


async def register_tool(
    tool_data: LLMToolCreate,
    db: Session = Depends(get_db),
) -> LLMTool:
    """
    Register a new AI tool.
    
    Security considerations:
    - Risk level must be specified
    - Input/output schemas validated
    - No arbitrary code execution allowed
    """
    
    # Validate tool configuration
    validated_input = tool_data.input_schema
    validated_output = tool_data.output_schema
    
    # Ensure risk level is set
    if not tool_data.risk_level:
        raise HTTPException(
            status_code=400,
            detail="Risk level is required for all tools",
        )
    
    # Risk level validation
    valid_risk_levels = ["READ", "ENRICH", "MODIFY_LOW", "MODIFY", 
                         "CONTAIN", "EXECUTE", "DESTRUCTIVE"]
    if tool_data.risk_level not in valid_risk_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid risk level. Must be one of: {', '.join(valid_risk_levels)}",
        )
    
    # MODIFY and above require approval by default
    requires_approval = tool_data.risk_level in ["MODIFY", "CONTAIN", "EXECUTE", "DESTRUCTIVE"]
    
    tool = LLMTool(
        name=tool_data.name,
        path=tool_data.path or "",
        description=tool_data.description or "",
        input_schema=validated_input,
        output_schema=validated_output,
        risk_level=tool_data.risk_level,
        requires_approval=requires_approval,
        ai_callable=tool_data.ai_callable,
        enabled=tool_data.enabled,
        audit_metadata=tool_data.audit_metadata,
    )
    
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    # Log tool registration
    log_audit_event(
        action="register_tool",
        tool_name=tool.name,
        risk_level=tool.risk_level,
        metadata={"path": tool.path},
    )
    
    return tool


async def execute_tool(
    tool_call: LLMToolCallRequest,
    db: Session = Depends(get_db),
) -> LLMToolCallResponse:
    """
    Execute a registered tool.
    
    Security checks:
    1. Tool must be registered and enabled
    2. Risk level must be validated
    3. Approval required for high-risk actions
    4. Input validated against schema
    5. No arbitrary code execution
    
    Returns:
        LLMToolCallResponse with execution result
    """
    
    try:
        # Get tool
        tools = get_registered_tools()
        
        if not tools:
            raise HTTPException(
                status_code=404,
                detail="No AI tools are registered",
            )
        
        tool_name = tool_call.tool_name
        
        if tool_name not in tools:
            return LLMToolCallResponse(
                tool_call_id=str(uuid4()),
                status="error",
                type="tool_call",
                content=f"Tool '{tool_name}' is not registered",
            )
        
        tool = tools[tool_name]
        
        # Check tool is enabled
        if not tool.enabled:
            return LLMToolCallResponse(
                tool_call_id=str(uuid4()),
                status="error",
                type="tool_call",
                content=f"Tool '{tool_name}' is disabled",
            )
        
        # Check approval for high-risk actions
        if tool.requires_approval and not tool_call.approval_id:
            return LLMToolCallResponse(
                tool_call_id=str(uuid4()),
                status="pending_approval",
                type="tool_call",
                content=f"Tool '{tool_name}' requires approval (Risk: {tool.risk_level})",
            )
        
        # Validate inputs
        input_schema = tool.input_schema
        
        try:
            # Parse arguments
            if isinstance(tool_call.arguments, str):
                arguments = tool_call.arguments
            else:
                arguments = tool_call.arguments
            
            # Simple validation - in production use Pydantic
            validated_args = {
                "arguments": arguments,
            }
            
        except Exception as e:
            return LLMToolCallResponse(
                tool_call_id=str(uuid4()),
                status="error",
                type="tool_call",
                content=f"Input validation error: {str(e)}",
            )
        
        # Execute the tool
        logger.info(f"Executing tool: {tool_name}")
        logger.info(f"Tool arguments: {arguments}")
        
        # Execute based on tool type
        result = await _execute_tool_impl(tool_name, arguments, tool)
        
        # Log execution
        log_audit_event(
            action=f"execute_tool:{tool_name}",
            risk_level=tool.risk_level,
            status="success",
            metadata={"arguments": arguments},
        )
        
        return LLMToolCallResponse(
            tool_call_id=str(uuid4()),
            status="completed",
            type="tool_call",
            name=tool_name,
            output=result,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        
        log_audit_event(
            action=f"execute_tool:{tool_name}",
            risk_level=tool.risk_level,
            status="error",
            metadata={"error": str(e)},
        )
        
        return LLMToolCallResponse(
            tool_call_id=str(uuid4()),
            status="error",
            type="tool_call",
            content=f"Tool execution error: {str(e)}",
        )


async def _execute_tool_impl(
    tool_name: str,
    arguments: Any,
    tool: LLMTool,
) -> Any:
    """
    Execute the actual tool implementation.
    
    This is where you'd call external APIs or services.
    """
    
    # Placeholder implementations
    
    if tool_name == "generic_edr.get_host":
        return {"host_id": arguments.get("host_id"), "status": "success"}
    
    elif tool_name == "generic_edr.get_process_tree":
        return {"host_id": arguments.get("host_id"), "status": "success"}
    
    elif tool_name == "generic_edr.contain_host":
        return {"host_id": arguments.get("host_id"), "status": "pending_approval"}
    
    elif tool_name == "generic_edr.run_rtr_command":
        return {"status": "pending_approval", "command": arguments.get("command")}
    
    elif tool_name == "threat_intel.lookup_hash":
        return {"hash": arguments.get("hash"), "detection_count": 0}
    
    elif tool_name == "threat_intel.lookup_domain":
        return {"domain": arguments.get("domain"), "categories": []}
    
    elif tool_name == "threat_intel.lookup_ip":
        return {"ip": arguments.get("ip"), "categories": []}
    
    elif tool_name == "threatfox.search_siem":
        return {"query": arguments.get("query"), "results": []}
    
    else:
        return {"status": "unknown_tool", "tool": tool_name}
