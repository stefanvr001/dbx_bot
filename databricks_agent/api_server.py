"""
FastAPI REST API & MCP Server Endpoint for Databricks Customer Service Agent.
Provides endpoints for UI integration, webhooks, chat widgets, and MCP clients.
"""
import os
import sys
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

try:
    from fastapi import FastAPI, HTTPException, Header, Depends
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from databricks_agent.engine.agent import agent
from databricks_agent.tools.registry import tool_registry
from databricks_agent.mcp.mcp_server import mcp_server

# Define Pydantic API Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., description="Customer correspondence / chat message text.")
    customer_identifier: Optional[str] = Field(None, description="Optional customer email, phone, or customer ID.")
    override_policy_number: Optional[str] = Field(None, description="Optional explicit policy number if selected by user.")

class ChatResponse(BaseModel):
    status: str
    policy_number: Optional[str] = None
    intent_detected: Optional[str] = None
    tool_called: Optional[str] = None
    agent_response: str
    tool_result: Optional[Dict[str, Any]] = None
    policy_context: Optional[Dict[str, Any]] = None

class MCPRPCRequest(BaseModel):
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="MCP method: tools/list or tools/call")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    id: Optional[Any] = 1

def create_app():
    """Create and configure the FastAPI app."""
    app = FastAPI(
        title="Databricks Customer Service Agent API",
        description="REST & MCP API for Insurance Customer Service Agent (Document Dispatch, Debit Orders, T&C Q&A)",
        version="1.0.0"
    )
    
    # Enable CORS for Web UI / Chat Widget integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health", tags=["Health"])
    def health_check():
        """Health check endpoint."""
        return {"status": "HEALTHY", "service": "Databricks Customer Service Agent API"}
        
    @app.post("/api/v1/chat", response_model=ChatResponse, tags=["Agent Chat API"])
    def process_chat(request: ChatRequest):
        """
        Primary REST API endpoint for Chatbots, Web UIs, WhatsApp, and Mobile Apps.
        Handles intent classification, policy disambiguation, and tool execution.
        """
        try:
            result = agent.process_message(
                message=request.message,
                customer_identifier=request.customer_identifier,
                override_policy_number=request.override_policy_number
            )
            return ChatResponse(
                status=result["status"],
                policy_number=result.get("policy_number"),
                intent_detected=result.get("intent_detected"),
                tool_called=result.get("tool_called"),
                agent_response=result["agent_response"],
                tool_result=result.get("tool_result"),
                policy_context=result.get("policy_context")
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    @app.post("/api/v1/mcp", tags=["Model Context Protocol (MCP)"])
    def handle_mcp_rpc(rpc_request: MCPRPCRequest):
        """
        Model Context Protocol (MCP) JSON-RPC 2.0 endpoint over HTTP.
        Supports standard `tools/list` and `tools/call` methods.
        """
        import json
        req_json = rpc_request.json()
        resp_json = mcp_server.handle_request(req_json)
        return json.loads(resp_json)
        
    @app.get("/api/v1/tools", tags=["Tools Catalog"])
    def list_registered_tools():
        """Get schema catalog of all registered policy intent tools."""
        return {
            "tools_count": len(tool_registry.list_tools()),
            "tools": tool_registry.to_openai_tools(),
            "mcp_manifest": tool_registry.to_mcp_manifest()
        }

    return app

app = create_app() if FASTAPI_AVAILABLE else None

if __name__ == "__main__":
    if not FASTAPI_AVAILABLE:
        print("FastAPI / uvicorn not installed. Install via: pip install fastapi uvicorn")
    else:
        print("Starting Databricks Customer Service Agent API on http://0.0.0.0:8000 ...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
