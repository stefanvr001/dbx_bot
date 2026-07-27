import os
import sys
import json
import uvicorn

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# Custom
from databricks_agent.engine.agent import agent
from databricks_agent.engine.chat_history import chat_history
from databricks_agent.mcp.mcp_server import mcp_server
from databricks_agent.tools.registry import tool_registry

class ChatRequest(BaseModel):
    session_id: str = Field(
        ..., description="Caller-provided session ID for conversation history."
    )
    message: str = Field(
        ..., description="Customer correspondence / chat message text."
    )
    customer_identifier: Optional[str] = Field(
        None, description="Optional customer email, phone, or customer ID."
    )
    override_policy_number: Optional[str] = Field(
        None, description="Optional explicit policy number if selected by user."
    )

class ChatResponse(BaseModel):
    status: str
    session_id: Optional[str] = None
    policy_number: Optional[str] = None
    intent_detected: Optional[str] = None
    tool_called: Optional[str] = None
    agent_response: str
    tool_result: Optional[Dict[str, Any]] = None
    policy_context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None

class MCPRPCRequest(BaseModel):
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="MCP method: tools/list or tools/call")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    id: Optional[Any] = 1

def create_app():
    app = FastAPI(
        title="Databricks Customer Service Agent API",
        description="REST & MCP API for Insurance Customer Service Agent"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check():
        return {"status": "HEALTHY", "service": "Databricks Customer Service Agent API"}

    @app.post("/api/v1/chat", response_model=ChatResponse)
    def process_chat(request: ChatRequest):
        try:
            result = agent.process_message(
                message=request.message,
                session_id=request.session_id,
                customer_identifier=request.customer_identifier,
                override_policy_number=request.override_policy_number
            )
            return ChatResponse(
                status=result["status"],
                session_id=result.get("session_id"),
                policy_number=result.get("policy_number"),
                intent_detected=result.get("intent_detected"),
                tool_called=result.get("tool_called"),
                agent_response=result["agent_response"],
                tool_result=result.get("tool_result"),
                policy_context=result.get("policy_context"),
                conversation_history=result.get("conversation_history")
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/v1/mcp")
    def handle_mcp_rpc(rpc_request: MCPRPCRequest):
        req_json = rpc_request.json()
        resp_json = mcp_server.handle_request(req_json)
        return json.loads(resp_json)

    @app.get("/api/v1/tools")
    def list_registered_tools():
        return {
            "tools_count": len(tool_registry.list_tools()),
            "tools": tool_registry.to_openai_tools(),
            "mcp_manifest": tool_registry.to_mcp_manifest()
        }

    @app.get("/api/v1/history/{session_id}")
    def get_session_history(session_id: str, last_n: Optional[int] = None):
        history = chat_history.get_history(session_id, last_n=last_n)
        meta = chat_history.get_session_meta(session_id)
        return {
            "session_id": session_id,
            "message_count": len(history),
            "session_meta": meta,
            "messages": history
        }

    @app.delete("/api/v1/history/{session_id}")
    def clear_session_history(session_id: str):
        removed = chat_history.clear_session(session_id)
        return {
            "session_id": session_id,
            "cleared": removed
        }

    @app.get("/api/v1/sessions")
    def list_active_sessions():
        return {
            "sessions": chat_history.list_sessions()
        }

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
